import logging
import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.log import Log
from app.core.config import settings
from loguru import logger

class LoggingService:
    """로깅 서비스 - 데이터베이스와 파일에 로그 저장"""
    
    @staticmethod
    def setup_logging():
        """로깅 설정"""
        # Create logs directory if it doesn't exist
        os.makedirs(settings.LOG_FILE_PATH, exist_ok=True)
        
        # Configure loguru
        logger.remove()  # Remove default handler
        
        # Add console handler
        logger.add(
            lambda msg: print(msg, end=""),
            level=settings.LOG_LEVEL,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        
        # Add file handler for daily logs
        logger.add(
            f"{settings.LOG_FILE_PATH}/app_{{time:YYYY-MM-DD}}.log",
            level=settings.LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="00:00",  # Rotate at midnight
            retention="30 days",  # Keep logs for 30 days
            compression="zip"
        )
        
        # Add error file handler
        logger.add(
            f"{settings.LOG_FILE_PATH}/error_{{time:YYYY-MM-DD}}.log",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="00:00",
            retention="90 days",
            compression="zip"
        )
    
    @staticmethod
    def log_to_db(level: str, message: str, module: str = None, function: str = None, 
                  user_id: int = None, product_id: int = None, context: dict = None, 
                  traceback: str = None, ip_address: str = None, user_agent: str = None,
                  request_path: str = None, request_method: str = None):
        """데이터베이스에 로그 저장"""
        try:
            db = SessionLocal()
            log_entry = Log(
                level=level.upper(),
                message=message,
                module=module,
                function=function,
                user_id=user_id,
                product_id=product_id,
                context=context,
                traceback=traceback,
                ip_address=ip_address,
                user_agent=user_agent,
                request_path=request_path,
                request_method=request_method
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            # Fallback to file logging if database fails
            logger.error(f"Failed to save log to database: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def log_info(message: str, **kwargs):
        """정보 로그"""
        logger.info(message)
        LoggingService.log_to_db("INFO", message, **kwargs)
    
    @staticmethod
    def log_warning(message: str, **kwargs):
        """경고 로그"""
        logger.warning(message)
        LoggingService.log_to_db("WARNING", message, **kwargs)
    
    @staticmethod
    def log_error(message: str, **kwargs):
        """에러 로그"""
        logger.error(message)
        LoggingService.log_to_db("ERROR", message, **kwargs)
    
    @staticmethod
    def log_debug(message: str, **kwargs):
        """디버그 로그"""
        logger.debug(message)
        LoggingService.log_to_db("DEBUG", message, **kwargs)
    
    @staticmethod
    def log_critical(message: str, **kwargs):
        """치명적 오류 로그"""
        logger.critical(message)
        LoggingService.log_to_db("CRITICAL", message, **kwargs)
    
    @staticmethod
    def log_exception(message: str, exception: Exception, **kwargs):
        """예외 로그"""
        import traceback
        logger.exception(message)
        LoggingService.log_to_db(
            "ERROR", 
            message, 
            traceback=traceback.format_exc(),
            **kwargs
        )
    
    @staticmethod
    def get_log_stats(days: int = 7):
        """로그 통계 조회"""
        try:
            db = SessionLocal()
            from datetime import datetime, timedelta
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get logs within date range
            logs = db.query(Log).filter(
                Log.created_at >= start_date,
                Log.created_at <= end_date
            ).all()
            
            # Calculate statistics
            total_logs = len(logs)
            level_counts = {}
            module_counts = {}
            
            for log in logs:
                # Count by level
                level_counts[log.level] = level_counts.get(log.level, 0) + 1
                
                # Count by module
                if log.module:
                    module_counts[log.module] = module_counts.get(log.module, 0) + 1
            
            # Get error logs
            error_logs = [log for log in logs if log.level == "ERROR"]
            
            return {
                "total_logs": total_logs,
                "error_count": len(error_logs),
                "level_distribution": level_counts,
                "module_distribution": module_counts,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Failed to get log stats: {str(e)}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def cleanup_old_logs(days: int = 30):
        """오래된 로그 정리"""
        try:
            db = SessionLocal()
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Count logs to be deleted
            count = db.query(Log).filter(Log.created_at < cutoff_date).count()
            
            # Delete old logs
            db.query(Log).filter(Log.created_at < cutoff_date).delete()
            db.commit()
            
            logger.info(f"Cleaned up {count} old log entries")
            return count
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {str(e)}")
            db.rollback()
            return 0
        finally:
            db.close()

# Initialize logging when module is imported
LoggingService.setup_logging()
