import os
import shutil
import random
from pathlib import Path

def prepare_yolo_structure():
    """
    Organiza el dataset sintético en la estructura requerida por YOLOv8
    dividiendo equitativamente en Entrenamiento (80%) y Validación (20%).
    """
    BASE_DIR = Path(r"c:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project")
    SYN_DIR = BASE_DIR / "datos" / "synthetic_dataset"
    
    # Directorio de salida final para YOLO
    YOLO_DATASET_DIR = BASE_DIR / "datos" / "yolo_dataset"
    
    # Crear estructura de carpetas YOLO
    splits = ["train", "val"]
    types = ["images", "labels"]
    
    for s in splits:
        for t in types:
            (YOLO_DATASET_DIR / t / s).mkdir(parents=True, exist_ok=True)
    
    # Obtener todas las imágenes generadas
    all_images = list((SYN_DIR / "images").glob("*.png"))
    random.shuffle(all_images)
    
    # Dividir 80-20
    split_idx = int(len(all_images) * 0.8)
    train_files = all_images[:split_idx]
    val_files = all_images[split_idx:]
    
    def move_files(file_list, split_name):
        for img_path in file_list:
            file_id = img_path.stem
            label_path = SYN_DIR / "labels" / f"{file_id}.txt"
            
            if label_path.exists():
                # Copiar imagen
                shutil.copy(str(img_path), str(YOLO_DATASET_DIR / "images" / split_name / f"{file_id}.png"))
                # Copiar label
                shutil.copy(str(label_path), str(YOLO_DATASET_DIR / "labels" / split_name / f"{file_id}.txt"))
    
    print(f"[*] Organizando dataset para YOLOv8...")
    move_files(train_files, "train")
    move_files(val_files, "val")
    
    # Crear archivo dataset.yaml
    yaml_content = f"""path: {str(YOLO_DATASET_DIR.resolve())}
train: images/train
val: images/val
test:  # opcional

names:
  0: stamp
"""
    
    with open(YOLO_DATASET_DIR / "dataset.yaml", "w") as f:
        f.write(yaml_content)
        
    print(f"\n[✓] Organización completada:")
    print(f"    - Train: {len(train_files)} imágenes")
    print(f"    - Val:   {len(val_files)} imágenes")
    print(f"    - Configuración: {YOLO_DATASET_DIR / 'dataset.yaml'}")

if __name__ == "__main__":
    prepare_yolo_structure()
