# -*- coding: utf-8 -*-
"""
Phase 3a: Pipeline Completo
Clasificación + Filtro Horizontal + Filtro Bloques + LaMa Inpainting
"""
import numpy as np
import cv2
from pathlib import Path
from PIL import Image
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "classification"))
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from chromatic_separator import ChromaticSeparator
from advanced_inpainter import LamaInpainterWrapper
from stamp_classifier_rgb import RGBStampClassifier

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


class Phase3aComplete:
    """
    Pipeline completo Phase 3a:
    1. Clasificación de píxeles (5 categorías)
    2. Filtro de barrido horizontal (por fila)
    3. Filtro de barrido por bloques
    4. LaMa inpainting
    """

    def __init__(self, block_size=20, min_text_pixels=1, final_dilation=3, debug=False):
        """
        Args:
            block_size: Tamaño de bloque para filtro de bloques
            min_text_pixels: Mínimo píxeles TEXTO por bloque
            final_dilation: Kernel para dilatar máscara antes de inpaint (default 3)
            debug: Guardar imágenes/máscaras de debug (default False)
        """
        self.separator = ChromaticSeparator(
            translucent_intensity_low=80,
            translucent_white_threshold=240,
            translucent_dominance_low=15,
            translucent_dominance_high=80
        )
        self.inpainter = LamaInpainterWrapper(debug=debug)
        self.block_size = block_size
        self.min_text_pixels = min_text_pixels
        self.final_dilation = final_dilation

    def process(self, image_bgr, bbox_yolo):
        """
        Procesa imagen a través de todo el pipeline Phase 3a

        Args:
            image_bgr: Imagen en formato BGR
            bbox_yolo: Bounding box normalizado (xc, yc, w, h)

        Returns:
            dict con resultados:
            - image_inpainted: Imagen final después de LaMa
            - pixel_map_original: Clasificación original
            - pixel_map_filtered: Clasificación después de ambos filtros
            - final_mask: Máscara final dilatada usada en LaMa
            - roi_coords: Coordenadas del ROI
            - stats: Estadísticas de procesamiento
        """

        h, w = image_bgr.shape[:2]

        # PASO 1: Extracción ROI y clasificación
        roi_bgr, roi_coords = self.separator.extract_stamp_roi(image_bgr, bbox_yolo)
        pixel_map_original = self.separator.classify_pixels(roi_bgr)
        pixel_map_current = pixel_map_original.copy()

        x1, y1, x2, y2 = roi_coords
        roi_h = y2 - y1
        roi_w = x2 - x1

        # PASO 2: Filtro Horizontal
        pixel_map_current = self.separator.apply_horizontal_sweep_filter(
            pixel_map_current, roi_coords
        )

        # PASO 3: Filtro Bloques
        block_result = self.separator.apply_block_sweep_filter(
            pixel_map_current,
            block_size=self.block_size,
            min_text_pixels_per_block=self.min_text_pixels
        )
        pixel_map_current = block_result['pixel_map_filtered']

        # PASO 4: Construir máscara final
        # Máscara solo con píxeles SELLO(1) y MIXTO(2) que sobrevivieron ambos filtros
        final_mask = np.zeros((h, w), dtype=np.uint8)

        for yi in range(roi_h):
            for xi in range(roi_w):
                # Activar máscara donde hay SELLO(1) o MIXTO(2)
                if pixel_map_current[yi, xi] in [1, 2]:
                    final_mask[y1 + yi, x1 + xi] = 255

        # PASO 5: Dilatar máscara para capturar bordes residuales
        if self.final_dilation > 0:
            kernel = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE,
                (self.final_dilation, self.final_dilation)
            )
            final_mask = cv2.dilate(final_mask, kernel, iterations=1)

        # PASO 5B: EXCLUIR EXPLÍCITAMENTE PÍXELES DE TEXTO
        # Crear mapa de TEXTO (categoría 0)
        text_map = np.zeros((h, w), dtype=np.uint8)
        for yi in range(roi_h):
            for xi in range(roi_w):
                if pixel_map_original[yi, xi] == 0:  # TEXTO
                    text_map[y1 + yi, x1 + xi] = 255

        # Operación crítica: final_mask = final_mask AND NOT text_map
        # Esto asegura que NO hay píxeles de TEXTO en la máscara
        text_map_negated = cv2.bitwise_not(text_map)
        final_mask = cv2.bitwise_and(final_mask, text_map_negated)

        import logging
        logger = logging.getLogger('MaskValidation')
        text_pixels_in_mask = np.sum((final_mask > 0) & (text_map > 0))
        logger.info(f"Validacion: Pixeles de TEXTO en mascara final: {text_pixels_in_mask}")
        if text_pixels_in_mask > 0:
            logger.warning(f"  ADVERTENCIA: {text_pixels_in_mask} pixeles de TEXTO en mascara!")
        else:
            logger.info(f"  OK: Mascara limpia de pixeles de TEXTO")

        # PASO 6: LaMa Inpainting
        image_inpainted = image_bgr.copy()

        # Aplicar inpainting solo al ROI
        roi_mask = final_mask[y1:y2, x1:x2]

        if np.any(roi_mask > 0):
            roi_bgr_inpainted = self.inpainter.inpaint(roi_bgr, roi_mask)
            image_inpainted[y1:y2, x1:x2] = roi_bgr_inpainted

        # Estadísticas
        stats = {
            'pixels_original_inpaint': np.sum(
                (pixel_map_original == 1) | (pixel_map_original == 2)
            ),
            'pixels_after_filters': np.sum(
                (pixel_map_current == 1) | (pixel_map_current == 2)
            ),
            'pixels_in_mask': np.sum(final_mask > 0),
            'reduction_pct': (
                np.sum((pixel_map_original == 1) | (pixel_map_original == 2)) -
                np.sum((pixel_map_current == 1) | (pixel_map_current == 2))
            ) / (np.sum((pixel_map_original == 1) | (pixel_map_original == 2)) * 100)
            if np.sum((pixel_map_original == 1) | (pixel_map_original == 2)) > 0 else 0
        }

        # Validación: Contar píxeles de TEXTO que podrían estar en la máscara
        text_pixels_in_mask = np.sum((final_mask > 0) & (text_map > 0))

        return {
            'image_inpainted': image_inpainted,
            'pixel_map_original': pixel_map_original,
            'pixel_map_filtered': pixel_map_current,
            'final_mask': final_mask,
            'roi_coords': roi_coords,
            'roi_bgr': roi_bgr,
            'stats': stats,
            'block_info': block_result['blocks_info'],
            'text_map': text_map,  # Para validación visual
            'text_pixels_in_mask': text_pixels_in_mask,  # Para verificación
            'roi_mask': roi_mask  # Máscara del ROI para análisis
        }


def process_single_image(img_path, label_path, pipeline, block_size=20, min_text_pixels=1, final_dilation=3):
    """Procesa una imagen con el pipeline Phase 3a completo"""
    img_pil = Image.open(img_path).convert('RGB')
    img_bgr = np.array(img_pil)[:, :, ::-1]

    with open(label_path, 'r') as f:
        parts = f.readline().strip().split()
        xc, yc, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
        bbox_yolo = (xc, yc, w, h)

    result = pipeline.process(img_bgr, bbox_yolo)

    return result


def main(debug=False):
    print("\n" + "=" * 100)
    print("PHASE 3A: PIPELINE COMPLETO (Clasificacion + Filtros + LaMa Inpainting)")
    print("=" * 100 + "\n")
    if debug:
        print("[DEBUG MODE ENABLED] Se guardarán imágenes de debug en ./debug_inpainting/\n")

    images_dir = DATA_PATH / "images"
    labels_dir = DATA_PATH / "labels"

    image_files = sorted(list(images_dir.glob("*.png")))[:5]

    block_size = 20
    min_text_pixels = 1
    final_dilation = 3

    print(f"Configuracion:")
    print(f"  Block size: {block_size}x{block_size}")
    print(f"  Min text pixels: {min_text_pixels}")
    print(f"  Final dilation: {final_dilation}")
    print()

    # Crear instancia pipeline para ver diagnosticos de LaMa
    print("Inicializando pipeline...")
    pipeline = Phase3aComplete(
        block_size=block_size,
        min_text_pixels=min_text_pixels,
        final_dilation=final_dilation,
        debug=debug
    )
    print()

    print("-" * 100)
    print(f"{'Imagen':<20} {'Orig Inpaint':<15} {'After Filters':<15} {'Final Mask':<15} {'Reduc %':<10}")
    print("-" * 100)

    for img_file in image_files:
        label_file = labels_dir / img_file.name.replace('.png', '.txt')

        if not label_file.exists():
            continue

        result = process_single_image(
            img_file, label_file,
            pipeline=pipeline,
            block_size=block_size,
            min_text_pixels=min_text_pixels,
            final_dilation=final_dilation
        )

        stats = result['stats']
        print(f"{img_file.name:<20} {stats['pixels_original_inpaint']:<15,d} "
              f"{stats['pixels_after_filters']:<15,d} {stats['pixels_in_mask']:<15,d} "
              f"{stats['reduction_pct']:>8.1f}%")

    print("-" * 100)
    print("\nPIPELINE PHASE 3A EXITOSO")
    print("\nPasos completados:")
    print("1. [OK] Clasificacion de pixeles en 5 categorias")
    print("2. [OK] Filtro de barrido horizontal (por fila)")
    print("3. [OK] Filtro de barrido por bloques")
    print("4. [OK] Construccion de mascara final (dilatada)")
    print(f"5. [OK] Inpainting: {pipeline.inpainter.source_used}")

    print("\nResultado: Imagen inpainted con sello removido")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    import sys
    debug = '--debug' in sys.argv
    main(debug=debug)
