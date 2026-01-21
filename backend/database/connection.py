import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
import logging
import time
from backend.core.config import settings

logger = logging.getLogger(__name__)

class Database:
    _pool = None
    
    @classmethod
    def initialize_pool(cls):
        """Initialize connection pool with retries"""
        if cls._pool is None and settings.DATABASE_URL:
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Creating database connection pool (attempt {attempt + 1}/{max_retries})...")
                    cls._pool = SimpleConnectionPool(
                        minconn=1,
                        maxconn=5,  # Reduced for memory efficiency
                        dsn=settings.DATABASE_URL,
                        cursor_factory=RealDictCursor
                    )
                    logger.info("✅ Database connection pool created")
                    return True
                except Exception as e:
                    logger.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"❌ Failed to create connection pool after {max_retries} attempts")
                        return False
        return True
    
    @classmethod
    def get_pool(cls):
        """Get or create connection pool"""
        if cls._pool is None:
            cls.initialize_pool()
        return cls._pool
    
    @classmethod
    def get_connection(cls):
        """Get connection from pool"""
        pool = cls.get_pool()
        if pool:
            try:
                return pool.getconn()
            except Exception as e:
                logger.error(f"Failed to get connection: {str(e)}")
                raise
        return None
    
    @classmethod
    def return_connection(cls, conn):
        """Return connection to pool"""
        pool = cls.get_pool()
        if pool and conn:
            try:
                pool.putconn(conn)
            except Exception as e:
                logger.error(f"Failed to return connection: {str(e)}")
    
    @classmethod
    def execute_query(cls, query, params=None, fetch_one=False, fetch_all=False):
        """Execute SQL query safely"""
        conn = None
        cursor = None
        try:
            conn = cls.get_connection()
            if not conn:
                raise Exception("No database connection available")
            
            cursor = conn.cursor()
            
            # Log query (truncated for security)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Executing query: {query[:100]}...")
                if params:
                    logger.debug(f"Params: {params}")
            
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
                conn.commit()
                return result
            elif fetch_all:
                result = cursor.fetchall()
                conn.commit()
                return result
            else:
                conn.commit()
                return cursor.rowcount
                
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"❌ Database error: {str(e)}")
            logger.error(f"Query: {query[:200]}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                cls.return_connection(conn)
    
    @classmethod
    def check_connection(cls):
        """Check if database connection works"""
        if not settings.DATABASE_URL:
            logger.warning("No DATABASE_URL configured")
            return False
        
        conn = None
        try:
            conn = cls.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            
            logger.debug("✅ Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {str(e)}")
            return False
        finally:
            if conn:
                cls.return_connection(conn)

    @classmethod
    def setup_tables(cls):
        """Setup basic database tables if they don't exist"""
        try:
            # Check if predictions table exists
            cls.execute_query("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id VARCHAR(255) PRIMARY KEY,
                    input_text TEXT NOT NULL,
                    output_text TEXT NOT NULL,
                    confidence FLOAT NOT NULL,
                    user_ip VARCHAR(50),
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create feedback table
            cls.execute_query("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    prediction_id VARCHAR(255) REFERENCES predictions(id) ON DELETE CASCADE,
                    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                    comment TEXT,
                    user_ip VARCHAR(50),
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            logger.info("✅ Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to setup tables: {str(e)}")
            return False