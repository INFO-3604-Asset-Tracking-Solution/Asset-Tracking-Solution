from App.database import db

class Room(db.Model):

    __tablename__ = "room"

    room_id = db.Column(db.Integer, primary_key=True, unique=True)
    room_code = db.Column(db.String(20), unique=True, nullable=False)  
    floor_id = db.Column(db.String(30),  nullable=False)
    building_id = db.Column(db.String(30), nullable=False)
    room_name = db.Column(db.String(50), nullable=False)

    assignments = db.relationship('AssetAssignment', backref='room', lazy=True)
    checkevents = db.relationship('CheckEvent', backref='room', lazy=True)


    def __init__(self, room_code, floor_id, building_id,room_name):
        self.room_code= room_code
        self.floor_id = floor_id
        self.building_id = building_id
        self.room_name = room_name


    def get_json(self):
        return {
            'room_id': self.room_id,
            'room_code': self.room_code,
            'floor_id': self.floor_id,
            'building_id': self.building_id,
            'room_name': self.room_name
        }