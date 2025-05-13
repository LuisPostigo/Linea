import os
import sys
import platform
import subprocess
import argparse

from linea.data_ingestion.data_ingestion_service import DataIngestionService
from linea.event_detection.event_detection_service import EventDetectionService

"""
Two modes:
- Runs manually: python auto_monitor.py --mode manual
- Runs on the background: python auto_monitor.py --mode auto
    or python auto_monitor.py
"""

def start_excel_monitoring():
    event_service = EventDetectionService()
    excel_path = os.path.join(os.getcwd(), "data", "input.xlsx")
    print(f"[INFO] Monitoring Excel at: {excel_path}")
    data_ingestor = DataIngestionService(event_service, excel_path)
    data_ingestor.start_monitoring_excel()


def relaunch_as_background():
    if platform.system() == "Windows":
        subprocess.Popen(["python", __file__, "--mode", "manual"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    elif platform.system() == "Darwin":
        subprocess.Popen(["nohup", "python3", __file__, "--mode", "manual"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif platform.system() == "Linux":
        subprocess.Popen(["nohup", "python3", __file__, "--mode", "manual"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print("Unsupported platform for background execution.")
    print("[INFO] Relaunched monitoring as background process.")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Linea Excel Monitor")
    parser.add_argument('--mode', choices=['auto', 'manual'], default='auto', help='Run mode: auto (default) or manual')

    args = parser.parse_args()

    if args.mode == "manual":
        print("[INFO] Running in manual mode.")
        start_excel_monitoring()
    elif args.mode == "auto":
        print(f"[INFO] Detected platform: {platform.system()} — launching in background...")
        relaunch_as_background()


if __name__ == "__main__":
    main()
