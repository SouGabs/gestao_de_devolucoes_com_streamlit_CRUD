from datetime import date, datetime
from typing import Any
import pandas as pd

from devolucoes.config import FACT_REQUIRED_COLUMNS


class WorkflowService:
    """Regras de fila e transição de etapa, independentes da interface."""

    @staticmethod
    def normalize_fact(frame: pd.DataFrame) -> pd.DataFrame:
        result = frame.copy()
        for column in FACT_REQUIRED_COLUMNS:
            if column not in result:
                result[column] = pd.NA
        return result

    @staticmethod
    def logistics_queue(frame: pd.DataFrame) -> pd.DataFrame:
        fact = WorkflowService.normalize_fact(frame)
        return fact[fact["COM_ID_Devolucao"].notna() & fact["LOG_Transportadora"].isna()].copy()

    @staticmethod
    def quality_queue(frame: pd.DataFrame) -> pd.DataFrame:
        fact = WorkflowService.normalize_fact(frame)
        return fact[fact["LOG_Transportadora"].notna() & fact["QUA_Status_Qualidade"].isna()].copy()

    @staticmethod
    def create_return(frame: pd.DataFrame, values: dict) -> pd.DataFrame:
        fact = WorkflowService.normalize_fact(frame)
        numeric_ids = pd.to_numeric(fact["COM_ID_Devolucao"], errors="coerce").dropna()
        new_id = int(numeric_ids.max()) + 1 if not numeric_ids.empty else 1
        row = {column: pd.NA for column in fact.columns}
        for column, value in values.items():
            row: dict[str, Any] = {column: pd.NA for column in fact.columns}
        row["COM_ID_Devolucao"] = new_id
        for column in row:
            if column not in fact:
                fact[column] = pd.NA
        return pd.concat([fact, pd.DataFrame([row])], ignore_index=True)

    @staticmethod
    def complete_stage(frame: pd.DataFrame, return_id, values: dict) -> pd.DataFrame:
        fact = WorkflowService.normalize_fact(frame)
        matches = fact["COM_ID_Devolucao"].eq(return_id)
        if not matches.any():
            raise ValueError(f"Devolução {return_id} não encontrada.")
        for column, value in values.items():
            if column not in fact:
                fact[column] = pd.NA
            normalized_value = WorkflowService._coerce_value(fact[column], value)
            fact.loc[matches, column] = normalized_value
        return fact

    @staticmethod
    def _coerce_value(column: pd.Series, value):
        """Adapta valores dos widgets ao dtype atual da coluna, inclusive Arrow."""
        if value is None or value is pd.NA:
            return pd.NA
        if pd.api.types.is_string_dtype(column.dtype):
            if isinstance(value, (date, datetime, pd.Timestamp)):
                return value.isoformat()
            return str(value)
        if pd.api.types.is_datetime64_any_dtype(column.dtype):
            return pd.Timestamp(value) if isinstance(value, (date, datetime)) else value
        return value

    @staticmethod
    def with_dimension_names(frame: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
        result = frame.copy()
        if "COM_ID_Cliente" in result:
            customer_names = customers.rename(columns={"ID_Cliente": "COM_ID_Cliente", "Nome_Cliente": "Cliente"})
            result = result.merge(customer_names, how="left", on="COM_ID_Cliente")
        if "COM_ID_Produto" in result:
            product_names = products.rename(columns={"ID_Produto": "COM_ID_Produto", "Nome_Produto": "Produto"})
            result = result.merge(product_names, how="left", on="COM_ID_Produto")
        return result
