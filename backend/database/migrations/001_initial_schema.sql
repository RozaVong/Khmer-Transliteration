import logging
from backend.database.connection import Database

logger = logging.getLogger(__name__)

def run_initial_migration():
    """Run initial database migration with your exact schema"""
    try:
        logger.info("Running initial database migration...")
        
        # Enable UUID extension
        try:
            Database.execute_query("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
            logger.info("[OK] UUID extension enabled")
        except Exception as e:
            logger.warning(f"Could not enable UUID extension: {str(e)}")
        
        # Create predictions table EXACTLY as in your SQL
        Database.execute_query("""
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
        logger.info("[OK] Predictions table created")

        # Create feedback table EXACTLY as in your SQL
        Database.execute_query("""
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
        logger.info("[OK] Feedback table created")

        # Create system_metrics table EXACTLY as in your SQL
        Database.execute_query("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(100) NOT NULL,
                metric_value FLOAT NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("[OK] System metrics table created")

        # Create indexes EXACTLY as in your SQL
        Database.execute_query("""
            CREATE INDEX IF NOT EXISTS idx_predictions_created_at 
            ON predictions(created_at DESC)
        """)

        Database.execute_query("""
            CREATE INDEX IF NOT EXISTS idx_predictions_confidence 
            ON predictions(confidence)
        """)

        Database.execute_query("""
            CREATE INDEX IF NOT EXISTS idx_feedback_prediction_id 
            ON feedback(prediction_id)
        """)

        Database.execute_query("""
            CREATE INDEX IF NOT EXISTS idx_feedback_rating 
            ON feedback(rating)
        """)

        Database.execute_query("""
            CREATE INDEX IF NOT EXISTS idx_metrics_recorded_at 
            ON system_metrics(recorded_at DESC)
        """)
        logger.info("[OK] Indexes created")

        # Create function to update timestamps EXACTLY as in your SQL
        Database.execute_query("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        """)

        # Create triggers for updated_at EXACTLY as in your SQL
        Database.execute_query("""
            DROP TRIGGER IF EXISTS update_predictions_updated_at ON predictions
        """)

        Database.execute_query("""
            CREATE TRIGGER update_predictions_updated_at
                BEFORE UPDATE ON predictions
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()
        """)

        Database.execute_query("""
            DROP TRIGGER IF EXISTS update_feedback_updated_at ON feedback
        """)

        Database.execute_query("""
            CREATE TRIGGER update_feedback_updated_at
                BEFORE UPDATE ON feedback
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()
        """)
        logger.info("[OK] Triggers created")

        logger.info("[OK] Database migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    run_initial_migration()