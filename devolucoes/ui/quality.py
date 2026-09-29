import streamlit as st

from devolucoes.ui.forms import FormField, FormRenderer


FIELDS = (
    FormField("QUA_Data_Inspecao", "Data da inspeção", "date"),
    FormField("QUA_Inspetor", "Inspetor"),
    FormField("QUA_Status_Qualidade", "Status da qualidade", "status", True),
    FormField("QUA_Categoria_Defeito", "Categoria do defeito"),
    FormField("QUA_Gravidade", "Gravidade"),
    FormField("QUA_Qtd_Aproveitavel", "Quantidade aproveitável", "number"),
    FormField("QUA_Qtd_Descarte", "Quantidade para descarte", "number"),
    FormField("QUA_Custo_Inspecao", "Custo da inspeção", "number"),
    FormField("QUA_Laudo_Tecnico", "Laudo técnico", "textarea"),
    FormField("QUA_Acao_Recomendada", "Ação recomendada", "textarea"),
)


def render(service, repository, fact, customers, products):
    st.subheader("Fila da Garantia da Qualidade")
    queue = service.quality_queue(fact)
    st.dataframe(service.with_dimension_names(queue, customers, products), width="stretch", hide_index=True)
    ids = queue["COM_ID_Devolucao"].dropna().tolist()
    if not ids:
        st.info("Não há devoluções aguardando inspeção da Qualidade.")
        return
    with st.form("form_qualidade", clear_on_submit=True):
        selected_id = st.selectbox("ID da devolução", ids, key="quality_return_id")
        values = FormRenderer.render_fields(FIELDS, customers, products)
        submitted = st.form_submit_button("Salvar laudo", type="primary")
    if submitted:
        updated = service.complete_stage(fact, selected_id, values)
        repository.save_fact(updated)
        st.success("Laudo da Qualidade salvo.")
        st.rerun()
