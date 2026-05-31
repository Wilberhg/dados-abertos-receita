import logging

from src.core.paths import LOGS_DIR

LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("dados_abertos_receita")
logger.setLevel(logging.INFO)
logger.propagate = False

formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler(LOGS_DIR / "app.log", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
