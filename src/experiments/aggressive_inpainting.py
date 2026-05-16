# -*- coding: utf-8 -*-
import cv2
import numpy as np
from pathlib import Path

class AggressiveInpainter:
    """Inpainting agresivo: relleno preciso basado en color dominante de vecinos."""

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

    def analyze_neighbor_color_horizontal(self, y, x, radius=15):
        """
        Analiza el color dominante SOLO en eje X (izquierda y derecha).
        Ignora vecinos arriba/abajo para mantener estructura horizontal del documento.
        Retorna: 'blanco', 'negro', o 'mixto'
        """
        white_count = 0
        black_count = 0
        total_count = 0

        # SOLO analizar horizontalmente (eje X)
        for dx in range(-radius, radius + 1, 2):
            nx = x + dx

            if 0 <= nx < self.w and self.mask[y, nx] == 0:
                # Convertir a escala de grises
                pixel = self.image[y, nx]
                gray = np.mean(pixel).astype(int)

                if gray > 200:  # Blanco
                    white_count += 1
                elif gray < 80:  # Negro
                    black_count += 1

                total_count += 1

        if total_count == 0:
            return 'mixto'

        white_ratio = white_count / total_count
        black_ratio = black_count / total_count

        if white_ratio > 0.6:
            return 'blanco'
        elif black_ratio > 0.6:
            return 'negro'
        else:
            return 'mixto'

    def aggressive_fill_by_dominant_color(self):
        """
        Rellena cada pixel con SOLO blanco o negro puro (SIN GRISES).
        Analiza SOLO horizontalmente (eje X) para respetar estructura del documento.
        Si vecinos horizontales son blancos -> rellena con BLANCO PURO (255, 255, 255)
        Si vecinos horizontales son negros -> rellena con NEGRO PURO (0, 0, 0)
        """
        print("[*] Aplicando relleno BINARIO HORIZONTAL (sin grises, eje X)...")

        result = self.image.copy().astype(np.uint8)

        y_coords, x_coords = np.where(self.mask == 1)

        for y, x in zip(y_coords, x_coords):
            # Analizar SOLO vecinos horizontales (eje X)
            dominant_color = self.analyze_neighbor_color_horizontal(y, x, radius=15)

            # DECISION BINARIA: Blanco o Negro puro, NUNCA gris
            if dominant_color == 'blanco':
                result[y, x] = [255, 255, 255]  # BLANCO PURO
            elif dominant_color == 'negro':
                result[y, x] = [0, 0, 0]  # NEGRO PURO
            else:
                # Si es mixto, mirar mas lejos horizontalmente
                white_count = 0
                black_count = 0

                for dx in range(-25, 26, 2):
                    nx = x + dx

                    if 0 <= nx < self.w and self.mask[y, nx] == 0:
                        pixel = self.image[y, nx]
                        gray = np.mean(pixel).astype(int)

                        if gray > 200:
                            white_count += 1
                        elif gray < 80:
                            black_count += 1

                # Elegir el color mas dominante a nivel de fila
                if white_count > black_count:
                    result[y, x] = [255, 255, 255]
                else:
                    result[y, x] = [0, 0, 0]

        return result

    def fine_edge_refinement(self, image_after_fill):
        """
        Sin refinamiento gris - mantener completamente BINARIO.
        Solo asegurar que los bordes sean nítidos.
        """
        print("[*] Manteniendo valores BINARIOS (sin grises)...")

        # No introducir valores grises, mantener imagen tal como está
        return image_after_fill.astype(np.float32) / 255.0

    def sharp_edge_preservation(self, image_uint8):
        """
        Preserva bordes nítidos usando bilateral filter con parametros agresivos.
        """
        print("[*] Preservando bordes nitidos...")

        # Bilateral filter mantiene bordes pero suaviza areas planas
        sharpened = cv2.bilateralFilter(image_uint8, d=5, sigmaColor=30, sigmaSpace=30)

        return sharpened

    def inpaint_aggressive(self):
        """Ejecuta el pipeline agresivo completo."""
        print("\n" + "="*60)
        print("INPAINTING AGRESIVO (Color Dominante + Precision)")
        print("="*60)

        # Paso 1: Relleno agresivo por color dominante
        filled = self.aggressive_fill_by_dominant_color()

        # Paso 2: Refinamiento fino en bordes
        refined = self.fine_edge_refinement(filled)
        refined_uint8 = (refined * 255).astype(np.uint8)

        # Paso 3: Preservar bordes nitidos
        final = self.sharp_edge_preservation(refined_uint8)

        print("[OK] Inpainting agresivo completado")
        print("="*60)

        return final


def main():
    BASE_DIR = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project")
    SYNTHETIC_DIR = BASE_DIR / "datos" / "synthetic_dataset"
    OUTPUT_DIR = BASE_DIR / "datos" / "aggressive_inpainting_results"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Cargar imagen sintetica
    image_path = list((SYNTHETIC_DIR / "images").glob("*.png"))[0]
    mask_path = SYNTHETIC_DIR / "masks" / "{}_mask.png".format(image_path.stem)

    print("[*] Cargando imagen: {}".format(image_path.name))
    image = cv2.imread(str(image_path))
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)

    if image is None or mask is None:
        print("[!] Error cargando imagenes")
        return

    # Crear inpainter agresivo
    inpainter = AggressiveInpainter(image, mask)

    # Ejecutar inpainting agresivo
    result = inpainter.inpaint_aggressive()

    # Guardar resultados
    result_path = OUTPUT_DIR / "{}_aggressive_inpainting.png".format(image_path.stem)
    cv2.imwrite(str(result_path), result, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    print("[OK] Resultado guardado: {}".format(result_path))

    # Crear comparacion
    h, w = image.shape[:2]
    comparison = np.zeros((h, w * 2, 3), dtype=np.uint8)
    comparison[:, 0:w] = image
    comparison[:, w:w*2] = result

    comparison_path = OUTPUT_DIR / "aggressive_comparison.png"
    cv2.imwrite(str(comparison_path), comparison)
    print("[OK] Comparacion guardada: {}".format(comparison_path))

    print("\n[*] Ubicacion: {}".format(OUTPUT_DIR))


if __name__ == "__main__":
    main()
