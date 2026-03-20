from App.database import db
from datetime import datetime

class AssetAssignment(db.Model):
    __tablename__ = "asset_assignment"

    assignment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.String(50), db.ForeignKey('asset.asset_id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    floor_id = db.Column(db.String(50), db.ForeignKey('floor.floor_id'), nullable=False)
    assignment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)

    asset = db.relationship('Asset', backref='assignments', lazy=True)
    employee = db.relationship('Employee', backref='assignments', lazy=True)
    room = db.relationship('Room', backref='assignments', lazy=True)

    def __init__(self, asset_id, employee_id, floor_id, assignment_date=None, return_date=None):
        self.asset_id = asset_id
        self.employee_id = employee_id
        self.floor_id = floor_id
        self.assignment_date = assignment_date if assignment_date else datetime.utcnow()
        self.return_date = return_date

    def get_json(self):
        return {
            'assignment_id': self.assignment_id,
            'asset_id': self.asset_id,
            'employee_id': self.employee_id,
            'floor_id': self.floor_id,
            'assignment_date': self.assignment_date,
            'return_date': self.return_date
        }

    def __repr__(self):
        return f"<AssetAssignment {self.assignment_id}>"

    def __str__(self):
        return f'Assignment {self.assignment_id} (Asset: {self.asset_id}, Employee: {self.employee_id}, Floor: {self.floor_id})'