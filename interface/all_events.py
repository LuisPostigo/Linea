import streamlit as st
import sqlite3
import pandas as pd
from linea.data_ingestion.data_ingestion_service import DataIngestionService

def show(username: str):
    st.header("Historial de Reportes")
    service = DataIngestionService()
    db_path = service.db_saver.db_path

    with sqlite3.connect(db_path) as conn:
        query = f"""
            SELECT * FROM {service.db_saver.table_name}
            WHERE Usuario = ?
            ORDER BY id DESC
        """
        df = pd.read_sql_query(query, conn, params=(username,))

    if df.empty:
        st.info("No se encontraron reportes previos para este usuario.")
    else:
        st.dataframe(df)
