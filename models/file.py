from datetime import datetime, timezone
from models import db

class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    is_folder = db.Column(db.Boolean, default=False, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('files.id', ondelete='CASCADE'), nullable=True)
    language = db.Column(db.String(50), nullable=True)
    content = db.Column(db.Text, nullable=True)  # Store code content if file, empty if folder
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Self-referential relationship for directory structure
    children = db.relationship('File', 
                               backref=db.backref('parent', remote_side=[id]),
                               cascade="all, delete-orphan",
                               lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'is_folder': self.is_folder,
            'parent_id': self.parent_id,
            'language': self.language,
            'content': self.content if not self.is_folder else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
