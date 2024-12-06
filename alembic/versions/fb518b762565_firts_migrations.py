"""firts migrations

Revision ID: fb518b762565
Revises: 
Create Date: 2024-12-06 15:46:31.342337

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb518b762565'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('FieldType',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('signature', sa.String(), nullable=True),
    sa.Column('positionX', sa.String(), nullable=True),
    sa.Column('positionY', sa.String(), nullable=True),
    sa.Column('width', sa.String(), nullable=True),
    sa.Column('height', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_FieldType_id'), 'FieldType', ['id'], unique=False)
    op.create_index(op.f('ix_FieldType_name'), 'FieldType', ['name'], unique=True)
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
    op.create_table('documnet_fields',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('inserted', sa.Boolean(), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documnet_fields_id'), 'documnet_fields', ['id'], unique=False)
    op.create_table('recipient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('role', sa.Enum('SIGNER', 'APPROVER', 'CC', 'VIEWER', name='recipientrole'), nullable=False),
    sa.Column('status', sa.Enum('SIGNED', 'PENDING', 'COMPLETED', 'DRAFT', name='documentstatus'), nullable=True),
    sa.Column('signed_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipient_id'), 'recipient', ['id'], unique=False)
    op.create_table('signing_links',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('status', sa.Enum('SIGNED', 'PENDING', 'COMPLETED', 'DRAFT', name='documentstatus'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('signed_at', sa.DateTime(), nullable=True),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.Column('recipient_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.ForeignKeyConstraint(['recipient_id'], ['recipient.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_index(op.f('ix_signing_links_id'), 'signing_links', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_signing_links_id'), table_name='signing_links')
    op.drop_table('signing_links')
    op.drop_index(op.f('ix_recipient_id'), table_name='recipient')
    op.drop_table('recipient')
    op.drop_index(op.f('ix_documnet_fields_id'), table_name='documnet_fields')
    op.drop_table('documnet_fields')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_FieldType_name'), table_name='FieldType')
    op.drop_index(op.f('ix_FieldType_id'), table_name='FieldType')
    op.drop_table('FieldType')
    # ### end Alembic commands ###
