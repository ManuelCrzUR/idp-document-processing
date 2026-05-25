# -*- coding: utf-8 -*-
"""
Phase 3a: Pipeline con Filtro de Barrido Horizontal
Integración completa del filtro en el pipeline de inpainting
"""
import numpy as np
from pathlib import Path
from PIL import Image
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "classification"))
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from chromatic_separator import ChromaticSeparator
from lama_inpainter import LamaInpainter

DATA_PATH = Path("C:/Users/manue/Documents/Desktop_Archive_2026-03-14/Folders/PR_COMPUTER_VISION/idp-project/datos/synthetic_dataset")


def read_yolo_label(label_file):
    with open(label_file, 'r') as f:
        bboxes = []
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                xc, yc, w, h = parts[1:5]
                bboxes.append((float(xc), float(yc), float(w), float(h)))
        return bboxes


class Phase3aWithHorizontalSweep:
    """
    Phase 3a: Pipeline de inpainting con filtro de barrido horizontal

    Pasos:
    1. Extraer ROI del sello
    2. Clasificar píxeles en 5 categorías
    3. NUEVO: Aplicar filtro de barrido horizontal
    4. Generar máscara de inpainting
    5. Aplicar inpainting LAMA
    6. (Opcional) Limpiar residuos
    """

    def __init__(self, use_horizontal_sweep=True, clean_residuals=True):
        self.separator = ChromaticSeparator(
            translucent_intensity_low=80,
            translucent_white_threshold=240,
            translucent_dominance_low=15,
            translucent_dominance_high=80
        )
        self.inpainter = LamaInpainter()
        self.use_horizontal_sweep = use_horizontal_sweep
        self.clean_residuals = clean_residuals

    def process(self, image_bgr, bbox_yolo):
        """
        Pipeline completo Phase 3a con opcional filtro horizontal

        Args:
            image_bgr: Imagen en formato BGR
            bbox_yolo: Bounding box normalizado (xc, yc, w, h)

        Returns:
            dict con resultados:
            - image_result: Imagen inpaintada
            - pixel_map_original: Clasificación original
            - pixel_map_filtered: Clasificación después de filtro (si aplica)
            - refined_mask: Máscara de inpainting
            - roi_coords: Coordenadas del ROI
            - stats: Estadísticas
        """

        # PASO 1: Extraer ROI
        roi_bgr, roi_coords = self.separator.extract_stamp_roi(image_bgr, bbox_yolo)

        # PASO 2: Clasificar píxeles
        pixel_map = self.separator.classify_pixels(roi_bgr)
        pixel_map_original = pixel_map.copy()

        # PASO 3: NUEVO - Aplicar filtro de barrido horizontal (OPCIONAL)
        if self.use_horizontal_sweep:
            pixel_map = self.separator.apply_horizontal_sweep_filter(pixel_map, roi_coords)

        # PASO 4: Generar máscara de inpainting
        h, w = image_bgr.shape[:2]
        refined_mask = np.zeros((h, w), dtype=np.uint8)

        x1, y1, x2, y2 = roi_coords
        roi_height = y2 - y1
        roi_width = x2 - x1

        for yi in range(roi_height):
            for xi in range(roi_width):
                # Activar máscara donde hay SELLO (1), MIXTO (2) o SELLO_TRANSLUCIDO (4)
                if pixel_map[yi, xi] in [1, 2, 4]:
                    refined_mask[y1 + yi, x1 + xi] = 255

        # PASO 5: Aplicar inpainting
        image_result = image_bgr.copy()
        roi_mask = refined_mask[y1:y2, x1:x2]

        if np.any(roi_mask > 0):
            roi_inpainted = self.inpainter.inpaint(roi_bgr, roi_mask)
            image_result[y1:y2, x1:x2] = roi_inpainted

        # PASO 6: (Opcional) Limpiar residuos
        if self.clean_residuals:
            image_result = self.separator.clean_residuals(
                image_result, bbox_yolo, pixel_map, residue_dominance_threshold=40
            )

        # Calcular estadísticas
        stats = {
            'inpaint_pixels_original': np.sum((pixel_map_original == 1) |
                                             (pixel_map_original == 2) |
                                             (pixel_map_original == 4)),
            'inpaint_pixels_after_filter': np.sum((pixel_map == 1) |
                                                 (pixel_map == 2) |
                                                 (pixel_map == 4)),
            'filas_eliminadas': np.sum(
                (pixel_map_original != pixel_map) &
                (pixel_map == 3) &
                (pixel_map_original != 0)
            ) // roi_width if roi_width > 0 else 0
        }

        return {
            'image_result': image_result,
            'pixel_map_original': pixel_map_original,
            'pixel_map_filtered': pixel_map if self.use_horizontal_sweep else None,
            'refined_mask': refined_mask,
            'roi_coords': roi_coords,
            'roi_bgr': roi_bgr,
            'stats': stats
        }


def process_single_image(img_path, label_path, use_sweep=True):
    """Procesa una imagen con el pipeline Phase 3a"""
    img_pil = Image.open(img_path).convert('RGB')
    img_bgr = np.array(img_pil)[:, :, ::-1]

    with open(label_path, 'r') as f:
        parts = f.readline().strip().split()
        xc, yc, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
        bbox_yolo = (xc, yc, w, h)

    pipeline = Phase3aWithHorizontalSweep(use_horizontal_sweep=use_sweep)
    result = pipeline.process(img_bgr, bbox_yolo)

    return result


def main():
    print("\n" + "=" * 80)
    print("PHASE 3A: PIPELINE CON FILTRO DE BARRIDO HORIZONTAL")
    print("=" * 80 + "\n")

    images_dir = DATA_PATH / "images"
    labels_dir = DATA_PATH / "labels"

    # Procesar primeras 5 imágenes para demostración
    image_files = sorted(list(images_dir.glob("*.png")))[:5]

    print("Comparativa: CON vs SIN Filtro de Barrido Horizontal\n")
    print("-" * 80)
    print(f"{'Imagen':<20} {'Inpaint Orig':<15} {'Inpaint Filt':<15} {'Reducción':<15}")
    print("-" * 80)

    for img_file in image_files:
        label_file = labels_dir / img_file.name.replace('.png', '.txt')

        if not label_file.exists():
            continue

        # Procesar CON filtro
        result_with = process_single_image(img_file, label_file, use_sweep=True)

        # Procesar SIN filtro (para comparación)
        result_without = process_single_image(img_file, label_file, use_sweep=False)

        orig = result_without['stats']['inpaint_pixels_original']
        filt = result_with['stats']['inpaint_pixels_after_filter']
        reduccion = orig - filt
        pct = (reduccion / orig * 100) if orig > 0 else 0

        print(f"{img_file.name:<20} {orig:<15,d} {filt:<15,d} {reduccion:<10,d} ({pct:>5.1f}%)")

    print("-" * 80)
    print("\nPIPELINE EXITOSO")
    print("\nFases ejecutadas:")
    print("1. [OK] Extracción ROI del sello")
    print("2. [OK] Clasificación de píxeles en 5 categorías")
    print("3. [OK] Filtro de barrido horizontal por fila")
    print("4. [OK] Generación de máscara de inpainting optimizada")
    print("5. [OK] Aplicación de inpainting LAMA")
    print("6. [OK] Limpieza de residuos de color")

    print("\nPROXIMOS PASOS:")
    print("- Revisar galería: galeria_roi_4categorias_final.html")
    print("- Análisis detallado: python src/pipeline/analyze_horizontal_sweep.py")
    print("- Documentación: HORIZONTAL_SWEEP_FILTER.md")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
