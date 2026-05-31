from pathlib import Path

from src.infra.database.sqlite_connection import SqliteConnection
from src.models.execution_log import ExecutionLog


class ExecutionLogRepository:
    """Repositório para persistência de logs de execução."""

    def __init__(self, db_connection: SqliteConnection | None = None):
        self.db = db_connection or SqliteConnection()

    def save(self, log: ExecutionLog) -> int:
        """Salva um log de execução no banco de dados."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO execution_logs
            (stage_type, status, started_at, ended_at, duration_seconds, items_processed, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                log.stage_type,
                log.status,
                log.started_at,
                log.ended_at,
                log.duration_seconds,
                log.items_processed,
                log.error_message,
            ),
        )

        conn.commit()
        log_id = cursor.lastrowid
        conn.close()
        return log_id

    def get_by_id(self, log_id: int) -> ExecutionLog | None:
        """Obtém um log por ID."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM execution_logs WHERE id = ?",
            (log_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return ExecutionLog(
                id=row["id"],
                stage_type=row["stage_type"],
                status=row["status"],
                started_at=row["started_at"],
                ended_at=row["ended_at"],
                duration_seconds=row["duration_seconds"],
                items_processed=row["items_processed"],
                error_message=row["error_message"],
            )
        return None

    def get_by_stage(self, stage_type: str, limit: int = 100) -> list[ExecutionLog]:
        """Obtém logs de uma etapa específica."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM execution_logs
            WHERE stage_type = ?
            ORDER BY started_at DESC
            LIMIT ?
            """,
            (stage_type, limit),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            ExecutionLog(
                id=row["id"],
                stage_type=row["stage_type"],
                status=row["status"],
                started_at=row["started_at"],
                ended_at=row["ended_at"],
                duration_seconds=row["duration_seconds"],
                items_processed=row["items_processed"],
                error_message=row["error_message"],
            )
            for row in rows
        ]

    def get_all(self, limit: int = 1000) -> list[ExecutionLog]:
        """Obtém todos os logs."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM execution_logs
            ORDER BY started_at DESC
            LIMIT ?
            """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            ExecutionLog(
                id=row["id"],
                stage_type=row["stage_type"],
                status=row["status"],
                started_at=row["started_at"],
                ended_at=row["ended_at"],
                duration_seconds=row["duration_seconds"],
                items_processed=row["items_processed"],
                error_message=row["error_message"],
            )
            for row in rows
        ]

    def get_summary_by_stage(self, stage_type: str) -> dict:
        """Obtém um resumo de execuções por etapa."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                status,
                COUNT(*) as count,
                AVG(duration_seconds) as avg_duration,
                SUM(items_processed) as total_items,
                MAX(started_at) as last_execution
            FROM execution_logs
            WHERE stage_type = ?
            GROUP BY status
            """,
            (stage_type,),
        )

        rows = cursor.fetchall()
        conn.close()

        summary = {}
        for row in rows:
            summary[row["status"]] = {
                "count": row["count"],
                "avg_duration_seconds": row["avg_duration"],
                "total_items_processed": row["total_items"],
                "last_execution": row["last_execution"],
            }
        return summary

    def get_metrics(self) -> dict:
        """Obtém métricas gerais de execução."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Total de execuções
        cursor.execute(
            "SELECT COUNT(*) as count FROM execution_logs"
        )
        total_executions = cursor.fetchone()["count"]

        # Execuções por status
        cursor.execute(
            """
            SELECT status, COUNT(*) as count
            FROM execution_logs
            GROUP BY status
            """
        )
        status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}

        # Tempo total de execução
        cursor.execute(
            "SELECT SUM(duration_seconds) as total FROM execution_logs WHERE duration_seconds IS NOT NULL"
        )
        total_duration = cursor.fetchone()["total"] or 0.0

        # Total de itens processados
        cursor.execute(
            "SELECT SUM(items_processed) as total FROM execution_logs WHERE items_processed IS NOT NULL"
        )
        total_items = cursor.fetchone()["total"] or 0

        # FTE (Full-Time Equivalent) - assumindo 8h por dia útil
        fte_hours = total_duration / 3600 if total_duration else 0
        fte_days = fte_hours / 8
        fte_weeks = fte_days / 5

        conn.close()

        return {
            "total_executions": total_executions,
            "status_counts": status_counts,
            "total_duration_seconds": total_duration,
            "total_duration_hours": total_duration / 3600,
            "total_items_processed": total_items,
            "fte_hours": fte_hours,
            "fte_days": fte_days,
            "fte_weeks": fte_weeks,
        }
