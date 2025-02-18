"""Added role field to users

Revision ID: a889253579e6
Revises: e44625085d4b
Create Date: 2025-02-16 00:10:43.639104

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = 'a889253579e6'
down_revision: Union[str, None] = 'e44625085d4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the ENUM type
userrole_enum = ENUM('ADMIN', 'USER', name='userrole', create_type=True)

def upgrade() -> None:
    # Create ENUM type in PostgreSQL
    userrole_enum.create(op.get_bind(), checkfirst=True)

    # Add the new column using ENUM
    op.add_column('users', sa.Column('role', userrole_enum, nullable=False, server_default='USER'))

    # Create permissions table
    op.create_table('permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_permissions_id'), 'permissions', ['id'], unique=False)
    op.create_index(op.f('ix_permissions_name'), 'permissions', ['name'], unique=True)

    # Create role_permissions table
    op.create_table('role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

def downgrade() -> None:
    # Remove the column
    op.drop_column('users', 'role')

    # Drop the ENUM type
    userrole_enum.drop(op.get_bind(), checkfirst=True)

    # Drop role_permissions table
    op.drop_table('role_permissions')

    # Drop permissions table
    op.drop_index(op.f('ix_permissions_name'), table_name='permissions')
    op.drop_index(op.f('ix_permissions_id'), table_name='permissions')
    op.drop_table('permissions')
