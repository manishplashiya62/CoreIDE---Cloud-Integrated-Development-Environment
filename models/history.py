from datetime import datetime, timezone
from models import db

class ExecutionHistory(db.Model):
    __tablename__ = 'execution_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    source_code = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=True)
    error = db.Column(db.Text, nullable=True)
    execution_time = db.Column(db.Float, nullable=True)  # in seconds
    memory_usage = db.Column(db.Float, nullable=True)    # in MB
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    user = db.relationship('User', backref=db.backref('execution_history', lazy=True, cascade="all, delete-orphan"))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'language': self.language,
            'source_code': self.source_code,
            'output': self.output,
            'error': self.error,
            'execution_time': self.execution_time,
            'memory_usage': self.memory_usage,
            'created_at': self.created_at.isoformat()
        }
