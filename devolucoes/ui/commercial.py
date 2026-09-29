import streamlit as st

from devolucoes.services.workflow_service import WorkflowService
from devolucoes.ui.forms import FormField, FormRenderer


FIELDS = (
    FormField("COM_Data_Solicitacao", "Data da solicitação", "date", True),
    FormField("COM_ID_Cliente", "Cliente", "customer", True),
    FormField("COM_ID_Produto", "Produto", "product", True),
    FormField("COM_NFD", "Número da nota de devolução"),
    FormField("COM_NFO", "Número da nota original"),
    FormField("COM_Quantidade", "Quantidade", "number", True),
    FormField("COM_Valor_Unitario", "Valor unitário", "number"),
    FormField("COM_Motivo", "Motivo", "textarea", True),
)


def render(service, repository, fact, customers, products):
    st.subheader("Registrar devolução")
    if customers.empty or products.empty:
        st.warning("Cadastre ao menos um cliente e um produto antes de registrar devoluções.")
        return
    with st.form("form_comercial", clear_on_submit=True):
        values = FormRenderer.render_fields(FIELDS, customers, products)
        submitted = st.form_submit_button("Registrar devolução", type="primary")
    if submitted:
        updated = service.create_return(fact, values)
        repository.save_fact(updated)
        st.success("Devolução registrada.")
        st.rerun()
