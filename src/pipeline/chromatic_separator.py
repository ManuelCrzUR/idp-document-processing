# -*- coding: utf-8 -*-
"""
Separación cromática: clasifica píxeles en TEXTO, SELLO, MIXTO.

Usa intensidad (brillo) + dominancia (saturación RGB) para refinar la máscara.
Aplica inpainting SOLO en la zona del sello detectado.
"""
import numpy as np
from pathlib import Path


class ChromaticSeparator:
    """Clasifica píxeles del sello en 5 categorías para inpainting selectivo (incluye translúcidos)"""

    def __init__(self, text_intensity_threshold=30, text_dominance_threshold=30,
                 stamp_dominance_threshold=30, background_intensity_threshold=200,
                 translucent_intensity_low=80, translucent_white_threshold=240,
                 translucent_dominance_low=15, translucent_dominance_high=80):
        """
        Args:
            text_intensity_threshold: Máx brillo para considerar píxel como texto PURO (default 30)
            text_dominance_threshold: Máx dominancia para considerar píxel como texto (default 30)
            stamp_dominance_threshold: Mín dominancia para considerar píxel como sello saturado (default 30)
            background_intensity_threshold: Mín brillo para considerar píxel como fondo/papel (default 200)
            translucent_intensity_low: Mín intensidad para sello translúcido (default 80, no es texto oscuro)
            translucent_white_threshold: Máx valor RGB para sello translúcido (default 240, no es blanco puro)
            translucent_dominance_low: Mín dominancia para sello translúcido (default 15, tinte visible)
            translucent_dominance_high: Máx dominancia para sello translúcido (default 80, no saturado)
        """
        self.text_intensity_th = text_intensity_threshold
        self.text_dominance_th = text_dominance_threshold
        self.stamp_dominance_th = stamp_dominance_threshold
        self.background_intensity_th = background_intensity_threshold
        self.translucent_intensity_low = translucent_intensity_low
        self.translucent_white_th = translucent_white_threshold
        self.translucent_dominance_low = translucent_dominance_low
        self.translucent_dominance_high = translucent_dominance_high

    def classify_pixels(self, roi_bgr):
        """
        Clasifica píxeles del ROI en 5 categorías (incluye sellos translúcidos).

        Lógica:
        - TEXTO (0): mean < intensity_low AND dominance < dominance_low → negro puro, preservar
        - FONDO (3): max > white_threshold → blanco/papel, preservar
        - SELLO TRANSLUCIDO (4): mean >= intensity_low AND max < white_threshold AND dominance_low <= dominance < dominance_high
        - SELLO (1): dominance >= dominance_high → color saturado, reconstruir
        - MIXTO (2): resto → sombras/bordes, inpaint

        Args:
            roi_bgr: Región del sello en BGR uint8 (H, W, 3)

        Returns:
            pixel_map: np.ndarray uint8 (H, W) con valores {0, 1, 2, 3, 4}
            Donde: 0=TEXTO, 1=SELLO_SATURADO, 2=MIXTO, 3=FONDO, 4=SELLO_TRANSLUCIDO
        """
        if roi_bgr.size == 0 or len(roi_bgr.shape) != 3:
            return np.zeros(roi_bgr.shape[:2], dtype=np.uint8)

        # Convertir a float para cálculos
        roi_float = roi_bgr.astype(np.float32)

        # Calcular intensidad = (R + G + B) / 3
        intensidad = (roi_float[:, :, 0] + roi_float[:, :, 1] + roi_float[:, :, 2]) / 3.0

        # Calcular dominancia = max(R, G, B) - min(R, G, B)
        r, g, b = roi_float[:, :, 0], roi_float[:, :, 1], roi_float[:, :, 2]
        max_channel = np.maximum(np.maximum(r, g), b)
        min_channel = np.minimum(np.minimum(r, g), b)
        dominancia = max_channel - min_channel

        # Clasificar píxeles
        pixel_map = np.ones(roi_bgr.shape[:2], dtype=np.uint8) * 2  # Inicializar como MIXTO

        # TEXTO: mean < intensity_low AND dominance < dominance_low (negro puro)
        es_texto = (dominancia < self.translucent_dominance_low) & (intensidad < self.translucent_intensity_low)
        pixel_map[es_texto] = 0

        # FONDO: max > white_threshold (blanco/papel puro)
        es_fondo = max_channel > self.translucent_white_th
        pixel_map[es_fondo] = 3

        # SELLO TRANSLUCIDO: mean >= intensity_low AND max < white_threshold AND dominance_low <= dom < dominance_high
        es_translucido = (
            (intensidad >= self.translucent_intensity_low) &
            (max_channel < self.translucent_white_th) &
            (dominancia >= self.translucent_dominance_low) &
            (dominancia < self.translucent_dominance_high)
        )
        pixel_map[es_translucido] = 4

        # SELLO SATURADO: dominance >= dominance_high (color saturado)
        es_sello = dominancia >= self.translucent_dominance_high
        pixel_map[es_sello] = 1

        # MIXTO: el resto (transiciones, bordes con color débil, sombras)
        return pixel_map

    def apply_progressive_filter(self, pixel_map, window_sizes=[21, 11, 5, 3]):
        """
        Aplica filtro de vecindad progresivamente de grueso a fino.

        Estrategia coarse-to-fine:
        - Pasada 1 (21x21): Detecta TEXTO lejano, reemplaza grandes áreas
        - Pasada 2 (11x11): Refina bordes
        - Pasada 3 (5x5): Detalles medios
        - Pasada 4 (3x3): Precisión máxima (1px de vecindad)

        Args:
            pixel_map: Mapa de clasificación inicial (H, W)
            window_sizes: Lista de tamaños de ventana para cada pasada

        Returns:
            list: [pixel_map_original, mapa_pasada1, mapa_pasada2, ..., mapa_final]
        """
        results = [pixel_map.copy()]  # Guardar estado original

        pixel_map_current = pixel_map.copy()

        for window_size in window_sizes:
            pixel_map_current = self.apply_neighborhood_filter(pixel_map_current, window_size=window_size)
            results.append(pixel_map_current.copy())

        return results

    def apply_neighborhood_filter(self, pixel_map, window_size=5):
        """
        Filtra píxeles SELLO/MIXTO sin TEXTO cercano (reclasifica como FONDO).

        Lógica:
        - Para cada píxel SELLO (1) o MIXTO (2)
        - Revisar ventana de window_size x window_size centrada en ese píxel
        - Si NO hay ningún píxel TEXTO (0) en la ventana
        - Reclasificar píxel a FONDO (3) para preservarlo sin inpaint

        Args:
            pixel_map: Mapa de clasificación (H, W) con valores {0,1,2,3}
            window_size: Tamaño de ventana (default 5x5, debe ser impar)

        Returns:
            pixel_map_filtered: Mapa con píxeles reclasificados según vecindad
        """
        h, w = pixel_map.shape
        pixel_map_filtered = pixel_map.copy()

        half_win = window_size // 2

        for y in range(h):
            for x in range(w):
                # Solo revisar píxeles SELLO (1), MIXTO (2) o SELLO_TRANSLUCIDO (4)
                if pixel_map[y, x] in [1, 2, 4]:
                    # Definir ventana con límites seguros
                    y1 = max(0, y - half_win)
                    y2 = min(h, y + half_win + 1)
                    x1 = max(0, x - half_win)
                    x2 = min(w, x + half_win + 1)

                    # Revisar si hay TEXTO en la ventana
                    ventana = pixel_map[y1:y2, x1:x2]
                    tiene_texto = np.any(ventana == 0)

                    # Si NO hay texto cercano, convertir a FONDO
                    if not tiene_texto:
                        pixel_map_filtered[y, x] = 3

        return pixel_map_filtered

    def extract_stamp_roi(self, image_bgr, bbox_yolo):
        """Extrae región del sello usando bbox YOLO normalizado"""
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

        return image_bgr[y1:y2, x1:x2], (x1, y1, x2, y2)

    def build_refined_mask_in_roi(self, image_bgr, bbox_yolo):
        """
        Construye máscara refinada SOLO en región del sello.

        Solo reconstruye píxeles SELLO (dominancia alta).
        Preserva TEXTO, FONDO y MIXTO.

        Args:
            image_bgr: Imagen original BGR uint8
            bbox_yolo: Bounding box normalizado (xc, yc, w, h)

        Returns:
            refined_mask: Máscara refinada (H, W) uint8 con {0, 255}
            roi_coords: Tupla (x1, y1, x2, y2) de la región del sello
            pixel_map: Mapa de clasificación de píxeles en ROI
        """
        h, w = image_bgr.shape[:2]
        refined_mask = np.zeros((h, w), dtype=np.uint8)

        # Extraer ROI
        roi_bgr, (x1, y1, x2, y2) = self.extract_stamp_roi(image_bgr, bbox_yolo)

        # Clasificar píxeles en ROI
        pixel_map = self.classify_pixels(roi_bgr)

        # Aplicar filtro de vecindad: reclasificar SELLO/MIXTO sin TEXTO cercano como FONDO
        pixel_map = self.apply_neighborhood_filter(pixel_map, window_size=5)

        # Construir máscara refinada SOLO en región del sello
        # Activar (255) donde pixel_map = SELLO (1), MIXTO (2) o SELLO_TRANSLUCIDO (4)
        # Desactivar (0) donde pixel_map = TEXTO (0) o FONDO (3)
        roi_height = y2 - y1
        roi_width = x2 - x1

        for yi in range(roi_height):
            for xi in range(roi_width):
                if pixel_map[yi, xi] in [1, 2, 4]:  # SELLO, MIXTO, SELLO_TRANSLUCIDO
                    refined_mask[y1 + yi, x1 + xi] = 255

        return refined_mask, (x1, y1, x2, y2), pixel_map

    def apply_horizontal_sweep_filter(self, pixel_map, roi_coords):
        """
        Aplica filtro de barrido horizontal por fila.

        Para cada fila dentro del ROI:
        - Si hay al menos 1 píxel TEXTO (0) en esa fila → mantener la fila
        - Si NO hay píxel TEXTO en esa fila → convertir SELLO/MIXTO/TRANSLUCIDO a FONDO

        Esto asegura que la máscara de inpainting solo contiene filas donde
        el sello realmente intersecta con texto.

        Args:
            pixel_map: Mapa de clasificación (H_roi, W_roi) con valores {0,1,2,3,4}
            roi_coords: Tupla (x1, y1, x2, y2) del ROI en coordenadas de imagen global

        Returns:
            pixel_map_filtered: Mapa con filas sin texto reclasificadas como FONDO
        """
        pixel_map_filtered = pixel_map.copy()
        h_roi, w_roi = pixel_map.shape

        # Para cada fila en el ROI
        for row in range(h_roi):
            # Verificar si hay al menos 1 píxel de TEXTO en esta fila
            tiene_texto = np.any(pixel_map[row, :] == 0)

            # Si NO hay texto en la fila, convertir SELLO/MIXTO/TRANSLUCIDO a FONDO
            if not tiene_texto:
                # Convertir píxeles 1 (SELLO), 2 (MIXTO), 4 (TRANSLUCIDO) a 3 (FONDO)
                mask = pixel_map_filtered[row, :] != 0  # No es TEXTO
                mask = mask & (pixel_map_filtered[row, :] != 3)  # No es FONDO
                pixel_map_filtered[row, mask] = 3

        return pixel_map_filtered

    def apply_block_sweep_filter(self, pixel_map, block_size=20, min_text_pixels_per_block=1):
        """
        Aplica filtro de barrido por bloques como paso adicional.

        Divide el ROI en bloques y elimina bloques sin suficiente texto.

        Algoritmo:
        1. Dividir pixel_map en bloques de block_size x block_size
        2. Para cada bloque:
           - Contar píxeles TEXTO (categoría 0)
           - Si count < min_text_pixels_per_block → convertir SELLO/MIXTO/TRANS a FONDO
           - Si count >= min_text_pixels_per_block → mantener bloque
        3. Retornar pixel_map optimizado + info de bloques para visualización

        Args:
            pixel_map: Mapa de clasificación (H, W) con valores {0,1,2,3,4}
            block_size: Tamaño de bloque en píxeles (default 20)
            min_text_pixels_per_block: Mínimo píxeles de texto para mantener bloque (default 1)

        Returns:
            dict con:
            - pixel_map_filtered: Mapa optimizado
            - blocks_info: Lista de info sobre cada bloque (para debugging/visualización)
            - grid_overlay: Imagen de overlay con grid coloreado
        """
        pixel_map_filtered = pixel_map.copy()
        h, w = pixel_map.shape

        blocks_info = []
        grid_overlay = np.ones((h, w, 3), dtype=np.uint8) * 255  # Blanco por defecto

        # Iterar sobre bloques
        for block_y in range(0, h, block_size):
            for block_x in range(0, w, block_size):
                # Límites del bloque
                y1 = block_y
                y2 = min(block_y + block_size, h)
                x1 = block_x
                x2 = min(block_x + block_size, w)

                # Extraer bloque
                block = pixel_map[y1:y2, x1:x2]

                # Contar píxeles de TEXTO (0) en el bloque
                text_count = np.sum(block == 0)

                # Información del bloque
                block_info = {
                    'y1': y1, 'y2': y2, 'x1': x1, 'x2': x2,
                    'text_pixels': int(text_count),
                    'total_pixels': block.size,
                    'has_sufficient_text': text_count >= min_text_pixels_per_block
                }
                blocks_info.append(block_info)

                # Si NO hay suficiente texto en el bloque, convertir SELLO/MIXTO/TRANS a FONDO
                if text_count < min_text_pixels_per_block:
                    # Convertir píxeles 1, 2, 4 a 3 en este bloque
                    mask = (pixel_map_filtered[y1:y2, x1:x2] != 0) & \
                           (pixel_map_filtered[y1:y2, x1:x2] != 3)
                    pixel_map_filtered[y1:y2, x1:x2][mask] = 3

                    # Grid overlay: rojo para bloques limpiados
                    grid_overlay[y1:y2, x1:x2] = [0, 0, 255]  # Rojo en BGR
                else:
                    # Grid overlay: verde para bloques mantenidos
                    grid_overlay[y1:y2, x1:x2] = [0, 255, 0]  # Verde en BGR

                # Dibujar borde del bloque en negro para visualización
                if y1 > 0:
                    grid_overlay[y1, x1:x2] = [0, 0, 0]
                if x1 > 0:
                    grid_overlay[y1:y2, x1] = [0, 0, 0]

        return {
            'pixel_map_filtered': pixel_map_filtered,
            'blocks_info': blocks_info,
            'grid_overlay': grid_overlay
        }

    def create_block_grid_overlay(self, pixel_map, blocks_info, block_size=20):
        """
        Crea una imagen de overlay mostrando la decisión de cada bloque.

        Colores:
        - Rojo (255, 0, 0): Bloque limpiado (sin suficiente texto)
        - Verde (0, 255, 0): Bloque mantenido (con texto)
        - Negro: Bordes del grid

        Args:
            pixel_map: Mapa original
            blocks_info: Lista de info de bloques (del apply_block_sweep_filter)
            block_size: Tamaño de bloque

        Returns:
            grid_overlay: Imagen uint8 (H, W, 3) BGR
        """
        h, w = pixel_map.shape
        grid_overlay = np.ones((h, w, 3), dtype=np.uint8) * 255

        for block_info in blocks_info:
            y1, y2, x1, x2 = block_info['y1'], block_info['y2'], \
                             block_info['x1'], block_info['x2']

            # Color basado en decisión
            if block_info['has_sufficient_text']:
                # Verde para bloques mantenidos
                color = [0, 255, 0]
            else:
                # Rojo para bloques limpiados
                color = [0, 0, 255]

            # Rellenar bloque
            grid_overlay[y1:y2, x1:x2] = color

            # Dibujar bordes en negro
            if y1 > 0:
                grid_overlay[y1, x1:x2] = [0, 0, 0]
            if x1 > 0:
                grid_overlay[y1:y2, x1] = [0, 0, 0]
            if y2 < h:
                grid_overlay[y2-1, x1:x2] = [0, 0, 0]
            if x2 < w:
                grid_overlay[y1:y2, x2-1] = [0, 0, 0]

        return grid_overlay

    def clean_residuals(self, image_bgr, bbox_yolo, pixel_map, residue_dominance_threshold=40):
        """
        Limpia residuos de color (dominancia) que quedan después del inpainting.

        En áreas donde NO hay texto, reemplaza píxeles con color residual
        (dominancia > threshold) con blanco para un resultado más limpio.

        Lógica:
        - Dentro del bbox del sello
        - Donde pixel_map != TEXTO (0)
        - Si dominancia > residue_dominance_threshold
        - Reemplazar con blanco (255, 255, 255)

        Args:
            image_bgr: Imagen inpaintada en BGR uint8
            bbox_yolo: Bounding box normalizado del sello
            pixel_map: Mapa de clasificación original (TEXTO, FONDO, SELLO, MIXTO)
            residue_dominance_threshold: Mínima dominancia para considerar "residuo"
                                        Valores típicos: 30-50
                                        Menor = más agresivo limpiando

        Returns:
            image_cleaned: Imagen con residuos removidos (reemplazados con blanco)
        """
        h, w = image_bgr.shape[:2]
        image_cleaned = image_bgr.copy()

        # Extraer ROI
        roi_bgr, (x1, y1, x2, y2) = self.extract_stamp_roi(image_bgr, bbox_yolo)

        # Calcular dominancia en ROI
        roi_float = roi_bgr.astype(np.float32)
        r, g, b = roi_float[:, :, 0], roi_float[:, :, 1], roi_float[:, :, 2]
        max_channel = np.maximum(np.maximum(r, g), b)
        min_channel = np.minimum(np.minimum(r, g), b)
        dominancia = max_channel - min_channel

        # Detectar residuos: dominancia alta fuera de TEXTO
        # pixel_map: 0=TEXTO, 1=SELLO, 2=MIXTO, 3=FONDO
        roi_height, roi_width = pixel_map.shape

        for yi in range(roi_height):
            for xi in range(roi_width):
                # Si NO es TEXTO (0) ni FONDO (3) y tiene dominancia residual
                if (pixel_map[yi, xi] not in [0, 3] and dominancia[yi, xi] > residue_dominance_threshold):
                    # Reemplazar con blanco (255 en BGR)
                    image_cleaned[y1 + yi, x1 + xi] = [255, 255, 255]

        return image_cleaned

    def process_roi_only(self, image_bgr, bbox_yolo, inpainter, clean_residuals_flag=True,
                         residue_threshold=40):
        """
        Pipeline completo: separación cromática + inpainting + limpieza de residuos.

        Pasos:
        1. Clasificar píxeles en 4 categorías (TEXTO, FONDO, SELLO, MIXTO)
        2. Aplicar inpainting solo en píxeles SELLO
        3. (Opcional) Limpiar residuos de color fuera del texto

        Args:
            image_bgr: Imagen original BGR uint8
            bbox_yolo: Bounding box normalizado
            inpainter: Instancia de LamaInpainter
            clean_residuals_flag: Si True, limpia residuos de color después de inpaint
            residue_threshold: Dominancia mínima para considerar "residuo"

        Returns:
            (image_result, refined_mask, roi_coords, pixel_map):
            Imagen reconstruida + máscara + coords + clasificación
        """
        # Construir máscara refinada
        refined_mask, roi_coords, pixel_map = self.build_refined_mask_in_roi(image_bgr, bbox_yolo)

        # Aplicar inpainting SOLO en la región del sello
        image_result = image_bgr.copy()

        x1, y1, x2, y2 = roi_coords
        roi_bgr = image_bgr[y1:y2, x1:x2]
        roi_mask = refined_mask[y1:y2, x1:x2]

        # Aplicar inpainting solo al ROI
        if np.any(roi_mask > 0):
            roi_inpainted = inpainter.inpaint(roi_bgr, roi_mask)
            image_result[y1:y2, x1:x2] = roi_inpainted

        # Limpiar residuos de color si está activado
        if clean_residuals_flag:
            image_result = self.clean_residuals(image_result, bbox_yolo, pixel_map,
                                               residue_dominance_threshold=residue_threshold)

        return image_result, refined_mask, roi_coords, pixel_map


if __name__ == "__main__":
    from lama_inpainter import LamaInpainter

    print("\n[TEST] Inicializando ChromaticSeparator...\n")

    separator = ChromaticSeparator(
        text_intensity_threshold=80,
        text_dominance_threshold=30,
        stamp_dominance_threshold=30
    )

    # Crear imagen de prueba con sello de color + texto negro
    test_image = np.ones((300, 300, 3), dtype=np.uint8) * 240  # fondo blanco

    # Dibujar sello azul (B alta, R/G bajas)
    test_image[80:220, 80:220] = [0, 0, 200]  # BGR: azul

    # Dibujar texto negro encima (R=G=B=0)
    test_image[100:110, 100:150] = [0, 0, 0]  # texto

    print(f"Imagen test: {test_image.shape}")

    # Bbox del sello normalizado (centro, tamaño)
    bbox_yolo = (0.5, 0.5, 0.5, 0.5)

    # Máscara gruesa (todo el sello)
    coarse_mask = np.zeros((300, 300), dtype=np.uint8)
    coarse_mask[80:220, 80:220] = 255

    # Extraer ROI y clasificar
    roi_bgr, coords = separator.extract_stamp_roi(test_image, bbox_yolo)
    pixel_map = separator.classify_pixels(roi_bgr)

    print(f"ROI shape: {roi_bgr.shape}")
    print(f"Pixel map valores únicos: {np.unique(pixel_map)}")

    texto_count = np.sum(pixel_map == 0)
    sello_count = np.sum(pixel_map == 1)
    mixto_count = np.sum(pixel_map == 2)

    print(f"\nClasificación de píxeles en ROI:")
    print(f"  TEXTO (preservar):       {texto_count:6d} píxeles")
    print(f"  SELLO (reconstruir):     {sello_count:6d} píxeles")
    print(f"  MIXTO (reconstruir):     {mixto_count:6d} píxeles")

    # Construcción de máscara refinada
    refined_mask = separator.build_refined_mask(test_image, bbox_yolo, coarse_mask)
    print(f"\nMáscara refinada: {np.sum(refined_mask > 0)} píxeles marcados para inpainting")

    # Inpainting
    print("\nAplicando inpainting...")
    inpainter = LamaInpainter()
    result, _ = separator.process(test_image, bbox_yolo, coarse_mask, inpainter)

    print(f"Resultado: {result.shape}, dtype: {result.dtype}")
    print("[OK] Pipeline completado")
