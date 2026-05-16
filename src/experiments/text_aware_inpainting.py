# -*- coding: utf-8 -*-
import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from scipy import ndimage

class TextAwareInpainter:
    """Inpainting consciente de texto - Reconstruye letras interrumpidas."""

    def __init__(self, image, mask):
        """
        Args:
            image: Imagen con sello (BGR, uint8)
            mask: Mascara binaria donde 255 = sello, 0 = fondo
        """
        self.image = image.copy()
        self.image_float = image.astype(np.float32) / 255.0
        self.mask = (mask > 0).astype(np.uint8)
        self.h, self.w = self.image.shape[:2]

    # ========== OPCION 1: STROKE COMPLETION ==========
    def option1_stroke_completion(self):
        """Detecta y extiende strokes (lineas de tinta) que fueron cortadas."""
        print("[*] Aplicando Opcion 1: Stroke Completion...")

        result = self.image_float.copy()

        # Convertir a escala de grises para detectar text edges
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

        # Detectar bordes del texto con Canny (muy sensible)
        gray_uint8 = (gray * 255).astype(np.uint8)
        edges = cv2.Canny(gray_uint8, 30, 100)

        # Dilatar ligeramente para conectar strokes cercanos
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        edges = cv2.dilate(edges, kernel, iterations=1)

        # Encontrar strokes que cruzan el sello (edges que tocan mascara)
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_dilated = cv2.dilate(self.mask, kernel_dilate, iterations=1)

        crossing_strokes = edges & mask_dilated

        # Para cada pixel del sello, interpolar desde strokes que lo cruzan
        y_coords, x_coords = np.where(self.mask == 1)

        for y, x in zip(y_coords, x_coords):
            # Buscar strokes en vecindario
            best_color = None
            min_dist = float('inf')

            for dy in range(-15, 16, 2):
                for dx in range(-15, 16, 2):
                    ny, nx = y + dy, x + dx

                    if 0 <= ny < self.h and 0 <= nx < self.w:
                        if edges[ny, nx] > 0 and self.mask[ny, nx] == 0:
                            dist = np.sqrt(dy**2 + dx**2)

                            if dist < min_dist:
                                min_dist = dist
                                best_color = self.image_float[ny, nx]

            if best_color is not None:
                # Interpolar entre el pixel y el stroke mas cercano
                weight = min(1.0, min_dist / 15.0)
                result[y, x] = best_color * (1 - weight * 0.3) + result[y, x] * (weight * 0.3)

        return result

    # ========== OPCION 2: TEXT-AWARE INPAINTING ==========
    def option2_text_aware_inpainting(self):
        """Detecta zonas de texto y aplica inpainting selectivo."""
        print("[*] Aplicando Opcion 2: Text-Aware Inpainting...")

        result = self.image_float.copy()

        # Detectar texto usando Otsu (para documentos)
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Invertir para que texto sea blanco
        if np.mean(binary) > 127:
            binary = 255 - binary

        # Dilatar ligeramente para conectar caracteres
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        text_regions = cv2.dilate(binary, kernel, iterations=1)

        # Encontrar contornos de caracteres
        contours, _ = cv2.findContours(text_regions, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Para cada contorno que intersecta con el sello, aplicar inpainting local
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Verificar si este contorno intersecta con el sello
            contour_mask = np.zeros((self.h, self.w), dtype=np.uint8)
            cv2.drawContours(contour_mask, [contour], 0, 1, -1)

            if np.sum(contour_mask & self.mask) == 0:
                continue  # No intersecta, saltar

            # Extraer region local
            y1, y2 = max(0, y - 5), min(self.h, y + h + 5)
            x1, x2 = max(0, x - 5), min(self.w, x + w + 5)

            local_img = self.image[y1:y2, x1:x2].copy()
            local_mask = self.mask[y1:y2, x1:x2].copy()

            # Aplicar Telea inpainting solo en esta region
            if np.sum(local_mask) > 0:
                inpainted_local = cv2.inpaint(local_img, local_mask, 2, cv2.INPAINT_TELEA)
                result[y1:y2, x1:x2] = inpainted_local.astype(np.float32) / 255.0

        return result

    # ========== OPCION 3: STROKE DIRECTION + GRADIENT ==========
    def option3_stroke_direction_aware(self):
        """Completa letras respetando la direccion local de los strokes."""
        print("[*] Aplicando Opcion 3: Stroke Direction-Aware (RECOMENDADO)...")

        result = self.image_float.copy()

        # Calcular estructura local usando structure tensor
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

        # Calcular gradientes
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)

        # Suavizar gradientes para obtener direccion local (sin degradar)
        grad_x_smooth = cv2.GaussianBlur(grad_x, (5, 5), 1.0)
        grad_y_smooth = cv2.GaussianBlur(grad_y, (5, 5), 1.0)

        # Calcular angulo de direccion local
        angle = np.arctan2(grad_y_smooth, grad_x_smooth)

        # Para cada pixel del sello, interpolar en la direccion del stroke
        y_coords, x_coords = np.where(self.mask == 1)

        for y, x in zip(y_coords, x_coords):
            local_angle = angle[y, x]

            # Buscar pixeles en ambas direcciones del stroke
            colors_perpendicular = []

            # Buscar en direccion perpendicular al stroke
            perp_angle = local_angle + np.pi / 2

            for dist in range(3, 20, 2):
                # Direccion 1
                x1 = int(x + dist * np.cos(perp_angle))
                y1 = int(y + dist * np.sin(perp_angle))

                # Direccion 2 (opuesta)
                x2 = int(x - dist * np.cos(perp_angle))
                y2 = int(y - dist * np.sin(perp_angle))

                if 0 <= y1 < self.h and 0 <= x1 < self.w and self.mask[y1, x1] == 0:
                    colors_perpendicular.append(self.image_float[y1, x1])

                if 0 <= y2 < self.h and 0 <= x2 < self.w and self.mask[y2, x2] == 0:
                    colors_perpendicular.append(self.image_float[y2, x2])

            if colors_perpendicular:
                # Promediar colores encontrados
                avg_color = np.mean(colors_perpendicular, axis=0)
                result[y, x] = avg_color

        # Aplicar filtro bilateral muy suave para suavizar sin perder detalles
        result_uint8 = (result * 255).astype(np.uint8)
        result_uint8 = cv2.bilateralFilter(result_uint8, 5, 50, 50)
        result = result_uint8.astype(np.float32) / 255.0

        return result

    def inpaint(self, option=1):
        """
        Ejecuta opcion seleccionada.

        Args:
            option: 1, 2, o 3
        """
        if option == 1:
            return self.option1_stroke_completion()
        elif option == 2:
            return self.option2_text_aware_inpainting()
        elif option == 3:
            return self.option3_stroke_direction_aware()
        else:
            raise ValueError("Opcion invalida: {}".format(option))


def main():
    BASE_DIR = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project")
    SYNTHETIC_DIR = BASE_DIR / "datos" / "synthetic_dataset"
    OUTPUT_DIR = BASE_DIR / "datos" / "text_aware_inpainting_results"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Cargar imagen sintetica
    image_path = list((SYNTHETIC_DIR / "images").glob("*.png"))[0]
    mask_path = SYNTHETIC_DIR / "masks" / "{}_mask.png".format(image_path.stem)

    print("[*] Cargando: {}".format(image_path.name))
    image = cv2.imread(str(image_path))
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)

    if image is None or mask is None:
        print("[!] Error cargando imagenes")
        return

    inpainter = TextAwareInpainter(image, mask)

    print("\n[*] Procesando 3 opciones de text-aware inpainting...")

    # Opcion 1
    print("\n=== OPCION 1: STROKE COMPLETION ===")
    result1 = inpainter.inpaint(option=1)

    # Opcion 2
    print("\n=== OPCION 2: TEXT-AWARE INPAINTING ===")
    result2 = inpainter.inpaint(option=2)

    # Opcion 3
    print("\n=== OPCION 3: STROKE DIRECTION-AWARE ===")
    result3 = inpainter.inpaint(option=3)

    # Crear comparacion sin matplotlib (para evitar problemas de visualizacion)
    result1_uint8 = (result1 * 255).astype(np.uint8)
    result2_uint8 = (result2 * 255).astype(np.uint8)
    result3_uint8 = (result3 * 255).astype(np.uint8)

    # Crear imagen de comparacion manualmente
    h, w = image.shape[:2]
    comparison = np.zeros((h * 2, w * 2, 3), dtype=np.uint8)

    comparison[0:h, 0:w] = image
    comparison[0:h, w:w*2] = result1_uint8
    comparison[h:h*2, 0:w] = result2_uint8
    comparison[h:h*2, w:w*2] = result3_uint8

    comparison_path = OUTPUT_DIR / "text_aware_comparison.png"
    cv2.imwrite(str(comparison_path), comparison)
    print("\n[OK] Comparacion guardada: {}".format(comparison_path))

    # Guardar cada resultado individual en alta calidad
    for i, result in enumerate([result1, result2, result3], 1):
        result_uint8 = (result * 255).astype(np.uint8)
        result_path = OUTPUT_DIR / "opcion{}_text_aware.png".format(i)
        cv2.imwrite(str(result_path), result_uint8, [cv2.IMWRITE_PNG_COMPRESSION, 0])
        print("[OK] Opcion {} guardada (SIN COMPRESION): {}".format(i, result_path))

    print("\n[NOTA] Todas las imagenes se guardaron SIN compresion para preservar calidad de texto")
    print("[*] Usa el zoom para inspeccionar la legibilidad de las letras interrumpidas")

    plt.close('all')


if __name__ == "__main__":
    main()
