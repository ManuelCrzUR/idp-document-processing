# -*- coding: utf-8 -*-
"""
Advanced Inpainter: Mejorado OpenCV Inpainting
Intenta simular resultados LaMa usando técnicas avanzadas de OpenCV
"""
import numpy as np
import cv2
import logging
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(name)s] %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('AdvancedInpainter')


class AdvancedInpainter:
    """Inpainter mejorado que simula características de LaMa sin dependencias complejas"""

    def __init__(self):
        pass

    def inpaint_advanced(self, image_bgr, mask, method='telea'):
        """
        Inpainting avanzado con múltiples técnicas

        Args:
            image_bgr: Imagen en BGR
            mask: Máscara binaria (255 = inpaint, 0 = preserve)
            method: 'telea' (rápido) o 'ns' (lento pero mejor)

        Returns:
            image_inpainted: Imagen procesada
        """
        if method == 'telea':
            # Algoritmo rápido de Telea
            inpainted = cv2.inpaint(image_bgr, mask, 3, cv2.INPAINT_TELEA)
        else:
            # Algoritmo de Navier-Stokes (más lento, mejor calidad)
            inpainted = cv2.inpaint(image_bgr, mask, 5, cv2.INPAINT_NS)

        return inpainted

    def inpaint_multi_scale(self, image_bgr, mask):
        """
        Inpainting multi-escala: procesa en múltiples resoluciones y combina

        Intenta capturar detalles en múltiples escalas (similar a LaMa)
        """
        h, w = image_bgr.shape[:2]

        # Escala 1: Resolución original
        result_full = cv2.inpaint(image_bgr, mask, 5, cv2.INPAINT_NS)

        # Escala 2: Media resolución (más rápido, menos ruido)
        image_half = cv2.resize(image_bgr, (w // 2, h // 2))
        mask_half = cv2.resize(mask, (w // 2, h // 2))
        result_half = cv2.inpaint(image_half, mask_half, 3, cv2.INPAINT_NS)
        result_half = cv2.resize(result_half, (w, h))

        # Combinar: promedio ponderado (full resolution con más peso)
        result_combined = cv2.addWeighted(result_full, 0.7, result_half, 0.3, 0)

        return result_combined

    def inpaint_with_edge_preservation(self, image_bgr, mask, original_edges=None):
        """
        Inpainting con preservación de bordes (similar a LaMa)

        Detecta bordes en la máscara y los preserva mejor
        """
        # Dilatar máscara ligeramente para mejorar transiciones
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_dilated = cv2.dilate(mask, kernel, iterations=1)

        # Inpaint con máscara dilatada
        inpainted = cv2.inpaint(image_bgr, mask_dilated, 5, cv2.INPAINT_NS)

        # Post-procesamiento: suavizar transiciones
        # Aplicar bilateral filter para mantener bordes nítidos
        inpainted = cv2.bilateralFilter(inpainted, 9, 75, 75)

        return inpainted

    def inpaint_iterative(self, image_bgr, mask, iterations=2):
        """
        Inpainting iterativo: varias pasadas para mejor calidad

        Similar a técnicas multi-pass de LaMa
        """
        result = image_bgr.copy()
        current_mask = mask.copy()

        for i in range(iterations):
            # Inpaint
            result = cv2.inpaint(result, current_mask, 5, cv2.INPAINT_NS)

            # Dilatar máscara progresivamente para siguiente iteración
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            current_mask = cv2.dilate(current_mask, kernel, iterations=1)

            # Reducir intensidad de máscara para siguiente iteración (menos agresivo)
            current_mask = cv2.inpaint(current_mask, mask, 1, cv2.INPAINT_TELEA)

        return result


class LamaInpainterWrapper:
    """Wrapper que intenta usar LaMa si está disponible, fallback a Advanced"""

    def __init__(self, debug=False):
        self.use_lama = False
        self.lama_model = None
        self.debug = debug
        self.source_used = None  # Rastrea si se usó LaMa o fallback
        self.advanced = AdvancedInpainter()

        logger.info("=" * 80)
        logger.info("INICIALIZANDO LamaInpainterWrapper")
        logger.info("=" * 80)

        # Intentar cargar LaMa
        try:
            logger.info("Buscando checkpoint de LaMa...")
            from lama_cleaner.model.base import InpaintModel

            # Verificar rutas de checkpoint
            checkpoint_paths = [
                Path.home() / '.cache/hub/lama',
                Path.home() / '.cache/lama',
                Path('/tmp/lama_checkpoints'),
                Path('lama_checkpoints'),
            ]

            logger.info(f"Rutas de checkpoint a buscar:")
            for path in checkpoint_paths:
                logger.info(f"  - {path.resolve()}")

            logger.info("Inicializando modelo LaMa desde lama_cleaner...")
            self.lama_model = InpaintModel.init_model(
                'lama',
                'cpu',  # Usar CPU para compatibilidad
                disable_nsfw=True
            )
            self.use_lama = True
            logger.info("[OK] EXITO: LaMa inpainter cargado exitosamente")
            logger.info("=" * 80)

        except ImportError as e:
            logger.error("[FAIL] ImportError: modulo lama_cleaner no instalado")
            logger.error(f"  Detalle: {str(e)}")
            logger.error("  Solucion: pip install lama-cleaner")
            self.use_lama = False

        except FileNotFoundError as e:
            logger.error("[FAIL] FileNotFoundError: checkpoint de LaMa no encontrado")
            logger.error(f"  Detalle: {str(e)}")
            logger.error("  Solucion: Descargar checkpoint manualmente o permitir descarga")
            self.use_lama = False

        except Exception as e:
            logger.error("[FAIL] FALLO CRITICO al cargar LaMa")
            logger.error(f"  Tipo de error: {type(e).__name__}")
            logger.error(f"  Detalle completo: {str(e)}")
            logger.error("  Stack trace:")
            import traceback
            for line in traceback.format_exc().split('\n'):
                if line:
                    logger.error(f"    {line}")
            self.use_lama = False

        if not self.use_lama:
            logger.warning("[WARN] Usando Advanced OpenCV Inpainting como fallback")
            logger.info("=" * 80)

    def inpaint(self, image_bgr, mask):
        """
        Inpaint: usa LaMa si está disponible, fallback a Advanced

        Args:
            image_bgr: Imagen en formato BGR (uint8, [0, 255])
            mask: Máscara binaria (uint8, 0 o 255)

        Returns:
            image_inpainted: Imagen inpaintada en BGR (uint8, [0, 255])
        """

        # Validar inputs
        logger.info("-" * 80)
        logger.info("INPAINTING REQUEST")
        logger.info(f"  Image shape: {image_bgr.shape}, dtype: {image_bgr.dtype}, "
                   f"range: [{image_bgr.min()}, {image_bgr.max()}]")
        logger.info(f"  Mask shape: {mask.shape}, dtype: {mask.dtype}, "
                   f"unique values: {np.unique(mask)}")

        if self.debug:
            debug_dir = Path("debug_inpainting")
            debug_dir.mkdir(exist_ok=True)

            # Guardar imagen original
            debug_img_path = debug_dir / "01_image_bgr_input.png"
            cv2.imwrite(str(debug_img_path), image_bgr)
            logger.info(f"  DEBUG GUARDADO: {debug_img_path.resolve()}")

            # Guardar máscara original
            debug_mask_path = debug_dir / "02_mask_input.png"
            cv2.imwrite(str(debug_mask_path), mask)
            logger.info(f"  DEBUG GUARDADO: {debug_mask_path.resolve()}")

        if self.use_lama:
            try:
                logger.info("INTENTANDO: LaMa inpainting...")

                # Convertir BGR a RGB
                image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
                logger.info(f"  Convertido a RGB: shape={image_rgb.shape}, dtype={image_rgb.dtype}")

                # Convertir a float32 [0, 1]
                image_float = image_rgb.astype(np.float32) / 255.0
                logger.info(f"  Convertido a float32 [0,1]: "
                           f"dtype={image_float.dtype}, range=[{image_float.min():.3f}, {image_float.max():.3f}]")

                # Validar máscara
                unique_mask = np.unique(mask)
                logger.info(f"  Máscara valores únicos: {unique_mask}")

                if not set(unique_mask).issubset({0, 255}):
                    logger.warning(f"  [WARN] Mascara contiene valores invalidos: {unique_mask}")
                    logger.warning(f"  Normalizando mascara a [0, 255]...")
                    mask = np.where(mask > 127, 255, 0).astype(np.uint8)
                    logger.info(f"  Mascara normalizada: {np.unique(mask)}")

                if self.debug:
                    # Guardar formato que se pasa a LaMa
                    debug_dir = Path("debug_inpainting")

                    # RGB float32 [0, 1]
                    debug_float_path = debug_dir / "03_image_rgb_float32.npy"
                    np.save(str(debug_float_path), image_float)
                    logger.info(f"  DEBUG GUARDADO: {debug_float_path.resolve()}")

                    # Máscara uint8
                    debug_mask_uint8_path = debug_dir / "04_mask_uint8.png"
                    cv2.imwrite(str(debug_mask_uint8_path), mask)
                    logger.info(f"  DEBUG GUARDADO: {debug_mask_uint8_path.resolve()}")

                logger.info("  Llamando modelo LaMa...")
                result_rgb_float = self.lama_model(image_float, mask)
                logger.info(f"  LaMa retornó: dtype={result_rgb_float.dtype}, "
                           f"shape={result_rgb_float.shape}, "
                           f"range=[{result_rgb_float.min():.3f}, {result_rgb_float.max():.3f}]")

                # Convertir de vuelta a uint8 [0, 255]
                result_rgb_uint8 = (result_rgb_float * 255).astype(np.uint8)
                logger.info(f"  Convertido a uint8 [0,255]: range=[{result_rgb_uint8.min()}, {result_rgb_uint8.max()}]")

                # Convertir RGB a BGR
                result_bgr = cv2.cvtColor(result_rgb_uint8, cv2.COLOR_RGB2BGR)
                logger.info(f"  Convertido a BGR: {result_bgr.shape}")

                if self.debug:
                    debug_result_path = debug_dir / "05_result_bgr_final.png"
                    cv2.imwrite(str(debug_result_path), result_bgr)
                    logger.info(f"  DEBUG GUARDADO: {debug_result_path.resolve()}")

                self.source_used = "LaMa"
                logger.info("[OK] EXITO: LaMa inpainting completado exitosamente")
                logger.info("-" * 80)
                return result_bgr

            except Exception as e:
                logger.error("[FAIL] LaMa inpainting fallo")
                logger.error(f"  Tipo de error: {type(e).__name__}")
                logger.error(f"  Detalle: {str(e)}")
                logger.error("  Stack trace:")
                import traceback
                for line in traceback.format_exc().split('\n'):
                    if line:
                        logger.error(f"    {line}")
                logger.warning("  Usando fallback: Advanced OpenCV Inpainting")

        else:
            logger.info("SKIPPED: LaMa no está disponible")
            logger.warning("  Usando fallback: Advanced OpenCV Inpainting")

        # Fallback: Advanced OpenCV
        logger.info("INTENTANDO: Advanced OpenCV inpainting (iterative)...")
        result = self.advanced.inpaint_iterative(image_bgr, mask, iterations=2)
        self.source_used = "OpenCV (fallback)"
        logger.info("[OK] EXITO: OpenCV inpainting completado")
        logger.info(f"RESULTADO FINAL: {self.source_used}")
        logger.info("-" * 80)
        return result
