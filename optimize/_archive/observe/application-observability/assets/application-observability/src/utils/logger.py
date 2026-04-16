"""
Logging Configuration Module

Provides centralized logging setup with color-coded console output.
"""

import logging
import sys
from typing import Optional
import colorlog


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with color-coded console output.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create console handler with color formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Color formatter
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def log_api_call(logger: logging.Logger, endpoint: str, status: int, duration: float):
    """
    Log an API call with details.
    
    Args:
        logger: Logger instance
        endpoint: API endpoint called
        status: HTTP status code
        duration: Request duration in seconds
    """
    if status >= 200 and status < 300:
        logger.info(f"API Call: {endpoint} - Status: {status} - Duration: {duration:.2f}s")
    elif status >= 400:
        logger.error(f"API Call Failed: {endpoint} - Status: {status} - Duration: {duration:.2f}s")
    else:
        logger.warning(f"API Call: {endpoint} - Status: {status} - Duration: {duration:.2f}s")


def log_error(logger: logging.Logger, error: Exception, context: Optional[dict] = None):
    """
    Log an error with context information.
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context information
    """
    error_msg = f"Error: {type(error).__name__}: {str(error)}"
    
    if context:
        context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
        error_msg += f" | Context: {context_str}"
    
    logger.error(error_msg, exc_info=True)

# Made with Bob
