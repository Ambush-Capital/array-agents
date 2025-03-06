import logging
import os
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


def setup_logger(
    logger_name=None,
    log_level=logging.INFO,
    log_format=None,
    date_format="%Y-%m-%d %H:%M:%S",
    log_file=None,
    max_bytes=10485760,  # 10MB
    backup_count=5,
    file_log_level=None,
    console_output=True,
    console_log_level=None,
    propagate=False,
    timed_rotation=False,
    when='midnight',
    encoding='utf-8',
):
    """
    Setup and configure a logger with customizable parameters.
    
    Args:
        logger_name (str, optional): Name of the logger. If None, the root logger is used.
        log_level (int, optional): Default log level for all handlers. Defaults to logging.INFO.
        log_format (str, optional): Format string for log messages.
                                   If None, a default format is used.
        date_format (str, optional): Format string for dates in log messages.
        log_file (str, optional): Path to the log file. If None, file logging is disabled.
        max_bytes (int, optional): Maximum size of log file before rotation (for RotatingFileHandler).
        backup_count (int, optional): Number of backup log files to keep.
        file_log_level (int, optional): Log level for file handler.
                                       If None, the default log_level is used.
        console_output (bool, optional): Whether to enable console logging. Defaults to True.
        console_log_level (int, optional): Log level for console handler.
                                         If None, the default log_level is used.
        propagate (bool, optional): Whether the logger should propagate to parent loggers.
        timed_rotation (bool, optional): Use TimedRotatingFileHandler instead of RotatingFileHandler.
        when (str, optional): Interval type for TimedRotatingFileHandler rotation.
                            Options: 'S', 'M', 'H', 'D', 'W0'-'W6', 'midnight'.
        encoding (str, optional): Encoding for log files.
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Use default format if none is provided
    if log_format is None:
        log_format = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    
    # Create formatter
    formatter = logging.Formatter(log_format, date_format)
    
    # Get logger
    logger = logging.getLogger(logger_name)
    
    # Clear existing handlers if any
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Set the log level
    logger.setLevel(log_level)
    
    # Set propagation
    logger.propagate = propagate
    
    # Setup console handler if enabled
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(console_log_level if console_log_level is not None else log_level)
        logger.addHandler(console_handler)
    
    # Setup file handler if log_file is provided
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Setup file handler with appropriate rotation
        if timed_rotation:
            file_handler = TimedRotatingFileHandler(
                log_file,
                when=when,
                backupCount=backup_count,
                encoding=encoding
            )
        else:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding=encoding
            )
        
        file_handler.setFormatter(formatter)
        file_handler.setLevel(file_log_level if file_log_level is not None else log_level)
        logger.addHandler(file_handler)
    
    return logger

