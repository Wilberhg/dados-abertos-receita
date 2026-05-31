import sqlite3
from pathlib import Path

from src.core.paths import LOGS_DIR


class SqliteConnection:
    """Gerencia conexão com banco de dados SQLite."""

    DB_PATH = LOGS_DIR / "executions.db"

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or self.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Obtém uma conexão com o banco de dados."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        """Inicializa o schema do banco de dados."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stage_type TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                duration_seconds REAL,
                items_processed INTEGER,
                error_message TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_stage_type 
            ON execution_logs(stage_type)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_status 
            ON execution_logs(status)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_started_at 
            ON execution_logs(started_at)
            """
        )

        conn.commit()
        conn.close()

    def close(self) -> None:
        """Fecha a conexão."""
        pass
