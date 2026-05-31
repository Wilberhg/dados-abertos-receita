from src.core.logger import logger
from src.core.paths import (
    RAW_DIR,
    EXTRACTED_DIR,
    CONVERTED_DIR,
    assegura_criacao_diretorios,
)
from src.models.execution_log import ExecutionLog, StageType
from src.services.api_service import DadosAbertosService
from src.services.execution_log_service import ExecutionLogService
from src.services.monthly_service import MonthlyPipeline


def main() -> None:
    logger.info("Iniciando execução principal")
    
    execution_log_service = ExecutionLogService()
    log = ExecutionLog.create_started(StageType.PIPELINE_MONTHLY.value)
    log_id = execution_log_service.repository.save(log)
    log = ExecutionLog(
        id=log_id,
        stage_type=log.stage_type,
        status=log.status,
        started_at=log.started_at,
    )

    try:
        assegura_criacao_diretorios()

        service = DadosAbertosService(execution_log_service=execution_log_service)
        conteudo_pagina, data_base = service.checa_existencia_bases()
        if conteudo_pagina is None or data_base is None:
            raise RuntimeError("Não foi possível localizar bases disponíveis.")

        links_bases = service.coleta_urls_arquivos(conteudo_pagina)
        raw_dir = RAW_DIR / data_base
        sucesso = service.baixar_bases(links_bases, raw_dir=raw_dir)
        if not sucesso:
            raise RuntimeError("Não foi possível concluir o download das bases.")

        logger.info("Download das bases para %s concluído com sucesso.", data_base)

        extracted_dir = EXTRACTED_DIR / data_base
        converted_dir = CONVERTED_DIR / data_base
        extracted_dir.mkdir(parents=True, exist_ok=True)
        converted_dir.mkdir(parents=True, exist_ok=True)

        pipeline = MonthlyPipeline(
            raw_dir,
            extracted_dir,
            converted_dir,
            execution_log_service=execution_log_service,
        )
        pipeline.run()

        logger.info("Pipeline mensal para %s concluído com sucesso.", data_base)
        execution_log_service.log_success(log)
    except Exception:
        error_log = log.mark_failure("Falha na execução do pipeline")
        execution_log_service.repository.save(error_log)
        logger.exception("Falha na execução do pipeline")
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Falha na execução do pipeline")
        raise
