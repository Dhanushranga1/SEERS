from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision = "1bd904717289"
down_revision = "aafc1aecd2f4"  # The last working migration
branch_labels = None
depends_on = None


def upgrade():
    """Create the threat_logs table"""
    op.create_table(
        "threat_logs",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("source_ip", sa.String(), nullable=False),
        sa.Column("is_alert", sa.Boolean(), default=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    """Drop the threat_logs table"""
    op.drop_table("threat_logs")
