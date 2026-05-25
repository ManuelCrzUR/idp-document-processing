# -*- coding: utf-8 -*-
"""
Diagnóstico detallado del problema de inpainting en Phase 3A
"""
import cv2
import json
import numpy as np
from pathlib import Path

print("="*80)
print("DIAGNÓSTICO: ¿POR QUÉ NO SE INPAINTA EL SELLO?")
print("="*80)

# Paso 1: Cargar imágenes
print("\n[PASO 1] Cargar imágenes")
print("-"*80)

original = cv2.imread("output/prueba_completa/01_imagen_original.png")
cleaned = cv2.imread("test_results_corrected/phase_3a/cleaned_image.png")

print(f"Original shape: {original.shape}")
print(f"Cleaned shape: {cleaned.shape}")

# Paso 2: Cargar OCR results para ver la máscara final
print("\n[PASO 2] Cargar máscara final de inpainting")
print("-"*80)

try:
    # Cargar la visualización de máscara si existe
    mask_viz_path = "test_results_corrected/phase_3a/04_final_inpaint_mask.png"
    if Path(mask_viz_path).exists():
        mask_viz = cv2.imread(mask_viz_path)
        print(f"[OK] Loaded mask visualization: {mask_viz_path}")
        print(f"     Shape: {mask_viz.shape}")

        # Contar píxeles rojos (que representan áreas para inpaint)
        # En la visualización, rojo = 255 en canal B (BGR format)
        red_pixels = np.sum(mask_viz[:, :, 2] > 200)
        print(f"     Píxeles rojos (para inpaint): {red_pixels:,}")

        white_pixels = np.sum(np.all(mask_viz > 200, axis=2))
        print(f"     Píxeles blancos (preservar): {white_pixels:,}")
    else:
        print(f"[!] Archivo no encontrado: {mask_viz_path}")
except Exception as e:
    print(f"[ERROR] {e}")

# Paso 3: Analizar la región del sello antes y después
print("\n[PASO 3] Analizar región del sello")
print("-"*80)

# Región aproximada del sello (centro-inferior del documento)
seal_y_range = slice(1600, 2300)
seal_x_range = slice(800, 1700)

original_seal = original[seal_y_range, seal_x_range]
cleaned_seal = cleaned[seal_y_range, seal_x_range]

# Contar píxeles rojos
original_red = np.sum(original_seal[:, :, 2] > 200)
cleaned_red = np.sum(cleaned_seal[:, :, 2] > 200)

print(f"\nRegión del sello (y: 1600-2300, x: 800-1700):")
print(f"  Original - Píxeles rojos (R>200): {original_red:,}")
print(f"  Cleaned  - Píxeles rojos (R>200): {cleaned_red:,}")
print(f"  Diferencia: {original_red - cleaned_red:,} píxeles rojos removidos")
print(f"  Porcentaje removido: {100*(original_red-cleaned_red)/original_red:.2f}%")

if (original_red - cleaned_red) < 100:
    print(f"\n[!] PROBLEMA CRÍTICO: Solo se removieron {original_red-cleaned_red} píxeles rojos")
    print(f"    Esto indica que la máscara de inpainting probablemente está VACÍA")

# Paso 4: Cargar el archivo OCR JSON para más información
print("\n[PASO 4] Revisar logs de ejecución")
print("-"*80)

try:
    # Buscar el archivo JSON de resultados
    json_paths = [
        "test_results_corrected/phase_4/ocr_results.json",
        "test_results/phase_4/ocr_results.json",
    ]

    for json_path in json_paths:
        if Path(json_path).exists():
            with open(json_path) as f:
                data = json.load(f)
            print(f"[OK] Carregó: {json_path}")
            break
    else:
        print("[!] No se encontró archivo OCR JSON")
except Exception as e:
    print(f"[ERROR] {e}")

# Paso 5: Verificar si OpenCV/LaMa recibió correctamente la máscara
print("\n[PASO 5] Prueba directa de inpainting")
print("-"*80)

# Probar OpenCV inpainting en una región pequeña
from src.phase_3a.inpainter import OpenCVInpainter, HybridInpainter

print("[*] Probando OpenCV inpainting en región pequeña...")

# Extraer una región pequeña con el sello
test_roi = original[1800:2000, 1000:1300]
print(f"  Test ROI shape: {test_roi.shape}")

# Crear una máscara de prueba (todos los píxeles para inpaint)
test_mask = np.ones_like(test_roi[:, :, 0], dtype=np.uint8) * 255
print(f"  Test mask shape: {test_mask.shape}")
print(f"  Test mask pixels to inpaint: {np.sum(test_mask > 0)}")

# Aplicar OpenCV
try:
    inpainter_cv = OpenCVInpainter(radius=3)
    result_cv = inpainter_cv.inpaint(test_roi, test_mask)

    # Comparar entrada vs salida
    are_identical = np.array_equal(test_roi, result_cv)
    diff = cv2.absdiff(test_roi, result_cv)
    diff_pixels = np.sum(diff > 0)

    print(f"\n  [OpenCV] Entrada == Salida? {are_identical}")
    print(f"  [OpenCV] Píxeles que cambiaron: {diff_pixels:,}")

    if are_identical:
        print(f"  [!] OpenCV retornó la MISMA imagen sin modificar")
    else:
        print(f"  [OK] OpenCV sí modificó la imagen")

except Exception as e:
    print(f"  [ERROR] OpenCV falló: {e}")

# Paso 6: Revisar si LaMa está disponible
print("\n[PASO 6] Verificar disponibilidad de LaMa")
print("-"*80)

try:
    import torch
    from lama_cleaner.model_manager import ModelManager
    from lama_cleaner.schema import Config

    print("[OK] LaMa está disponible")
    print(f"     PyTorch version: {torch.__version__}")

    # Buscar checkpoint de LaMa
    import torch.hub
    torch_home = torch.hub.get_dir()
    print(f"     Torch home: {torch_home}")

except ImportError as e:
    print(f"[!] LaMa NO está disponible: {e}")

print("\n" + "="*80)
print("FIN DEL DIAGNÓSTICO")
print("="*80)
