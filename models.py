from datetime import datetime
from flask_login import UserMixin
from app import db  

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)  # Add this line
    password = db.Column(db.String(255), nullable=False)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(100), nullable=True)
    cover_photo = db.Column(db.String(100), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)
    country = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    timeline_events = db.relationship('TimelineEvent', backref='profile', lazy=True, cascade="all, delete-orphan")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def __repr__(self):
        return f'<Profile {self.name}>'

class TimelineEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    event_text = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Remove the back_populates to avoid conflict
    # profile = db.relationship('Profile', back_populates='timeline_events')