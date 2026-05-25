# -*- coding: utf-8 -*-
"""
Phase 4: OCR y Post-corrección (versión EasyOCR)
EasyOCR (principal) + simulación de fallback
"""
import numpy as np
import cv2
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "classification"))
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))


class Phase4OCREasy:
    """
    OCR Pipeline con EasyOCR principal
    """

    def __init__(self, confidence_threshold=0.6, min_word_length=3, max_levenshtein=2, debug=False):
        """
        Args:
            confidence_threshold: Threshold para usar fallback (default 0.6)
            min_word_length: Longitud mínima de palabra (default 3)
            max_levenshtein: Distancia Levenshtein máxima (default 2)
            debug: Guardar imágenes de debug (default False)
        """
        self.confidence_threshold = confidence_threshold
        self.min_word_length = min_word_length
        self.max_levenshtein = max_levenshtein
        self.debug = debug

        # Inicializar EasyOCR
        try:
            import easyocr
            self.reader = easyocr.Reader(['es'], gpu=False)
            self.easyocr_available = True
            print("[Phase4OCR] EasyOCR inicializado correctamente")
        except ImportError:
            print("[Phase4OCR] [WARN] EasyOCR no disponible")
            self.reader = None
            self.easyocr_available = False

    def process(self, clean_image, seal_bbox):
        """
        Procesa imagen limpia y extrae texto con OCR

        Args:
            clean_image: Imagen limpia en BGR (resultado de Phase 3A)
            seal_bbox: Bounding box del sello normalizado (xc, yc, w, h)

        Returns:
            dict con estructura JSON OCR
        """
        h, w = clean_image.shape[:2]

        print("\n" + "="*80)
        print("PHASE 4: OCR Y POST-CORRECCIÓN (EasyOCR)")
        print("="*80)
        print(f"Imagen: {w}x{h} píxeles")
        print(f"Threshold confianza: {self.confidence_threshold}")
        print()

        # PASO 1: Ejecutar EasyOCR
        bloques = []

        if self.easyocr_available:
            print("[PASO 1] Ejecutando EasyOCR...")
            bloques = self._extract_with_easyocr(clean_image)
            print(f"        Bloques detectados: {len(bloques)}")
        else:
            print("[ERROR] EasyOCR no disponible")
            return self._empty_result()

        # PASO 2: Procesar bloques (simular fallback)
        print(f"\n[PASO 2] Procesando bloques (confianza < {self.confidence_threshold})...")
        bloques_fallback = 0

        for bloque in bloques:
            # En versión real, aquí iría el fallback a Tesseract
            # Por ahora solo marcamos los que estarían en fallback
            if bloque['confianza'] < self.confidence_threshold:
                bloques_fallback += 1

        print(f"        Bloques que requerirían fallback: {bloques_fallback}")

        # PASO 3: Construir resultado JSON
        texto_completo = " ".join([b['texto_raw'] for b in bloques])
        confianza_promedio = np.mean([b['confianza'] for b in bloques]) if bloques else 0.0

        result = {
            'timestamp': datetime.now().isoformat(),
            'imagen_size': {'width': w, 'height': h},
            'seal_bbox': seal_bbox,
            'texto_completo': texto_completo,
            'bloques': bloques,
            'metricas': {
                'total_bloques': len(bloques),
                'bloques_fallback': bloques_fallback,
                'confianza_promedio': float(confianza_promedio),
                'confidence_threshold': self.confidence_threshold,
                'motors_usados': ['EasyOCR']
            }
        }

        # PASO 4: Imprimir resumen
        self._print_summary(result)

        return result

    def _extract_with_easyocr(self, image):
        """Extrae texto con EasyOCR"""
        bloques = []

        try:
            # EasyOCR requiere RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Ejecutar OCR
            resultado = self.reader.readtext(image_rgb, detail=1)

            for idx, deteccion in enumerate(resultado):
                # deteccion es: (bbox, text, confidence)
                # bbox es lista de 4 puntos [top-left, top-right, bottom-right, bottom-left]
                bbox, texto, confianza = deteccion

                # Convertir bbox a coordenadas
                coords = [[float(p[0]), float(p[1])] for p in bbox]

                bloque = {
                    'id': idx,
                    'texto_raw': texto.strip(),
                    'texto_corregido': texto.strip(),
                    'confianza': float(confianza),
                    'motor': 'EasyOCR',
                    'coordenadas': coords,
                    'entidades': []
                }
                bloques.append(bloque)

        except Exception as e:
            print(f"[ERROR] EasyOCR falló: {e}")
            return []

        return bloques

    def _empty_result(self):
        """Retorna estructura JSON vacía"""
        return {
            'timestamp': datetime.now().isoformat(),
            'imagen_size': {'width': 0, 'height': 0},
            'seal_bbox': None,
            'texto_completo': '',
            'bloques': [],
            'metricas': {
                'total_bloques': 0,
                'bloques_fallback': 0,
                'confianza_promedio': 0.0,
                'motors_usados': []
            }
        }

    def _print_summary(self, result):
        """Imprime resumen en consola"""
        metricas = result['metricas']

        print("\n" + "-"*80)
        print("RESUMEN OCR")
        print("-"*80)
        print(f"Total bloques detectados: {metricas['total_bloques']}")
        print(f"Bloques que requerirían fallback: {metricas['bloques_fallback']}")
        print(f"Confianza promedio: {metricas['confianza_promedio']:.3f}")
        print(f"Motores utilizados: {', '.join(metricas['motors_usados'])}")
        print(f"Longitud texto completo: {len(result['texto_completo'])} caracteres")
        print("-"*80 + "\n")

    def save_json(self, result, output_path):
        """Guarda resultado como JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"[OK] JSON guardado: {output_path}")


def phase_4_ocr(clean_image, seal_bbox, confidence_threshold=0.6, min_word_length=3, max_levenshtein=2, debug=False):
    """
    Función principal Phase 4: OCR y Post-corrección

    Args:
        clean_image: Imagen BGR limpia (resultado Phase 3A)
        seal_bbox: Bounding box del sello (xc, yc, w, h)
        confidence_threshold: Threshold para fallback (default 0.6)
        min_word_length: Longitud mínima palabra (default 3)
        max_levenshtein: Distancia Levenshtein máxima (default 2)
        debug: Modo debug (default False)

    Returns:
        dict: Resultado JSON OCR
    """
    ocr_pipeline = Phase4OCREasy(
        confidence_threshold=confidence_threshold,
        min_word_length=min_word_length,
        max_levenshtein=max_levenshtein,
        debug=debug
    )

    return ocr_pipeline.process(clean_image, seal_bbox)


def main():
    """Test con una imagen de ejemplo"""
    from PIL import Image
    from phase_3a_complete import Phase3aComplete

    DATA_PATH = Path("C:/Users/manue/Documents/Desktop_Archive_2026-03-14/Folders/PR_COMPUTER_VISION/idp-project/datos/synthetic_dataset")

    images_dir = DATA_PATH / "images"
    labels_dir = DATA_PATH / "labels"

    image_file = list(images_dir.glob("syn_0000.png"))[0]
    label_file = labels_dir / "syn_0000.txt"

    # Leer bbox
    with open(label_file, 'r') as f:
        parts = f.readline().strip().split()
        xc, yc, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
        bbox = (xc, yc, w, h)

    # Procesar con Phase 3A para obtener imagen limpia
    print("Procesando con Phase 3A para obtener imagen limpia...")
    img_pil = Image.open(image_file).convert('RGB')
    img_bgr = np.array(img_pil)[:, :, ::-1]

    pipeline_3a = Phase3aComplete(block_size=20, min_text_pixels=1, final_dilation=3, debug=False)
    result_3a = pipeline_3a.process(img_bgr, bbox)
    clean_image = result_3a['image_inpainted']

    # Ejecutar Phase 4
    print("\n" + "="*100)
    result_ocr = phase_4_ocr(clean_image, bbox)

    # Guardar JSON
    output_dir = Path("C:/Users/manue/Desktop/final_vision/ocr_results")
    output_dir.mkdir(exist_ok=True)

    ocr_pipeline = Phase4OCREasy()
    ocr_pipeline.save_json(result_ocr, output_dir / "syn_0000_ocr_easyocr.json")

    # Mostrar primeros bloques
    if result_ocr['bloques']:
        print("\nPrimeros 3 bloques detectados:")
        for bloque in result_ocr['bloques'][:3]:
            print(f"  [{bloque['id']}] '{bloque['texto_raw']}' (conf: {bloque['confianza']:.3f})")


if __name__ == "__main__":
    main()
