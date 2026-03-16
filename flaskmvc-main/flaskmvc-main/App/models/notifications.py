from App.database import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notification'

    notif_id = db.Column(db.String(30), primary_key=True)
    check_id = db.Column(db.String(30), db.ForeignKey('check_event.check_event_id'), nullable=False)
    recipient_id = db.Column(db.String(30), db.ForeignKey('user.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    recipient = db.relationship('User', backref='notifications', lazy=True)
    check_event = db.relationship('CheckEvent', backref='notifications', lazy=True)

    def __init__(self, notif_id, check_id, recipient_id, message, timestamp=None):
        self.notif_id = notif_id
        self.check_id = check_id
        self.recipient_id = recipient_id
        self.message = message
        self.timestamp = timestamp if timestamp else datetime.utcnow()