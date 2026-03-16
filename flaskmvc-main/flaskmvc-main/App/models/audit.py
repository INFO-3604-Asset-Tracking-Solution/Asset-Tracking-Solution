from App.database import db
from datetime import datetime

class Audit(db.Model):
    __tablename__ = 'audit'

    id = db.Column(db.String(30), primary_key=True)
    initiator_id = db.Column(db.String(30), db.ForeignKey('user.user_id'), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False)

    relocations = db.relationship('Relocation', backref='audit', lazy=True)
    missing_devices = db.relationship('MissingDevice', backref='audit', lazy=True)

    def __init__(self, id, initiator_id, status, start_date=None, end_date=None):
        self.id = id
        self.initiator_id = initiator_id
        self.status = status
        self.start_date = start_date if start_date else datetime.utcnow()
        self.end_date = end_date