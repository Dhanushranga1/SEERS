"""Fixed User Role Relationship

Revision ID: aafc1aecd2f4
Revises: acce4f21dc22
Create Date: 2025-02-16 00:48:52.916615

"""
from typing import Sequence, Union  # ✅ ADD THIS LINE
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'aafc1aecd2f4'
down_revision: Union[str, None] = 'acce4f21dc22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the ENUM type
user_role_enum = postgresql.ENUM('ADMIN', 'USER', name='userrole', create_type=True)

def upgrade() -> None:
    """Apply migration"""

    # ✅ Step 1: Create ENUM type before altering the column
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # ✅ Step 2: Convert existing 'roles.name' column to ENUM with explicit casting
    op.execute("ALTER TABLE roles ALTER COLUMN name TYPE userrole USING name::userrole")

    # ✅ Step 3: Drop the old index
    op.drop_index('ix_roles_name', table_name='roles')

    # ✅ Step 4: Ensure Unique Constraint on Role Name
    op.create_unique_constraint(None, 'roles', ['name'])

def downgrade() -> None:
    """Rollback migration"""

    # ✅ Step 1: Convert ENUM back to String before dropping ENUM type
    op.execute("ALTER TABLE roles ALTER COLUMN name TYPE VARCHAR")

    # ✅ Step 2: Drop ENUM type safely
    user_role_enum.drop(op.get_bind(), checkfirst=True)

    # ✅ Step 3: Recreate old index
    op.create_index('ix_roles_name', 'roles', ['name'], unique=True)
