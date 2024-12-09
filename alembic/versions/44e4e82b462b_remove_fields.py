"""remove fields

Revision ID: 44e4e82b462b
Revises: 29831e1b6d53
Create Date: 2024-12-10 13:53:47.570518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44e4e82b462b'
down_revision: Union[str, None] = '29831e1b6d53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documnet_field', sa.Column('signature', sa.String(), nullable=True))
    op.add_column('documnet_field', sa.Column('positionX', sa.String(), nullable=True))
    op.add_column('documnet_field', sa.Column('positionY', sa.String(), nullable=True))
    op.add_column('documnet_field', sa.Column('width', sa.String(), nullable=True))
    op.add_column('documnet_field', sa.Column('height', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('documnet_field', 'height')
    op.drop_column('documnet_field', 'width')
    op.drop_column('documnet_field', 'positionY')
    op.drop_column('documnet_field', 'positionX')
    op.drop_column('documnet_field', 'signature')
    # ### end Alembic commands ###
