from App.database import db
from datetime import datetime
import uuid

class Notification(db.Model):
    __tablename__ = 'notification'

    notif_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    audit_id = db.Column(db.String(30), db.ForeignKey('audit.audit_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # recipient = db.relationship('User', backref='notifications', lazy=True)
    # audit = db.relationship('Audit', backref='notifications', lazy=True)

    def __init__(self, audit_id, recipient_id, message, timestamp=None):
        self.audit_id = audit_id
        self.recipient_id = recipient_id
        self.message = message
        self.timestamp = timestamp if timestamp else datetime.utcnow()

    def get_json(self):
        return {
            'notif_id': self.notif_id,
            'audit_id': self.audit_id,
            'recipient_id': self.recipient_id,
            'message': self.message,
            'timestamp': self.timestamp
        }