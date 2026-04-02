from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from App.models import User

def role_required(*roles):
    # If a list was passed as the first argument, unpack it
    if len(roles) == 1 and isinstance(roles[0], (list, tuple)):
        allowed_roles = roles[0]
    else:
        allowed_roles = roles

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or user.role not in allowed_roles:
                return jsonify({"error": "Unauthorized"}), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator