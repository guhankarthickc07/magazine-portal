from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    passed_out_year = db.Column(db.String(10), nullable=True)  # Only for alumni
    location = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Student, Alumni, Admin
    profile_img = db.Column(db.String(200), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)  # Admin Approval

    # Relationship with Magazine
    magazines = db.relationship('Magazine', backref='user', lazy=True)

class Magazine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    pdf_file = db.Column(db.String(200), nullable=False)
    image_file = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)  # Admin Approval
