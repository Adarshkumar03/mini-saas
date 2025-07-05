# backend/app/tasks.py

from datetime import datetime
from sqlalchemy.orm import Session
from .database import SessionLocal # Import SessionLocal to get a new session for the task
from . import crud
import logging

# Configure logging for tasks
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def aggregate_daily_issue_stats():
    """
    Aggregates issue counts by status and saves them to the daily_stats table.
    This function runs as a background task.
    """
    logger.info("Starting daily issue stats aggregation task...")
    db: Session = SessionLocal() # Get a new database session for the task
    try:
        # Get today's date (or yesterday's if running late at night for previous day's stats)
        # For simplicity, let's aggregate for the current day when the task runs.
        # In a real-world scenario, you might aggregate for the *previous* day.
        today = datetime.utcnow().date()

        # Check if stats for today already exist to prevent duplicates
        existing_stats = crud.get_daily_stats_by_date(db, today)
        if existing_stats:
            logger.info(f"Daily stats for {today} already exist. Skipping aggregation.")
            return

        # Get current issue counts by status
        issue_counts = crud.get_issue_status_counts(db)

        # Convert Enum keys to string values for JSON storage
        stringified_counts = {status.value: count for status, count in issue_counts.items()}

        # Save to DailyStats table
        crud.create_daily_stats(db, today, stringified_counts)
        logger.info(f"Successfully aggregated and saved daily stats for {today}: {stringified_counts}")

    except Exception as e:
        logger.error(f"Error during daily issue stats aggregation: {e}", exc_info=True)
    finally:
        db.close() # Ensure the session is closed

