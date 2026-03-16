from App.database import db

class Assignee(db.Model):

    __tablename__ = "assignee"

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    room_id = db.Column(db.String(30), db.ForeignKey('room.room_id'), nullable=True)


    room = db.relationship('Room', backref=db.backref('assignees', lazy=True))


    def __init__(self, fname, lname=None, email=None, room_id=None):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.room_id = room_id


    def get_json(self):
        return {
            'id': self.id,
            'fname': self.fname,
            'lname': self.lname,
            'email': self.email,
            'room_id': self.room_id
        }


    def __repr__(self):
        return f'<Assignee {self.fname} {self.lname}>'