from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
FACT_FILE = DATA_DIR / "fato_devolucoes.xlsx"
CUSTOMERS_FILE = DATA_DIR / "dim_clientes.xlsx"
PRODUCTS_FILE = DATA_DIR / "dim_produtos.xlsx"

FACT_REQUIRED_COLUMNS = (
    "COM_ID_Devolucao",
    "COM_ID_Cliente",
    "COM_ID_Produto",
    "LOG_Transportadora",
    "QUA_Status_Qualidade",
)
