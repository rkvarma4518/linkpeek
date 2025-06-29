from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))  # 'user', 'provider', 'admin'
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    contact = db.Column(db.String(20))
    profession = db.Column(db.String(50))  # For providers only
    verified = db.Column(db.Boolean, default=False)
    about = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile = db.relationship('ProviderProfile', backref='user', uselist=False)
    
    is_email_verified = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

class ProviderProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    service_info = db.Column(db.Text)
    image_path = db.Column(db.String(150))
    video_path = db.Column(db.String(150))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ProviderProfile {self.full_name}>'
    
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))         # The user who gave the rating
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'))     # The provider who is rated
    rating = db.Column(db.Integer)  # 1–5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], backref='given_ratings')
    provider = db.relationship('User', foreign_keys=[provider_id], backref='received_ratings')