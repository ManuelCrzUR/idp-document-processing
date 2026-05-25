# -*- coding: utf-8 -*-
"""
Wrapper de inpainting con LaMa o fallback a OpenCV.

Intenta usar simple-lama-inpainting si está disponible.
Si no, usa cv2.inpaint como fallback (menos calidad pero funcional).
"""
import numpy as np
from PIL import Image

try:
    from simple_lama_inpainting import SimpleLama
    LAMA_AVAILABLE = True
except ImportError:
    LAMA_AVAILABLE = False
    print("[WARN] LaMa no disponible. Usando fallback con OpenCV.")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("[WARN] OpenCV no disponible. Inpainting deshabilitado.")


class LamaInpainter:
    """Wrapper de inpainting con prioridad LaMa → fallback OpenCV"""

    def __init__(self):
        self.use_lama = LAMA_AVAILABLE
        self.use_opencv = OPENCV_AVAILABLE

        if self.use_lama:
            try:
                self.lama_model = SimpleLama()
                print("[OK] LaMa cargado exitosamente")
            except Exception as e:
                print(f"[WARN] Error cargando LaMa: {e}. Usando fallback OpenCV.")
                self.use_lama = False
        else:
            if self.use_opencv:
                print("[OK] Usando fallback con OpenCV inpainting")
            else:
                print("[ERROR] Ni LaMa ni OpenCV disponibles!")

    def inpaint(self, image_bgr: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Reconstruye región enmascarada.

        Args:
            image_bgr: Imagen en BGR uint8 (H, W, 3)
            mask: Máscara uint8 (H, W) con 0 (preservar) y 255 (reconstruir)

        Returns:
            image_bgr: Imagen reconstruida en BGR uint8
        """
        if not (self.use_lama or self.use_opencv):
            print("[ERROR] Inpainting no disponible!")
            return image_bgr

        if self.use_lama:
            return self._inpaint_lama(image_bgr, mask)
        else:
            return self._inpaint_opencv(image_bgr, mask)

    def _inpaint_lama(self, image_bgr: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Inpainting con LaMa"""
        # BGR → RGB → PIL
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)

        # máscara → PIL (modo L para LaMa)
        mask_pil = Image.fromarray(mask, mode='L')

        # Aplicar LaMa
        result_pil = self.lama_model(image_pil, mask_pil)

        # PIL → RGB → BGR
        result_rgb = np.array(result_pil, dtype=np.uint8)
        result_bgr = cv2.cvtColor(result_rgb, cv2.COLOR_RGB2BGR)

        return result_bgr

    def _inpaint_opencv(self, image_bgr: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Inpainting con OpenCV (fallback)"""
        if not OPENCV_AVAILABLE:
            return image_bgr

        # cv2.inpaint requiere máscara con 255 en la región a reconstruir
        result = cv2.inpaint(image_bgr, mask, 3, cv2.INPAINT_TELEA)
        return result


if __name__ == "__main__":
    print("\n[TEST] Inicializando LamaInpainter...\n")

    inpainter = LamaInpainter()

    # Crear imagen de prueba simple
    test_image = np.ones((100, 100, 3), dtype=np.uint8) * 200  # gris claro
    test_mask = np.zeros((100, 100), dtype=np.uint8)
    test_mask[30:70, 30:70] = 255  # cuadrado central a reconstruir

    print(f"Imagen de prueba: {test_image.shape}, dtype: {test_image.dtype}")
    print(f"Máscara de prueba: {test_mask.shape}, dtype: {test_mask.dtype}")

    result = inpainter.inpaint(test_image, test_mask)

    print(f"Resultado: {result.shape}, dtype: {result.dtype}")
    print("[OK] Inpainting completado")
