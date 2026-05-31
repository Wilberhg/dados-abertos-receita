"""
Script para gerar relatórios de execução.

Uso:
    python -m src.utils.metrics_reporter
"""

from src.utils.metrics_reporter import print_metrics, print_recent_logs, export_metrics_json

if __name__ == "__main__":
    try:
        print_metrics()
        print("\n" * 2)
        print_recent_logs(limit=30)
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
