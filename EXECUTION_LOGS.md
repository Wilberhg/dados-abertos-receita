# Sistema de Logs de Execução SQLite

Este documento descreve a estrutura de logs de execução do projeto para rastreamento de métricas e FTE (Full-Time Equivalent).

## Visão Geral

O sistema registra cada etapa do pipeline em um banco de dados SQLite (`logs/executions.db`), permitindo:

- Rastreamento de tempo de execução por etapa
- Contagem de itens processados
- Identificação de falhas e erros
- Cálculo de métricas de FTE
- Histórico completo de execuções

## Estrutura de Dados

### Tabela: `execution_logs`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER | ID único (autoincremento) |
| `stage_type` | TEXT | Tipo de etapa (veja tipos abaixo) |
| `status` | TEXT | Status: STARTED, SUCCESS, FAILURE |
| `started_at` | TEXT | ISO timestamp de início |
| `ended_at` | TEXT | ISO timestamp de fim (NULL se em progresso) |
| `duration_seconds` | REAL | Duração em segundos |
| `items_processed` | INTEGER | Quantidade de itens processados |
| `error_message` | TEXT | Mensagem de erro (se houver) |
| `created_at` | TEXT | Timestamp de criação do registro |

### Tipos de Etapa (`StageType`)

- `PIPELINE_MONTHLY`: Execução do pipeline mensal completo
- `DOWNLOAD_BASES`: Download de bases da API Dados Abertos
- `EXTRACT_ZIPS`: Extração de arquivos ZIP
- `CONVERT_CSVS`: Conversão de CSV para Parquet
- `API_SEARCH`: Busca de bases disponíveis
- `PROCESS_CLIENTS`: Processamento de clientes

### Status de Execução

- `STARTED`: Etapa iniciada
- `SUCCESS`: Etapa concluída com sucesso
- `FAILURE`: Etapa falhou

## Como Usar

### Integração Automática

Os serviços principais já foram integrados com o sistema de logs:

```python
from src.services.execution_log_service import ExecutionLogService
from src.repositories.execution_log_repository import ExecutionLogRepository

# O logger é iniciado automaticamente nos serviços principais
# Exemplo: api_service, monthly_service, cliente_service
```

### Consultar Métricas

#### Via Python

```python
from src.repositories.execution_log_repository import ExecutionLogRepository

repo = ExecutionLogRepository()

# Métricas gerais
metrics = repo.get_metrics()
print(f"Total de execuções: {metrics['total_executions']}")
print(f"FTE horas: {metrics['fte_hours']}")
print(f"FTE dias: {metrics['fte_days']}")
print(f"FTE semanas: {metrics['fte_weeks']}")

# Resumo por etapa
summary = repo.get_summary_by_stage("EXTRACT_ZIPS")
print(summary)

# Logs recentes
logs = repo.get_by_stage("DOWNLOAD_BASES", limit=10)
for log in logs:
    print(log)
```

#### Via Relatório

```bash
# Exibir relatório no terminal
python -m src.utils.metrics_reporter

# Exportar para JSON
python -c "from src.utils.metrics_reporter import export_metrics_json; export_metrics_json('my_metrics.json')"
```

## Exemplos

### Rastrear Execução Customizada

```python
from src.services.execution_log_service import ExecutionLogService
from src.models.execution_log import StageType, ExecutionLog

service = ExecutionLogService()

# Opção 1: Context manager (recomendado)
try:
    log = ExecutionLog.create_started("CUSTOM_STAGE")
    log_id = service.repository.save(log)
    log = ExecutionLog(
        id=log_id,
        stage_type=log.stage_type,
        status=log.status,
        started_at=log.started_at,
    )
    
    # Fazer processamento
    items_count = 100
    
    service.log_success(log, items_processed=items_count)
except Exception as e:
    error_log = log.mark_failure(str(e))
    service.repository.save(error_log)
    raise
```

## Métricas de FTE

FTE (Full-Time Equivalent) é calculado com base no tempo total de execução:

- **FTE Horas**: Total de segundos / 3600
- **FTE Dias**: FTE Horas / 8 (assumindo dia útil de 8h)
- **FTE Semanas**: FTE Dias / 5 (assumindo semana de 5 dias)

Exemplo:
- Se o pipeline rodou por 40 horas no total
- FTE = 40h / 8h = 5 dias
- FTE = 5 dias / 5 = 1 semana

## Consultas SQL Úteis

```sql
-- Total de execuções por etapa
SELECT stage_type, COUNT(*) as count
FROM execution_logs
GROUP BY stage_type;

-- Tempo médio por etapa
SELECT 
    stage_type,
    AVG(duration_seconds) as avg_duration,
    MAX(duration_seconds) as max_duration,
    MIN(duration_seconds) as min_duration
FROM execution_logs
WHERE status = 'SUCCESS'
GROUP BY stage_type;

-- Última execução de cada etapa
SELECT 
    stage_type,
    MAX(started_at) as last_execution,
    status
FROM execution_logs
GROUP BY stage_type;

-- Taxa de sucesso por etapa
SELECT 
    stage_type,
    status,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM execution_logs WHERE stage_type = e.stage_type), 2) as percentage
FROM execution_logs e
GROUP BY stage_type, status
ORDER BY stage_type, status;

-- Erros recentes
SELECT id, stage_type, started_at, error_message
FROM execution_logs
WHERE error_message IS NOT NULL
ORDER BY started_at DESC
LIMIT 10;
```

## Limpeza de Dados

Para manter o banco de dados limpo, você pode deletar logs antigos:

```python
import sqlite3
from src.infra.database.sqlite_connection import SqliteConnection

conn = SqliteConnection().get_connection()
cursor = conn.cursor()

# Deletar logs com mais de 30 dias
cursor.execute("""
    DELETE FROM execution_logs
    WHERE created_at < datetime('now', '-30 days')
""")

conn.commit()
conn.close()
```

## Troubleshooting

### Arquivo não encontrado: `executions.db`

O banco de dados é criado automaticamente na primeira execução. Se não existir:

```python
from src.infra.database.sqlite_connection import SqliteConnection
db = SqliteConnection()  # Cria o banco e o schema
```

### Sem dados no relatório

1. Execute o pipeline pelo menos uma vez
2. Verifique se `logs/executions.db` existe
3. Verifique se o banco está sendo acessível:

```python
from src.repositories.execution_log_repository import ExecutionLogRepository
repo = ExecutionLogRepository()
logs = repo.get_all()
print(f"Total de logs: {len(logs)}")
```
