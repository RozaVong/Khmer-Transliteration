#!/usr/bin/env python3
"""
Setup database for Khmer Transliteration System
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database.connection import Database
from backend.database.migrations import run_initial_migration
from backend.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("=" * 60)
    print("Database Setup for Khmer Transliteration System")
    print("=" * 60)
    
    print(f"📊 Using database: {settings.DATABASE_URL[:50]}...")
    
    # Test connection
    print("\n1. Testing database connection...")
    try:
        if Database.check_connection():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        sys.exit(1)
    
    # Run migrations
    print("\n2. Running database migrations...")
    try:
        if run_initial_migration():
            print("✅ Database migrations completed successfully")
        else:
            print("❌ Database migrations failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Migration error: {str(e)}")
        sys.exit(1)
    
    # Verify tables
    print("\n3. Verifying tables...")
    try:
        # Check predictions table
        result = Database.execute_query("SELECT COUNT(*) as count FROM predictions", fetch_one=True)
        if result:
            print(f"✅ Predictions table: {result['count']} rows")
        else:
            print("✅ Predictions table created")
        
        # Check feedback table
        result = Database.execute_query("SELECT COUNT(*) as count FROM feedback", fetch_one=True)
        if result:
            print(f"✅ Feedback table: {result['count']} rows")
        else:
            print("✅ Feedback table created")
        
        print("\n" + "=" * 60)
        print("✅ Database setup completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error verifying tables: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()