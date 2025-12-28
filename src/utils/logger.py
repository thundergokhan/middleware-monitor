import logging
import os
import sys
from logging.handlers import RotatingFileHandler
import colorama

# Initialize colorama
colorama.init()

class EnterpriseLogger:
    """
    Centralized logging configuration for the middleware monitor.
    Supports both Console (colored) and File logging.
    """
    
    _instance = None

    @staticmethod
    def get_logger(name="MiddlewareMonitor"):
        """
        Static access method for the logger.
        """
        if EnterpriseLogger._instance is None:
            EnterpriseLogger._instance = EnterpriseLogger._setup_logger(name)
        return EnterpriseLogger._instance

    @staticmethod
    def _setup_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'app.log')

        # Formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )

        # File Handler (Rotating)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)

        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger

# Convenience function
def get_logger(name="MiddlewareMonitor"):
    return EnterpriseLogger.get_logger(name)
