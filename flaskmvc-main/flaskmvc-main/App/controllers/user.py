import os
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer # type: ignore
from App.models import User
from App.database import db

VALID_ROLES = ["Administrator", "Manager", "Auditor"]


def create_user(email, username, password, role="Auditor"):
    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return None

    # Validate role
    if role not in VALID_ROLES:
        return None
        
    # Create new user with role
    new_user = User(email=email, username=username, password=password, role=role)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {e}")
        return None


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def get_user(id):
    return User.query.get(id)


def get_all_users():
    return User.query.all()


def get_all_users_json():
    users = User.query.all()
    if not users:
        return []
    return [user.get_json() for user in users]


def update_user(id, email, username, new_password=None, role=None):
    try:
        # Convert id to integer if it's a string
        if isinstance(id, str) and id.isdigit():
            id = int(id)
            
        # Try to get the user directly by id
        user = User.query.get(id)
        
        # If that fails, try filter_by
        if not user:
            user = User.query.filter_by(id=id).first()
            
        if not user:
            return None
            
        # Update user information
        user.email = email
        user.username = username
        
        # Update password if provided
        if new_password:
            user.set_password(new_password)

        # Update role if provided
        if role:
            if role in VALID_ROLES:
                user.role = role
            
        # Commit changes
        db.session.add(user)
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Error updating user: {e}")
        return None


def delete_user(id):
    try:
        user = get_user(id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user: {e}")
        return False


# 🔐 Password Reset Logic

def generate_reset_token(email):
    """Generate a secure time-limited token for password reset"""
    secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt='password-reset-salt')


def verify_reset_token(token, expiration=3600):
    """Verify the reset token and return the associated email"""
    secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=expiration
        )
        return email
    except (SignatureExpired, BadSignature):
        return None


def reset_password(email, new_password):
    """Reset a user's password using their email"""
    user = get_user_by_email(email)
    if user:
        user.set_password(new_password)
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error resetting password: {e}")
            return False
    return False