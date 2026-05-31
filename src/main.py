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
    if conteudo_pagina is None or data_base is None:
        raise RuntimeError("Não foi possível localizar bases disponíveis.")

    links_bases = service.coleta_urls_arquivos(conteudo_pagina)
    raw_dir = RAW_DIR / data_base
    sucesso = service.baixar_bases(links_bases, raw_dir=raw_dir)
    if not sucesso:
        raise RuntimeError("Não foi possível concluir o download das bases.")
''
    print(f"Download das bases para {data_base} concluído com sucesso.")

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
