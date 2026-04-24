"""
Configuration Management Module

Loads and validates environment variables for the Instana Observability Dashboard.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    
    # Instana Configuration
    INSTANA_BASE_URL: str = os.getenv("INSTANA_BASE_URL", "")
    INSTANA_API_TOKEN: str = os.getenv("INSTANA_API_TOKEN", "")
    INSTANA_APPLICATION_NAME: str = os.getenv("INSTANA_APPLICATION_NAME", "finvault")
    
    # Application Configuration
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8050"))
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Data Settings
    REFRESH_INTERVAL: int = int(os.getenv("REFRESH_INTERVAL", "300"))
    DEFAULT_TIMEFRAME: int = int(os.getenv("DEFAULT_TIMEFRAME", "3600000"))  # 1 hour in ms
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate required configuration parameters.
        
        Returns:
            bool: True if all required parameters are present
            
        Raises:
            ValueError: If required configuration is missing
        """
        required = [
            ("INSTANA_BASE_URL", cls.INSTANA_BASE_URL),
            ("INSTANA_API_TOKEN", cls.INSTANA_API_TOKEN),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}. "
                f"Please check your .env file."
            )
        
        return True
    
    @classmethod
    def get_instana_headers(cls) -> dict:
        """
        Get HTTP headers for Instana API requests.
        
        Returns:
            dict: Headers dictionary with authorization token
        """
        return {
            "Authorization": f"apiToken {cls.INSTANA_API_TOKEN}",
            "Content-Type": "application/json"
        }


# Validate configuration on module import
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️  Configuration Error: {e}")
    print("Please copy .env.example to .env and configure it with your credentials.")

# Made with Bob
