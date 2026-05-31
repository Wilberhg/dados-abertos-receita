from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOGS_DIR = PROJECT_ROOT / "logs"
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
RAW_DIR = OUTPUT_DIR / "raw"
EXTRACTED_DIR = OUTPUT_DIR / "extracted"
CONVERTED_DIR = OUTPUT_DIR / "converted"


def assegura_criacao_diretorios() -> None:
    """
    Garante que os diretórios necessários existam.
    """
    for directory in [
        OUTPUT_DIR,
        LOGS_DIR,
        DATA_DIR,
        INPUT_DIR,
        RAW_DIR,
        EXTRACTED_DIR,
        CONVERTED_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)
