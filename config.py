import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from a .env file if it exists
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# Browser configurations
HEADLESS = os.getenv("BROWSER_HEADLESS", "False").lower() in ("true", "1", "yes")
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))  # in milliseconds

# Output directories
SCREENSHOT_DIR = BASE_DIR / os.getenv("SCREENSHOT_DIR", "screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Logging configuration
LOG_FILE_PATH = BASE_DIR / os.getenv("LOG_FILE", "automation.log")

def setup_logging():
    """
    Configures logging to write logs to both the console (stdout) and a log file.
    Logs are structured with timestamp, log level, logger name, and the message.
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Prevent adding multiple handlers if setup_logging is called more than once
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File Handler
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logging.info("Logging configured successfully. Logs are saved to %s", LOG_FILE_PATH)

# Initialize logging immediately on import
setup_logging()
logger = logging.getLogger("config")
logger.info("Configuration loaded: HEADLESS=%s, DEFAULT_TIMEOUT=%d, SCREENSHOT_DIR=%s", HEADLESS, DEFAULT_TIMEOUT, SCREENSHOT_DIR)
