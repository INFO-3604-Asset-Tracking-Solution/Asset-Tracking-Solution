from App.database import db
from sqlalchemy import Enum
from datetime import datetime
from nanoid import generate

def generate_short_id():
    return generate(size=10)

class CheckEvent(db.Model):

    __tablename__ = "checkevent"

    check_id = db.Column(db.String(30), primary_key=True, default=generate_short_id)
    audit_id = db.Column(db.String(30), db.ForeignKey('audit.audit_id'), nullable=False)
    asset_id = db.Column(db.String(50), db.ForeignKey('asset.asset_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    found_room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), nullable=False)
    condition = db.Column(
        Enum('Good', 'Needs Repair', 'Beyond Repair', name='condition_enum'),
        nullable=False
    )

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


    def __init__(self, audit_id, asset_id, user_id, found_room_id, condition):
        self.audit_id = audit_id
        self.asset_id = asset_id
        self.user_id = user_id
        self.found_room_id = found_room_id
        self.condition = condition


    def get_json(self):
        return {
            "check_id": self.check_id,
            "audit_id": self.audit_id,
            "asset_id": self.asset_id,
            "user_id": self.user_id,
            "found_room_id": self.found_room_id,
            "condition": self.condition,
            "timestamp": self.timestamp
        }