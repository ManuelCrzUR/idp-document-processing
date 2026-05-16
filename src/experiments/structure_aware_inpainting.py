# -*- coding: utf-8 -*-
import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

class StructureAwareInpainter:
    """Inpainting que detecta y reconstruye lineas/bordes interrumpidos."""

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

    def detect_edge_candidates(self, use_bilateral=True):
        """Detecta edges en la imagen para identificar lineas interrumpidas."""
        if use_bilateral:
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.bilateralFilter(gray, 9, 75, 75)
        else:
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Detectar edges con Canny
        edges = cv2.Canny(blurred, 50, 150)

        # Dilatar ligeramente para conectar edges cercanos
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=1)

        return edges

    def find_interrupted_lines(self, edges, dilation_radius=3):
        """Encuentra lineas que cruzan el sello (interrumpidas)."""

        # Dilatar máscara del sello para identificar areas alrededor
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*dilation_radius+1, 2*dilation_radius+1))
        seal_dilated = cv2.dilate(self.mask, kernel, iterations=1)

        # Edges que intersectan con el sello = lineas interrumpidas
        interrupted = edges & seal_dilated

        return interrupted, seal_dilated

    def complete_interrupted_lines(self, edges, interrupted, seal_region):
        """Intenta completar lineas que fueron interrumpidas por el sello."""

        result = self.image_float.copy()

        # Usar HoughLinesP para detectar lineas
        lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=30,
                               minLineLength=20, maxLineGap=10)

        if lines is None:
            return result

        # Para cada linea detectada, si toca el sello, intentar extenderla
        for line in lines:
            x1, y1, x2, y2 = line[0]

            # Calcular ecuacion de la linea (y = mx + b)
            if x2 - x1 == 0:
                continue

            m = (y2 - y1) / (x2 - x1 + 1e-6)
            b = y1 - m * x1

            # Buscar puntos donde la linea intersecta con la mascara del sello
            for y in range(self.h):
                x = int((y - b) / (m + 1e-6))

                if 0 <= x < self.w and self.mask[y, x] == 1:
                    # Estimar color de la linea segun los extremos
                    color_1 = self.image_float[y1, x1] if 0 <= y1 < self.h and 0 <= x1 < self.w else np.array([0.9, 0.9, 0.9])
                    color_2 = self.image_float[y2, x2] if 0 <= y2 < self.h and 0 <= x2 < self.w else np.array([0.9, 0.9, 0.9])
                    color_interpolated = (color_1 + color_2) / 2.0

                    result[y, x] = color_interpolated

        return result

    def gradient_aware_fill(self):
        """Rellena el sello preservando gradientes y estructura."""
        print("[*] Aplicando relleno consciente de gradientes...")

        result = self.image_float.copy()

        # Calcular gradientes fuera del sello
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

        # Gradiente X e Y usando Sobel
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)

        # Para cada pixel del sello, interpolar basado en gradientes vecinos
        y_coords, x_coords = np.where(self.mask == 1)

        for y, x in zip(y_coords, x_coords):
            # Buscar gradientes en vecindario sin sello
            neighbors_grad_x = []
            neighbors_grad_y = []
            neighbors_color = []

            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    ny, nx = y + dy, x + dx

                    if 0 <= ny < self.h and 0 <= nx < self.w and self.mask[ny, nx] == 0:
                        neighbors_grad_x.append(grad_x[ny, nx])
                        neighbors_grad_y.append(grad_y[ny, nx])
                        neighbors_color.append(self.image_float[ny, nx])

            if neighbors_color:
                # Interpolar color usando promedio de vecinos
                avg_color = np.mean(neighbors_color, axis=0)

                # Ajustar segun gradiente promedio
                avg_grad_x = np.mean(neighbors_grad_x)
                avg_grad_y = np.mean(neighbors_grad_y)

                # Desplazar el color segun el gradiente
                displacement = np.sqrt(avg_grad_x**2 + avg_grad_y**2)
                if displacement > 0:
                    direction_x = avg_grad_x / displacement
                    direction_y = avg_grad_y / displacement
                    avg_color += np.array([direction_x, direction_y, 0]) * 0.1

                result[y, x] = np.clip(avg_color, 0, 1)

        return result

    def hybrid_inpaint(self):
        """Combina deteccion de lineas + gradient-aware fill."""
        print("[*] Aplicando inpainting hibrido (estructura + gradientes)...")

        # Detectar edges
        edges = self.detect_edge_candidates()

        # Encontrar lineas interrumpidas
        interrupted, seal_dilated = self.find_interrupted_lines(edges)

        # Completar lineas interrumpidas
        result = self.complete_interrupted_lines(edges, interrupted, seal_dilated)

        # Aplicar gradient-aware fill para el resto
        result = self.gradient_aware_fill()

        # Suavizar resultado final
        result_uint8 = (result * 255).astype(np.uint8)
        result_uint8 = cv2.bilateralFilter(result_uint8, 9, 75, 75)
        result = result_uint8.astype(np.float32) / 255.0

        return result


def visualize_structure_analysis(image, mask):
    """Visualiza la deteccion de lineas interrumpidas."""

    inpainter = StructureAwareInpainter(image, mask)

    edges = inpainter.detect_edge_candidates()
    interrupted, seal_dilated = inpainter.find_interrupted_lines(edges)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # Original
    axes[0, 0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    axes[0, 0].set_title("Original", weight='bold')
    axes[0, 0].axis('off')

    # Mascara del sello
    axes[0, 1].imshow(mask, cmap='gray')
    axes[0, 1].set_title("Mascara del sello", weight='bold')
    axes[0, 1].axis('off')

    # Edges detectados
    axes[0, 2].imshow(edges, cmap='gray')
    axes[0, 2].set_title("Edges detectados (Canny)", weight='bold')
    axes[0, 2].axis('off')

    # Lineas interrumpidas
    axes[1, 0].imshow(interrupted, cmap='gray')
    axes[1, 0].set_title("Lineas interrumpidas", weight='bold')
    axes[1, 0].axis('off')

    # Resultado inpainting
    result = inpainter.hybrid_inpaint()
    result_uint8 = (result * 255).astype(np.uint8)
    axes[1, 1].imshow(cv2.cvtColor(result_uint8, cv2.COLOR_BGR2RGB))
    axes[1, 1].set_title("Resultado (estructura consciente)", weight='bold')
    axes[1, 1].axis('off')

    # Diferencia
    diff = cv2.absdiff(image, result_uint8)
    axes[1, 2].imshow(cv2.cvtColor(diff, cv2.COLOR_BGR2RGB))
    axes[1, 2].set_title("Cambios realizados", weight='bold')
    axes[1, 2].axis('off')

    plt.tight_layout()
    return fig, result


def main():
    BASE_DIR = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project")
    SYNTHETIC_DIR = BASE_DIR / "datos" / "synthetic_dataset"
    OUTPUT_DIR = BASE_DIR / "datos" / "structure_inpainting_results"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Cargar primera imagen sintetica
    image_path = list((SYNTHETIC_DIR / "images").glob("*.png"))[0]
    mask_path = SYNTHETIC_DIR / "masks" / "{}_mask.png".format(image_path.stem)

    print("[*] Cargando: {}".format(image_path.name))
    image = cv2.imread(str(image_path))
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)

    if image is None or mask is None:
        print("[!] Error cargando imagenes")
        return

    # Visualizar analisis
    fig, result = visualize_structure_analysis(image, mask)

    result_path = OUTPUT_DIR / "structure_analysis.png"
    plt.savefig(str(result_path), dpi=150, bbox_inches='tight')
    print("[OK] Analisis guardado: {}".format(result_path))

    # Guardar resultado final
    result_uint8 = (result * 255).astype(np.uint8)
    final_path = OUTPUT_DIR / "{}_structure_aware.png".format(image_path.stem)
    cv2.imwrite(str(final_path), result_uint8)
    print("[OK] Resultado guardado: {}".format(final_path))

    plt.close('all')


if __name__ == "__main__":
    main()
