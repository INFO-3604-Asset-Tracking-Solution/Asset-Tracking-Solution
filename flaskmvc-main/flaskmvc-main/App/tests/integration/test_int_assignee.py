import unittest
from App.controllers import (
    create_assignee, update_assignee
)

class AssigneeIntegrationTests(unittest.TestCase):

    def test_create_assignee(self):
        assignee = create_assignee("Alice", "Smith", "alice@example.com", "R1")
        self.assertEqual(assignee.email, "alice@example.com")

    def test_update_assignee(self):
        assignee = create_assignee("Bob", "Jones", "bob@example.com", "R2")
        updated = update_assignee(assignee.id, "Robert", "Jones", "bob@example.com", "R3")
        self.assertEqual(updated.fname, "Robert")
        self.assertEqual(updated.room_id, "R3")