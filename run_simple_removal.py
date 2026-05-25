# -*- coding: utf-8 -*-
"""
Enfoque simplificado y directo para eliminacion del sello.
Pipeline de 5 pasos sin dependencias complejas (sin LaMa).
"""
import sys
import cv2
import numpy as np
import json
from pathlib import Path
from typing import Tuple

# Configurar stdout para UTF-8 en Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================================
# CONFIGURACION
# ============================================================================

ORIGINAL_IMAGE_PATH = "output/prueba_completa/01_imagen_original.png"
OUTPUT_DIR = Path("output/prueba_completa")

# Bounding box del sello (aproximado de analisis previos)
# Y: fila de imagen, X: columna de imagen
SEAL_ROI = {
    'y_min': 1600,
    'y_max': 2300,
    'x_min': 800,
    'x_max': 1700
}

print("=" * 80)
print("ELIMINACION SIMPLIFICADA DEL SELLO - PIPELINE DE 5 PASOS")
print("=" * 80)

# ============================================================================
# PASO 1: Cargar imagen y extraer ROI del sello
# ============================================================================
print("\n[PASO 1] Extraer region del sello")
print("-" * 80)

original = cv2.imread(ORIGINAL_IMAGE_PATH)
if original is None:
    print(f"[ERROR] No se pudo cargar: {ORIGINAL_IMAGE_PATH}")
    exit(1)

h, w = original.shape[:2]
print(f"Imagen original: {w}x{h} pixeles")

# Extraer ROI
y_min, y_max = SEAL_ROI['y_min'], SEAL_ROI['y_max']
x_min, x_max = SEAL_ROI['x_min'], SEAL_ROI['x_max']
roi_original = original[y_min:y_max, x_min:x_max].copy()

roi_h, roi_w = roi_original.shape[:2]
print(f"ROI del sello: {roi_w}x{roi_h} pixeles")
print(f"  Coordenadas: Y[{y_min}:{y_max}], X[{x_min}:{x_max}]")

# Guardar ROI original
roi_original_path = OUTPUT_DIR / "evidencia_01_roi_original.png"
cv2.imwrite(str(roi_original_path), roi_original)
print(f"[OK] Guardado: {roi_original_path}")

# ============================================================================
# PASO 2: Clasificar pixeles dentro del ROI
# ============================================================================
print("\n[PASO 2] Clasificar pixeles dentro del ROI")
print("-" * 80)

# Crear mapas de clasificacion
roi_bgr = roi_original.astype(np.float32)
mean_rgb = np.mean(roi_bgr, axis=2)
max_rgb = np.max(roi_bgr, axis=2)
min_rgb = np.min(roi_bgr, axis=2)
dominance = max_rgb - min_rgb

# Clasificacion segun reglas
# 0 = TEXTO (negro)
# 1 = FONDO (blanco)
# 2 = SELLO (todo lo demas)
pixel_class = np.zeros((roi_h, roi_w), dtype=np.uint8)

# Si mean(R,G,B) < 80 AND max-min < 15 -> TEXTO NEGRO
mask_texto = (mean_rgb < 80) & (dominance < 15)
pixel_class[mask_texto] = 0

# Si max(R,G,B) > 240 -> FONDO BLANCO
mask_fondo = max_rgb > 240
pixel_class[mask_fondo] = 1

# Todo lo demas -> SELLO
mask_sello = ~mask_texto & ~mask_fondo
pixel_class[mask_sello] = 2

# Estadisticas
num_texto = np.sum(pixel_class == 0)
num_fondo = np.sum(pixel_class == 1)
num_sello = np.sum(pixel_class == 2)
total = roi_h * roi_w

print(f"Clasificacion de pixeles:")
print(f"  TEXTO NEGRO:   {num_texto:7,d} pixeles ({100*num_texto/total:5.2f}%)")
print(f"  FONDO BLANCO:  {num_fondo:7,d} pixeles ({100*num_fondo/total:5.2f}%)")
print(f"  SELLO:         {num_sello:7,d} pixeles ({100*num_sello/total:5.2f}%)")
print(f"  TOTAL:         {total:7,d} pixeles")

# Crear visualizacion de clasificacion (para debugging)
# Negro=TEXTO, Rojo=SELLO, Blanco=FONDO
clasificacion_viz = np.zeros_like(roi_bgr, dtype=np.uint8)
clasificacion_viz[pixel_class == 0] = [0, 0, 0]      # Negro
clasificacion_viz[pixel_class == 1] = [255, 255, 255]  # Blanco
clasificacion_viz[pixel_class == 2] = [0, 0, 255]    # Rojo (BGR)

clasificacion_path = OUTPUT_DIR / "evidencia_02_clasificacion_pixeles.png"
cv2.imwrite(str(clasificacion_path), clasificacion_viz)
print(f"[OK] Guardado: {clasificacion_path}")

# Crear mascara binaria del sello
sello_mask = (pixel_class == 2).astype(np.uint8) * 255
sello_mask_path = OUTPUT_DIR / "evidencia_03_mascara_sello.png"
cv2.imwrite(str(sello_mask_path), sello_mask)
print(f"[OK] Guardado: {sello_mask_path}")

# Crear mapa de texto detectado
texto_map = np.zeros_like(roi_bgr, dtype=np.uint8)
texto_map[pixel_class == 0] = [0, 255, 0]  # Verde para texto
texto_deteccion_path = OUTPUT_DIR / "evidencia_04_deteccion_texto.png"
cv2.imwrite(str(texto_deteccion_path), texto_map)
print(f"[OK] Guardado: {texto_deteccion_path}")

# ============================================================================
# PASO 3: Aplicar filtro de barrido horizontal por fila
# ============================================================================
print("\n[PASO 3] Aplicar filtro horizontal por fila")
print("-" * 80)

roi_limpio = roi_original.copy().astype(np.float32)
roi_limpio_uint8 = roi_original.copy()

filas_sin_texto = 0
pixeles_limpios = 0

for y in range(roi_h):
    # Contar pixeles de TEXTO en esta fila
    num_texto_en_fila = np.sum(pixel_class[y, :] == 0)

    if num_texto_en_fila == 0:
        # Esta fila NO tiene texto -> limpiar todos los pixeles de SELLO a blanco
        mask_sello_en_fila = pixel_class[y, :] == 2
        roi_limpio_uint8[y, mask_sello_en_fila] = [255, 255, 255]
        pixeles_limpios += np.sum(mask_sello_en_fila)
        filas_sin_texto += 1

print(f"Filtro horizontal aplicado:")
print(f"  Filas sin texto:    {filas_sin_texto} (de {roi_h})")
print(f"  Pixeles limpios:    {pixeles_limpios:,}")

# Visualizar ROI despues del filtro horizontal
filtro_h_path = OUTPUT_DIR / "evidencia_05_filtro_horizontal.png"
cv2.imwrite(str(filtro_h_path), roi_limpio_uint8)
print(f"[OK] Guardado: {filtro_h_path}")

# ============================================================================
# PASO 4: Guardar ROI limpio final
# ============================================================================
print("\n[PASO 4] ROI limpio final")
print("-" * 80)

roi_final = roi_limpio_uint8.astype(np.uint8)
roi_final_path = OUTPUT_DIR / "evidencia_06_roi_limpio.png"
cv2.imwrite(str(roi_final_path), roi_final)
print(f"[OK] Guardado: {roi_final_path}")

# ============================================================================
# PASO 5: Pegar ROI limpio sobre imagen original
# ============================================================================
print("\n[PASO 5] Pegar ROI limpio sobre imagen original")
print("-" * 80)

documento_final = original.copy()
documento_final[y_min:y_max, x_min:x_max] = roi_final

documento_final_path = OUTPUT_DIR / "evidencia_07_documento_final.png"
cv2.imwrite(str(documento_final_path), documento_final)
print(f"[OK] Documento limpio guardado: {documento_final_path}")

# ============================================================================
# PASO 6: Aplicar OCR con EasyOCR
# ============================================================================
print("\n[PASO 6] Aplicar OCR con EasyOCR")
print("-" * 80)

ocr_blocks = []

try:
    import easyocr

    print("[*] Inicializando EasyOCR...")
    ocr_reader = easyocr.Reader(['es'], gpu=False)

    print("[*] Ejecutando OCR sobre documento limpio...")
    results = ocr_reader.readtext(str(documento_final_path))

    # Procesar resultados
    for result in results:
        bbox = result[0]  # Lista de 4 puntos [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        text = result[1]
        confidence = result[2]

        ocr_blocks.append({
            'bbox': [[int(p[0]), int(p[1])] for p in bbox],
            'text': text,
            'confidence': float(confidence)
        })

    print(f"[OK] OCR completado: {len(ocr_blocks)} bloques detectados")

except ImportError:
    print("[!] EasyOCR no esta instalado. Instalando...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'easyocr', '-q'])

    import easyocr
    print("[*] Inicializando EasyOCR...")
    ocr_reader = easyocr.Reader(['es'], gpu=False)

    print("[*] Ejecutando OCR sobre documento limpio...")
    results = ocr_reader.readtext(str(documento_final_path))

    # Procesar resultados
    for result in results:
        bbox = result[0]
        text = result[1]
        confidence = result[2]

        ocr_blocks.append({
            'bbox': [[int(p[0]), int(p[1])] for p in bbox],
            'text': text,
            'confidence': float(confidence)
        })

    print(f"[OK] OCR completado: {len(ocr_blocks)} bloques detectados")

# Guardar resultados OCR en JSON
if ocr_blocks:
    ocr_json = {
        'total_bloques': len(ocr_blocks),
        'bloques': ocr_blocks,
        'confianza_promedio': np.mean([b['confidence'] for b in ocr_blocks])
    }
else:
    ocr_json = {
        'total_bloques': 0,
        'bloques': [],
        'confianza_promedio': 0.0
    }

ocr_json_path = OUTPUT_DIR / "ocr_resultado_simple.json"
with open(ocr_json_path, 'w', encoding='utf-8') as f:
    json.dump(ocr_json, f, ensure_ascii=False, indent=2)
print(f"[OK] Resultados OCR guardados: {ocr_json_path}")

# ============================================================================
# PASO 7: Dibujar bloques OCR sobre documento
# ============================================================================
print("\n[PASO 7] Dibujar bloques OCR")
print("-" * 80)

documento_con_ocr = documento_final.copy()

for block in ocr_blocks:
    bbox = np.array(block['bbox'], dtype=np.int32)
    confidence = block['confidence']

    # Dibujar rectangulo verde
    cv2.polylines(documento_con_ocr, [bbox], True, (0, 255, 0), 2)

    # Dibujar confianza
    x1 = min([p[0] for p in bbox])
    y1 = min([p[1] for p in bbox])
    text = f"{confidence:.2f}"
    cv2.putText(documento_con_ocr, text, (int(x1), int(y1) - 5),
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

ocr_resultado_path = OUTPUT_DIR / "evidencia_08_ocr_resultado.png"
cv2.imwrite(str(ocr_resultado_path), documento_con_ocr)
print(f"[OK] Documento con OCR guardado: {ocr_resultado_path}")

# ============================================================================
# PASO 8: Crear comparacion side-by-side
# ============================================================================
print("\n[PASO 8] Crear comparacion side-by-side")
print("-" * 80)

# Crear separador blanco
separator = np.ones((original.shape[0], 20, 3), dtype=np.uint8) * 255

# Stack: original | separador | limpio | separador | con OCR
comparacion = np.hstack([original, separator, documento_final, separator, documento_con_ocr])

# Agregar labels
label_height = 60
label_img = np.ones((label_height, comparacion.shape[1], 3), dtype=np.uint8) * 255

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1.0
font_color = (0, 0, 0)
thickness = 2

col_width = original.shape[1]
cv2.putText(label_img, "ORIGINAL", (col_width // 2 - 60, 40),
           font, font_scale, font_color, thickness)
cv2.putText(label_img, "LIMPIO", (col_width + 20 + col_width // 2 - 50, 40),
           font, font_scale, font_color, thickness)
cv2.putText(label_img, "CON OCR", (col_width * 2 + 40 + col_width // 2 - 50, 40),
           font, font_scale, font_color, thickness)

comparacion_final = np.vstack([label_img, comparacion])

comparacion_path = OUTPUT_DIR / "evidencia_09_comparacion.png"
cv2.imwrite(str(comparacion_path), comparacion_final)
print(f"[OK] Comparacion guardada: {comparacion_path}")
print(f"  Tamaño: {comparacion_final.shape[1]}x{comparacion_final.shape[0]} pixeles")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "=" * 80)
print("RESUMEN FINAL")
print("=" * 80)

print(f"\n[STATS] ESTADISTICAS DE LIMPIEZA:")
print(f"   Pixeles de sello detectados:  {num_sello:,}")
print(f"   Pixeles limpios (blanqueados): {pixeles_limpios:,}")
if num_sello > 0:
    print(f"   Porcentaje limpiado:          {100*pixeles_limpios/num_sello:.2f}%")
else:
    print(f"   Porcentaje limpiado:          0.00%")

print(f"\n[FILES] ARCHIVOS GENERADOS:")
evidencia_files = [
    ("evidencia_01_roi_original.png", "ROI original del sello"),
    ("evidencia_02_clasificacion_pixeles.png", "Mapa: negro=texto, rojo=sello, blanco=fondo"),
    ("evidencia_03_mascara_sello.png", "Mascara binaria del sello"),
    ("evidencia_04_deteccion_texto.png", "Pixeles de texto detectados (verde)"),
    ("evidencia_05_filtro_horizontal.png", "ROI despues del barrido horizontal"),
    ("evidencia_06_roi_limpio.png", "ROI final limpio"),
    ("evidencia_07_documento_final.png", "Documento completo con ROI limpio"),
    ("evidencia_08_ocr_resultado.png", "Documento con bloques OCR"),
    ("evidencia_09_comparacion.png", "Comparacion: original vs limpio vs OCR"),
]

for filename, description in evidencia_files:
    filepath = OUTPUT_DIR / filename
    if filepath.exists():
        size = filepath.stat().st_size / (1024*1024)
        print(f"   [OK] {filename:<40s} ({size:6.2f} MB)")
    else:
        print(f"   [NO] {filename:<40s} (NO ENCONTRADO)")

print(f"\n[DONE] PIPELINE COMPLETADO EXITOSAMENTE")
print(f"   Documentos procesados: 1")
print(f"   Bloques OCR detectados: {len(ocr_blocks)}")
print(f"   Confianza OCR promedio: {ocr_json['confianza_promedio']:.2f}")

print("\n" + "=" * 80)
