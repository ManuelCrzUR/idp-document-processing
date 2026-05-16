import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json

def analyze_failed_cleaning(stamps_clean_dir: str):
    """
    Analiza la carpeta de sellos 'limpios' para detectar cuáles 
    todavía tienen mucho blanco (falló la transparencia).
    """
    clean_dir = Path(stamps_clean_dir)
    report = {
        "still_oapque_white": [],  # Archivos que parecen seguir teniendo fondo blanco
        "mostly_empty": [],        # Archivos donde se borró casi todo
        "stats": []
    }
    
    files = list(clean_dir.glob("*.png"))
    print(f"[*] Auditando {len(files)} sellos procesados...")

    for path in tqdm(files):
        img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if img is None or img.shape[2] < 4:
            continue
            
        alpha = img[:,:,3]
        
        # 1. ¿Cuánta transparencia hay realmente?
        total_pixels = alpha.size
        opaque_pixels = np.sum(alpha > 200)
        transparent_pixels = np.sum(alpha < 50)
        
        opaque_ratio = opaque_pixels / total_pixels
        
        # Si más del 90% es opaco pero el canal alpha existe, algo falló en el threshold
        if opaque_ratio > 0.90:
            # Tomar una muestra del color opaco para ver si es 'blanco'
            # (Si es blanco y opaco, el threshold falló)
            mask = alpha > 200
            avg_color = img[mask][:, :3].mean(axis=0) if np.any(mask) else [0,0,0]
            
            if np.mean(avg_color) > 200: # Es blanco y opaco
                report["still_oapque_white"].append({
                    "file": path.name,
                    "opaque_ratio": round(opaque_ratio, 3),
                    "avg_color": [round(float(c), 1) for c in avg_color]
                })

    return report

if __name__ == "__main__":
    BASE_DIR = Path(r"c:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project")
    CLEAN_DIR = BASE_DIR / "datos" / "stamps_clean"
    
    audit_results = analyze_failed_cleaning(str(CLEAN_DIR))
    
    print(f"\n[!] Hallazgos de la auditoría:")
    print(f"- Sellos que aún tienen fondo blanco opaco: {len(audit_results['still_oapque_white'])}")
    
    if audit_results['still_oapque_white']:
        print("\nEjemplos de fallos (primeros 5):")
        for fail in audit_results['still_oapque_white'][:5]:
            print(f"  > {fail['file']}: Ratio Opaco {fail['opaque_ratio']}, Color Promedio {fail['avg_color']}")
    
    # Guardar para análisis
    with open(BASE_DIR / "datos" / "audit_cleaning.json", "w") as f:
        json.dump(audit_results, f, indent=4)
