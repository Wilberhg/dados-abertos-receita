from __future__ import annotations

from typing import Protocol
from xml.etree.ElementTree import Element

from src.models.cliente import ClienteProcessado


class ClienteApiPort(Protocol):
    def buscar_cliente(self, cpf: str) -> dict[str, str]:
        ...


class ClienteRepositoryPort(Protocol):
    def salvar(self, cliente: ClienteProcessado) -> str:
        ...


class DadosAbertosPort(Protocol):
    def consultar_data_base(self, data: str) -> Element | None:
        ...

    def baixa_base_empresas(self, link_arquivo: str) -> bytes | None:
        ...
