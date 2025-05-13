import time
import threading
import os
from typing import Dict, List
import pandas as pd

from linea.data_ingestion.data_ingestion_service import DataIngestionService

class EventDetectionService:
    """
    Service for processing and validating events triggered by data ingestion,
    particularly from Excel files.
    """
    REQUIRED_COLUMNS = [
        "Planta",
        "Periodo",
        "Fecha de inicio",
        "Material",
        "Descripcion del material",
        "Batch",
        "Vendedor",
        "Complain Qty",
        "Tiempo de parada",
        "Se rechazo la materia prima?",
        "Se rechazo la masa?",
        "Se rechazo el packaging?"
    ]

    def __init__(self) -> None:
        """
        Initializes the EventDetectionService.
        """
        self.logged_events: List[Dict] = []
        self.previous_hashes: set = set()
        self.running = False
        self.excel_path = os.path.join(os.getcwd(), "data", "input.xlsx")
        self.data_ingestion_service = DataIngestionService()

    def _fetch_new_data(self) -> List[Dict]:
        """
        Reads the Excel file and returns the data as a list of dictionaries.
        Converts all fields to strings and strips whitespace.
        """
        try:
            df = pd.read_excel(self.excel_path)
            df = df.astype(str).apply(lambda col: col.str.strip() if col.dtype == 'object' else col)
            return df.to_dict(orient="records")
        except Exception as e:
            print(f"\033[91m[EventDetection] Failed to read Excel file: {e}\033[0m")
            return []

    def _row_hash(self, row: Dict) -> str:
        """
        Returns a hashable string that uniquely represents a row based on required columns.
        """
        return "|".join(str(row.get(col, "")).strip() for col in self.REQUIRED_COLUMNS)

    def _is_missing(self, value: str) -> bool:
        """
        Checks if a value is considered missing or invalid.
        """
        return not value or str(value).strip().lower() in {"", "nan", "none", "null"}

    def _detect_new_entries(self, current_data: List[Dict]) -> None:
        """
        Detect new entries with complete data that weren't previously seen.
        """
        for row in current_data:
            row_id = self._row_hash(row)

            if row_id in self.previous_hashes:
                continue

            missing = [col for col in self.REQUIRED_COLUMNS if self._is_missing(row.get(col, ""))]

            if not missing:
                print("\n\033[92m[EventDetection] New entry detected!\033[0m")
                for k, v in row.items():
                    print(f"{k}: {v}")
                self.logged_events.append(row)

                try:
                    self.data_ingestion_service.ingest_event(row)
                    print("[EventDetection] Data sent to DataIngestionService.")
                except Exception as e:
                    print(f"\033[91m[EventDetection] Failed to send data to DataIngestionService: {e}\033[0m")
            else:
                print(f"\033[93m[EventDetection] Incomplete row ignored (missing {len(missing)}): {missing}\033[0m")
                print("  Columns:", " | ".join(self.REQUIRED_COLUMNS))
                print("  Values: ", " | ".join(str(row.get(col, "")).strip() for col in self.REQUIRED_COLUMNS))

            self.previous_hashes.add(row_id)

    def start_monitoring(self) -> None:
        """
        Start background thread to monitor Excel file for new complete entries.
        """
        self.running = True

        def monitor_loop():
            print("[EventDetection] Monitoring started...")
            while self.running:
                current_data = self._fetch_new_data()
                self._detect_new_entries(current_data)
                time.sleep(2)

        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()

    def stop_monitoring(self) -> None:
        self.running = False
        print("[EventDetection] Monitoring stopped.")
