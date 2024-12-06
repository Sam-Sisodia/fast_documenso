"""firts migrations

Revision ID: 82e42431fd10
Revises: 
Create Date: 2024-12-06 16:04:34.583366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82e42431fd10'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('fieldtype',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('signature', sa.String(), nullable=True),
    sa.Column('positionX', sa.String(), nullable=True),
    sa.Column('positionY', sa.String(), nullable=True),
    sa.Column('width', sa.String(), nullable=True),
    sa.Column('height', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fieldtype_id'), 'fieldtype', ['id'], unique=False)
    op.create_index(op.f('ix_fieldtype_name'), 'fieldtype', ['name'], unique=True)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(), nullable=True),
    sa.Column('signature', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)
    op.create_table('documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('userId', sa.Integer(), nullable=True),
    sa.Column('file_data', sa.String(), nullable=True),
    sa.Column('createdAt', sa.DateTime(), nullable=True),
    sa.Column('updatedAt', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Enum('SIGNED', 'PENDING', 'COMPLETED', 'DRAFT', name='documentstatus'), nullable=True),
    sa.ForeignKeyConstraint(['userId'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_table('documnet_field',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('inserted', sa.Boolean(), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.Column('field_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['field_id'], ['fieldtype.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documnet_field_id'), 'documnet_field', ['id'], unique=False)
    op.create_table('recipient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('role', sa.Enum('SIGNER', 'APPROVER', 'CC', 'VIEWER', name='recipientrole'), nullable=False),
    sa.Column('status', sa.Enum('SIGNED', 'PENDING', 'COMPLETED', 'DRAFT', name='documentstatus'), nullable=True),
    sa.Column('signed_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipient_id'), 'recipient', ['id'], unique=False)
    op.create_table('documentsharedlink',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('status', sa.Enum('SIGNED', 'PENDING', 'COMPLETED', 'DRAFT', name='documentstatus'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('signed_at', sa.DateTime(), nullable=True),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.Column('recipient_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['recipient_id'], ['recipient.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_index(op.f('ix_documentsharedlink_id'), 'documentsharedlink', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_documentsharedlink_id'), table_name='documentsharedlink')
    op.drop_table('documentsharedlink')
    op.drop_index(op.f('ix_recipient_id'), table_name='recipient')
    op.drop_table('recipient')
    op.drop_index(op.f('ix_documnet_field_id'), table_name='documnet_field')
    op.drop_table('documnet_field')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_fieldtype_name'), table_name='fieldtype')
    op.drop_index(op.f('ix_fieldtype_id'), table_name='fieldtype')
    op.drop_table('fieldtype')
    # ### end Alembic commands ###
