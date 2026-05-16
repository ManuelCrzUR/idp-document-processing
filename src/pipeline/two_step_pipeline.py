# -*- coding: utf-8 -*-
import sys
import cv2
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "experiments"))
from smart_inpainting import SmartInpainter
from aggressive_inpainting import AggressiveInpainter

class TwoStepPipeline:
    """Pipeline en 2 pasos: 1) Eliminar sello, 2) Reconstruir texto interrumpido."""

    def __init__(self, image, mask):
        """
        Args:
            image: Imagen con sello (BGR, uint8)
            mask: Mascara del sello (uint8)
        """
        self.image_original = image.copy()
        self.mask = mask.copy()
        self.h, self.w = image.shape[:2]

    def step1_smooth_blend_removal(self):
        """Paso 1: Elimina el sello general usando Smooth Blend."""
        print("[PASO 1/2] Aplicando Smooth Blend para eliminar sello...")

        inpainter = SmartInpainter(self.image_original, self.mask)
        result_step1 = inpainter.inpaint(method='smooth_blend')

        return result_step1

    def step2_aggressive_fill(self, image_after_step1):
        """Paso 2: Relleno agresivo preciso (Color Dominante + Bordes Nitidos)."""
        print("[PASO 2/2] Aplicando relleno agresivo preciso...")

        # Convertir resultado de paso 1 a uint8 para procesamiento
        image_uint8 = (image_after_step1 * 255).astype(np.uint8)

        # Crear inpainter agresivo
        aggressive_inpainter = AggressiveInpainter(image_uint8, self.mask)

        # Aplicar inpainting agresivo
        result_step2_uint8 = aggressive_inpainter.inpaint_aggressive()

        # Convertir a float para consistencia
        result_step2_float = result_step2_uint8.astype(np.float32) / 255.0

        return result_step2_float

    def process(self):
        """Ejecuta el pipeline completo en 2 pasos."""
        print("\n" + "="*60)
        print("INICIANDO PIPELINE EN 2 PASOS")
        print("="*60)

        # Paso 1: Eliminar sello
        result_step1 = self.step1_smooth_blend_removal()

        # Paso 2: Relleno agresivo preciso
        result_step2 = self.step2_aggressive_fill(result_step1)

        print("\n[OK] Pipeline completado exitosamente")
        print("="*60)

        return result_step1, result_step2


def visualize_pipeline(image_original, mask, result_step1, result_step2):
    """Crea visualizacion del pipeline completo."""

    # Convertir a uint8 para visualizacion
    img_orig_uint8 = image_original
    result_step1_uint8 = (result_step1 * 255).astype(np.uint8)
    result_step2_uint8 = (result_step2 * 255).astype(np.uint8)

    # Crear imagen de comparacion (4 paneles)
    h, w = image_original.shape[:2]
    comparison = np.zeros((h * 2, w * 2, 3), dtype=np.uint8)

    comparison[0:h, 0:w] = img_orig_uint8
    comparison[0:h, w:w*2] = result_step1_uint8
    comparison[h:h*2, 0:w] = result_step1_uint8
    comparison[h:h*2, w:w*2] = result_step2_uint8

    return comparison


def main():
    BASE_DIR = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project")
    SYNTHETIC_DIR = BASE_DIR / "datos" / "synthetic_dataset"
    OUTPUT_DIR = BASE_DIR / "datos" / "two_step_pipeline_results"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Cargar imagen sintetica
    image_path = list((SYNTHETIC_DIR / "images").glob("*.png"))[0]
    mask_path = SYNTHETIC_DIR / "masks" / "{}_mask.png".format(image_path.stem)

    print("[*] Cargando imagen: {}".format(image_path.name))
    image = cv2.imread(str(image_path))
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)

    if image is None or mask is None:
        print("[!] Error cargando imagenes")
        return

    # Ejecutar pipeline
    pipeline = TwoStepPipeline(image, mask)
    result_step1, result_step2 = pipeline.process()

    # Guardar resultados
    result_step1_uint8 = (result_step1 * 255).astype(np.uint8)
    result_step2_uint8 = (result_step2 * 255).astype(np.uint8)

    # Paso 1
    step1_path = OUTPUT_DIR / "{}_paso1_smooth_blend.png".format(image_path.stem)
    cv2.imwrite(str(step1_path), result_step1_uint8, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    print("[OK] Paso 1 guardado: {}".format(step1_path.name))

    # Paso 2
    step2_path = OUTPUT_DIR / "{}_paso2_texto_reconstruido.png".format(image_path.stem)
    cv2.imwrite(str(step2_path), result_step2_uint8, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    print("[OK] Paso 2 guardado: {}".format(step2_path.name))

    # Comparacion visual
    comparison = visualize_pipeline(image, mask, result_step1, result_step2)
    comparison_path = OUTPUT_DIR / "pipeline_comparison.png"
    cv2.imwrite(str(comparison_path), comparison)
    print("[OK] Comparacion guardada: {}".format(comparison_path.name))

    print("\n[NOTA] Todas las imagenes se guardaron SIN compresion (PNG nivel 0)")
    print("[*] Ubicacion: {}".format(OUTPUT_DIR))


if __name__ == "__main__":
    main()
