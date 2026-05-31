from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"


class StageType(str, Enum):
    PIPELINE_MONTHLY = "PIPELINE_MONTHLY"
    EXTRACT_ZIPS = "EXTRACT_ZIPS"
    CONVERT_CSVS = "CONVERT_CSVS"
    DOWNLOAD_BASES = "DOWNLOAD_BASES"
    PROCESS_CLIENTS = "PROCESS_CLIENTS"
    API_SEARCH = "API_SEARCH"


@dataclass(frozen=True)
class ExecutionLog:
    stage_type: str
    status: str
    started_at: str
    ended_at: str | None = None
    duration_seconds: float | None = None
    items_processed: int | None = None
    error_message: str | None = None
    id: int | None = None

    def as_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def create_started(stage_type: str) -> ExecutionLog:
        """Cria um log de início de execução."""
        return ExecutionLog(
            stage_type=stage_type,
            status=ExecutionStatus.STARTED.value,
            started_at=datetime.utcnow().isoformat(),
        )

    def mark_success(
        self,
        items_processed: int | None = None,
    ) -> ExecutionLog:
        """Marca o log como sucesso."""
        ended_at = datetime.utcnow().isoformat()
        started = datetime.fromisoformat(self.started_at)
        ended = datetime.fromisoformat(ended_at)
        duration = (ended - started).total_seconds()

        return ExecutionLog(
            stage_type=self.stage_type,
            status=ExecutionStatus.SUCCESS.value,
            started_at=self.started_at,
            ended_at=ended_at,
            duration_seconds=duration,
            items_processed=items_processed,
            id=self.id,
        )

    def mark_failure(self, error_message: str) -> ExecutionLog:
        """Marca o log como falha."""
        ended_at = datetime.utcnow().isoformat()
        started = datetime.fromisoformat(self.started_at)
        ended = datetime.fromisoformat(ended_at)
        duration = (ended - started).total_seconds()

        return ExecutionLog(
            stage_type=self.stage_type,
            status=ExecutionStatus.FAILURE.value,
            started_at=self.started_at,
            ended_at=ended_at,
            duration_seconds=duration,
            error_message=error_message,
            id=self.id,
        )
