from App.database import db
from datetime import datetime

class Relocation(db.Model):
    __tablename__ = 'relocation'

    relocation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    audit_id = db.Column(db.Integer, db.ForeignKey('audit.id'), nullable=False)
    found_in_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    audit = db.relationship('Audit', backref='relocations', lazy=True)
    missing_devices_found = db.relationship('MissingDevice', backref='found_relocation', lazy=True)

    def __init__(self, audit_id, found_in_id):
        self.audit_id = audit_id
        self.found_in_id = found_in_id

    def get_json(self):
        return {
            'relocation_id': self.relocation_id,
            'audit_id': self.audit_id,
            'found_in_id': self.found_in_id,
            'date': self.date
        }