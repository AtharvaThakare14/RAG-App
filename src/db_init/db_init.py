"""
Lambda function to initialize the PostgreSQL database with pgvector extension.
"""
import os
import json
import boto3
import logging
import psycopg2
import time
import socket
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
secretsmanager = boto3.client('secretsmanager')

# Get environment variables
DB_SECRET_ARN = os.environ.get('DB_SECRET_ARN')
STAGE = os.environ.get('STAGE')
MAX_RETRIES = int(os.environ.get('MAX_RETRIES'))
RETRY_DELAY = int(os.environ.get('RETRY_DELAY'))  # seconds


def get_postgres_credentials():
    """
    Get PostgreSQL credentials from Secrets Manager.
    """
    try:
        secret_response = secretsmanager.get_secret_value(
            SecretId=DB_SECRET_ARN
        )
        secret = json.loads(secret_response['SecretString'])
        return secret
    except Exception as e:
        logger.error(f"Error getting PostgreSQL credentials: {str(e)}")
        raise e


def check_dns_resolution(host):
    """
    Check if hostname can be resolved to an IP address.
    
    Args:
        host (str): Hostname to resolve
        
    Returns:
        bool: True if hostname can be resolved, False otherwise
    """
    try:
        socket.gethostbyname(host)
        return True
    except socket.gaierror:
        return False


def create_database_if_not_exists(credentials, dbname, retry_count=0):
    """
    Create the database if it doesn't exist.
    
    Args:
        credentials (dict): PostgreSQL credentials
        dbname (str): Database name
        retry_count (int): Current retry attempt count
    
    Returns:
        bool: True if successful, False otherwise
    """
    host = credentials['host']
    
    # Check if DNS can resolve the host
    if not check_dns_resolution(host):
        if retry_count < MAX_RETRIES:
            logger.warning(f"Could not resolve hostname '{host}'. Retrying in {RETRY_DELAY}s ({retry_count + 1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
            return create_database_if_not_exists(credentials, dbname, retry_count + 1)
        else:
            logger.error(f"Could not resolve hostname '{host}' after {MAX_RETRIES} attempts.")
            return False
    
    try:
        # Connect to the default 'postgres' database to create the new database if needed
        logger.info(f"Connecting to PostgreSQL at {host} to create database if needed")
        conn = psycopg2.connect(
            host=credentials['host'],
            port=credentials['port'],
            user=credentials['username'],
            password=credentials['password'],
            dbname='postgres',
            connect_timeout=10
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'")
        exists = cursor.fetchone()
        
        if not exists:
            logger.info(f"Creating database '{dbname}'...")
            cursor.execute(f"CREATE DATABASE {dbname}")
            logger.info(f"Database '{dbname}' created successfully")
        else:
            logger.info(f"Database '{dbname}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        if retry_count < MAX_RETRIES:
            logger.warning(f"Database connection error: {str(e)}. Retrying in {RETRY_DELAY}s ({retry_count + 1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
            return create_database_if_not_exists(credentials, dbname, retry_count + 1)
        else:
            logger.error(f"Database connection error after {MAX_RETRIES} attempts: {str(e)}")
            return False
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        return False


def initialize_database(credentials, retry_count=0):
    """
    Initialize the database with pgvector extension and schema.
    
    Args:
        credentials (dict): PostgreSQL credentials
        retry_count (int): Current retry attempt count
    
    Returns:
        bool: True if successful, False otherwise
    """
    host = credentials['host']
    dbname = credentials['dbname']
    
    # Check if DNS can resolve the host
    if not check_dns_resolution(host):
        if retry_count < MAX_RETRIES:
            logger.warning(f"Could not resolve hostname '{host}'. Retrying in {RETRY_DELAY}s ({retry_count + 1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
            return initialize_database(credentials, retry_count + 1)
        else:
            logger.error(f"Could not resolve hostname '{host}' after {MAX_RETRIES} attempts.")
            return False
    
    try:
        # Connect to the database
        logger.info(f"Connecting to database '{dbname}' at {host} to initialize schema")
        conn = psycopg2.connect(
            host=credentials['host'],
            port=credentials['port'],
            user=credentials['username'],
            password=credentials['password'],
            dbname=credentials['dbname'],
            connect_timeout=10
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create pgvector extension if it doesn't exist
        logger.info("Creating pgvector extension...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        # Create documents table
        logger.info("Creating documents table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            document_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            file_name TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            status TEXT NOT NULL,
            bucket TEXT NOT NULL,
            key TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """)
        
        # Create index on document_id
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_documents_document_id ON documents (document_id)
        """)
        
        # Create index on user_id
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents (user_id)
        """)
        
        # Create chunks table with vector support
        logger.info("Creating chunks table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id SERIAL PRIMARY KEY,
            chunk_id TEXT NOT NULL,
            document_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata JSONB,
            embedding VECTOR(768),
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """)
        
        # Create index on document_id
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks (document_id)
        """)
        
        # Create index on user_id
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_chunks_user_id ON chunks (user_id)
        """)
        
        # Create vector index on embedding - wrap in try/except as this could fail
        # if pgvector doesn't fully support the version of Postgres
        try:
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
            """)
        except Exception as e:
            logger.warning(f"Failed to create vector index (this is OK if using older PostgreSQL): {str(e)}")
            # Try creating a simpler index without IVF
            try:
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks
                USING btree (embedding)
                """)
                logger.info("Created fallback BTree index on embedding column")
            except Exception as e2:
                logger.warning(f"Failed to create fallback index: {str(e2)}")
        
        logger.info("Database initialization completed successfully")
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        if retry_count < MAX_RETRIES:
            logger.warning(f"Database connection error: {str(e)}. Retrying in {RETRY_DELAY}s ({retry_count + 1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
            return initialize_database(credentials, retry_count + 1)
        else:
            logger.error(f"Database connection error after {MAX_RETRIES} attempts: {str(e)}")
            return False
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False


def handler(event, context):
    """
    Lambda function handler to initialize the PostgreSQL database.
    """
    logger.info(f"Starting database initialization for stage: {STAGE}")
    
    try:
        # Check if this is a health check
        if isinstance(event, dict) and event.get('action') == 'healthcheck':
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'DB initialization function is healthy',
                    'stage': STAGE
                })
            }
        
        # Get PostgreSQL credentials
        credentials = get_postgres_credentials()
        
        logger.info(f"Attempting to initialize database at {credentials['host']}")
        
        # Create database if it doesn't exist
        if not create_database_if_not_exists(credentials, credentials['dbname']):
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Failed to create database. Please check that the RDS instance is available.'
                })
            }
        
        # Initialize database
        if not initialize_database(credentials):
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Failed to initialize database schema. Please check logs for details.'
                })
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Database initialization completed successfully'
            })
        }
        
    except Exception as e:
        logger.error(f"Error in database initialization: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"Error in database initialization: {str(e)}"
            })
        }