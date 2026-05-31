from pathlib import Path
from typing import Optional
from xml.etree.ElementTree import Element

from src.core.config import coleta_data_atual, formata_data_base, subtrai_data_base
from src.core.logger import logger
from src.core.paths import OUTPUT_DIR
from src.core.ports import DadosAbertosPort
from src.infra.api.dados_abertos import ApiDadosAbertos


class DadosAbertosService:

    NOMES_ARQUIVOS = ("Empresas", "Estabelecimentos")

    def __init__(
        self,
        client: DadosAbertosPort | None = None,
        output_dir: Path | None = None,
    ):
        self.client = client or ApiDadosAbertos()
        self.output_dir = output_dir or OUTPUT_DIR

    def checa_existencia_bases(self) -> tuple[Element | None, str | None]:
        data_atual = coleta_data_atual()
        data_base = formata_data_base(data_atual)
        logger.info("Buscando bases disponíveis para a data de referência %s", data_base)
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
                return conteudo_pagina, data_base
            data_base = subtrai_data_base(data_base)
        return None, None

    def coleta_urls_arquivos(self, conteudo_pagina: Element | None) -> list[str]:
        links_bases: list[str] = []
        if conteudo_pagina is None:
            return links_bases

        namespace = {"d": "DAV:"}
        for response in conteudo_pagina.findall("d:response", namespace):
            href = response.find("d:href", namespace)
            if (
                href is not None
                and href.text
                and any(word in href.text for word in self.NOMES_ARQUIVOS)
            ):
                links_bases.append(href.text)
        return links_bases

    def baixar_bases(
        self,
        links_bases: list[str],
        raw_dir: Path | None = None,
    ) -> bool:
        if not links_bases:
            return False

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
