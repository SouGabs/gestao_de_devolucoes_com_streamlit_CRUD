import streamlit as st
import datetime
from devolucoes.services.workflow_service import WorkflowService
from devolucoes.ui.forms import FormField, FormRenderer


FIELDS = (
    FormField("LOG_Transportadora", "Transportadora", required=True),
    FormField("LOG_Cod_Rastreio", "Código de rastreio"),
    FormField("LOG_Data_Coleta", "Data da coleta", "date"),
    FormField("LOG_Data_Recebimento", "Data de recebimento", "date"),
    FormField("LOG_Custo_Frete", "Custo do frete", "number"),
    FormField("LOG_Status_Transp", "Status do transporte"),
    FormField("LOG_Motorista", "Motorista"),
    FormField("LOG_Placa_Veiculo", "Placa do veículo"),
    FormField("LOG_Avaria_Transp", "Avaria no transporte", "textarea"),
    FormField("LOG_Observacoes", "Observações", "textarea"),
)


def render(service, repository, fact, customers, products):
    st.subheader("Fila da Logística")
    queue = service.logistics_queue(fact)
    st.dataframe(service.with_dimension_names(queue, customers, products), width="stretch", hide_index=True)
    ids = queue["COM_ID_Devolucao"].dropna().tolist()
    if not ids:
        st.info("Não há devoluções aguardando a Logística.")
        return
    with st.form("form_logistica", clear_on_submit=True):
        selected_id = st.selectbox("ID da devolução", ids, key="log_return_id")
        values = FormRenderer.render_fields(FIELDS, customers, products)
        submitted = st.form_submit_button("Salvar dados de transporte", type="primary")
   

    if submitted:
        if not values["LOG_Transportadora"].strip():
            st.error("Informe a transportadora.")
            return
        
        # Correção: Converter objetos date para string no formato AAAA-MM-DD
        for key, val in values.items():
            if isinstance(val, datetime.date):
                values[key] = val.strftime('%Y-%m-%d')
                
        updated = service.complete_stage(fact, selected_id, values)
        repository.save_fact(updated)
        st.success("Dados de transporte salvos.")
        st.rerun()
