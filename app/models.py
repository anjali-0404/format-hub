from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    files = db.relationship('File', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    original_filename = db.Column(db.String(128))
    cloudinary_url = db.Column(db.String(256))
    public_id = db.Column(db.String(128))
    file_type = db.Column(db.String(32))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    conversions = db.relationship('Conversion', backref='file', lazy='dynamic')

class Conversion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    output_format = db.Column(db.String(32))
    cloudinary_url = db.Column(db.String(256))
    public_id = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
