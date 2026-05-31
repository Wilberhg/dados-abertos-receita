import sys

from loguru import logger
from src.core.paths import LOGS_DIR

LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger.remove()
logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name} | {message}",
    level="INFO",
    colorize=False,
)
logger.add(
    str(LOGS_DIR / "app.log"),
    rotation="10 MB",
    retention="10 days",
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name} | {message}",
    level="INFO",
)
