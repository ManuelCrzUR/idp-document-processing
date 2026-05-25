# -*- coding: utf-8 -*-
"""
Validacion Visual: Verifica que la máscara final NO contiene píxeles de TEXTO
Muestra side-by-side: Clasificación vs Máscara
"""
import numpy as np
from pathlib import Path
from PIL import Image
import cv2
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "classification"))
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from phase_3a_complete import Phase3aComplete

DATA_PATH = Path("C:/Users/manue/Documents/Desktop_Archive_2026-03-14/Folders/PR_COMPUTER_VISION/idp-project/datos/synthetic_dataset")
OUTPUT_DIR = Path("C:/Users/manue/Desktop/final_vision")


def read_yolo_label(label_file):
    with open(label_file, 'r') as f:
        bboxes = []
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                xc, yc, w, h = parts[1:5]
                bboxes.append((float(xc), float(yc), float(w), float(h)))
        return bboxes


def create_classification_viz(pixel_map):
    """Crea visualización de clasificación con colores"""
    h, w = pixel_map.shape
    viz = np.zeros((h, w, 3), dtype=np.uint8)

    colors = {
        0: (0, 0, 0),        # TEXTO - Negro ⭐ IMPORTANTE
        1: (0, 0, 255),      # SELLO SATURADO - Rojo
        2: (255, 0, 255),    # MIXTO - Magenta
        3: (128, 128, 128),  # FONDO - Gris
        4: (255, 255, 0),    # TRANSLUCIDO - Cyan
    }

    for label, color in colors.items():
        mask = pixel_map == label
        viz[mask] = color

    return viz


def create_mask_viz_for_comparison(final_mask, roi_coords, h, w):
    """Crea visualización de la máscara final (solo área de inpaint)"""
    viz = np.zeros((h, w, 3), dtype=np.uint8)

    # Blanco donde hay máscara = área a inpaint
    viz[final_mask > 0] = [255, 255, 255]

    # Gris donde NO hay máscara = preservado
    viz[final_mask == 0] = [64, 64, 64]

    return viz


def validate_mask_for_image(img_name):
    """Valida que la máscara NO contiene píxeles de TEXTO"""
    images_dir = DATA_PATH / "images"
    labels_dir = DATA_PATH / "labels"

    img_path = images_dir / img_name
    label_file = labels_dir / img_name.replace('.png', '.txt')

    if not img_path.exists() or not label_file.exists():
        return None

    # Cargar imagen
    img_pil = Image.open(img_path).convert('RGB')
    img_bgr = np.array(img_pil)[:, :, ::-1]
    bboxes = read_yolo_label(label_file)
    bbox = bboxes[0]

    # Procesar con pipeline
    pipeline = Phase3aComplete(block_size=20, min_text_pixels=1, final_dilation=3, debug=False)
    result = pipeline.process(img_bgr, bbox)

    # Extraer información
    pixel_map_original = result['pixel_map_original']
    final_mask = result['final_mask']
    text_map = result['text_map']
    text_pixels_in_mask = result['text_pixels_in_mask']
    roi_coords = result['roi_coords']

    h, w = img_bgr.shape[:2]
    x1, y1, x2, y2 = roi_coords

    # Extraer ROI de las visualizaciones
    roi_h = y2 - y1
    roi_w = x2 - x1

    # Crear visualizaciones del ROI
    classification_viz = create_classification_viz(pixel_map_original)
    roi_mask_only = final_mask[y1:y2, x1:x2]
    roi_text_map = text_map[y1:y2, x1:x2]

    # Visualización de máscara (solo ROI)
    mask_viz = np.zeros((roi_h, roi_w, 3), dtype=np.uint8)
    mask_viz[roi_mask_only > 0] = [255, 255, 255]  # Blanco = inpaint
    mask_viz[roi_mask_only == 0] = [64, 64, 64]    # Gris = preservado

    # Crear overlay: mostrar donde hay TEXTO y máscara (PROBLEMA!)
    problem_viz = np.zeros((roi_h, roi_w, 3), dtype=np.uint8)

    # Verde = TEXTO preservado correctamente
    problem_viz[(roi_text_map > 0) & (roi_mask_only == 0)] = [0, 255, 0]

    # ROJO = PROBLEMA: TEXTO siendo inpaintado!
    problem_viz[(roi_text_map > 0) & (roi_mask_only > 0)] = [0, 0, 255]

    # Blanco = SELLO/MIXTO a inpaint (correcto)
    problem_viz[(roi_text_map == 0) & (roi_mask_only > 0)] = [255, 255, 255]

    # Gris = Fondo o preservado
    problem_viz[(roi_text_map == 0) & (roi_mask_only == 0)] = [128, 128, 128]

    # Crear side-by-side para comparación
    comparison = np.hstack([classification_viz, mask_viz])

    return {
        'img_name': img_name,
        'classification': classification_viz,
        'mask': mask_viz,
        'problem_map': problem_viz,
        'comparison': comparison,
        'text_pixels_in_mask': text_pixels_in_mask,
        'text_map': text_map,
        'final_mask': final_mask,
        'roi_coords': roi_coords,
    }


def main():
    print("\n" + "=" * 80)
    print("VALIDACION DE MASCARA: Verifica que NO contiene píxeles de TEXTO")
    print("=" * 80 + "\n")

    images_dir = DATA_PATH / "images"
    image_files = sorted(list(images_dir.glob("*.png")))[:5]

    for idx, img_file in enumerate(image_files, 1):
        print(f"\n[{idx}] {img_file.name}")
        print("-" * 80)

        result = validate_mask_for_image(img_file.name)
        if not result:
            continue

        text_in_mask = result['text_pixels_in_mask']

        if text_in_mask > 0:
            print(f"  [ERROR] ENCONTRADOS {text_in_mask} PIXELES DE TEXTO EN MASCARA!")
            print(f"          Esto causara que LaMa borre texto legitimo.")
        else:
            print(f"  [OK] Mascara LIMPIA de pixeles de TEXTO")

        # Guardar visualizaciones de comparación
        output_dir = OUTPUT_DIR / "validacion_mascara"
        output_dir.mkdir(exist_ok=True)

        # Guardar clasificación
        cv2.imwrite(
            str(output_dir / f"{idx:02d}_{img_file.stem}_01_clasificacion.png"),
            result['classification']
        )

        # Guardar máscara
        cv2.imwrite(
            str(output_dir / f"{idx:02d}_{img_file.stem}_02_mascara.png"),
            result['mask']
        )

        # Guardar mapa de problemas
        cv2.imwrite(
            str(output_dir / f"{idx:02d}_{img_file.stem}_03_problema_map.png"),
            result['problem_map']
        )

        # Guardar comparison side-by-side
        cv2.imwrite(
            str(output_dir / f"{idx:02d}_{img_file.stem}_04_comparison.png"),
            result['comparison']
        )

        # Estadísticas (solo del ROI)
        x1, y1, x2, y2 = result['roi_coords']
        roi_mask_pixels = result['final_mask'][y1:y2, x1:x2]
        roi_text_pixels = result['text_map'][y1:y2, x1:x2]

        total_mask_pixels = np.sum(roi_mask_pixels > 0)
        total_text_pixels = np.sum(roi_text_pixels > 0)
        roi_h = y2 - y1
        roi_w = x2 - x1
        mask_coverage = (total_mask_pixels / (roi_h * roi_w)) * 100
        text_coverage = (total_text_pixels / (roi_h * roi_w)) * 100

        print(f"\n  Estadisticas:")
        print(f"    Pixeles en mascara: {total_mask_pixels:,} ({mask_coverage:.2f}%)")
        print(f"    Pixeles de TEXTO: {total_text_pixels:,} ({text_coverage:.2f}%)")
        print(f"    Solapamiento (PROBLEMA): {text_in_mask} pixeles")

        if text_in_mask > 0:
            print(f"\n  [SOLUCION] Se aplicó bitwise_and para excluir TEXTO de la máscara.")
            print(f"             Verifica que el problema sea resuelto en la próxima ejecución.")
        else:
            print(f"\n  [VALIDACION] La máscara está correctamente construida.")

    print("\n" + "=" * 80)
    print("Imágenes de validación guardadas en:")
    print(f"  {OUTPUT_DIR / 'validacion_mascara'}")
    print("\nAbre las imágenes para verificar visualmente:")
    print("  01_clasificacion.png    - Mapa de clasificación original")
    print("  02_mascara.png          - Máscara final (blanco = inpaint)")
    print("  03_problema_map.png     - Rojo = PROBLEMA, Verde = OK, Blanco = SELLO")
    print("  04_comparison.png       - Side-by-side para comparación")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
