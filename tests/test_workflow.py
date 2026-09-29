import tempfile
import unittest
from datetime import date
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from devolucoes.repositories.excel_repository import ExcelRepository
from devolucoes.services.workflow_service import WorkflowService


class WorkflowServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = WorkflowService()
        self.fact = pd.DataFrame(
            [
                {"COM_ID_Devolucao": 10, "COM_ID_Cliente": 1, "COM_ID_Produto": 2,
                 "LOG_Transportadora": None, "QUA_Status_Qualidade": None},
                {"COM_ID_Devolucao": 11, "COM_ID_Cliente": 1, "COM_ID_Produto": 3,
                 "LOG_Transportadora": "Expresso", "QUA_Status_Qualidade": None},
                {"COM_ID_Devolucao": 12, "COM_ID_Cliente": 2, "COM_ID_Produto": 4,
                 "LOG_Transportadora": "Correios", "QUA_Status_Qualidade": "Aprovado"},
                {"COM_ID_Devolucao": None, "COM_ID_Cliente": 3, "COM_ID_Produto": 5,
                 "LOG_Transportadora": None, "QUA_Status_Qualidade": None},
            ]
        )

    def test_queues_follow_workflow_rules(self):
        self.assertEqual(self.service.logistics_queue(self.fact)["COM_ID_Devolucao"].tolist(), [10])
        self.assertEqual(self.service.quality_queue(self.fact)["COM_ID_Devolucao"].tolist(), [11])

    def test_creates_next_sequential_id_and_preserves_columns(self):
        created = self.service.create_return(self.fact, {"COM_Motivo": "Defeito"})
        self.assertEqual(created.iloc[-1]["COM_ID_Devolucao"], 13)
        self.assertEqual(created.iloc[-1]["COM_Motivo"], "Defeito")
        self.assertIn("LOG_Transportadora", created.columns)

    def test_creates_first_id_for_empty_table(self):
        created = self.service.create_return(pd.DataFrame(), {"COM_Motivo": "Avaria"})
        self.assertEqual(created.iloc[0]["COM_ID_Devolucao"], 1)

    def test_commercial_date_is_compatible_with_arrow_string_column(self):
        fact = pd.DataFrame({
            "COM_ID_Devolucao": pd.Series([1], dtype="int64[pyarrow]"),
            "COM_Data_Solicitacao": pd.Series(["2026-01-01"], dtype="string[pyarrow]"),
            "LOG_Transportadora": pd.Series([pd.NA], dtype="string[pyarrow]"),
            "QUA_Status_Qualidade": pd.Series([pd.NA], dtype="string[pyarrow]"),
        })
        created = self.service.create_return(fact, {"COM_Data_Solicitacao": date(2026, 9, 29)})
        self.assertEqual(created.iloc[-1]["COM_Data_Solicitacao"], "2026-09-29")
        self.assertEqual(str(created["COM_Data_Solicitacao"].dtype), "string")

    def test_logistics_date_is_compatible_with_arrow_string_column(self):
        fact = pd.DataFrame({
            "COM_ID_Devolucao": pd.Series([10], dtype="int64[pyarrow]"),
            "LOG_Transportadora": pd.Series([pd.NA], dtype="string[pyarrow]"),
            "LOG_Data_Coleta": pd.Series([pd.NA], dtype="string[pyarrow]"),
            "QUA_Status_Qualidade": pd.Series([pd.NA], dtype="string[pyarrow]"),
        })
        updated = self.service.complete_stage(fact, 10, {
            "LOG_Transportadora": "Frete Rápido",
            "LOG_Data_Coleta": date(2026, 9, 29),
        })
        self.assertEqual(updated.iloc[0]["LOG_Data_Coleta"], "2026-09-29")
        self.assertEqual(updated.iloc[0]["LOG_Transportadora"], "Frete Rápido")

    def test_quality_date_is_compatible_with_arrow_string_column(self):
        fact = pd.DataFrame({
            "COM_ID_Devolucao": pd.Series([11], dtype="int64[pyarrow]"),
            "LOG_Transportadora": pd.Series(["Transportadora"], dtype="string[pyarrow]"),
            "QUA_Status_Qualidade": pd.Series([pd.NA], dtype="string[pyarrow]"),
            "QUA_Data_Inspecao": pd.Series([pd.NA], dtype="string[pyarrow]"),
        })
        updated = self.service.complete_stage(fact, 11, {
            "QUA_Status_Qualidade": "Aprovado",
            "QUA_Data_Inspecao": date(2026, 9, 29),
        })
        self.assertEqual(updated.iloc[0]["QUA_Data_Inspecao"], "2026-09-29")
        self.assertEqual(updated.iloc[0]["QUA_Status_Qualidade"], "Aprovado")

    def test_completes_selected_record_without_changing_other_rows(self):
        updated = self.service.complete_stage(self.fact, 10, {"LOG_Transportadora": "Transportadora X"})
        self.assertEqual(updated.loc[updated["COM_ID_Devolucao"] == 10, "LOG_Transportadora"].iloc[0], "Transportadora X")
        self.assertTrue(pd.isna(updated.loc[updated["COM_ID_Devolucao"] == 11, "LOG_Transportadora"].iloc[0]) is False)

    def test_rejects_unknown_return_id(self):
        with self.assertRaisesRegex(ValueError, "não encontrada"):
            self.service.complete_stage(self.fact, 999, {"LOG_Transportadora": "X"})

    def test_joins_customer_and_product_names_to_prefixed_ids(self):
        customers = pd.DataFrame({"ID_Cliente": [1], "Nome_Cliente": ["Cliente A"]})
        products = pd.DataFrame({"ID_Produto": [2], "Nome_Produto": ["Produto B"]})
        result = self.service.with_dimension_names(self.fact.iloc[:1], customers, products)
        self.assertEqual(result.iloc[0]["Cliente"], "Cliente A")
        self.assertEqual(result.iloc[0]["Produto"], "Produto B")


class ExcelRepositoryTests(unittest.TestCase):
    def test_reads_and_writes_excel_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fact_path, customers_path, products_path = (root / name for name in ("fact.xlsx", "customers.xlsx", "products.xlsx"))
            fact = pd.DataFrame({"COM_ID_Devolucao": [1], "COM_ID_Cliente": [7], "COM_ID_Produto": [9]})
            customers = pd.DataFrame({"ID_Cliente": [7], "Nome_Cliente": ["Cliente"]})
            products = pd.DataFrame({"ID_Produto": [9], "Nome_Produto": ["Produto"]})
            fact.to_excel(fact_path, index=False)
            customers.to_excel(customers_path, index=False)
            products.to_excel(products_path, index=False)

            repository = ExcelRepository(fact_path, customers_path, products_path)
            self.assertEqual(repository.missing_files(), [])
            read_fact = repository.read_fact()
            self.assertIn("LOG_Transportadora", read_fact.columns)
            self.assertEqual(repository.read_customers().iloc[0]["Nome_Cliente"], "Cliente")
            self.assertEqual(repository.read_products().iloc[0]["Nome_Produto"], "Produto")
            repository.save_fact(read_fact.assign(LOG_Transportadora="Frete"))
            self.assertEqual(pd.read_excel(fact_path).iloc[0]["LOG_Transportadora"], "Frete")


class StreamlitSmokeTests(unittest.TestCase):
    def test_app_starts_without_streamlit_exceptions(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path), default_timeout=20).run()
        self.assertEqual(len(app.exception), 0)

    def test_each_profile_screen_renders_without_exceptions(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path), default_timeout=20).run()
        self.assertEqual(len(app.exception), 0)
        for profile in ("Logística", "Qualidade"):
            app.radio[0].set_value(profile).run()
            self.assertEqual(len(app.exception), 0, f"Erro ao renderizar o perfil {profile}")


if __name__ == "__main__":
    unittest.main()
