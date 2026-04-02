

import unittest
from App.models import User

class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User("bob@gmail.com", "bob", "bobpass", "Auditor")
        self.assertEqual(user.user_id, None)
        self.assertEqual(user.username, "bob")
        self.assertEqual(user.email, "bob@gmail.com")
        self.assertEqual(user.role, "Auditor")

    def test_get_json(self):
        user = User("bob@gmail.com", "bob", "bobpass", "Administrator")
        user_json = user.get_json()
        expected = {
            "user id": None,
            "email": "bob@gmail.com",
            "username": "bob",
            "role": "Administrator"
        }
        self.assertDictEqual(user_json, expected)
    
    def test_roles(self):
        roles = ['Administrator', 'Manager', 'Auditor']
        for role in roles:
            user = User("test@example.com", "user", "pass", role)
            self.assertEqual(user.role, role)

    def test_password_validation(self):
        user = User("bob@gmail.com", "bob", "mypass", "Auditor")
        # Check correct password
        self.assertTrue(user.check_password("mypass"))
        # Check incorrect password
        self.assertFalse(user.check_password("wrongpass"))
        # Check empty password
        self.assertFalse(user.check_password(""))
        # Check case sensitivity
        self.assertFalse(user.check_password("MYPASS"))

    def test_empty_fields(self):
        user = User("", "", "", "Auditor")
        self.assertEqual(user.email, "")
        self.assertEqual(user.username, "")
        self.assertNotEqual(user.password, "")

