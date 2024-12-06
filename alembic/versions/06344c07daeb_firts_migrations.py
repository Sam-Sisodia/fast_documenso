"""firts migrations

Revision ID: 06344c07daeb
Revises: 20c5d6d0447f
Create Date: 2024-12-06 17:22:47.027734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06344c07daeb'
down_revision: Union[str, None] = '20c5d6d0447f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fieldtype', 'inserted')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fieldtype', sa.Column('inserted', sa.BOOLEAN(), nullable=True))
    # ### end Alembic commands ###
