import cv2
import numpy as np
import torch
from ultralytics import YOLO
import os
from pathlib import Path

class StampRemover:
    def __init__(self, model_path, device=None):
        """
        Inicializa el detector de sellos con el modelo YOLOv8 entrenado.
        """
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
            
        print(f"Cargando modelo YOLOv8 desde {model_path} en {self.device}...")
        self.model = YOLO(model_path)
        
    def detect_stamps(self, image, conf=0.4):
        """
        Detecta sellos en una imagen y devuelve las cajas (bboxes).
        """
        results = self.model.predict(image, conf=conf, device=self.device, verbose=False)
        boxes = results[0].boxes.xyxy.cpu().numpy()
        return boxes

    def create_mask(self, image, boxes, padding=10):
        """
        Crea una máscara binaria para los sellos detectados.
        """
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            # Añadir un pequeño padding para asegurar que cubrimos los bordes del sello
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(image.shape[1], x2 + padding)
            y2 = min(image.shape[0], y2 + padding)
            
            # Dibujar un rectángulo blanco en la máscara
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
            
        return mask

    def remove_and_inpaint(self, image, mask, method='telea'):
        """
        Aplica inpainting para remover el contenido de la máscara.
        Métodos: 'telea' (rápido), 'ns' (Navier-Stokes)
        """
        if method.lower() == 'telea':
            flags = cv2.INPAINT_TELEA
        else:
            flags = cv2.INPAINT_NS
            
        # El radio debe ser pequeño para no emborronar demasiado el texto cercano
        radius = 3
        inpainted = cv2.inpaint(image, mask, radius, flags)
        return inpainted

    def process_document(self, image_path, output_path=None):
        """
        Pipeline completo: Cargar -> Detectar -> Máscara -> Inpaint -> Guardar
        """
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"No se pudo cargar la imagen en {image_path}")
            
        boxes = self.detect_stamps(img)
        
        if len(boxes) == 0:
            print(f"No se detectaron sellos en {image_path}")
            return img, False
            
        print(f"Detectados {len(boxes)} sellos. Aplicando restauración...")
        mask = self.create_mask(img, boxes)
        result = self.remove_and_inpaint(img, mask)
        
        if output_path:
            cv2.imwrite(str(output_path), result)
            
        return result, True

if __name__ == "__main__":
    # Ejemplo de uso
    BASE_DIR = Path("c:/Users/manue/Documents/Desktop_Archive_2026-03-14/Folders/PR_COMPUTER_VISION/idp-project")
    MODEL_PATH = BASE_DIR / "models/yolo_stamps/best.pt"
    TEST_IMAGE = BASE_DIR / "datos/synthetic_dataset/images/syn_0001.png" # Imagen sintética con sello garantizado
    OUTPUT_FOLDER = BASE_DIR / "datos/restored_docs"
    
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    
    if not MODEL_PATH.exists():
        print(f"ERROR: No se encuentra el modelo en {MODEL_PATH}")
    else:
        remover = StampRemover(MODEL_PATH)
        # Probaremos con una imagen del dataset de stamps_synthetic para ver resultados inmediatos
        # O mejor una de test si ya tenemos.
        result, success = remover.process_document(TEST_IMAGE, OUTPUT_FOLDER / "test_restoration.png")
        if success:
            print(f"Proceso finalizado. Imagen guardada en {OUTPUT_FOLDER / 'test_restoration.png'}")
