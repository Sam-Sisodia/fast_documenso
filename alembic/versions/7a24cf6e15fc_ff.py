"""ff

Revision ID: 7a24cf6e15fc
Revises: 7780775a2638
Create Date: 2024-12-16 12:08:53.416388

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a24cf6e15fc'
down_revision: Union[str, None] = '7780775a2638'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('documentsigningprocess',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=True),
    sa.Column('recipient_id', sa.Integer(), nullable=True),
    sa.Column('signed_at', sa.DateTime(), nullable=True),
    sa.Column('sign_status', sa.Boolean(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.Column('is_current', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['recipient_id'], ['recipients.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documentsigningprocess_id'), 'documentsigningprocess', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_documentsigningprocess_id'), table_name='documentsigningprocess')
    op.drop_table('documentsigningprocess')
    # ### end Alembic commands ###
