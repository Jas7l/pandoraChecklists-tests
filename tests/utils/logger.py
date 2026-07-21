import os
import logging
from datetime import datetime
from typing import Optional
from tests.config.settings import settings


class Logger:
    """Logger for test logging"""

    _loggers: dict = {}

    @staticmethod
    def get_logger(
        name: str,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
    ) -> logging.Logger:
        """Get logger instance"""

        if name in Logger._loggers:
            return Logger._loggers[name]

        logger = logging.getLogger(name)

        # Clear any existing handlers to avoid duplicates
        logger.handlers = []
        logger.propagate = False

        logger.setLevel(log_level or settings.log_level)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level or settings.log_level or 'INFO')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        if log_file is None:
            project_root = (
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            )
            logs_dir = os.path.join(project_root, 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = os.path.join(logs_dir, f'test_{timestamp}.log')

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level or settings.log_level or 'INFO')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        Logger._loggers[name] = logger
        return logger


def get_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """Logger instance"""

    return Logger.get_logger(name, log_level)
