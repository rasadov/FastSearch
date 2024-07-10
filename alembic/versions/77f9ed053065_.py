"""empty message

Revision ID: 77f9ed053065
Revises: e00e983626f0
Create Date: 2024-07-10 20:29:51.044052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77f9ed053065'
down_revision: Union[str, None] = 'e00e983626f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('user', 'UserModel')


def downgrade() -> None:
    op.rename_table('UserModel', 'user')
