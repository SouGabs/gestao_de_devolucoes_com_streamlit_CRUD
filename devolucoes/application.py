from pathlib import Path

import streamlit as st

from devolucoes.config import CUSTOMERS_FILE, FACT_FILE, PRODUCTS_FILE
from devolucoes.repositories.excel_repository import ExcelRepository
from devolucoes.services.workflow_service import WorkflowService
from devolucoes.ui import commercial, logistics, quality


@st.cache_data
def _load_customers(path: str):
    return ExcelRepository._read_dimension(Path(path), "ID_Cliente", "Nome_Cliente")


@st.cache_data
def _load_products(path: str):
    return ExcelRepository._read_dimension(Path(path), "ID_Produto", "Nome_Produto")


def run_application():
    st.set_page_config(page_title="Gestão de Devoluções", page_icon="↩️", layout="wide")
    st.title("Gestão de Devoluções")
    st.caption("Fluxo de trabalho: Comercial → Logística → Garantia da Qualidade")

    repository = ExcelRepository(FACT_FILE, CUSTOMERS_FILE, PRODUCTS_FILE)
    missing = repository.missing_files()
    if missing:
        st.error("Arquivos necessários não encontrados:\n\n" + "\n".join(f"- `{path}`" for path in missing))
        st.stop()

    try:
        fact = repository.read_fact()  # Sem cache para ler atualizações no arquivo.
        customers = _load_customers(str(CUSTOMERS_FILE))
        products = _load_products(str(PRODUCTS_FILE))
    except (RuntimeError, ValueError) as exc:
        st.error(str(exc))
        st.stop()

    service = WorkflowService()
    profile = st.sidebar.radio("Perfil de Acesso", ["Comercial", "Logística", "Qualidade"])
    st.sidebar.metric("Devoluções cadastradas", len(fact))
    if profile == "Comercial":
        commercial.render(service, repository, fact, customers, products)
    elif profile == "Logística":
        logistics.render(service, repository, fact, customers, products)
    else:
        quality.render(service, repository, fact, customers, products)
