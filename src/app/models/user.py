"""
This module contains the User class, which represents a user in the application.
"""

from datetime import datetime
from typing import Self

from flask_login import UserMixin
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped
from itsdangerous import SignatureExpired

from app import bcrypt, db, s

class User(UserMixin, db.Model):
    """
    Represents a user in the application.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        name (str): The name of the user.
        email_address (str): The email address of the user.
        password_hash (str): The hashed password of the user.
        created_on (datetime): The date and time when the user was created.
        role (str): The role of the user.
        confirmed_on (datetime): The date and time when the user was confirmed.
        subscribed_till (datetime): The date and time until which the user is subscribed.

    Methods:
        is_admin(): Checks if the user has admin privileges.
        is_owner(): Checks if the user is the owner.
        password(): Gets the password of the user.
        password.setter(): Sets the password of the user.
        chech_password_correction(attempted_password): Checks if the attempted password is correct.
        username_exists(username): Checks if a user with the given username exists.
        email_registered(email_address): Checks if a user with the given email address exists.
        is_confirmed(): Checks if the user is confirmed.
        is_subscribed(): Checks if the user is subscribed.
        items(): Returns a dictionary of the user's attributes.
        get_verification_token(expires_sec): Generates a verification token for the user.
        verify_verification_token(token): Verifies a verification token for the user.
        get_reset_token(expires_sec): Generates a reset token for the user.
        verify_reset_token(token): Verifies a reset token for the user.
        __repr__(): Returns a string representation of the user.

    """

    # Attributes

    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    id : Mapped[int] = mapped_column(primary_key=True)
    username : Mapped[str] = mapped_column(String(length=30), unique=True, default=None, nullable=True)
    name : Mapped[str] = mapped_column(String(length=30), default=None, nullable=True)
    email_address : Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash : Mapped[str] = mapped_column(String(length=100), default=None, nullable=True)
    created_on : Mapped[datetime] = mapped_column(nullable=False, default=datetime.now().date())
    role : Mapped[str] = mapped_column(nullable=False, default="user")
    confirmed_on : Mapped[datetime] = mapped_column(nullable=True)
    subscribed_till : Mapped[datetime] = mapped_column(nullable=True, default=None)

    # Methods

    def __init__(
        self,
        email_address,
        password=None,
        username=None,
        name=None,
        confirmed_on=None,
        subscribed_till=None,
        role="user",
    ) -> None:
        """
        Initializes a new instance of the User class.

        Args:
            email_address (str): The email address of the user.
            password (str, optional): The password of the user. Defaults to None.
            username (str, optional): The username of the user. Defaults to None.
            name (str, optional): The name of the user. Defaults to None.
            confirmed_on (datetime, optional):
            The date and time when the user was confirmed. Defaults to None.
            subscribed_till (datetime, optional):
            The date and time until which the user is subscribed. Defaults to None.
            role (str, optional): The role of the user. Defaults to 'user'.
        """
        self.username = username
        self.email_address = email_address
        self.password = password
        self.name = name
        self.confirmed_on = confirmed_on
        self.subscribed_till = subscribed_till
        self.role = role

    def get_attributes(self) -> dict:
        """
        Returns a dictionary of the user's attributes for editing.

        Returns:
            dict: A dictionary of the user's attributes for editing.
        """
        return {
            "username": self.username,
            "name": self.name,
            "email_address": self.email_address,
            "role": self.role,
            "confirmed_on": self.confirmed_on,
            "subscribed_till": self.subscribed_till,
        }

    def is_admin(self) -> bool:
        """
        Checks if the user has admin privileges.

        Returns:
            bool: True if the user has admin privileges, False otherwise.
        """
        return self.role in ["admin", "owner"]

    def is_owner(self) -> bool:
        """
        Checks if the user is the owner.

        Returns:
            bool: True if the user is the owner, False otherwise.
        """
        return self.role == "owner"

    @property
    def password(self) -> str:
        """
        Gets the password of the user.

        Returns:
            str: The password of the user.
        """
        return self.password

    @password.setter
    def password(self, plain_text_password) -> None:
        """
        Sets the password of the user.

        Args:
            plain_text_password (str): The plain text password to set.
        """
        if plain_text_password is None:
            return
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode(
            "utf-8"
        )

    def chech_password_correction(self, attempted_password) -> bool:
        """
        Checks if the attempted password is correct.

        Args:
            attempted_password (str): The password to check.

        Returns:
            bool: True if the attempted password is correct, False otherwise.
        """
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    @staticmethod
    def username_exists(username) -> bool:
        """
        Checks if a user with the given username exists.

        Args:
            username (str): The username to check.

        Returns:
            bool: True if a user with the given username exists, False otherwise.
        """
        return username and User.query.filter_by(username=username).count()

    @staticmethod
    def email_registered(email_address) -> bool:
        """
        Checks if a user with the given email address exists.

        Args:
            email_address (str): The email address to check.

        Returns:
            bool: True if a user with the given email address exists, False otherwise.
        """
        return User.query.filter_by(email_address=email_address).count()

    def is_confirmed(self) -> bool:
        """
        Checks if the user is confirmed.

        Returns:
            bool: True if the user is confirmed, False otherwise.
        """
        return self.confirmed_on is not None

    def is_subscribed(self) -> bool:
        """
        Checks if the user is subscribed.

        Returns:
            bool: True if the user is subscribed, False otherwise.
        """
        if self.role in ["admin", "owner"]:
            return True
        return self.subscribed_till and self.subscribed_till >= datetime.now().date()

    def get_verification_token(self) -> str:
        """
        Generates a verification token for the user.

        Args:
            expires_sec (int, optional):
            The expiration time of the token in seconds. Defaults to 1800.

        Returns:
            str: The verification token.
        """
        return s.dumps({"user_id": self.id}, salt="email-confirmation")

    @staticmethod
    def verify_verification_token(token) -> Self | None:
        """
        Verify the validity of a verification token.

        Args:
            token (str): The verification token to be verified.

        Returns:
            User or None: The User object associated with the token if it is valid, otherwise None.
        """
        try:
            user_id = s.loads(token, salt="email-confirmation", max_age=1800)["user_id"]
        except SignatureExpired:
            return None
        return User.query.get(user_id)

    def get_reset_token(self) -> str:
        """
        Generates a reset token for the user.

        Returns:
            str: The reset token.
        """
        return s.dumps({"user_id": self.id}, salt="password-reset")

    @staticmethod
    def verify_reset_token(token) -> Self | None:
        """
        Verify the validity of a password reset token.

        Parameters:
        - token (str): The password reset token to be verified.

        Returns:
        - User or None: The User object associated with the token if it is valid, otherwise None.
        """
        try:
            user_id = s.loads(token, salt="password-reset", max_age=1800)["user_id"]
        except SignatureExpired:
            return None
        return User.query.get(user_id)

    def to_dict(self) -> dict:
        """
        Returns a dictionary of the user's attributes.

        Returns:
            dict: A dictionary of the user's attributes.
        """
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "email_address": self.email_address,
            "role": self.role,
            "confirmed_on": self.confirmed_on,
            "subscribed_till": self.subscribed_till,
        }

    def __repr__(self) -> str:
        """
        Returns a string representation of the user.

        Returns:
            str: A string representation of the user.
        """
        return f"<User {self.id}:{self.email_address}>"
