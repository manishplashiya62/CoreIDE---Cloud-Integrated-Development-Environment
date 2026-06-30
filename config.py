import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'web-ide-secure-dev-key-1948')
    DEBUG = True
    
    # AI Chatbot configuration
    AI_API_KEY = os.environ.get('AI_API_KEY', '')
    AI_API_URL = os.environ.get('AI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent')

    
    # Path configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # SQLite Database configuration
    DATABASE_DIR = os.path.join(BASE_DIR, 'database')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(DATABASE_DIR, 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload and Run configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    TEMP_EXECUTION_DIR = os.path.join(UPLOAD_FOLDER, 'temp_executions')
    
    # Logs directory
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    
    # Execution constraints
    MAX_EXECUTION_TIME = 5.0  # seconds
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
    
    @classmethod
    def init_app(cls):
        # Create directories if they don't exist
        os.makedirs(cls.DATABASE_DIR, exist_ok=True)
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(cls.TEMP_EXECUTION_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
