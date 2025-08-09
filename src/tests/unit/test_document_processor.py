"""Test cases for the document_processor Lambda function."""
import json
import os
import unittest
from unittest.mock import MagicMock, patch

"""Set up test environment."""
# Set environment variables
os.environ["DOCUMENTS_BUCKET"] = "test-bucket"
os.environ["METADATA_TABLE"] = "test-table"
os.environ["STAGE"] = "test"
os.environ["DB_SECRET_ARN"] = "test-db-secret"
os.environ["GEMINI_SECRET_ARN"] = "test-gemini-secret"
os.environ["GEMINI_EMBEDDING_MODEL"] = "test-embedding-model"
os.environ["TEMPERATURE"] = "0.2"
os.environ["MAX_OUTPUT_TOKENS"] = "1024"
os.environ["TOP_K"] = "40"
os.environ["TOP_P"] = "0.8"
os.environ["SIMILARITY_THRESHOLD"] = "0.7"

# Now import the module under test - mocks are already in place globally from conftest
from document_processor.document_processor import (
    handler, get_gemini_api_key, get_postgres_credentials, get_postgres_connection,
    embed_query, embed_documents, get_document_loader, chunk_documents, process_document
)

class TestDocumentProcessor(unittest.TestCase):
    """Test cases for the document_processor Lambda function."""

    def setUp(self):
        
        # Mock boto3 clients
        self.client_patcher = patch('document_processor.document_processor.client')
        self.mock_client = self.client_patcher.start()
        self.s3_patcher = patch("document_processor.document_processor.s3_client")
        self.dynamodb_patcher = patch("document_processor.document_processor.dynamodb")
        self.secrets_patcher = patch("document_processor.document_processor.secretsmanager")
        
        self.mock_s3 = self.s3_patcher.start()
        self.mock_dynamodb = self.dynamodb_patcher.start()
        self.mock_secretsmanager = self.secrets_patcher.start()
        
        # Set up DynamoDB table mock
        self.mock_table = MagicMock()
        self.mock_dynamodb.Table.return_value = self.mock_table

    def tearDown(self):
        """Clean up test environment."""
        # Clean up environment variables
        for key in [
            "DOCUMENTS_BUCKET", "METADATA_TABLE", "STAGE", "DB_SECRET_ARN",
            "GEMINI_SECRET_ARN", "GEMINI_EMBEDDING_MODEL", "TEMPERATURE",
            "MAX_OUTPUT_TOKENS", "TOP_K", "TOP_P", "SIMILARITY_THRESHOLD"
        ]:
            if key in os.environ:
                del os.environ[key]
                
        # Stop patchers
        self.s3_patcher.stop()
        self.dynamodb_patcher.stop()
        self.secrets_patcher.stop()

    @patch("document_processor.document_processor.secretsmanager")
    def test_get_gemini_api_key(self, mock_secretsmanager):
        """Test getting Gemini API key from Secrets Manager."""
        # Mock the Secrets Manager response
        mock_secret_string = json.dumps({"GEMINI_API_KEY": "mock-api-key"})
        mock_response = {"SecretString": mock_secret_string}
        mock_secretsmanager.get_secret_value.return_value = mock_response

        # Call the function
        api_key = get_gemini_api_key()

        # Verify results
        self.assertEqual(api_key, "mock-api-key")
        mock_secretsmanager.get_secret_value.assert_called_once_with(
            SecretId="test-gemini-secret"
        )
        
    @patch("document_processor.document_processor.secretsmanager")
    def test_get_postgres_credentials(self, mock_secretsmanager):
        """Test getting PostgreSQL credentials from Secrets Manager."""
        # Mock the Secrets Manager response
        mock_credentials = {
            "host": "test-host",
            "port": 5432,
            "username": "test-user",
            "password": "test-password",
            "dbname": "test-db"
        }
        mock_response = {"SecretString": json.dumps(mock_credentials)}
        mock_secretsmanager.get_secret_value.return_value = mock_response

        # Call the function
        credentials = get_postgres_credentials()

        # Verify results
        self.assertEqual(credentials, mock_credentials)
        mock_secretsmanager.get_secret_value.assert_called_once_with(
            SecretId="test-db-secret"
        )

    @patch("document_processor.document_processor.psycopg2")
    def test_get_postgres_connection(self, mock_psycopg2):
        """Test getting a PostgreSQL connection."""
        # Mock the psycopg2 connection
        mock_conn = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn

        # Test credentials
        credentials = {
            "host": "test-host",
            "port": 5432,
            "username": "test-user",
            "password": "test-password",
            "dbname": "test-db"
        }

        # Call the function
        conn = get_postgres_connection(credentials)

        # Verify results
        self.assertEqual(conn, mock_conn)
        mock_psycopg2.connect.assert_called_once_with(
            host="test-host",
            port=5432,
            user="test-user",
            password="test-password",
            dbname="test-db"
        )

    @patch("document_processor.document_processor.client")
    def test_embed_query(self, mock_client):
        """Test embedding a query using Gemini."""
        # Mock the Gemini embedding response
        mock_embeddings = MagicMock()
        mock_embeddings.embeddings = [MagicMock()]
        mock_embeddings.embeddings[0].values = [0.1, 0.2, 0.3]
        mock_client.models.embed_content.return_value = mock_embeddings

        # Call the function
        result = embed_query("Test query")

        # Verify results
        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_client.models.embed_content.assert_called_once()

    @patch("document_processor.document_processor.embed_query")
    def test_embed_documents(self, mock_embed_query):
        """Test embedding multiple documents."""
        # Mock the embed_query function
        mock_embed_query.side_effect = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6]
        ]

        # Test documents
        docs = ["Document 1", "Document 2"]

        # Call the function
        result = embed_documents(docs)

        # Verify results
        self.assertEqual(result, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        self.assertEqual(mock_embed_query.call_count, 2)
        mock_embed_query.assert_any_call("Document 1")
        mock_embed_query.assert_any_call("Document 2")

    @patch("document_processor.document_processor.PyPDFLoader")
    def test_get_document_loader_pdf(self, mock_loader_class):
        """Test getting document loader for PDF files."""
        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader
        
        loader = get_document_loader("test.pdf", "application/pdf")
        
        self.assertEqual(loader, mock_loader)
        mock_loader_class.assert_called_once_with("test.pdf")

    @patch("document_processor.document_processor.TextLoader")
    def test_get_document_loader_text(self, mock_loader_class):
        """Test getting document loader for text files."""
        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader
        
        loader = get_document_loader("test.txt", "text/plain")
        
        self.assertEqual(loader, mock_loader)
        mock_loader_class.assert_called_once_with("test.txt")

    @patch("document_processor.document_processor.CSVLoader")
    def test_get_document_loader_csv(self, mock_loader_class):
        """Test getting document loader for CSV files."""
        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader
        
        loader = get_document_loader("test.csv", "text/csv")
        
        self.assertEqual(loader, mock_loader)
        mock_loader_class.assert_called_once_with("test.csv")

    @patch("document_processor.document_processor.TextLoader")
    def test_get_document_loader_unknown(self, mock_loader_class):
        """Test getting document loader for unknown file types."""
        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader
        
        loader = get_document_loader("test.unknown", "application/octet-stream")
        
        self.assertEqual(loader, mock_loader)
        mock_loader_class.assert_called_once_with("test.unknown")

    @patch("document_processor.document_processor.RecursiveCharacterTextSplitter")
    def test_chunk_documents(self, mock_splitter_class):
        """Test chunking documents."""
        # Mock the splitter
        mock_splitter = MagicMock()
        mock_splitter_class.return_value = mock_splitter
        
        # Mock the split_documents method
        mock_chunks = ["chunk1", "chunk2"]
        mock_splitter.split_documents.return_value = mock_chunks
        
        # Test documents
        docs = ["doc1", "doc2"]
        
        # Call the function
        result = chunk_documents(docs)
        
        # Verify results
        self.assertEqual(result, mock_chunks)
        mock_splitter_class.assert_called_once_with(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        mock_splitter.split_documents.assert_called_once_with(docs)

    @patch("document_processor.document_processor.tempfile")
    @patch("document_processor.document_processor.get_document_loader")
    @patch("document_processor.document_processor.chunk_documents")
    @patch("document_processor.document_processor.embed_query")
    @patch("document_processor.document_processor.get_postgres_credentials")
    @patch("document_processor.document_processor.get_postgres_connection")
    @patch("document_processor.document_processor.os.unlink")
    @patch("document_processor.document_processor.uuid.uuid4")
    @patch("document_processor.document_processor.datetime")
    def test_process_document(
        self, mock_datetime, mock_uuid, mock_unlink, mock_get_conn, mock_get_creds,
        mock_embed, mock_chunk, mock_loader, mock_tempfile
    ):
        """Test processing a document."""
        # Mock datetime
        mock_now = MagicMock()
        mock_datetime.now.return_value = mock_now
        
        # Mock the temporary file
        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/test_file"
        mock_tempfile.NamedTemporaryFile.return_value.__enter__.return_value = mock_temp_file
        
        # Mock UUID
        mock_uuid.side_effect = ["chunk-1", "chunk-2"]
        
        # Mock document loader
        mock_doc_loader = MagicMock()
        mock_loader.return_value = mock_doc_loader
        
        # Create mock documents
        class MockDocument:
            def __init__(self, page_content, metadata):
                self.page_content = page_content
                self.metadata = metadata
        
        mock_documents = [
            MockDocument("Content 1", {"page": 1}),
            MockDocument("Content 2", {"page": 2})
        ]
        mock_doc_loader.load.return_value = mock_documents
        
        # Mock chunking
        mock_chunks = [
            MockDocument("Chunk 1", {"page": 1}),
            MockDocument("Chunk 2", {"page": 2})
        ]
        mock_chunk.return_value = mock_chunks
        
        # Mock embedding
        mock_embed.side_effect = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6]
        ]
        
        # Mock PostgreSQL connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock credentials
        mock_get_creds.return_value = {"host": "test-host"}
        
        # Test parameters
        bucket = "test-bucket"
        key = "uploads/user-1/doc-1/test.pdf"
        document_id = "doc-1"
        user_id = "user-1"
        mime_type = "application/pdf"
        
        # Call the function
        num_chunks, chunk_ids = process_document(bucket, key, document_id, user_id, mime_type)
        
        # Verify results
        self.assertEqual(num_chunks, 2)
        self.assertEqual(chunk_ids, ["chunk-1", "chunk-2"])
        
        # Verify S3 download
        self.mock_s3.download_file.assert_called_once_with(
            bucket, key, "/tmp/test_file"
        )
        
        # Verify temporary file cleanup
        mock_unlink.assert_called_once_with("/tmp/test_file")
        
        # Verify document insertion
        mock_cursor.execute.assert_any_call(
            """
        INSERT INTO documents (document_id, user_id, file_name, mime_type, status, bucket, key, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
            unittest.mock.ANY  # We don't need to check the exact values here
        )
        
        # Verify chunk insertions
        self.assertEqual(mock_cursor.execute.call_count, 3)  # 1 for document + 2 for chunks

    def test_handler_healthcheck(self):
        """Test the Lambda handler for a health check."""
        # Create a health check event
        event = {"action": "healthcheck"}

        # Call the handler
        response = handler(event, {})

        # Verify results
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Document processor is healthy")
        self.assertEqual(response_body["stage"], "test")

    @patch("document_processor.document_processor.process_document")
    def test_handler_s3_event(self, mock_process):
        """Test the Lambda handler for an S3 event."""
        # Mock the process_document function
        mock_process.return_value = (2, ["chunk-1", "chunk-2"])
        
        # Create an S3 event
        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {
                            "name": "test-bucket"
                        },
                        "object": {
                            "key": "uploads/user-1/doc-1/test.pdf"
                        }
                    }
                }
            ]
        }

        # Call the handler
        response = handler(event, {})

        # Verify results
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Successfully processed document: doc-1")
        self.assertEqual(response_body["document_id"], "doc-1")
        self.assertEqual(response_body["num_chunks"], 2)
        
        # Verify process_document call
        mock_process.assert_called_once_with(
            "test-bucket", "uploads/user-1/doc-1/test.pdf", "doc-1", "user-1", "application/pdf"
        )
        
        # Verify DynamoDB put_item call
        self.mock_table.put_item.assert_called_once()

    def test_handler_direct_invocation(self):
        """Test the Lambda handler for a direct invocation with no Records."""
        # Create a direct invocation event (no Records)
        event = {}

        # Call the handler
        response = handler(event, {})

        # Verify results
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Document processor is healthy")
        self.assertEqual(response_body["stage"], "test")


if __name__ == "__main__":
    unittest.main()