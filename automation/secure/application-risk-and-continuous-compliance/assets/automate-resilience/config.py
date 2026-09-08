"""
Configuration module for IBM Concert Dashboard
Handles environment variables, logging setup, and application configuration
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Logs directory
LOGS_DIR = PROJECT_ROOT / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# IBM Concert API Configuration
CONCERT_BASE_URL = os.getenv('CONCERT_BASE_URL', '')
C_API_KEY = os.getenv('C_API_KEY', '')
INSTANCE_ID = os.getenv('INSTANCE_ID', '')

# Application Configuration
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', '8050'))

# API Configuration
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
API_PAGE_LIMIT = int(os.getenv('API_PAGE_LIMIT', '100'))

def setup_logging():
    """
    Configure logging for the application
    Logs to both file and console with appropriate formatting
    """
    log_file = LOGS_DIR / 'app.log'
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

def validate_config():
    """
    Validate required configuration parameters
    Raises ValueError if critical configuration is missing
    """
    errors = []
    
    if not CONCERT_BASE_URL:
        errors.append("CONCERT_BASE_URL is not set")
    
    if not C_API_KEY:
        errors.append("C_API_KEY is not set")
    
    if not INSTANCE_ID:
        errors.append("INSTANCE_ID is not set")
    
    if errors:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)
    
    return True

# Initialize logging
logger = setup_logging()
logger.info("Configuration module loaded")
logger.info(f"Concert Base URL: {CONCERT_BASE_URL}")
logger.info(f"Instance ID: {INSTANCE_ID}")
logger.info(f"Debug Mode: {DEBUG_MODE}")

# Made with Bob
