from src.core.logger import logger
from src.repositories.cliente_repository import ClienteRepository
from src.services.cliente_api_service import ClienteApiService
from src.services.cliente_service import ClienteService
from src.utils.json_utils import carregar_clientes


def executar() -> None:
    logger.info("Iniciando processamento")

    clientes = carregar_clientes()
    service = ClienteService(
        api_client=ClienteApiService(),
        repository=ClienteRepository(),
    )

    for cliente in clientes:
        try:
            service.processar(cliente)
        except Exception as error:
            logger.exception(
                "Erro ao processar cliente %s: %s",
                cliente.cpf,
                error,
            )

    logger.info("Processamento finalizado")
