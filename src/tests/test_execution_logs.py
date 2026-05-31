"""
Script de teste para validar o sistema de logs de execução.

Uso:
    python -m src.tests.test_execution_logs
"""

import time
from datetime import datetime

from src.infra.database.sqlite_connection import SqliteConnection
from src.models.execution_log import ExecutionLog, StageType
from src.repositories.execution_log_repository import ExecutionLogRepository
from src.services.execution_log_service import ExecutionLogService


def test_basic_operations():
    """Testa operações básicas do repositório."""
    print("Testando operações básicas...")
    repo = ExecutionLogRepository()

    # Criar log
    log = ExecutionLog.create_started(StageType.EXTRACT_ZIPS.value)
    log_id = repo.save(log)
    print(f"✓ Log criado com ID: {log_id}")

    # Simular processamento
    time.sleep(0.5)

    # Marcar como sucesso
    success_log = log.mark_success(items_processed=42)
    log_with_id = ExecutionLog(
        id=log_id,
        stage_type=success_log.stage_type,
        status=success_log.status,
        started_at=success_log.started_at,
        ended_at=success_log.ended_at,
        duration_seconds=success_log.duration_seconds,
        items_processed=success_log.items_processed,
    )
    repo.save(log_with_id)
    print(f"✓ Log marcado como sucesso")

    # Recuperar log
    retrieved = repo.get_by_id(log_id)
    assert retrieved is not None
    assert retrieved.items_processed == 42
    assert retrieved.status == "SUCCESS"
    print(f"✓ Log recuperado: {retrieved}")


def test_failure_handling():
    """Testa tratamento de falhas."""
    print("\nTestando tratamento de falhas...")
    repo = ExecutionLogRepository()

    log = ExecutionLog.create_started(StageType.CONVERT_CSVS.value)
    log_id = repo.save(log)

    # Simular falha
    error_log = log.mark_failure("Erro ao processar arquivo")
    log_with_id = ExecutionLog(
        id=log_id,
        stage_type=error_log.stage_type,
        status=error_log.status,
        started_at=error_log.started_at,
        ended_at=error_log.ended_at,
        duration_seconds=error_log.duration_seconds,
        error_message=error_log.error_message,
    )
    repo.save(log_with_id)
    print(f"✓ Log de falha registrado")

    retrieved = repo.get_by_id(log_id)
    assert retrieved.status == "FAILURE"
    assert retrieved.error_message == "Erro ao processar arquivo"
    print(f"✓ Log de falha verificado")


def test_metrics():
    """Testa cálculo de métricas."""
    print("\nTestando métricas...")
    repo = ExecutionLogRepository()

    # Limpar dados antigos para teste limpo
    conn = SqliteConnection().get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM execution_logs WHERE created_at < datetime('now', '-1 day')")
    conn.commit()
    conn.close()

    # Criar alguns logs de teste
    for i in range(3):
        log = ExecutionLog.create_started(StageType.DOWNLOAD_BASES.value)
        log_id = repo.save(log)
        time.sleep(0.1)
        success_log = log.mark_success(items_processed=10 + i)
        log_with_id = ExecutionLog(
            id=log_id,
            stage_type=success_log.stage_type,
            status=success_log.status,
            started_at=success_log.started_at,
            ended_at=success_log.ended_at,
            duration_seconds=success_log.duration_seconds,
            items_processed=success_log.items_processed,
        )
        repo.save(log_with_id)

    metrics = repo.get_metrics()
    print(f"✓ Métricas calculadas:")
    print(f"  - Total execuções: {metrics['total_executions']}")
    print(f"  - Total itens: {metrics['total_items_processed']}")
    print(f"  - Duração total: {metrics['total_duration_hours']:.4f}h")
    print(f"  - FTE dias: {metrics['fte_days']:.4f}")
    print(f"  - FTE semanas: {metrics['fte_weeks']:.4f}")


def test_stage_summary():
    """Testa resumo por etapa."""
    print("\nTestando resumo por etapa...")
    repo = ExecutionLogRepository()

    summary = repo.get_summary_by_stage(StageType.DOWNLOAD_BASES.value)
    print(f"✓ Resumo da etapa DOWNLOAD_BASES:")
    for status, stats in summary.items():
        print(f"  - {status}: {stats['count']} execuções")


def test_service():
    """Testa serviço de logs."""
    print("\nTestando serviço de logs...")
    service = ExecutionLogService()

    log = ExecutionLog.create_started("TEST_STAGE")
    log_id = service.repository.save(log)
    log = ExecutionLog(
        id=log_id,
        stage_type=log.stage_type,
        status=log.status,
        started_at=log.started_at,
    )

    time.sleep(0.2)
    service.log_success(log, items_processed=100)
    print(f"✓ Serviço testado com sucesso")


def run_all_tests():
    """Executa todos os testes."""
    print("=" * 60)
    print("TESTE DO SISTEMA DE LOGS DE EXECUÇÃO")
    print("=" * 60)

    try:
        test_basic_operations()
        test_failure_handling()
        test_metrics()
        test_stage_summary()
        test_service()

        print("\n" + "=" * 60)
        print("✓ TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        print("\nAgora você pode usar o sistema de logs para rastrear execuções.")
        print("Execute: python -m src.utils.metrics_reporter")
        print("Para ver o relatório de métricas.")
    except AssertionError as e:
        print(f"\n✗ TESTE FALHOU: {e}")
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
