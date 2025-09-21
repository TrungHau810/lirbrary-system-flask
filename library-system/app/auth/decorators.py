from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user


def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):

            if not current_user.is_authenticated:
                return redirect(url_for('login', next=request.path))
            role_name = None


            if getattr(current_user, 'user_role', None):
                try:
                    role_name = current_user.user_role.name
                except Exception:
                    role_name = str(current_user.user_role)

            if role_name not in roles:
                flash('Bạn không có quyền truy cập chức năng này.', 'warning')
                return redirect(url_for('index'))
            return view_func(*args, **kwargs)

        return wrapper
    return decorator
