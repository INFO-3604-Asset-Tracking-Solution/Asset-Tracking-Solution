from App.database import db
from datetime import datetime
from sqlalchemy import Enum
from nanoid import generate

def generate_short_id():
    return generate(size=8)

class Audit(db.Model):
    __tablename__ = 'audit'

    audit_id = db.Column(db.String(30), primary_key=True, default=generate_short_id)
    initiator_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(Enum('pending', 'in_progress', 'completed', name='audit_status'), nullable=False)

    relocations = db.relationship('Relocation', backref='audit', lazy=True)
    missing_devices = db.relationship('MissingDevice', backref='audit', lazy=True)

    def __init__(self, initiator_id, status, start_date=None, end_date=None):
        self.initiator_id = initiator_id
        self.status = status
        self.start_date = start_date if start_date else datetime.utcnow()
        self.end_date = end_date

    def get_json(self):
        return {
            'id': self.id,
            'initiator_id': self.initiator_id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'status': self.status
        }