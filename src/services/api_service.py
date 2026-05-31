from pathlib import Path
from typing import Optional
from xml.etree.ElementTree import Element

from src.core.config import coleta_data_atual, formata_data_base, subtrai_data_base
from src.core.logger import logger
from src.core.paths import OUTPUT_DIR
from src.core.ports import DadosAbertosPort
from src.infra.api.dados_abertos import ApiDadosAbertos
from src.models.execution_log import ExecutionLog, StageType
from src.services.execution_log_service import ExecutionLogService


class DadosAbertosService:

    NOMES_ARQUIVOS = ("Empresas", "Estabelecimentos")

    def __init__(
        self,
        client: DadosAbertosPort | None = None,
        output_dir: Path | None = None,
        execution_log_service: ExecutionLogService | None = None,
    ):
        self.client = client or ApiDadosAbertos()
        self.output_dir = output_dir or OUTPUT_DIR
        self.execution_log_service = execution_log_service or ExecutionLogService()
log = ExecutionLog.create_started(StageType.API_SEARCH.value)
        log_id = self.execution_log_service.repository.save(log)
        log = ExecutionLog(
            id=log_id,
            stage_type=log.stage_type,
            status=log.status,
            started_at=log.started_at,
        )

        data_atual = coleta_data_atual()
        data_base = formata_data_base(data_atual)
        logger.info("Buscando bases disponíveis para a data de referência %s", data_base)
        try:
            for attempt in range(1, 4):
                try:
                    conteudo_pagina = self.client.consultar_data_base(data_base)
                except Exception:
                    conteudo_pagina = None
                    logger.warning(
                        "Tentativa %s falhou para data %s. Regressando para data anterior.",
                        attempt,
                        data_base,
                    )

                if conteudo_pagina is not None:
                    logger.info("Base disponível encontrada para %s", data_base)
                    self.execution_log_service.log_success(log)
                    return conteudo_pagina, data_base
                data_base = subtrai_data_base(data_base)

            error_log = log.mark_failure("Nenhuma base disponível encontrada")
            self.execution_log_service.repository.save(error_log)
            return None, None
        except Exception as e:
            error_log = log.mark_failure(str(e))
            self.execution_log_service.repository.save(error_log)
            raisonteudo_pagina, data_base
            data_base = subtrai_data_base(data_base)
        return None, None

    def coleta_urls_arquivos(self, conteudo_pagina: Element | None) -> list[str]:
        links_bases: list[str] = []
        if conteudo_pagina is None:
        log = ExecutionLog.create_started(StageType.DOWNLOAD_BASES.value)
        log_id = self.execution_log_service.repository.save(log)
        log = ExecutionLog(
            id=log_id,
            stage_type=log.stage_type,
            status=log.status,
            started_at=log.started_at,
        )

        if not links_bases:
            error_log = log.mark_failure("Nenhum link de base fornecido")
            self.execution_log_service.repository.save(error_log)
            return False

        raw_dir = raw_dir or self.output_dir / "raw"
        downloaded_count = 0

        try:
            for link in links_bases:
                _, data_base, nome_arqv = link.rsplit("/", 2)
                diretorio = raw_dir / data_base / nome_arqv
                diretorio.parent.mkdir(parents=True, exist_ok=True)
                if diretorio.exists():
                    logger.info("Arquivo já existe e será ignorado: %s", diretorio)
                    continue

                logger.info("Baixando base %s", link)
                conteudo_arquivo = self.client.baixa_base_empresas(link_arquivo=link)
                if conteudo_arquivo is None:
                    logger.error("Falha ao baixar o arquivo %s", link)
                    error_log = log.mark_failure(f"Falha ao baixar {link}")
                    self.execution_log_service.repository.save(error_log)
                    return False

                diretorio.write_bytes(conteudo_arquivo)
                downloaded_count += 1
                logger.info("Arquivo salvo em %s", diretorio)

            self.execution_log_service.log_success(log, items_processed=downloaded_count)
            return True
        except Exception as e:
            error_log = log.mark_failure(str(e))
            self.execution_log_service.repository.save(error_log)
            rais
        raw_dir = raw_dir or self.output_dir / "raw"
        for link in links_bases:
            _, data_base, nome_arqv = link.rsplit("/", 2)
            diretorio = raw_dir / data_base / nome_arqv
            diretorio.parent.mkdir(parents=True, exist_ok=True)
            if diretorio.exists():
                logger.info("Arquivo já existe e será ignorado: %s", diretorio)
                continue

            logger.info("Baixando base %s", link)
            conteudo_arquivo = self.client.baixa_base_empresas(link_arquivo=link)
            if conteudo_arquivo is None:
                logger.error("Falha ao baixar o arquivo %s", link)
                return False

            diretorio.write_bytes(conteudo_arquivo)
            logger.info("Arquivo salvo em %s", diretorio)
        return True
