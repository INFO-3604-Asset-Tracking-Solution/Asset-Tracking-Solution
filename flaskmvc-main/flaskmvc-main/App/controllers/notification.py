from App.models import Notification
from App.database import db
from datetime import datetime

def create_notification(notif_id, check_id, recipient_id, message, timestamp=None):
    new_notification = Notification(notif_id, check_id, recipient_id, message, timestamp)

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


def get_notifications_by_check_id(check_id):
    return Notification.query.filter_by(check_id=check_id).all()


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
    notifications = [notification.get_json() for notification in notifications]
    return notifications


def update_notification(notif_id, check_id, recipient_id, message, timestamp=None):
    notification = get_notification_by_id(notif_id)

    if notification:
        notification.check_id = check_id
        notification.recipient_id = recipient_id
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