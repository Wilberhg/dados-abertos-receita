from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Cliente:
    id: str
    nome: str
    cpf: str


@dataclass(frozen=True)
class ClienteProcessado:
    id: str
    nome: str
    cpf: str
    status: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)
