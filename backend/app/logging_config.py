# backend/app/logging_config.py

import logging
from pythonjsonlogger import jsonlogger

def configure_logging():
    """
    Configures structured logging for the application.
    Logs will be output in JSON format to stdout.
    """
    log_level = logging.INFO # Default log level
    
    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create a JSON formatter (moved outside the if block to ensure it's always created)
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s'
    )

    # Configure root logger handlers
    if not logger.handlers:
        # Create a console handler
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        # Add the handler to the logger
        logger.addHandler(handler)

    # Configure uvicorn's access logger to use our JSON formatter
    # This disables default uvicorn access logs and re-adds with our formatter
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.setLevel(log_level)
    # Clear existing handlers to prevent duplicate logs
    uvicorn_access_logger.handlers = [] 
    if not uvicorn_access_logger.handlers: # Check again after clearing
        uvicorn_access_handler = logging.StreamHandler()
        uvicorn_access_handler.setFormatter(formatter)
        uvicorn_access_logger.addHandler(uvicorn_access_handler)

    # Configure uvicorn's error logger (optional, but good practice)
    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.setLevel(log_level)
    uvicorn_error_logger.handlers = []
    if not uvicorn_error_logger.handlers:
        uvicorn_error_handler = logging.StreamHandler()
        uvicorn_error_handler.setFormatter(formatter)
        uvicorn_error_logger.addHandler(uvicorn_error_handler)

    print("Logging configured for JSON output.")

