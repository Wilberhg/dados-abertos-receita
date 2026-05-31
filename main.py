from src.core.paths import (
    RAW_DIR,
    EXTRACTED_DIR,
    CONVERTED_DIR,
    assegura_criacao_diretorios,
)

from src.services.api_service import DadosAbertosService
from src.services.monthly_service import MonthlyPipeline


def main() -> None:
    assegura_criacao_diretorios()

    service = DadosAbertosService()
    conteudo_pagina, data_base = service.checa_existencia_bases()
    if not conteudo_pagina or not data_base:
        raise RuntimeError("Não foi possível localizar bases disponíveis.")

    links_bases = service.coleta_urls_arquivos(conteudo_pagina)
    sucesso = service.baixar_bases(links_bases)
    if not sucesso:
        raise RuntimeError("Não foi possível concluir o download das bases.")

    print(f"Download das bases para {data_base} concluído com sucesso.")

    raw_dir = RAW_DIR / data_base
    extracted_dir = EXTRACTED_DIR / data_base
    converted_dir = CONVERTED_DIR / data_base
    extracted_dir.mkdir(parents=True, exist_ok=True)
    converted_dir.mkdir(parents=True, exist_ok=True)

    pipeline = MonthlyPipeline(
        raw_dir,
        extracted_dir,
        converted_dir,
    )
    pipeline.run()

    print(f"Pipeline mensal para {data_base} concluído com sucesso.")


if __name__ == "__main__":
    main()
