from pathlib import Path


def arquivos_pendentes(
    origem: list[Path],
    destino: list[Path],
) -> list[Path]:
    processados = {arquivo.stem for arquivo in destino}

    return [arquivo for arquivo in origem if arquivo.stem not in processados]
