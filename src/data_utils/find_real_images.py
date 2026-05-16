# -*- coding: utf-8 -*-
import cv2
import numpy as np
from pathlib import Path
import shutil

def find_real_document_images():
    """Busca y copia imagenes reales de documentos con sellos para testing."""

    BASE_DIR = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project")
    DATOS_DIR = BASE_DIR / "datos"

    # Directorios donde buscar
    search_dirs = [
        DATOS_DIR / "spanishocr" / "images",
        DATOS_DIR / "data",
    ]

    # Directorio de salida para imagenes reales de testing
    TEST_DIR = BASE_DIR / "datos" / "real_images_for_testing"
    TEST_DIR.mkdir(parents=True, exist_ok=True)

    print("[*] Buscando imagenes reales de documentos...")

    found_images = []

    for search_dir in search_dirs:
        if not search_dir.exists():
            print("[!] Directorio no existe: {}".format(search_dir))
            continue

        print("  - Buscando en: {}".format(search_dir))

        # Buscar PNG y JPG
        for pattern in ["*.png", "*.jpg", "*.jpeg"]:
            for img_path in search_dir.glob(pattern):
                try:
                    img = cv2.imread(str(img_path))

                    if img is None:
                        continue

                    # Verificar que sea una imagen valida
                    if img.size < 10000:  # Muy pequena
                        continue

                    found_images.append(img_path)

                except Exception as e:
                    pass

    print("\n[OK] Encontradas {} imagenes reales".format(len(found_images)))

    if len(found_images) == 0:
        print("[!] No se encontraron imagenes reales. Asegúrate de que existan en:")
        for d in search_dirs:
            print("    - {}".format(d))
        return

    # Copiar una muestra (max 10 para testing)
    sample_size = min(10, len(found_images))
    print("\n[*] Copiando {} imagenes para testing...".format(sample_size))

    for i, src_path in enumerate(found_images[:sample_size]):
        dst_path = TEST_DIR / src_path.name

        if not dst_path.exists():
            shutil.copy(str(src_path), str(dst_path))
            print("  [{}/{}] Copiada: {}".format(i+1, sample_size, src_path.name))

    print("\n[OK] Imagenes reales de testing en: {}".format(TEST_DIR))
    print("[*] Proximos pasos:")
    print("  1. Ejecuta YOLO para detectar sellos en estas imagenes")
    print("  2. Usa Smooth Blend para eliminarlos")
    print("  3. Compara OCR antes/despues")

if __name__ == "__main__":
    find_real_document_images()
