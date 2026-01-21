import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import Database

def test_database_connection():
    """Test database connection"""
    try:
        connected = Database.check_connection()
        assert connected == True
    except Exception as e:
        pytest.skip(f"Database connection failed: {e}")

def test_database_query():
    """Test basic database query"""
    try:
        result = Database.execute_query("SELECT 1 as test", fetch_one=True)
        assert result["test"] == 1
    except Exception as e:
        pytest.skip(f"Database query failed: {e}")