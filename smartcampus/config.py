import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application configuration settings
APP_NAME = os.getenv("APP_NAME", "Smart Campus Management System")
SECRET_KEY = os.getenv("SECRET_KEY", "smart_campus_secret_key_default")
DATABASE_PATH = os.getenv("DATABASE_PATH", "database")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Ensure the database directory exists
os.makedirs(DATABASE_PATH, exist_ok=True)
