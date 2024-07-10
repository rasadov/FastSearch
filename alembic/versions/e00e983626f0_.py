"""empty message

Revision ID: e00e983626f0
Revises: 
Create Date: 2024-07-10 20:18:52.658474

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.sql import func
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e00e983626f0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('username', sa.String(length=30), nullable=True, unique=True),
        sa.Column('name', sa.String(length=30), nullable=True),
        sa.Column('email_address', sa.String(), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=100), nullable=True),
        sa.Column('created_on', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('role', sa.String(), nullable=False, server_default='user'),
        sa.Column('confirmed_on', sa.DateTime(), nullable=True),
        sa.Column('subscribed_till', sa.DateTime(), nullable=True)
    )

    op.create_table('product',
    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('price_currency', sa.String(), nullable=False, server_default='USD'),
    sa.Column('item_class', sa.String(), nullable=True),
    sa.Column('producer', sa.String(), nullable=True),
    sa.Column('amount_of_ratings', sa.Integer(), nullable=True),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('availability', sa.String(), nullable=True),
    sa.Column('tsvector_title', TSVECTOR(), sa.Computed("to_tsvector('english', title)", persisted=True))
    )

    op.create_table(
        'price_history',
        sa.Column('price_history_id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('product.id'), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('price_currency', sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column('change_date', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('price_history_id'),
        sa.ForeignKeyConstraint(['product_id'], ['product.id']),
    )

    op.create_table(
        'message',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('text', sa.String(length=1000), nullable=False),
        sa.Column('sender_id', sa.Integer(), sa.ForeignKey('UserModel.id'), nullable=False),
        sa.Column('recipient_id', sa.Integer(), sa.ForeignKey('UserModel.id'), nullable=False),
        sa.Column('read', sa.Boolean(), nullable=False, default=False)
    )

    op.create_table(
        'cart',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('UserModel.id'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('product.id'), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('cart')
    op.drop_table('message')
    op.drop_table('price_history')
    op.drop_table('product')
    op.drop_table('UserModel')
