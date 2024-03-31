"""
This module contains the Message class, which represents a message in the application.
"""

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from app import db

class Message(db.Model):
    """
    Represents a message sent between users.

    Attributes:
        id (int): The unique identifier of the message.
        text (str): The content of the message.
        sender_id (int): The ID of the user who sent the message.
        recipient_id (int): The ID of the user who received the message.
        read (bool): Indicates whether the message has been read or not.
    """

    __table_args__ = {'extend_existing': True}
    __tablename__ = 'message'

    id : Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(length=1000), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey('User.id'), nullable=False)
    recipient_id: Mapped[int] = mapped_column(ForeignKey('User.id'), nullable=False)
    read: Mapped[bool] = mapped_column(default=False)

    def __init__(self, text, sender_id, recipient_id):
        # Constructor implementation goes here
        """
        Initializes a new instance of the Message class.

        Args:
            text (str): The text content of the message.
            sender_id (int): The ID of the sender user.
            recipient_id (int): The ID of the recipient user.
        """
        self.text = text
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.read = False

    def mark_as_read(self):
        # Method implementation goes here
        """
        Marks the message as read.
        """
        self.read = True
