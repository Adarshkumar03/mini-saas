# alembic/env.py

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os # Import os to access environment variables
from dotenv import load_dotenv # Import load_dotenv

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# We need to import our Base and models here.
# This ensures Alembic's autogenerate can detect our models.

# Load environment variables from .env file FIRST
load_dotenv()

# Import Base from your main application file
# This links Alembic to your SQLAlchemy models
from app.database import Base
from app import models # noqa: F401 - Import models to ensure they are registered with Base

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not a connection, though an existing connection
    can also be used.  By default we don't need to use a connection
    here.  The script output is written to stdout.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Get DATABASE_URL directly from environment, ensuring it's loaded
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable not set. Please check your .env file.")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario, we need to create an Engine
    and associate a connection with the context.

    """
    # Get DATABASE_URL directly from environment, ensuring it's loaded
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable not set. Please check your .env file.")

    # Pass the URL directly to engine_from_config
    connectable = engine_from_config(
        {"sqlalchemy.url": url}, # Pass URL as a dictionary
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

