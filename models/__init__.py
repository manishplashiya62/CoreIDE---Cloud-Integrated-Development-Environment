from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Expose models
from .user import User
from .project import Project
from .file import File
from .history import ExecutionHistory
