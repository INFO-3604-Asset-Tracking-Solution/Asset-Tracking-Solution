from App.models import Notification
from App.database import db


def create_notification(audit_id, recipient_id, message, timestamp=None):
    new_notification = Notification(audit_id, recipient_id, message, timestamp)

    try:
        db.session.add(new_notification)
        db.session.commit()
        return new_notification
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")
        return None


def get_notification_by_id(notif_id):
    if not notif_id:
        return None
    return Notification.query.get(notif_id)


def get_notifications_by_audit_id(audit_id):
    return Notification.query.filter_by(audit_id=audit_id).all()


def get_notifications_by_recipient_id(recipient_id):
    return Notification.query.filter_by(recipient_id=recipient_id).all()


def get_notifications_by_message(message):
    return Notification.query.filter_by(message=message).all()


def get_all_notifications():
    return Notification.query.all()


def get_all_notifications_json():
    notifications = Notification.query.all()
    if not notifications:
        return []
    return [notification.get_json() for notification in notifications]


def update_notification(notif_id, audit_id=None, recipient_id=None, message=None, timestamp=None):
    notification = get_notification_by_id(notif_id)

    if notification:
        if audit_id is not None:
            notification.audit_id = audit_id
        if recipient_id is not None:
            notification.recipient_id = recipient_id
        if message is not None:
            notification.message = message
        if timestamp is not None:
            notification.timestamp = timestamp

        try:
            db.session.commit()
            return notification
        except Exception as e:
            db.session.rollback()
            print(f"Error updating notification: {e}")
            return None

    return None


def delete_notification(notif_id):
    notification = get_notification_by_id(notif_id)

    if notification:
        try:
            db.session.delete(notification)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting notification: {e}")
            return False

    return False