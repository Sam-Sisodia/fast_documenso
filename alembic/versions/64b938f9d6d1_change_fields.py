"""change fields

Revision ID: 64b938f9d6d1
Revises: f6b725c3b222
Create Date: 2024-12-04 12:06:21.094303

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64b938f9d6d1'
down_revision: Union[str, None] = 'f6b725c3b222'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documents', sa.Column('file_data', sa.String(), nullable=True))
    op.drop_index('ix_documents_externalId', table_name='documents')
    op.drop_column('documents', 'externalId')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documents', sa.Column('externalId', sa.VARCHAR(), nullable=True))
    op.create_index('ix_documents_externalId', 'documents', ['externalId'], unique=False)
    op.drop_column('documents', 'file_data')
    # ### end Alembic commands ###
