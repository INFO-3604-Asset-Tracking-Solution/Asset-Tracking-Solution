import unittest
from App.controllers import (
    create_user, get_all_users_json,
    get_user, update_user
)
from App.database import db
from App.models import User

class UsersIntegrationTests(unittest.TestCase):
    def setUp(self):
        db.session.query(User).delete()
        db.session.commit()

    def test_create_user(self):
        user = create_user("rick@gmail.com", "rick", "bobpass", "Manager")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "rick@gmail.com")

    def test_get_all_users_json(self):
        create_user("bob@gmail.com", "bob", "bobpass", "Administrator")
        create_user("rick@gmail.com", "rick", "bobpass", "Manager")
        users_json = get_all_users_json()
        self.assertEqual(len(users_json), 2)
        # Checking if emails are in the returned JSON
        emails = [u["email"] for u in users_json]
        self.assertIn("bob@gmail.com", emails)
        self.assertIn("rick@gmail.com", emails)

    def test_update_user(self):
        user = create_user("ronnie@gmail.com", "ronnie", "pass", "Auditor")
        success = update_user(user.user_id, "ronnie_new@gmail.com", "ronnie2", role="Manager")
        self.assertTrue(success)
        
        updated_user = get_user(user.user_id)
        self.assertEqual(updated_user.username, "ronnie2")
        self.assertEqual(updated_user.email, "ronnie_new@gmail.com")
        self.assertEqual(updated_user.role, "Manager")