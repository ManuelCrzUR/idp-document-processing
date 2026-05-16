# -*- coding: utf-8 -*-
import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from scipy import ndimage
import sys

class SmartInpainter:
    """Reconstruccion inteligente de fondo sin degradados."""

    def __init__(self, image, mask):
        """
        Args:
            image: Imagen con sello (BGR, uint8)
            mask: Mascara binaria donde 255 = sello, 0 = fondo (uint8)
        """
        self.image = image.astype(np.float32) / 255.0
        self.mask = (mask > 0).astype(np.uint8)
        self.h, self.w = self.image.shape[:2]

    def extract_pure_background(self, margin=0.15):
        """Extrae pixeles de fondo puro (sin sello)."""
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        expanded_mask = cv2.dilate(self.mask, kernel, iterations=2)

        valid_bg = (expanded_mask == 0)
        bg_pixels = self.image[valid_bg]

        return bg_pixels, valid_bg

    def estimate_background_statistics(self):
        """Calcula media y desviacion estandar del fondo."""
        bg_pixels, _ = self.extract_pure_background()

        if len(bg_pixels) < 10:
            print("[!] Advertencia: muy pocos pixeles de fondo puro")
            return None, None

        mean = np.mean(bg_pixels, axis=0)
        std = np.std(bg_pixels, axis=0)

        return mean, std

    def method_statistical_fill(self):
        """Metodo 1: Relleno estadistico - usa distribucion del fondo."""
        print("[*] Aplicando relleno estadistico...")

        mean, std = self.estimate_background_statistics()
        if mean is None:
            return self.image.copy()

        result = self.image.copy()

        num_pixels = np.sum(self.mask)
        synthetic = np.random.normal(mean, std, (int(num_pixels), 3))
        synthetic = np.clip(synthetic, 0, 1)

        result[self.mask == 1] = synthetic

        return result

    def method_nearest_neighbor(self, patch_size=5):
        """Metodo 2: Busqueda de vecino mas cercano (PatchMatch simple)."""
        print("[*] Aplicando nearest neighbor (PatchMatch)...")

        result = self.image.copy()
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        boundary = cv2.dilate(self.mask, kernel, iterations=1) - self.mask

        y_coords, x_coords = np.where(self.mask == 1)

        for i, (y, x) in enumerate(zip(y_coords, x_coords)):
            if i % 1000 == 0:
                print("[*] Procesando: {}/{}".format(i, len(y_coords)))

            y1, y2 = max(0, y - patch_size), min(self.h, y + patch_size + 1)
            x1, x2 = max(0, x - patch_size), min(self.w, x + patch_size + 1)

            seal_patch = self.image[y1:y2, x1:x2]

            best_dist = float('inf')
            best_patch = seal_patch.copy()

            boundary_y, boundary_x = np.where(boundary == 1)

            if len(boundary_y) > 0:
                sample_indices = np.random.choice(len(boundary_y), min(50, len(boundary_y)), replace=False)

                for idx in sample_indices:
                    by, bx = boundary_y[idx], boundary_x[idx]
                    by1, by2 = max(0, by - patch_size), min(self.h, by + patch_size + 1)
                    bx1, bx2 = max(0, bx - patch_size), min(self.w, bx + patch_size + 1)

                    candidate = self.image[by1:by2, bx1:bx2]

                    if candidate.shape == seal_patch.shape:
                        dist = np.mean((seal_patch - candidate) ** 2)
                        if dist < best_dist:
                            best_dist = dist
                            best_patch = candidate.copy()

            result[y, x] = best_patch[patch_size, patch_size] if best_patch.ndim == 3 else best_patch

        print("[*] Completado")
        return result

    def method_morphological_fill(self):
        """Metodo 3: Relleno morfologico - suavizado iterativo."""
        print("[*] Aplicando relleno morfologico...")

        result = self.image.copy()
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

        mask_uint8 = (self.mask * 255).astype(np.uint8)
        result_uint8 = (result * 255).astype(np.uint8)

        inpainted = cv2.inpaint(result_uint8, mask_uint8, 3, cv2.INPAINT_TELEA)

        return inpainted.astype(np.float32) / 255.0

    def method_smooth_blend(self):
        """Metodo 4: Fusion suave - transicion gradual con borde."""
        print("[*] Aplicando fusion suave con bordes...")

        result = self.method_statistical_fill()

        dist_transform = cv2.distanceTransform(1 - self.mask, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
        max_dist = np.max(dist_transform)

        if max_dist > 0:
            fade_mask = np.clip(dist_transform / (max_dist * 0.3), 0, 1)
        else:
            fade_mask = np.ones_like(dist_transform)

        fade_mask = np.dstack([fade_mask] * 3)
        result = result * (1 - fade_mask) + self.image * fade_mask

        result_uint8 = (result * 255).astype(np.uint8)
        result_uint8 = cv2.bilateralFilter(result_uint8, 9, 75, 75)
        result = result_uint8.astype(np.float32) / 255.0

        return result

    def inpaint(self, method='smooth_blend'):
        """
        Ejecuta el metodo de inpainting seleccionado.

        Args:
            method: 'statistical', 'nearest_neighbor', 'morphological', 'smooth_blend'
        """
        if method == 'statistical':
            return self.method_statistical_fill()
        elif method == 'nearest_neighbor':
            return self.method_nearest_neighbor()
        elif method == 'morphological':
            return self.method_morphological_fill()
        elif method == 'smooth_blend':
            return self.method_smooth_blend()
        else:
            raise ValueError("Metodo desconocido: {}".format(method))


def visualize_comparison(image_orig, mask, results_dict, title="Comparacion de Metodos de Inpainting"):
    """Visualiza resultados de multiples metodos."""

    n_methods = len(results_dict) + 1
    fig, axes = plt.subplots(1, n_methods, figsize=(4 * n_methods, 4))

    if n_methods == 1:
        axes = [axes]

    axes[0].imshow(cv2.cvtColor((image_orig * 255).astype(np.uint8), cv2.COLOR_BGR2RGB))
    axes[0].set_title("Original (con sello)", fontsize=10, weight='bold')
    axes[0].axis('off')

    for idx, (method_name, result) in enumerate(results_dict.items(), start=1):
        result_uint8 = (result * 255).astype(np.uint8) if result.dtype == np.float32 else result
        axes[idx].imshow(cv2.cvtColor(result_uint8, cv2.COLOR_BGR2RGB))
        axes[idx].set_title(method_name, fontsize=10, weight='bold')
        axes[idx].axis('off')

    plt.suptitle(title, fontsize=14, weight='bold', y=0.98)
    plt.tight_layout()
    return fig


def main():
    BASE_DIR = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project")
    SYNTHETIC_DIR = BASE_DIR / "datos" / "synthetic_dataset"
    OUTPUT_DIR = BASE_DIR / "datos" / "inpainting_results"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    image_path = list((SYNTHETIC_DIR / "images").glob("*.png"))[0]
    mask_path = SYNTHETIC_DIR / "masks" / "{}_mask.png".format(image_path.stem)

    print("[*] Cargando imagen: {}".format(image_path.name))
    image = cv2.imread(str(image_path))
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)

    if image is None or mask is None:
        print("[!] Error al cargar imagenes")
        return

    inpainter = SmartInpainter(image, mask)

    print("\n[*] Probando metodos de inpainting...")
    results = {}

    methods = ['statistical', 'morphological', 'smooth_blend']

    for method in methods:
        print("\n--- Metodo: {} ---".format(method.upper()))
        inpainted = inpainter.inpaint(method=method)
        results[method.replace('_', ' ').title()] = inpainted

    fig = visualize_comparison(image.astype(np.float32) / 255.0, mask, results)

    result_path = OUTPUT_DIR / "comparison.png"
    plt.savefig(str(result_path), dpi=150, bbox_inches='tight')
    print("\n[OK] Comparacion guardada: {}".format(result_path))

    best_result = results['Smooth Blend']
    best_result_uint8 = (best_result * 255).astype(np.uint8)
    best_path = OUTPUT_DIR / "{}_inpainted_smooth_blend.png".format(image_path.stem)
    cv2.imwrite(str(best_path), best_result_uint8)
    print("[OK] Mejor resultado guardado: {}".format(best_path))

    print("\n[*] Estadisticas del fondo:")
    mean, std = inpainter.estimate_background_statistics()
    if mean is not None:
        print("  - Color medio: B={:.3f}, G={:.3f}, R={:.3f}".format(mean[0], mean[1], mean[2]))
        print("  - Desv. estandar: B={:.3f}, G={:.3f}, R={:.3f}".format(std[0], std[1], std[2]))

    plt.show()


if __name__ == "__main__":
    main()
