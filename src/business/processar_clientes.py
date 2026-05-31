from src.core.logger import logger
from src.models.execution_log import ExecutionLog, StageType
from src.repositories.cliente_repository import ClienteRepository
from src.services.cliente_api_service import ClienteApiService
from src.services.cliente_service import ClienteService
from src.services.execution_log_service import ExecutionLogService
from src.utils.json_utils import carregar_clientes


def executar() -> None:
    logger.info("Iniciando processamento de clientes")

    log = ExecutionLog.create_started(StageType.PROCESS_CLIENTS.value)
    execution_log_service = ExecutionLogService()
    log_id = execution_log_service.repository.save(log)
    log = ExecutionLog(
        id=log_id,
        stage_type=log.stage_type,
        status=log.status,
        started_at=log.started_at,
    )

    clientes = carregar_clientes()
    service = ClienteService(
        api_client=ClienteApiService(),
        repository=ClienteRepository(),
        execution_log_service=execution_log_service,
    )

    processed_count = 0
    try:
        for cliente in clientes:
            try:
                service.processar(cliente)
                processed_count += 1
            except Exception as error:
                logger.exception(
                    "Erro ao processar cliente %s: %s",
                    cliente.cpf,
                    error,
                )

        execution_log_service.log_success(log, items_processed=processed_count)
        logger.info("Processamento de %s clientes finalizado com sucesso", processed_count)
    except Exception as e:
        error_log = log.mark_failure(str(e))
        execution_log_service.repository.save(error_log)
        logger.error("Falha no processamento de clientes: %s", str(e))
        raise
