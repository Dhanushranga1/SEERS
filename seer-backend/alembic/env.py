from logging.config import fileConfig
from sqlalchemy import create_engine, pool
import os
from dotenv import load_dotenv
from alembic import context
from app.models.user import Base  # Ensure this is correct

# ✅ Load environment variables
load_dotenv()

# ✅ Get DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables")

# ✅ Alembic Config object
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)  # ✅ Explicitly set the database URL

# ✅ Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ Set target metadata for migrations
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, avoiding the need for a database connection.
    """
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Here we create an Engine and associate a connection with the context.
    """
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)  # ✅ Corrected engine creation

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
