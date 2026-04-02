from App.database import db

class Room(db.Model):

    __tablename__ = "room"

    room_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    floor_id = db.Column(db.Integer, db.ForeignKey('floor.floor_id'), nullable=False)
    room_name = db.Column(db.String(50), nullable=False)

    assignments = db.relationship('AssetAssignment', backref='room', lazy=True)
    checkevents = db.relationship('CheckEvent', backref='room', lazy=True)


    def __init__(self, floor_id, room_name):
        self.floor_id = floor_id
        self.room_name = room_name


    def get_json(self):
        return {
            'room_id': self.room_id,
            'floor_id': self.floor_id,
            'room_name': self.room_name
        }