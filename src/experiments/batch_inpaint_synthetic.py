# -*- coding: utf-8 -*-
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
import sys
from smart_inpainting import SmartInpainter

def batch_inpaint_synthetic_dataset():
    """Procesa TODO el dataset sintetico con Smooth Blend inpainting."""

    BASE_DIR = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project")
    SYNTHETIC_DIR = BASE_DIR / "datos" / "synthetic_dataset"
    OUTPUT_DIR = BASE_DIR / "datos" / "synthetic_inpainted"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "images").mkdir(exist_ok=True)
    (OUTPUT_DIR / "labels").mkdir(exist_ok=True)

    images_dir = SYNTHETIC_DIR / "images"
    masks_dir = SYNTHETIC_DIR / "masks"
    labels_dir = SYNTHETIC_DIR / "labels"

    image_paths = sorted(list(images_dir.glob("*.png")))

    if not image_paths:
        print("[!] No hay imagenes sinteticas para procesar")
        return

    print("[*] Iniciando procesamiento batch de {} imagenes".format(len(image_paths)))
    print("[*] Salida: {}".format(OUTPUT_DIR))

    processed = 0
    failed = 0

    for image_path in tqdm(image_paths, desc="Inpainting"):
        try:
            mask_path = masks_dir / "{}_mask.png".format(image_path.stem)
            label_path = labels_dir / "{}.txt".format(image_path.stem)

            if not mask_path.exists():
                failed += 1
                continue

            image = cv2.imread(str(image_path))
            mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)

            if image is None or mask is None:
                failed += 1
                continue

            # Inpainting con Smooth Blend
            inpainter = SmartInpainter(image, mask)
            inpainted = inpainter.inpaint(method='smooth_blend')
            inpainted_uint8 = (inpainted * 255).astype(np.uint8)

            # Guardar imagen inpainted
            output_img_path = OUTPUT_DIR / "images" / image_path.name
            cv2.imwrite(str(output_img_path), inpainted_uint8)

            # Copiar etiqueta (sin cambios, la region de sello ya no existe)
            if label_path.exists():
                with open(str(label_path), 'r') as f:
                    label_content = f.read()
                output_label_path = OUTPUT_DIR / "labels" / label_path.name
                with open(str(output_label_path), 'w') as f:
                    f.write(label_content)

            processed += 1

        except Exception as e:
            print("\n[!] Error procesando {}: {}".format(image_path.name, str(e)))
            failed += 1

    print("\n[OK] Procesamiento completado")
    print("  - Procesadas: {}".format(processed))
    print("  - Errores: {}".format(failed))
    print("  - Ubicacion: {}".format(OUTPUT_DIR))

if __name__ == "__main__":
    batch_inpaint_synthetic_dataset()
