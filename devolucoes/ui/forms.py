from dataclasses import dataclass
from datetime import date

import streamlit as st


@dataclass(frozen=True)
class FormField:
    column: str
    label: str
    kind: str = "text"
    required: bool = False


class FormRenderer:
    """Renderiza campos compartilhados de formulários por metadados."""

    @staticmethod
    def render(field: FormField, customers, products):
        if field.kind == "customer":
            lookup = customers.set_index("ID_Cliente")["Nome_Cliente"].to_dict()
            choices = customers["ID_Cliente"].tolist()
            return st.selectbox(field.label, choices, format_func=lambda key: str(lookup[key]), key=field.column)
        if field.kind == "product":
            lookup = products.set_index("ID_Produto")["Nome_Produto"].to_dict()
            choices = products["ID_Produto"].tolist()
            return st.selectbox(field.label, choices, format_func=lambda key: str(lookup[key]), key=field.column)
        if field.kind == "date":
            return st.date_input(field.label, value=date.today(), key=field.column)
        if field.kind == "number":
            return st.number_input(field.label, min_value=0.0, step=1.0, key=field.column)
        if field.kind == "status":
            return st.selectbox(field.label, ["Aprovado", "Reprovado", "Aprovado com ressalvas"], key=field.column)
        if field.kind == "textarea":
            return st.text_area(field.label, key=field.column)
        return st.text_input(field.label, key=field.column)

    @classmethod
    def render_fields(cls, fields, customers, products) -> dict:
        return {field.column: cls.render(field, customers, products) for field in fields}
