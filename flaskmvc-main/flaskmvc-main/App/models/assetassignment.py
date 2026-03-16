from App.database import db
from datetime import datetime

class AssetAssignment(db.Model):

    __tablename__ = "assetassignment"

    assignment_id = db.Column(db.String(50), primary_key=True)
    asset_id = db.Column(db.String(50), db.ForeignKey('asset.asset_id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('assignee.id'), nullable=False)
    room_id = db.Column(db.String(30), db.ForeignKey('room.room_id'), nullable=False)
    condition = db.Column(
        db.Enum('Good', 'Needs Repair', 'Beyond Repair', name='condition_enum'),
        nullable=False
    )
    assignment_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)


    def __init__(self, assignment_id, asset_id, assignee_id, room_id, condition):
        self.assignment_id = assignment_id
        self.asset_id = asset_id
        self.assignee_id = assignee_id
        self.room_id = room_id
        self.condition = condition


    def get_json(self):
        return {
            'assignment_id': self.assignment_id,
            'asset_id': self.asset_id,
            'assignee_id': self.assignee_id,
            'room_id': self.room_id,
            'condition': self.condition,
            'assignment_date': self.assignment_date,
            'return_date': self.return_date
        }


    def __repr__(self):
        return f"<AssetAssignment {self.assignment_id}>"