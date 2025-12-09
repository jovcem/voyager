"""Configuration management"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', 5432)),
    'database': os.getenv('DATABASE_NAME', 'voyager'),
    'user': os.getenv('DATABASE_USER', 'voyager_user'),
    'password': os.getenv('DATABASE_PASSWORD', 'voyager_password')
}

def get_config():
    """Get application configuration"""
    return {
        'database': DB_CONFIG,
        'app_name': 'Voyager Price Scraper',
        'version': '1.0.0',
    }
