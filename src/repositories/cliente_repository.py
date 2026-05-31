import json
from pathlib import Path

from src.core.paths import OUTPUT_DIR
from src.models.cliente import ClienteProcessado


class ClienteRepository:

    def __init__(self, storage_dir: Path | None = None):
        self.storage_dir = storage_dir or OUTPUT_DIR / "clientes"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def salvar(self, cliente: ClienteProcessado) -> Path:
        arquivo = self.storage_dir / f"{cliente.cpf}.json"
        arquivo.write_text(
            json.dumps(cliente.as_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return arquivo
