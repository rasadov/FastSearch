from app.models import User
from app import db, login_manager

# Configure the login manager to load the user
@login_manager.user_loader
def load_user(user_id):
    """
    Load a user from the database based on the user ID.

    Args:
      user_id (int): The ID of the user to load.

    Returns:
      User or None: The loaded user object if found, None otherwise.
    """
    try:
        return db.session.get(User, int(user_id))  # noqa: F405
    except (AttributeError, ValueError):
        return None