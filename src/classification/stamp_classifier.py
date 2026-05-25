# -*- coding: utf-8 -*-
import cv2
import numpy as np
from pathlib import Path

DEFAULT_THRESHOLD = 50


def extract_stamp_roi(image_bgr, bbox_yolo):
    """
    Extrae la región de interés (ROI) del sello desde un bounding box YOLO normalizado.

    Args:
        image_bgr: Imagen en formato BGR (np.ndarray)
        bbox_yolo: Tupla (xc_norm, yc_norm, w_norm, h_norm) con coordenadas normalizadas [0,1]

    Returns:
        roi_bgr: Región del sello extraída en BGR (np.ndarray)
    """
    h, w = image_bgr.shape[:2]
    xc_norm, yc_norm, w_norm, h_norm = bbox_yolo

    xc = int(xc_norm * w)
    yc = int(yc_norm * h)
    w_px = int(w_norm * w)
    h_px = int(h_norm * h)

    x1 = max(0, xc - w_px // 2)
    y1 = max(0, yc - h_px // 2)
    x2 = min(w, xc + w_px // 2)
    y2 = min(h, yc + h_px // 2)

    roi_bgr = image_bgr[y1:y2, x1:x2]
    return roi_bgr


def compute_mean_saturation(roi_bgr):
    """
    Calcula la saturación media del canal S (HSV) de una región.

    Args:
        roi_bgr: Región de imagen en BGR (np.ndarray)

    Returns:
        mean_saturation: Valor medio de saturación [0, 255] (float)
    """
    if roi_bgr.size == 0:
        return 0.0

    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    mean_saturation = float(saturation.mean())

    return mean_saturation


def classify_stamp(image_bgr, bbox_yolo, threshold=None):
    """
    Clasifica un sello como de color o negro basándose en la saturación media HSV.

    Args:
        image_bgr: Imagen en formato BGR (np.ndarray)
        bbox_yolo: Tupla (xc_norm, yc_norm, w_norm, h_norm) con coordenadas normalizadas
        threshold: Umbral de saturación para clasificación. Si es None, usa DEFAULT_THRESHOLD

    Returns:
        dict con claves:
            - mean_saturation: Valor medio de saturación (float)
            - label: "color" si S >= threshold, "negro" si S < threshold
            - threshold_used: Umbral utilizado para la clasificación
    """
    if threshold is None:
        threshold = DEFAULT_THRESHOLD

    roi = extract_stamp_roi(image_bgr, bbox_yolo)
    mean_sat = compute_mean_saturation(roi)

    label = "color" if mean_sat >= threshold else "negro"

    return {
        "mean_saturation": mean_sat,
        "label": label,
        "threshold_used": threshold
    }


if __name__ == "__main__":
    import glob

    real_images_dir = Path("real_images_for_testing")
    if not real_images_dir.exists():
        print(f"Directorio {real_images_dir} no encontrado.")
        print("Ejecuta primero: python src/data_utils/find_real_images.py")
    else:
        images = list(real_images_dir.glob("*.png")) + list(real_images_dir.glob("*.jpg"))
        if not images:
            print(f"No hay imágenes en {real_images_dir}")
        else:
            img_path = images[0]
            print(f"\nCargando imagen de prueba: {img_path}")
            img = cv2.imread(str(img_path))

            if img is None:
                print(f"Error al cargar {img_path}")
            else:
                h, w = img.shape[:2]
                bbox_yolo = (0.5, 0.5, 0.2, 0.2)

                result = classify_stamp(img, bbox_yolo)

                print(f"Imagen: {img_path.name}")
                print(f"Tamaño: {w}x{h}")
                print(f"BBox YOLO (ejemplo): {bbox_yolo}")
                print(f"\nResultado:")
                print(f"  Saturación media: {result['mean_saturation']:.2f}")
                print(f"  Clasificación: {result['label'].upper()}")
                print(f"  Umbral usado: {result['threshold_used']}")
