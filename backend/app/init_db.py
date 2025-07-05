from app.database import Base, engine

# Import your logging configuration
import logging
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Checking and creating database tables...")
    try:
        # The create_all function checks for the existence of tables before creating them
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables checked and created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise