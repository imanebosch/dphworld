import awswrangler as wr
import pandas as pd


class Dataset:
    def __init__(self, name, path, format="csv"):
        self.name = name
        self.path = path
        self.format = format

    def read(self) -> pd.DataFrame:
        if self.format == "json":
            return wr.s3.read_json(self.path)
        elif self.format == "parquet":
            return wr.s3.read_parquet(self.path)
        elif self.format == "csv":
            return wr.s3.read_csv(self.path)
        else:
            raise ValueError(f"Unsupported format: {self.format}")

    def write(self, df: pd.DataFrame):
        if self.format == "csv":
            wr.s3.to_csv(
                df, path=self.path, index=False, mode="overwrite", dataset=True
            )
        elif self.format == "parquet":
            wr.s3.to_parquet(
                df, path=self.path, index=False, mode="overwrite", dataset=True
            )
        else:
            raise ValueError(f"Unsupported format: {self.format}")
