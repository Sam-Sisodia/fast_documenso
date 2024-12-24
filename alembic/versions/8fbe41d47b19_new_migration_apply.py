from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fbe41d47b19'
down_revision: Union[str, None] = 'c2e696366e13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the "order" column as nullable initially
    op.add_column('documnet_field', sa.Column('order', sa.Integer(), nullable=True))
    
    # Populate existing rows with a default value for "order"
    session = op.get_bind()  # Get the session to run raw SQL
    session.execute("UPDATE documnet_field SET order = 0 WHERE order IS NULL")
    session.commit()

    # Alter the "order" column to NOT NULL after updating existing records
    op.alter_column('documnet_field', 'order', nullable=False)


def downgrade() -> None:
    # Drop the "order" column during a downgrade
    op.drop_column('documnet_field', 'order')
