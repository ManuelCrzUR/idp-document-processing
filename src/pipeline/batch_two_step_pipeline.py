# -*- coding: utf-8 -*-
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
from two_step_pipeline import TwoStepPipeline

def batch_process_dataset(dataset_name, images_dir, masks_dir, output_dir):
    """Procesa un dataset completo con el pipeline en 2 pasos."""

    print("\n" + "="*70)
    print("PROCESANDO DATASET: {}".format(dataset_name.upper()))
    print("="*70)

    image_paths = sorted(list(images_dir.glob("*.png")))

    if not image_paths:
        print("[!] No se encontraron imagenes en: {}".format(images_dir))
        return 0

    print("[*] Encontradas {} imagenes".format(len(image_paths)))
    print("[*] Salida: {}".format(output_dir))

    processed = 0
    failed = 0

    (output_dir / "paso1").mkdir(parents=True, exist_ok=True)
    (output_dir / "paso2").mkdir(parents=True, exist_ok=True)

    for image_path in tqdm(image_paths, desc="Procesando {}".format(dataset_name)):
        try:
            mask_path = masks_dir / "{}_mask.png".format(image_path.stem)

            if not mask_path.exists():
                failed += 1
                continue

            image = cv2.imread(str(image_path))
            mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)

            if image is None or mask is None:
                failed += 1
                continue

            # Ejecutar pipeline
            pipeline = TwoStepPipeline(image, mask)
            result_step1, result_step2 = pipeline.process()

            # Guardar paso 1 (Smooth Blend)
            result_step1_uint8 = (result_step1 * 255).astype(np.uint8)
            step1_path = output_dir / "paso1" / image_path.name
            cv2.imwrite(str(step1_path), result_step1_uint8, [cv2.IMWRITE_PNG_COMPRESSION, 0])

            # Guardar paso 2 (Texto reconstruido)
            result_step2_uint8 = (result_step2 * 255).astype(np.uint8)
            step2_path = output_dir / "paso2" / image_path.name
            cv2.imwrite(str(step2_path), result_step2_uint8, [cv2.IMWRITE_PNG_COMPRESSION, 0])

            processed += 1

        except Exception as e:
            failed += 1

    return processed, failed


def main():
    BASE_DIR = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project")
    SYNTHETIC_DIR = BASE_DIR / "datos" / "synthetic_dataset"
    SYNTHETIC_OUTPUT = BASE_DIR / "datos" / "pipeline_final_synthetic"

    print("[*] INICIANDO PROCESAMIENTO BATCH CON PIPELINE EN 2 PASOS")
    print("[*] Paso 1: Smooth Blend (elimina sello)")
    print("[*] Paso 2: Text-Aware Inpainting Opcion 3 (reconstruye texto)")

    # Procesar dataset sintetico
    processed_syn, failed_syn = batch_process_dataset(
        "Sintetico",
        SYNTHETIC_DIR / "images",
        SYNTHETIC_DIR / "masks",
        SYNTHETIC_OUTPUT
    )

    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE PROCESAMIENTO")
    print("="*70)
    print("[SINTETICO]")
    print("  - Procesadas: {}".format(processed_syn))
    print("  - Errores: {}".format(failed_syn))
    print("  - Ubicacion: {}".format(SYNTHETIC_OUTPUT))
    print("    - Paso 1 (Smooth Blend): {}".format(SYNTHETIC_OUTPUT / "paso1"))
    print("    - Paso 2 (Texto): {}".format(SYNTHETIC_OUTPUT / "paso2"))
    print("="*70)

    print("\n[OK] Pipeline completado")
    print("[*] Proximos pasos:")
    print("  1. Revisar imagenes en paso2/ (resultado final)")
    print("  2. Ejecutar OCR (PaddleOCR/Tesseract) antes vs despues")
    print("  3. Medir mejora con CER/WER")


if __name__ == "__main__":
    main()
