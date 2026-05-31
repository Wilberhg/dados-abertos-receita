import json
from pathlib import Path

from src.core.paths import INPUT_DIR
from src.models.cliente import Cliente


def carregar_clientes(source: Path | None = None) -> list[Cliente]:
    source = source or INPUT_DIR / "clientes.json"
    if not source.exists():
        raise FileNotFoundError(f"Arquivo de clientes não encontrado em {source}")

    with source.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    return [Cliente(**item) for item in dados]
