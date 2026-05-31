from typing import Any, Optional

from src.core.config import coleta_data_atual, formata_data_base, subtrai_data_base
from src.infra.api.dados_abertos import ApiDadosAbertos
from src.core.paths import OUTPUT_DIR


class DadosAbertosService:

    NOMES_ARQUIVOS = ("Empresas", "Estabelecimentos")

    def __init__(self, client: Optional[ApiDadosAbertos] = None):
        self.client = client or ApiDadosAbertos()

    def buscar_cliente(self, cpf: str) -> dict[str, str]:
        return self.client.buscar_cliente(cpf)

    def checa_existencia_bases(self) -> bool | Any:
        conteudo_pagina = None
        data_atual = coleta_data_atual()
        data_base = formata_data_base(data_atual)
        for _ in range(3):
            conteudo_pagina = self.client.consultar_data_base(data_base)
            if conteudo_pagina is not None:
                break
            data_base = subtrai_data_base(data_base)
        else:
            conteudo_pagina = False
        return conteudo_pagina

    def coleta_urls_arquivos(self, conteudo_pagina: Any) -> list[str] | bool:
        links_bases: list[str] = []
        namespace = {"d": "DAV:"}
        if conteudo_pagina is not None and conteudo_pagina is not False:
            for response in conteudo_pagina.findall("d:response", namespace):
                href = response.find("d:href", namespace)

                if (
                    href is not None
                    and href.text
                    and any(word in href.text for word in self.NOMES_ARQUIVOS)
                ):
                    links_bases.append(href.text)
            return links_bases
        return False

    def baixar_bases(self, links_bases: list[str] | bool) -> bool:
        if links_bases:
            for indice, link in enumerate(links_bases):
                _, data_base, nome_arqv = link.rsplit("/", 2)
                diretorio = OUTPUT_DIR / "raw" / data_base / nome_arqv
                if indice == 0:
                    diretorio.parent.mkdir(parents=True, exist_ok=True)
                if not diretorio.exists():
                    conteudo_arquivo = self.client.baixa_base_empresas(
                        link_arquivo=link
                    )
                    diretorio.write_bytes(conteudo_arquivo)
            return True
        return False
