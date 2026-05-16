# -*- coding: utf-8 -*-
import cv2
import numpy as np
from pathlib import Path

class MultiDirectionInpainter:
    """Inpainting con analisis multi-direccional para mayor precision."""

    def __init__(self, image, mask):
        """
        Args:
            image: Imagen con sello (BGR, uint8)
            mask: Mascara binaria donde 255 = sello, 0 = fondo
        """
        self.image = image.copy()
        self.mask = (mask > 0).astype(np.uint8)
        self.h, self.w = self.image.shape[:2]

    def analyze_direction(self, y, x, dy, dx, radius=15):
        """
        Analiza color dominante en una direccion especifica.
        dy, dx define la direccion (ej: (0,1) horizontal, (1,0) vertical, etc)
        """
        white_count = 0
        black_count = 0

        for i in range(1, radius + 1):
            ny = y + (dy * i)
            nx = x + (dx * i)

            if 0 <= ny < self.h and 0 <= nx < self.w and self.mask[ny, nx] == 0:
                pixel = self.image[ny, nx]
                gray = np.mean(pixel).astype(int)

                if gray > 200:
                    white_count += 1
                elif gray < 80:
                    black_count += 1

        return 'blanco' if white_count > black_count else 'negro'

    # ========== OPCION A: VOTO MAYORITARIO 4 DIRECCIONES ==========
    def option_a_four_directions_voting(self):
        """
        Analiza 4 direcciones (H, V, D1, D2) y elige por voto mayoritario.
        Mas robusto pero mas lento.
        """
        print("[*] Opcion A: Voto Mayoritario en 4 Direcciones...")

        result = self.image.copy().astype(np.uint8)
        y_coords, x_coords = np.where(self.mask == 1)

        for y, x in zip(y_coords, x_coords):
            # Analizar 4 direcciones
            directions = [
                (0, 1),   # Horizontal derecha
                (1, 0),   # Vertical abajo
                (1, 1),   # Diagonal ↘
                (1, -1),  # Diagonal ↙
            ]

            votes = {'blanco': 0, 'negro': 0}

            for dy, dx in directions:
                color = self.analyze_direction(y, x, dy, dx, radius=12)
                votes[color] += 1

            # Resultado: color con mas votos
            if votes['blanco'] > votes['negro']:
                result[y, x] = [255, 255, 255]
            else:
                result[y, x] = [0, 0, 0]

        return result

    # ========== OPCION B: HIBRIDO HORIZONTAL + VERTICAL ==========
    def option_b_hybrid_hv(self):
        """
        Analiza Horizontal y Vertical, equilibra los dos.
        Mas rapido pero completo.
        """
        print("[*] Opcion B: Hibrido Horizontal + Vertical...")

        result = self.image.copy().astype(np.uint8)
        y_coords, x_coords = np.where(self.mask == 1)

        for y, x in zip(y_coords, x_coords):
            # Horizontal
            h_color = self.analyze_direction(y, x, 0, 1, radius=15)

            # Vertical
            v_color = self.analyze_direction(y, x, 1, 0, radius=15)

            # Si ambas coinciden, usar ese. Si no, usar horizontal (es mas importante para docs)
            if h_color == v_color:
                final_color = h_color
            else:
                final_color = h_color  # Horizontal dominante

            if final_color == 'blanco':
                result[y, x] = [255, 255, 255]
            else:
                result[y, x] = [0, 0, 0]

        return result

    def process_both_options(self):
        """Ejecuta ambas opciones para comparar."""
        result_a = self.option_a_four_directions_voting()
        result_b = self.option_b_hybrid_hv()

        return result_a, result_b


def main():
    BASE_DIR = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project")
    SYNTHETIC_DIR = BASE_DIR / "datos" / "synthetic_dataset"
    OUTPUT_DIR = BASE_DIR / "datos" / "multi_direction_comparison"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Cargar imagen despues de paso 1 (Smooth Blend)
    pipeline_results = BASE_DIR / "datos" / "two_step_pipeline_results"
    paso1_path = pipeline_results / "syn_0000_paso1_smooth_blend.png"

    print("[*] Cargando imagen post-Smooth Blend: {}".format(paso1_path.name))
    image_paso1 = cv2.imread(str(paso1_path))

    # Cargar mascara original
    mask_path = SYNTHETIC_DIR / "masks" / "syn_0000_mask.png"
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)

    if image_paso1 is None or mask is None:
        print("[!] Error cargando imagenes")
        return

    # Procesar ambas opciones
    print("\n" + "="*60)
    print("COMPARANDO 2 ESTRATEGIAS MULTI-DIRECCIONALES")
    print("="*60)

    inpainter = MultiDirectionInpainter(image_paso1, mask)
    result_a, result_b = inpainter.process_both_options()

    # Guardar resultados
    print("\n[OK] Guardando resultados...")

    # Opcion A
    a_path = OUTPUT_DIR / "opcion_a_cuatro_direcciones.png"
    cv2.imwrite(str(a_path), result_a, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    print("[OK] Opcion A (4 direcciones): {}".format(a_path.name))

    # Opcion B
    b_path = OUTPUT_DIR / "opcion_b_hibrido_hv.png"
    cv2.imwrite(str(b_path), result_b, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    print("[OK] Opcion B (Hibrido H+V): {}".format(b_path.name))

    # Crear comparacion 3 paneles
    h, w = image_paso1.shape[:2]
    comparison = np.zeros((h, w * 3, 3), dtype=np.uint8)
    comparison[:, 0:w] = image_paso1  # Paso 1 original
    comparison[:, w:w*2] = result_a    # Opcion A
    comparison[:, w*2:w*3] = result_b  # Opcion B

    comp_path = OUTPUT_DIR / "comparacion_multi_direcciones.png"
    cv2.imwrite(str(comp_path), comparison)
    print("[OK] Comparacion: {}".format(comp_path.name))

    print("\n[*] Ubicacion: {}".format(OUTPUT_DIR))
    print("[*] Ahora puedes decidir cual te gusta mas")


if __name__ == "__main__":
    main()
