from sqlalchemy import String, ForeignKey, MetaData, Table, Column, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship


from app import db

class Message(db.Model):
    __table_args__ = {'extend_existing': True}


    __tablename__ = 'message'
    extend_existing = True
    id : Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(length=1000), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey('User.id'), nullable=False)
    recipient_id: Mapped[int] = mapped_column(ForeignKey('User.id'), nullable=False)

    read: Mapped[bool] = mapped_column(default=False)

    def __init__(self, text, sender_id, recipient_id):
        self.text = text
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.read = False