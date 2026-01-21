import logging
import time
from datetime import datetime
from typing import Dict, Any
import json
from pathlib import Path
from backend.core.config import settings

logger = logging.getLogger(__name__)

class MonitoringService:
    def __init__(self):
        self.logs_dir = settings.LOGS_DIR
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup file handlers
        self.prediction_log = self.logs_dir / "predictions.log"
        self.access_log = self.logs_dir / "access.log"
        self.error_log = self.logs_dir / "error.log"
        
        # Initialize logs
        self._initialize_logs()
    
    def _initialize_logs(self):
        """Initialize log files with headers"""
        timestamp = datetime.utcnow().isoformat()
        
        # Ensure logs directory exists and is writable
        try:
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Try to set permissions (works on Unix-like systems)
            try:
                import os
                os.chmod(str(self.logs_dir), 0o777)  # RWX for all
            except:
                pass  # Ignore permission errors on Windows or if not supported
        except Exception as e:
            logger.warning(f"Cannot create logs directory: {e}")
            # Fallback to console logging only
            self.prediction_log = None
            self.access_log = None
            self.error_log = None
            return
        
        try:
            if not self.prediction_log.exists():
                with open(self.prediction_log, 'w', encoding='utf-8') as f:
                    f.write(f"# Khmer Transliteration - Predictions Log\n")
                    f.write(f"# Started: {timestamp}\n")
                    f.write(f"# Format: JSON lines\n\n")
        except PermissionError as e:
            logger.warning(f"Cannot create prediction log: {e}")
            self.prediction_log = None
        
        try:
            if not self.access_log.exists():
                with open(self.access_log, 'w', encoding='utf-8') as f:
                    f.write(f"# Khmer Transliteration - Access Log\n")
                    f.write(f"# Started: {timestamp}\n")
                    f.write(f"# Format: JSON lines\n\n")
        except PermissionError as e:
            logger.warning(f"Cannot create access log: {e}")
            self.access_log = None
        
        try:
            if not self.error_log.exists():
                with open(self.error_log, 'w', encoding='utf-8') as f:
                    f.write(f"# Khmer Transliteration - Error Log\n")
                    f.write(f"# Started: {timestamp}\n")
                    f.write(f"# Format: JSON lines\n\n")
        except PermissionError as e:
            logger.warning(f"Cannot create error log: {e}")
            self.error_log = None
    
    def log_prediction(self, data: Dict[str, Any]):
        """
        Log prediction details
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'prediction',
            'data': data
        }
        
        self._write_log(self.prediction_log, log_entry)
        logger.info(f"📝 Prediction: '{data.get('input', '?')}' -> '{data.get('output', '?')}'")
    
    def log_access(self, request_data: Dict[str, Any], response_data: Dict[str, Any]):
        """
        Log API access
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'access',
            'request': request_data,
            'response': response_data
        }
        
        self._write_log(self.access_log, log_entry)
    
    def log_error(self, error_data: Dict[str, Any]):
        """
        Log error details
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'error',
            'data': error_data
        }
        
        self._write_log(self.error_log, log_entry)
        logger.error(f"❌ Error: {error_data.get('error', 'Unknown')}")
    
    def log_user_feedback(self, feedback_data: Dict[str, Any]):
        """
        Log user feedback
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'feedback',
            'data': feedback_data
        }
        
        self._write_log(self.prediction_log, log_entry)
        logger.info(f"⭐ Feedback: {feedback_data.get('prediction_id', '?')}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get system metrics from log files
        """
        try:
            # Count predictions from console logs
            prediction_count = 0
            error_count = 0
            feedback_count = 0
            
            # Try to get counts from log files if they exist
            if self.prediction_log and self.prediction_log.exists():
                prediction_count = self._count_log_entries(self.prediction_log, 'prediction')
                feedback_count = self._count_log_entries(self.prediction_log, 'feedback')
            
            if self.error_log and self.error_log.exists():
                error_count = self._count_log_entries(self.error_log, 'error')
            
            return {
                'total_predictions': prediction_count,
                'total_errors': error_count,
                'total_feedback': feedback_count,
                'log_files': {
                    'predictions': str(self.prediction_log) if self.prediction_log else 'Not available',
                    'access': str(self.access_log) if self.access_log else 'Not available',
                    'error': str(self.error_log) if self.error_log else 'Not available'
                }
            }
        except Exception as e:
            logger.error(f"Failed to get metrics: {str(e)}")
            return {}
    
    def _write_log(self, log_file: Path, data: Dict[str, Any]):
        """Write log entry to file or fallback to console"""
        if log_file is None:
            # Fallback to console logging
            logger.info(f"Log entry (file not available): {data}")
            return
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        except PermissionError:
            logger.warning(f"Permission denied for log file: {log_file}")
        except Exception as e:
            logger.error(f"Failed to write log: {str(e)}")
    
    def _count_log_entries(self, log_file: Path, entry_type: str) -> int:
        """Count log entries of specific type"""
        if not log_file or not log_file.exists():
            return 0
        
        try:
            count = 0
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        try:
                            entry = json.loads(line)
                            if entry.get('type') == entry_type:
                                count += 1
                        except json.JSONDecodeError:
                            continue
            return count
        except Exception as e:
            logger.error(f"Failed to count log entries: {str(e)}")
            return 0

# Singleton instance
monitoring_service = MonitoringService()