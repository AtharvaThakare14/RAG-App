"""
Global pytest configuration
"""
import os
import sys
from unittest.mock import MagicMock, patch

# ------------------------------------------------------------------------------
# Path Configuration
# ------------------------------------------------------------------------------

# Add the project root to the system path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

# Add the src directory to the system path
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# ------------------------------------------------------------------------------
# Environment Setup
# ------------------------------------------------------------------------------

# Set AWS default region for boto3
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# ------------------------------------------------------------------------------
# Mock Setup
# ------------------------------------------------------------------------------

# Mock response for Secrets Manager
mock_secret_response = MagicMock()
mock_secret_response.return_value = {"SecretString": '{"GEMINI_API_KEY": "test-api-key"}'}

# Mock boto3
mock_boto3 = MagicMock()
mock_client = MagicMock()
mock_resource = MagicMock()
mock_client.get_secret_value = mock_secret_response
mock_boto3.client.return_value = mock_client
mock_boto3.resource.return_value = mock_resource

# Mock Google Gemini
mock_google = MagicMock()
mock_genai = MagicMock()
mock_genai_types = MagicMock()
mock_genai_client = MagicMock()

# Mock PostgreSQL
mock_psycopg2 = MagicMock()
mock_psycopg2_extensions = MagicMock()
mock_psycopg2_extensions.ISOLATION_LEVEL_AUTOCOMMIT = 0

# Mock LangChain
mock_langchain = MagicMock()
mock_document_loaders = MagicMock()
mock_text_splitter = MagicMock()
mock_schema = MagicMock()
mock_langchain_community = MagicMock()
mock_langchain_community_document_loaders = MagicMock()

# ------------------------------------------------------------------------------
# Mock Classes
# ------------------------------------------------------------------------------

# Create a Document class for LangChain
class MockDocument:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}

# ------------------------------------------------------------------------------
# Module Injection into sys.modules
# ------------------------------------------------------------------------------

sys.modules['boto3'] = mock_boto3
sys.modules['botocore'] = MagicMock()
sys.modules['botocore.exceptions'] = MagicMock()
sys.modules['psycopg2'] = mock_psycopg2
sys.modules['psycopg2.extensions'] = mock_psycopg2_extensions
sys.modules['google'] = mock_google
sys.modules['google.genai'] = mock_genai
sys.modules['google.genai.types'] = mock_genai_types
sys.modules['langchain'] = mock_langchain
sys.modules['langchain.document_loaders'] = mock_document_loaders
sys.modules['langchain.text_splitter'] = mock_text_splitter
sys.modules['langchain.schema'] = mock_schema
sys.modules['langchain.schema'].Document = MockDocument
sys.modules['langchain_community'] = mock_langchain_community
sys.modules['langchain_community.document_loaders'] = mock_langchain_community_document_loaders
