from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with the Role table
    role = db.relationship('Role', back_populates='users')

    def get_id(self):
        return str(self.user_id)

class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(30), nullable=False, default='user')
    description = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with the User table
    users = db.relationship('User', back_populates='role')

class SystemMetric(db.Model):
    __tablename__ = 'metrics'
    id = db.Column(db.Integer, primary_key=True)
    system_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    cpu = db.Column(db.Float)
    memory = db.Column(db.Float)
