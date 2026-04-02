from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from sqlalchemy import Enum

class User(db.Model):

    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(
        Enum('Administrator', 'Manager', 'Auditor', name='role_enum'),
        nullable=False
    )

    audits = db.relationship('Audit', backref='user', lazy=True)
    checkevents = db.relationship('CheckEvent', backref='user', lazy=True)


    def __init__(self, email, username, password, role):
        self.email = email
        self.username = username
        self.role = role
        self.set_password(password)


    def get_json(self):
        return {
            'user id': self.user_id,
            'email': self.email,
            'username': self.username,
            'role': self.role
        }


    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)


    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)