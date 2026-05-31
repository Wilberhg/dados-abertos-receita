from pathlib import Path
from src.infra.files.file_discovery import arquivos_pendentes
from src.infra.files.parquet_converter import CsvToParquetConverter
from src.infra.files.zip_extractor import ZipExtractor


class MonthlyPipeline:

    def __init__(
        self,
        raw_dir: Path,
        extracted_dir: Path,
        converted_dir: Path,
        extractor: ZipExtractor | None = None,
        converter: CsvToParquetConverter | None = None,
    ):
        self.raw_dir = raw_dir
        self.extracted_dir = extracted_dir
        self.converted_dir = converted_dir
        self.extractor = extractor or ZipExtractor()
        self.converter = converter or CsvToParquetConverter()

    def run(self) -> None:
        self.extract_zips()
        self.convert_csvs()

    def extract_zips(self) -> None:
        zip_files = list(self.raw_dir.rglob("*.zip"))
        csv_files = list(self.extracted_dir.rglob("*.csv"))
        pending = arquivos_pendentes(zip_files, csv_files)

        for source_file in pending:
            self.extractor.process(source_file, self.extracted_dir)

    def convert_csvs(self) -> None:
        csv_files = list(self.extracted_dir.rglob("*.csv"))
        parquet_files = list(self.converted_dir.rglob("*.parquet"))
        pending = arquivos_pendentes(csv_files, parquet_files)

        for source_file in pending:
            self.converter.process(source_file, self.converted_dir)
