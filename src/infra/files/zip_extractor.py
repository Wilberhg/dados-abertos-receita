from pathlib import Path
from zipfile import ZipFile


class ZipExtractor:
    def process(
        self,
        source: Path,
        target_dir: Path,
    ) -> Path:
        with ZipFile(source, "r") as zip_file:
            internal_file = zip_file.namelist()[0]
            zip_file.extractall(target_dir)

        extracted_file = target_dir / internal_file
        final_file = target_dir / source.with_suffix(".csv").name
        extracted_file.rename(final_file)
        return final_file
