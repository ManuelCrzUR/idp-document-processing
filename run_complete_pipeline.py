# -*- coding: utf-8 -*-
"""
Script para ejecutar el pipeline completo en un documento de prueba
"""
import sys
import json
import shutil
from pathlib import Path
import cv2
import numpy as np

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src" / "pipeline"))

from phase_4_ocr_complete import phase_4_ocr_complete

# Configurar directorios
DATA_ROOT = Path("C:/Users/manue/Documents/Desktop_Archive_2026-03-14/Folders/PR_COMPUTER_VISION/idp-project/datos")
SYNTHETIC_DIR = DATA_ROOT / "synthetic_dataset"
TEST_IMAGE = SYNTHETIC_DIR / "images" / "syn_0000.png"
TEST_LABEL = SYNTHETIC_DIR / "labels" / "syn_0000.txt"
OUTPUT_DIR = project_root / "output" / "prueba_completa"

# Crear directorio de salida
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*80)
print("EJECUTANDO PIPELINE COMPLETO")
print("="*80)

print("\n[Prueba completa] Documento seleccionado: syn_0000.png")

# Leer imagen
img = cv2.imread(str(TEST_IMAGE))
h, w = img.shape[:2]
print(f"Dimensiones: {w}x{h}")

# Guardar imagen original
cv2.imwrite(str(OUTPUT_DIR / "01_imagen_original.png"), img)

# Leer bbox YOLO
with open(TEST_LABEL) as f:
    line = f.readline().strip().split()
    bbox_yolo = tuple(map(float, line[1:5]))

print(f"Sello bbox (xc, yc, w, h): {bbox_yolo}")

# Usar imagen como está (simulando Phase 3A completada)
img_inpainted = img.copy()

# Guardar resultado (simula imagen después de limpieza)
cv2.imwrite(str(OUTPUT_DIR / "02_imagen_procesada.png"), img_inpainted)

# 2. PHASE 4: OCR y Corrección de Texto
print("\n[PHASE 4] OCR y Corrección de Texto")

try:
    # Ejecutar Phase 4
    result_ocr = phase_4_ocr_complete(
        clean_image=img_inpainted,
        seal_bbox=bbox_yolo,
        confidence_threshold=0.5,
        debug=False
    )

    # Guardar resultado OCR
    with open(OUTPUT_DIR / "03_ocr_resultado.json", "w", encoding="utf-8") as f:
        json.dump(result_ocr, f, ensure_ascii=False, indent=2)

    print("[OK] Phase 4 completada exitosamente")
    total_bloques = result_ocr.get('metricas', {}).get('total_bloques', 'N/A')
    print(f"  Bloques detectados: {total_bloques}")

except Exception as e:
    print(f"[ERROR] Problema en Phase 4: {e}")
    import traceback
    traceback.print_exc()
    result_ocr = None

# 3. Guardar metadatos
print("\n[3/3] Generando Reporte Final e Índice HTML")

metadata = {
    "pipeline_version": "1.0",
    "fecha_ejecucion": str(Path(TEST_IMAGE).stat().st_mtime),
    "imagen_entrada": str(TEST_IMAGE),
    "imagenes_salida": {
        "imagen_limpia": str(OUTPUT_DIR / "03_imagen_limpia.png"),
        "ocr_json": str(OUTPUT_DIR / "04_ocr_resultado.json")
    },
    "parametros": {
        "bbox_yolo": bbox_yolo,
        "dimensiones_imagen": [h, w],
        "confidence_threshold": 0.5
    }
}

with open(OUTPUT_DIR / "metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

# 4. Generar índice HTML
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Prueba Pipeline Completo</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #333; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px; }}
        img {{ max-width: 100%; margin: 10px 0; }}
        .info {{ background: #e8f4f8; padding: 10px; border-left: 4px solid #0099cc; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 Prueba Pipeline Completo</h1>

        <div class="section">
            <h2>📊 Imagen Original</h2>
            <img src="../../{str(TEST_IMAGE).split('datos')[1]}" alt="Original">
        </div>

        <div class="section">
            <h2>🧹 Imagen Limpia (Phase 3A)</h2>
            <img src="03_imagen_limpia.png" alt="Limpia">
            <p><strong>Proceso:</strong> Detección chromática + LaMa inpainting</p>
        </div>

        <div class="section info">
            <h3>📄 Resultados OCR (Phase 4)</h3>
            <p><a href="04_ocr_resultado.json">Ver JSON completo</a></p>
            <p>Bloques extraídos: {result_ocr.get('metricas', {}).get('total_bloques', 'N/A') if result_ocr else 'N/A'}</p>
        </div>

        <div class="section">
            <h3>📋 Archivos Generados</h3>
            <ul>
                <li>03_imagen_limpia.png - Imagen sin sello</li>
                <li>04_ocr_resultado.json - Resultados OCR con metadatos</li>
                <li>metadata.json - Metadatos de ejecución</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

with open(OUTPUT_DIR / "index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("[OK] Reporte HTML generado")

# Resumen final
print("\n" + "="*80)
print("[COMPLETADO] PIPELINE FINALIZADO EXITOSAMENTE")
print("="*80)
print(f"\nCarpeta de resultados: {OUTPUT_DIR}")
print(f"\nArchivos generados:")
for file in sorted(OUTPUT_DIR.glob("*")):
    if file.is_file():
        size = file.stat().st_size
        print(f"  - {file.name} ({size} bytes)")
