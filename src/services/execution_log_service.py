from contextlib import contextmanager

from src.core.logger import logger
from src.models.execution_log import ExecutionLog, StageType
from src.repositories.execution_log_repository import ExecutionLogRepository


class ExecutionLogService:
    """Serviço para gerenciar logs de execução."""

    def __init__(self, repository: ExecutionLogRepository | None = None):
        self.repository = repository or ExecutionLogRepository()

    @contextmanager
    def track_execution(self, stage_type: str):
        """Context manager para rastrear execução de uma etapa."""
        log = ExecutionLog.create_started(stage_type)
        log_id = self.repository.save(log)
        log = ExecutionLog(
            id=log_id,
            stage_type=log.stage_type,
            status=log.status,
            started_at=log.started_at,
        )

        logger.info(
            "Iniciando etapa %s (ID: %s)",
            stage_type,
            log_id,
        )

        try:
            yield log
        except Exception as e:
            error_log = log.mark_failure(str(e))
            self.repository.save(error_log)
            logger.error(
                "Falha em %s (ID: %s): %s",
                stage_type,
                log_id,
                str(e),
            )
            raise

    def log_success(
        self,
        log: ExecutionLog,
        items_processed: int | None = None,
    ) -> ExecutionLog:
        """Registra sucesso de uma execução."""
        success_log = log.mark_success(items_processed=items_processed)
        self.repository.save(success_log)

        logger.info(
            "Etapa %s concluída com sucesso (ID: %s, itens: %s, duração: %.2fs)",
            log.stage_type,
            log.id,
            items_processed or 0,
            success_log.duration_seconds or 0,
        )

        return success_log

    def get_stage_metrics(self, stage_type: str) -> dict:
        """Obtém métricas de uma etapa específica."""
        return self.repository.get_summary_by_stage(stage_type)

    def get_all_metrics(self) -> dict:
        """Obtém métricas gerais de execução."""
        return self.repository.get_metrics()

    def get_recent_logs(self, stage_type: str | None = None, limit: int = 50) -> list[ExecutionLog]:
        """Obtém logs recentes."""
        if stage_type:
            return self.repository.get_by_stage(stage_type, limit=limit)
        return self.repository.get_all(limit=limit)
