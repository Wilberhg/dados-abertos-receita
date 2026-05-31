from pathlib import Path
import polars as pl


class CsvToParquetConverter:
    def process(
        self,
        source: Path,
        target_dir: Path,
    ) -> Path:
        parquet_file = target_dir / source.with_suffix(".parquet").name
        (
            pl.scan_csv(
                source,
                encoding="utf8-lossy",
            ).sink_parquet(parquet_file)
        )
        return parquet_file
