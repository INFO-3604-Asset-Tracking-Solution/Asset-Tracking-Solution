import unittest
from App.controllers import (
    create_user, get_all_users_json,
    get_user, update_user, login 
)

def test_authenticate():
    user = create_user("bob@gmail.com", "bob", "bobpass")
    assert login("bob@gmail.com", "bobpass") != None


class UsersIntegrationTests(unittest.TestCase):

    def test_create_user(self):
        user = create_user("rick@gmail.com", "rick", "bobpass")
        assert user.email == "rick@gmail.com"

    def test_get_all_users_json(self):
        users_json = get_all_users_json()
        self.assertListEqual([{"id":1, "email":"bob@gmail.com", "username":"bob"}, {"id":2, "email":"rick@gmail.com", "username":"rick"}], users_json)

    # Tests data changes in the database
    def test_update_user(self):
        update_user(1, "ronnie@gmail.com", "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"
        