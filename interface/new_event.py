import streamlit as st
from datetime import date
from linea.data_ingestion.data_ingestion_service import DataIngestionService

def show(username: str):
    st.header("📄 Formulario de Nueva Parada")
    with st.form("event_form"):
        planta = st.text_input("Planta", value="8373")
        periodo = st.text_input("Periodo")
        fecha_inicio = st.date_input("Fecha de inicio", value=date.today())
        fecha_termino = st.date_input("Fecha de termino", value=date.today())
        material = st.text_input("Material")
        descripcion = st.text_input("Descripcion del material")
        batch = st.text_input("Batch")
        vendedor = st.text_input("Vendedor")
        complain_qty = st.text_input("Complain Qty")
        tiempo_parada = st.text_input("Tiempo de parada")
        consecuencia = st.selectbox(
            "Consecuencia",
            ["", "Se rechazo la materia prima?", "Se rechazo la masa?", "Se rechazo el packaging?"]
        )

        submitted = st.form_submit_button("Enviar")

        if submitted:
            if all([planta, periodo, fecha_inicio, fecha_termino, material, descripcion,
                    batch, vendedor, complain_qty, tiempo_parada, consecuencia]):
                event_data = {
                    "Usuario": username,
                    "Planta": planta,
                    "Periodo": periodo,
                    "Fecha de inicio": str(fecha_inicio),
                    "Fecha de termino": str(fecha_termino),
                    "Material": material,
                    "Descripcion del material": descripcion,
                    "Batch": batch,
                    "Vendedor": vendedor,
                    "Complain Qty": complain_qty,
                    "Tiempo de parada": tiempo_parada,
                    "Consecuencia": consecuencia
                }
                service = DataIngestionService()
                service.ingest_event(event_data)
                st.success("Formulario enviado exitosamente 🎉")
            else:
                st.error("Por favor, completa todos los campos.")
