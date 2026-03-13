import os
import logging

logger = logging.getLogger(__name__)

REQUIRED_ENV_VARS = [
    "DB_USER",
    "DB_PASSWORD"
]

def validate_env():
    missing = []

    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        logger.critical(f"Missing environment variables: {missing}")
        raise Exception("Environment configuration error")