import os
os.environ["YOLO_OFFLINE"] = "true"
from ultralytics import YOLO
import torch
import time
from pathlib import Path

def test_train():
    device = "0" if torch.cuda.is_available() else "cpu"
    print(f"[*] Dispositivo: {device}")
    model = YOLO("yolov8n.pt")
    BASE_DIR = Path(r"c:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project")
    DATA_YAML = BASE_DIR / "datos" / "yolo_dataset" / "dataset.yaml"
    print("INICIANDO PRUEBA...")
    start = time.time()
    try:
        model.train(
            data=str(DATA_YAML), 
            epochs=5, 
            imgsz=640, 
            batch=4, 
            device=device, 
            workers=0, 
            project=str(BASE_DIR / "runs"), 
            name="test", 
            exist_ok=True, 
            verbose=False
        )
        dur = time.time() - start
        print(f"TIEMPO: {dur:.2f}s (Avg: {dur/5:.2f}s/epoch)")
        if device == "0" or (dur/5) < 40:
            print(">>> RECOMENDACIÓN: LOCAL")
        else:
            print(">>> RECOMENDACIÓN: COLAB")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_train()
