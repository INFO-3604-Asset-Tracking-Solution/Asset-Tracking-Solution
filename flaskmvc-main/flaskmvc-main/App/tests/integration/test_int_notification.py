import unittest
from App.models import Notification, Audit
from App.controllers.notification import (
    create_notification, get_notifications_by_recipient_id,
    update_notification, delete_notification
)
from App.controllers.audit import create_audit
from App.database import db

class NotificationIntegrationTests(unittest.TestCase):
    def setUp(self):
        db.session.query(Notification).delete()
        db.session.query(Audit).delete()
        db.session.commit()
        
        # Create a dummy audit for foreign key
        self.audit = create_audit(initiator_id=1)
        db.session.add(self.audit)
        db.session.commit()

    def test_create_notification(self):
        notif = create_notification(self.audit.audit_id, 1, "Test Message")
        self.assertIsNotNone(notif)
        self.assertIsNotNone(notif.notif_id)
        self.assertEqual(notif.message, "Test Message")

    def test_get_notifications(self):
        create_notification(self.audit.audit_id, 2, "Msg 1")
        create_notification(self.audit.audit_id, 2, "Msg 2")
        notifs = get_notifications_by_recipient_id(2)
        self.assertEqual(len(notifs), 2)

    def test_update_notification(self):
        notif = create_notification(self.audit.audit_id, 1, "Old Msg")
        updated = update_notification(notif.notif_id, message="New Msg")
        self.assertIsNotNone(updated)
        self.assertEqual(updated.message, "New Msg")

    def test_delete_notification(self):
        notif = create_notification(self.audit.audit_id, 1, "Delete me")
        success = delete_notification(notif.notif_id)
        self.assertTrue(success)
        self.assertIsNone(Notification.query.get(notif.notif_id))
