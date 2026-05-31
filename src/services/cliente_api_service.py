from src.core.ports import ClienteApiPort


class ClienteApiService(ClienteApiPort):
    def buscar_cliente(self, cpf: str) -> dict[str, str]:
        # Implementar integração real com API de cliente quando disponível.
        return {"cpf": cpf, "status": "indisponível"}
