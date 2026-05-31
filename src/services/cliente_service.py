from src.core.logger import logger
from src.core.ports import ClienteApiPort, ClienteRepositoryPort
from src.models.cliente import Cliente, ClienteProcessado
from src.models.execution_log import ExecutionLog, StageType
from src.services.execution_log_service import ExecutionLogService


class ClienteService:

    def __init__(
        self,
        api_client: ClienteApiPort,
        repository: ClienteRepositoryPort,
        execution_log_service: ExecutionLogService | None = None,
    ):
        self.api = api_client
        self.repository = repository
        self.execution_log_service = execution_log_service or ExecutionLogService()

    def processar(self, cliente: Cliente) -> ClienteProcessado:
        logger.info("Processando cliente %s", cliente.nome)

        dados_api = self.api.buscar_cliente(cliente.cpf)

        cliente_processado = ClienteProcessado(
            id=cliente.id,
            nome=cliente.nome,
            cpf=cliente.cpf,
            status=dados_api.get("status", "desconhecido"),
        )

        self.repository.salvar(cliente_processado)
        return cliente_processado
