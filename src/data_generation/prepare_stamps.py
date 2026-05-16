import cv2
import numpy as np
from pathlib import Path
import json
from tqdm import tqdm

def inspect_stamps(stamps_dir: str):
    """
    Inspecciona la carpeta de sellos y clasifica su contenido según el fondo y canales.
    """
    stamps_dir = Path(stamps_dir)
    report = {
        "transparent": [], 
        "white_bg": [], 
        "color_bg": [], 
        "problematic": []
    }

    print(f"[*] Inspeccionando sellos en: {stamps_dir}")
    all_files = list(stamps_dir.glob("*.*"))
    
    for path in tqdm(all_files, desc="Inspeccionando"):
        img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if img is None:
            report["problematic"].append(path.name)
            continue

        channels = img.shape[2] if len(img.shape) == 3 else 1

        if channels == 4:
            # Si el canal alpha tiene algún pixel transparente (< 255)
            if img[:,:,3].min() < 250:
                report["transparent"].append(path.name)
            else:
                report["white_bg"].append(path.name)
        elif channels == 3:
            # Analizar esquinas para ver si el fondo es predominantemente blanco
            corners = np.array([img[0,0], img[0,-1], img[-1,0], img[-1,-1]])
            if corners.mean(axis=0).min() > 220:
                report["white_bg"].append(path.name)
            else:
                report["color_bg"].append(path.name)
        else:
            report["problematic"].append(path.name)

    return report

def prepare_stamp(stamp_path: str) -> np.ndarray:
    """
    Toma un sello con fondo (usualmente blanco o grisáceo) y devuelve una versión
    BGRA con el fondo removido mediante una combinación de umbral de luminancia
    y análisis de saturación de color para fondos azulados/grisáceos.
    """
    img = cv2.imread(str(stamp_path), cv2.IMREAD_UNCHANGED)
    if img is None:
        return None

    # Caso 1: Ya tiene canal Alpha
    if len(img.shape) == 3 and img.shape[2] == 4:
        return img

    # Convertir a BGR si es escala de grises para poder analizar saturación
    if len(img.shape) == 2:
        bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    else:
        bgr = img[:,:,:3]

    # --- SOLUCIÓN 1: Umbral de Luminancia más agresivo (210 en lugar de 240) ---
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    _, mask_lum = cv2.threshold(gray, 215, 255, cv2.THRESH_BINARY_INV)

    # --- SOLUCIÓN 2: Máscara por Crominancia (Saturación) ---
    # Los fondos grisáceos/azulados suelen tener muy baja saturación comparado con el sello.
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    saturation = hsv[:,:,1]
    # Si la saturación es > 30, probablemente es tinta del sello, no fondo.
    _, mask_sat = cv2.threshold(saturation, 35, 255, cv2.THRESH_BINARY)

    # Combinamos ambas: un pixel se queda si es oscuro (mask_lum) O si tiene color real (mask_sat)
    alpha = cv2.bitwise_or(mask_lum, mask_sat)
    
    # Limpieza final: Eliminar pequeños ruidos (puntos sueltos en el fondo)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Suavizar bordes para evitar aliasing
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0)

    # Combinar BGR + Alpha
    bgra = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    bgra[:,:,3] = alpha
    
    return bgra

def main():
    # Rutas basadas en la estructura del workspace
    BASE_DIR = Path(r"c:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project")
    INPUT_DIR = BASE_DIR / "datos" / "stamps_synthetic" / "images" / "Stapms Dataset"
    OUTPUT_DIR = BASE_DIR / "datos" / "stamps_clean"
    REPORT_PATH = BASE_DIR / "datos" / "prep_stamps_report.json"

    if not INPUT_DIR.exists():
        print(f"[!] Error: No se encontró la carpeta de entrada {INPUT_DIR}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Inspeccionar
    report = inspect_stamps(str(INPUT_DIR))
    
    # 2. Procesar
    processed_count = 0
    errors = []

    print(f"[*] Limpiando fondos y generando imágenes con Alpha...")
    # Solo procesamos los que tienen fondo blanco o color (los transparentes ya están bien)
    to_process = report["white_bg"] + report["color_bg"] + report["transparent"]
    
    for filename in tqdm(to_process, desc="Procesando sellos"):
        output_path = OUTPUT_DIR / f"{Path(filename).stem}.png"
        
        # Saltamos si ya existe (opcional)
        # if output_path.exists(): continue

        clean_img = prepare_stamp(INPUT_DIR / filename)
        if clean_img is not None:
            cv2.imwrite(str(output_path), clean_img)
            processed_count += 1
        else:
            errors.append(filename)

    # 3. Finalizar reporte
    final_report = {
        "inspection": {
            "total_files": len(report["transparent"]) + len(report["white_bg"]) + len(report["color_bg"]) + len(report["problematic"]),
            "categories": {k: len(v) for k, v in report.items()}
        },
        "processing": {
            "processed_successfully": processed_count,
            "errors": len(errors),
            "errors_list": errors,
            "output_directory": str(OUTPUT_DIR)
        }
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=4, ensure_ascii=False)

    print("\n" + "="*40)
    print("✓ PROCESO COMPLETADO")
    print(f"- Total encontrados: {final_report['inspection']['total_files']}")
    print(f"- Con fondo blanco: {final_report['inspection']['categories']['white_bg']}")
    print(f"- Procesados con éxito: {processed_count}")
    print(f"- Reporte guardado en: {REPORT_PATH.name}")
    print("="*40)

if __name__ == "__main__":
    main()
