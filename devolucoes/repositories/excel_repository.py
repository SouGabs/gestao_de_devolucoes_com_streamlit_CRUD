from pathlib import Path

import pandas as pd

from devolucoes.config import FACT_REQUIRED_COLUMNS


class ExcelRepository:
    """Persistência das tabelas Excel. A tabela fato é sempre relida do disco."""

    def __init__(self, fact_path: Path, customers_path: Path, products_path: Path):
        self.fact_path = Path(fact_path)
        self.customers_path = Path(customers_path)
        self.products_path = Path(products_path)

    def missing_files(self) -> list[Path]:
        return [path for path in (self.fact_path, self.customers_path, self.products_path) if not path.is_file()]

    def read_fact(self) -> pd.DataFrame:
        try:
            frame = pd.read_excel(self.fact_path)
        except Exception as exc:
            raise RuntimeError(f"Não foi possível ler {self.fact_path}: {exc}") from exc
        # Assegura colunas do fluxo sem remover as demais colunas existentes.
        for column in FACT_REQUIRED_COLUMNS:
            if column not in frame.columns:
                frame[column] = pd.NA
        return frame

    def read_customers(self) -> pd.DataFrame:
        return self._read_dimension(self.customers_path, "ID_Cliente", "Nome_Cliente")

    def read_products(self) -> pd.DataFrame:
        return self._read_dimension(self.products_path, "ID_Produto", "Nome_Produto")

    @staticmethod
    def _read_dimension(path: Path, id_column: str, name_column: str) -> pd.DataFrame:
        try:
            frame = pd.read_excel(path)
        except Exception as exc:
            raise RuntimeError(f"Não foi possível ler {path}: {exc}") from exc
        missing = [column for column in (id_column, name_column) if column not in frame.columns]
        if missing:
            raise ValueError(f"{path.name} não contém as colunas obrigatórias: {', '.join(missing)}")
        return frame[[id_column, name_column]].dropna(subset=[id_column, name_column]).drop_duplicates()

    def save_fact(self, frame: pd.DataFrame) -> None:
        try:
            frame.to_excel(self.fact_path, index=False)
        except Exception as exc:
            raise RuntimeError(f"Não foi possível salvar {self.fact_path}: {exc}") from exc
