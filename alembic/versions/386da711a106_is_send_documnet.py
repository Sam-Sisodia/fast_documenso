"""is send documnet


Revision ID: 386da711a106
Revises: 0bd7eee2589a
Create Date: 2024-12-10 13:48:11.742974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '386da711a106'
down_revision: Union[str, None] = '0bd7eee2589a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documents', sa.Column('is_send', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('documents', 'is_send')
    # ### end Alembic commands ###
