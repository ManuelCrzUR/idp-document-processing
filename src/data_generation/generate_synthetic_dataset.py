import cv2
import numpy as np
import random
from pathlib import Path
from tqdm import tqdm
import json

def compose_stamp_on_document(doc_img, stamp_bgra, 
                               scale_range=(0.10, 0.35), 
                               opacity_range=(0.45, 0.90), 
                               rotation_range=(-45, 45)):
    """
    Superpone un sello (BGRA) sobre un documento al azar con variabilidades reales.
    """
    doc_h, doc_w = doc_img.shape[:2]
    
    # 1. Redimensionar sello proporcional al documento
    scale = random.uniform(*scale_range)
    target_w = int(doc_w * scale)
    # Mantener relación de aspecto del sello
    aspect_ratio = stamp_bgra.shape[0] / stamp_bgra.shape[1]
    target_h = int(target_w * aspect_ratio)

    stamp_resized = cv2.resize(stamp_bgra, (target_w, target_h), interpolation=cv2.INTER_AREA)

    # 2. Rotación aleatoria
    angle = random.uniform(*rotation_range)
    center = (target_w // 2, target_h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    # Calcular tamaño de caja contenedora para no cortar esquinas tras rotar
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    n_w = int((target_h * sin) + (target_w * cos))
    n_h = int((target_h * cos) + (target_w * sin))
    M[0, 2] += (n_w / 2) - center[0]
    M[1, 2] += (n_h / 2) - center[1]
    
    stamp_rot = cv2.warpAffine(stamp_resized, M, (n_w, n_h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
    
    # 3. Ubicación aleatoria (evitando bordes extremos)
    margin = 0.1
    x = random.randint(int(doc_w * margin), doc_w - n_w - int(doc_w * margin))
    y = random.randint(int(doc_h * margin), doc_h - n_h - int(doc_h * margin))
    
    # 4. Mezcla con opacidad (Alpha Blending)
    opacity = random.uniform(*opacity_range)
    dirty = doc_img.copy().astype(np.float32)
    roi = dirty[y:y+n_h, x:x+n_w]
    
    # Normalizar alpha del sello e integrarlo con la opacidad aleatoria
    s_alpha = (stamp_rot[:,:,3].astype(np.float32) / 255.0) * opacity
    s_bgr = stamp_rot[:,:,:3].astype(np.float32)
    
    for c in range(3):
        roi[:,:,c] = s_bgr[:,:,c] * s_alpha + roi[:,:,c] * (1 - s_alpha)
        
    dirty[y:y+n_h, x:x+n_w] = roi
    
    # 5. Generar Máscara Binaria (Ground Truth para Inpainting)
    mask = np.zeros((doc_h, doc_w), dtype=np.uint8)
    # Umbral de 0.1 para capturar incluso trazos finos del sello en la máscara
    mask[y:y+n_h, x:x+n_w] = (s_alpha > 0.1).astype(np.uint8) * 255
    
    # 6. Calcular Bounding Box para YOLO (x_center, y_center, width, height) normalizados
    x_center = (x + n_w / 2) / doc_w
    y_center = (y + n_h / 2) / doc_h
    w_norm = n_w / doc_w
    h_norm = n_h / doc_h
    
    yolo_label = f"0 {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}"
    
    return dirty.astype(np.uint8), mask, yolo_label

def get_clean_stamps_list(stamps_dir: Path, audit_report_path: Path):
    """
    Filtra los sellos que pasaron la auditoría (sin fondo blanco opaco).
    """
    total_stamps = list(stamps_dir.glob("*.png"))
    
    if not audit_report_path.exists():
        print("[!] No se encontró reporte de auditoría. Usando todos los sellos.")
        return total_stamps
        
    with open(audit_report_path, "r") as f:
        audit_data = json.load(f)
        
    failed_files = [item["file"] for item in audit_data.get("still_oapque_white", [])]
    clean_stamps = [p for p in total_stamps if p.name not in failed_files]
    
    print(f"[*] Auditoría aplicada:")
    print(f"    - Sellos totales: {len(total_stamps)}")
    print(f"    - Sellos excluidos (fondo opaco): {len(failed_files)}")
    print(f"    - Sellos APTOS: {len(clean_stamps)}")
    
    return clean_stamps

def main():
    # Rutas del workspace
    BASE_DIR = Path(r"c:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project")
    DOCS_DIR = BASE_DIR / "datos" / "spanishocr" / "images"
    STAMPS_DIR = BASE_DIR / "datos" / "stamps_clean"
    AUDIT_REPORT = BASE_DIR / "datos" / "audit_cleaning.json"
    
    OUTPUT_DIR = BASE_DIR / "datos" / "synthetic_dataset"
    
    # Limpiar carpeta anterior para evitar mezclas con datos malos
    import shutil
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
        
    (OUTPUT_DIR / "images").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "labels").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "masks").mkdir(parents=True, exist_ok=True)

    doc_paths = list(DOCS_DIR.glob("*.png"))
    # APLICAR EXCLUSIÓN DE SELLOS MALOS
    stamp_paths = get_clean_stamps_list(STAMPS_DIR, AUDIT_REPORT)

    if not doc_paths or not stamp_paths:
        print("[!] Error fatal: No hay documentos o sellos aptos.")
        return

    num_samples = 200
    print(f"[*] Iniciando generación de {num_samples} tripletes sintéticos...")

    for i in tqdm(range(num_samples)):
        doc_path = random.choice(doc_paths)
        stamp_path = random.choice(stamp_paths)
        
        doc_img = cv2.imread(str(doc_path))
        stamp_bgra = cv2.imread(str(stamp_path), cv2.IMREAD_UNCHANGED)
        
        if doc_img is None or stamp_bgra is None:
            continue
            
        dirty, mask, yolo_label = compose_stamp_on_document(doc_img, stamp_bgra)
        
        # Guardar resultados
        file_id = f"syn_{i:04d}"
        cv2.imwrite(str(OUTPUT_DIR / "images" / f"{file_id}.png"), dirty)
        cv2.imwrite(str(OUTPUT_DIR / "masks" / f"{file_id}_mask.png"), mask)
        
        with open(OUTPUT_DIR / "labels" / f"{file_id}.txt", "w") as f:
            f.write(yolo_label)

    print(f"\n[✓] ¡Éxito! Dataset listo en {OUTPUT_DIR}")
    print(f"- Imágenes con sellos: {len(list((OUTPUT_DIR/'images').glob('*.png')))}")
    print(f"- Etiquetas YOLO: {len(list((OUTPUT_DIR/'labels').glob('*.txt')))}")
    print(f"- Máscaras de inpainting: {len(list((OUTPUT_DIR/'masks').glob('*.png')))}")

if __name__ == "__main__":
    main()
