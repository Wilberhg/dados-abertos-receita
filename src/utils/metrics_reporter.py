"""
Utilitário para gerar relatórios e métricas de execução.

Uso:
    python -m src.utils.metrics_reporter
"""

import json
from datetime import datetime, timedelta

from src.repositories.execution_log_repository import ExecutionLogRepository


def format_duration(seconds: float) -> str:
    """Formata duração em segundos para formato legível."""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}h"


def print_stage_summary(stage_type: str, summary: dict) -> None:
    """Imprime resumo de uma etapa."""
    print(f"\n{stage_type}")
    print("=" * 60)

    for status, stats in summary.items():
        print(f"\n  Status: {status}")
        print(f"    Execuções: {stats['count']}")
        if stats["avg_duration_seconds"]:
            print(f"    Duração média: {format_duration(stats['avg_duration_seconds'])}")
        if stats["total_items_processed"]:
            print(f"    Total de itens: {stats['total_items_processed']}")
        if stats["last_execution"]:
            print(f"    Última execução: {stats['last_execution']}")


def print_metrics() -> None:
    """Imprime métricas gerais de execução."""
    repo = ExecutionLogRepository()
    metrics = repo.get_metrics()

    print("\n" + "=" * 60)
    print("MÉTRICAS DE EXECUÇÃO DO PIPELINE")
    print("=" * 60)

    print(f"\nTotal de execuções: {metrics['total_executions']}")
    print(f"Total de itens processados: {metrics['total_items_processed']}")
    print(f"Tempo total de execução: {format_duration(metrics['total_duration_seconds'])}")

    print("\n--- Status ---")
    for status, count in metrics["status_counts"].items():
        percentage = (count / metrics["total_executions"] * 100) if metrics["total_executions"] > 0 else 0
        print(f"  {status}: {count} ({percentage:.1f}%)")

    print("\n--- FTE (Full-Time Equivalent) ---")
    print(f"  Total de horas: {metrics['fte_hours']:.2f}h")
    print(f"  Total de dias (8h/dia): {metrics['fte_days']:.2f} dias")
    print(f"  Total de semanas (5 dias/semana): {metrics['fte_weeks']:.2f} semanas")

    # Mostrar resumo por etapa
    print("\n\n--- Resumo por Etapa ---")
    stage_types = [
        "PIPELINE_MONTHLY",
        "DOWNLOAD_BASES",
        "EXTRACT_ZIPS",
        "CONVERT_CSVS",
        "API_SEARCH",
        "PROCESS_CLIENTS",
    ]

    for stage_type in stage_types:
        summary = repo.get_summary_by_stage(stage_type)
        if summary:
            print_stage_summary(stage_type, summary)


def print_recent_logs(stage_type: str | None = None, limit: int = 20) -> None:
    """Imprime logs recentes."""
    repo = ExecutionLogRepository()
    logs = repo.get_recent_logs(stage_type=stage_type, limit=limit)

    title = f"LOGS RECENTES - {stage_type}" if stage_type else "LOGS RECENTES"
    print(f"\n{title}")
    print("=" * 100)
    print(f"{'ID':<5} {'Etapa':<20} {'Status':<10} {'Início':<25} {'Duração':<10} {'Itens':<8}")
    print("-" * 100)

    for log in logs:
        duration_str = format_duration(log.duration_seconds) if log.duration_seconds else "N/A"
        items_str = str(log.items_processed) if log.items_processed else "N/A"
        print(
            f"{log.id:<5} {log.stage_type:<20} {log.status:<10} "
            f"{log.started_at:<25} {duration_str:<10} {items_str:<8}"
        )

    if logs and any(log.error_message for log in logs):
        print("\n--- Erros ---")
        for log in logs:
            if log.error_message:
                print(f"  ID {log.id}: {log.error_message}")


def export_metrics_json(output_path: str = "metrics.json") -> None:
    """Exporta métricas para arquivo JSON."""
    repo = ExecutionLogRepository()
    metrics = repo.get_metrics()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print(f"\nMétricas exportadas para {output_path}")


if __name__ == "__main__":
    print_metrics()
    print("\n" * 2)
    print_recent_logs(limit=30)
