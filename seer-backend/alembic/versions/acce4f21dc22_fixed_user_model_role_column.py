"""Fixed User model role column

Revision ID: acce4f21dc22
Revises: a889253579e6
Create Date: 2025-02-16 00:21:50.423233
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'acce4f21dc22'
down_revision: Union[str, None] = 'a889253579e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define ENUM type
user_role_enum = postgresql.ENUM('ADMIN', 'USER', name='userrole', create_type=False)

def upgrade() -> None:
    conn = op.get_bind()

    # ✅ 1. Create ENUM type before altering column
    user_role_enum.create(conn, checkfirst=True)

    # ✅ 2. Ensure roles table has at least the 'USER' role
    conn.execute(sa.text("""
        INSERT INTO roles (name) 
        VALUES ('USER') 
        ON CONFLICT (name) DO NOTHING;
    """))

    # ✅ 3. Assign 'USER' role ID to all users where role_id is NULL
    conn.execute(sa.text("""
        UPDATE users 
        SET role_id = (SELECT id FROM roles WHERE name = 'USER') 
        WHERE role_id IS NULL;
    """))

    # ✅ 4. Now safely enforce NOT NULL constraint
    op.alter_column('users', 'role_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ✅ 5. Drop the old `role` column if it exists
    op.drop_column('users', 'role')

def downgrade() -> None:
    conn = op.get_bind()

    # ❌ Reverse ENUM type conversion
    op.execute("ALTER TABLE roles ALTER COLUMN name TYPE VARCHAR")

    # ❌ Drop ENUM type safely
    user_role_enum.drop(conn, checkfirst=True)

    # ❌ Restore the old 'role' column
    op.add_column('users', sa.Column('role', postgresql.ENUM('ADMIN', 'USER', name='userrole'),
                                     server_default=sa.text("'USER'::userrole"),
                                     autoincrement=False, nullable=False))

    # ❌ Make users.role_id nullable again
    op.alter_column('users', 'role_id',
               existing_type=sa.INTEGER(),
               nullable=True)
