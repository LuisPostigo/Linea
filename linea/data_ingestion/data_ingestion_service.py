import os
import sqlite3
from typing import Dict
from directories import EVENTS_DB_PATH


class DataIngestionService:
    """
    Main service for handling incoming event data.
    It saves it to a database and then processes consequences.
    """

    def __init__(self) -> None:
        self.db_saver = self.SaveToDatabase()
        self.scenario_handler = self.Scenarios()

    def ingest_event(self, event_data: Dict) -> None:
        """
        Orchestrates the ingestion pipeline: save + scenario handling.
        """
        print("[IngestEvent] Received data:", event_data)
        self.db_saver.ingest_event(event_data)
        self.scenario_handler.handle(event_data)
        self.db_saver.debug_show_all()

    class SaveToDatabase:
        """
        Handles saving of event data into SQLite.
        """

        def __init__(self) -> None:
            self.db_path = EVENTS_DB_PATH
            self.table_name = "events"
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            print(f"[Init] Using DB path: {self.db_path}")
            self._ensure_table_exists()

        def _ensure_table_exists(self) -> None:
            """
            Creates the events table if it doesn't exist.
            """
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Usuario TEXT,
                        Planta TEXT,
                        Periodo TEXT,
                        Fecha_de_inicio TEXT,
                        Fecha_de_termino TEXT,
                        Material TEXT,
                        Descripcion_del_material TEXT,
                        Batch TEXT,
                        Vendedor TEXT,
                        Complain_Qty TEXT,
                        Tiempo_de_parada TEXT,
                        Consecuencia TEXT,
                        id_origen TEXT
                    );
                """)
                conn.commit()
                print("[Database] Table checked/created.")

        def ingest_event(self, event_data: Dict) -> None:
            """
            Inserts a single validated event dictionary into the database.
            """
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    INSERT INTO {self.table_name} (
                        Usuario, Planta, Periodo, Fecha_de_inicio, Fecha_de_termino, Material,
                        Descripcion_del_material, Batch, Vendedor, Complain_Qty, Tiempo_de_parada,
                        Consecuencia, id_origen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_data.get("Usuario", ""),
                    event_data.get("Planta", ""),
                    event_data.get("Periodo", ""),
                    event_data.get("Fecha_de_inicio", ""),
                    event_data.get("Fecha_de_termino", ""),
                    event_data.get("Material", ""),
                    event_data.get("Descripcion_del_material", ""),
                    event_data.get("Batch", ""),
                    event_data.get("Vendedor", ""),
                    event_data.get("Complain_Qty", ""),
                    event_data.get("Tiempo_de_parada", ""),
                    event_data.get("Consecuencia", ""),
                    event_data.get("id_origen", "")
                ))
                conn.commit()
                print("[Insert] Event successfully saved to database.")

        def debug_show_all(self) -> None:
            """
            Prints all entries from the events table.
            """
            print("[Debug] Current records in the database:")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {self.table_name}")
                rows = cursor.fetchall()
                for row in rows:
                    print("  ", row)

    class Scenarios:
        """
        Handles logic depending on the type of consequence.
        """

        def handle(self, event_data: Dict) -> None:
            consequence = event_data.get("Consecuencia", "").strip().lower()

            if consequence == "se rechazo la materia prima?":
                self._handle_raw_material_rejection(event_data)
            elif consequence == "se rechazo la masa?":
                self._handle_dough_rejection(event_data)
            elif consequence == "se rechazo el packaging?":
                self._handle_packaging_rejection(event_data)
            elif consequence in {"", "none"}:
                print("[Scenarios] No consequence to evaluate.")
            else:
                print(f"[Scenarios] Unknown consequence: {consequence}")

        def _handle_raw_material_rejection(self, data: Dict) -> None:
            print("[Scenarios] Handling raw material rejection...")
            # Add logic here

        def _handle_dough_rejection(self, data: Dict) -> None:
            print("[Scenarios] Handling dough rejection...")
            # Add logic here

        def _handle_packaging_rejection(self, data: Dict) -> None:
            print("[Scenarios] Handling packaging rejection...")
            # Add logic here
