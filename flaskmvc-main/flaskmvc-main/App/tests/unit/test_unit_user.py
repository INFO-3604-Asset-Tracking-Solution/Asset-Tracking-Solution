

import unittest
from werkzeug.security import generate_password_hash
from App.models import User

class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User( "bob@gmail.com", "bob", "bobpass")
        self.assertEqual(user.id, None)
        self.assertEqual(user.username, "bob")
        #assert user.email == "bob@gmail.com"
        self.assertEqual(user.email, "bob@gmail.com")
       # self.assertEqual(user.password, "bobpass")
        

    # pure function no side effects or integrations called
    def test_get_json(self):
        user = User( "bob@gmail.com", "bob", "bobpass")
        user_json = user.get_json()
        self.assertDictEqual(user_json, {"id":None, "email":"bob@gmail.com", "username":"bob" })
    
    def test_hashed_password(self):
        password = "mypass"
        hashed = generate_password_hash(password, method='sha256')
        user = User("bob@gmail.com", "bob", password)
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob@gmail.com", "bob", password)
        assert user.check_password(password)