from App.database import db

class Floor(db.Model):
    __tablename__ = 'floor'
    floor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.building_id'), nullable=False)
    floor_name = db.Column(db.String(100), nullable=False)

    # rooms = db.relationship('Room', backref='floor', lazy=True, cascade="all, delete-orphan")

    def __init__(self, building_id, floor_name):
        self.building_id = building_id
        self.floor_name = floor_name

    def get_json(self):
        return {
            'floor_id': self.floor_id,
            'building_id': self.building_id,
            'floor_name': self.floor_name
        }

    def __repr__(self):
        return f'<Floor {self.floor_id}: {self.floor_name} (Building {self.building_id})>'
