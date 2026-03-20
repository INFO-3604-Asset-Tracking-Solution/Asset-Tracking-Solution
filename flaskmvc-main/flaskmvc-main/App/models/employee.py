from App.database import db

class Employee(db.Model):

    __tablename__ = "employee"

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)


    def __init__(self, fname, lname=None, email=None):
        self.fname = fname
        self.lname = lname
        self.email = email


    def get_json(self):
        return {
            'id': self.id,
            'fname': self.fname,
            'lname': self.lname,
            'email': self.email
        }


    def __repr__(self):
        return f'<Assignee {self.fname} {self.lname}>'