# -*- coding: utf-8 -*-
"""
Phase 4: OCR y Post-corrección
PaddleOCR v4 (principal) + Tesseract fallback (baja confianza)
"""
import numpy as np
import cv2
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "classification"))
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))


class Phase4OCR:
    """
    OCR Pipeline con PaddleOCR principal y Tesseract fallback
    """

    def __init__(self, confidence_threshold=0.6, min_word_length=3, max_levenshtein=2, debug=False):
        """
        Args:
            confidence_threshold: Threshold para usar fallback (default 0.6)
            min_word_length: Longitud mínima de palabra para corregir (default 3)
            max_levenshtein: Distancia Levenshtein máxima para corrección (default 2)
            debug: Guardar imágenes de debug (default False)
        """
        self.confidence_threshold = confidence_threshold
        self.min_word_length = min_word_length
        self.max_levenshtein = max_levenshtein
        self.debug = debug

        # Inicializar PaddleOCR
        try:
            from paddleocr import PaddleOCR
            try:
                self.paddle = PaddleOCR(lang='es', use_angle_cls=True)
                self.paddle_available = True
                print("[Phase4OCR] PaddleOCR inicializado correctamente")
            except RuntimeError as e:
                print(f"[Phase4OCR] [WARN] PaddleOCR no completamente disponible: {str(e)[:80]}")
                self.paddle = None
                self.paddle_available = False
        except (ImportError, RuntimeError):
            print("[Phase4OCR] [WARN] PaddleOCR no disponible, usando Tesseract como principal")
            self.paddle = None
            self.paddle_available = False

        # Inicializar Tesseract
        try:
            import pytesseract
            self.tesseract = pytesseract
            self.tesseract_available = True
            print("[Phase4OCR] Tesseract inicializado correctamente")
        except ImportError:
            print("[Phase4OCR] [WARN] Tesseract no disponible")
            self.tesseract = None
            self.tesseract_available = False

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
        print("PHASE 4: OCR Y POST-CORRECCIÓN")
        print("="*80)
        print(f"Imagen: {w}x{h} píxeles")
        print(f"Threshold confianza: {self.confidence_threshold}")
        print()

        # PASO 1: Ejecutar PaddleOCR (si disponible)
        bloques = []

        if self.paddle_available:
            print("[PASO 1] Ejecutando PaddleOCR...")
            bloques = self._extract_with_paddle(clean_image)
            print(f"        Bloques detectados: {len(bloques)}")
        elif self.tesseract_available:
            print("[PASO 1] PaddleOCR no disponible, usando Tesseract como principal...")
            bloques = self._extract_with_tesseract_full(clean_image)
            print(f"        Bloques detectados: {len(bloques)}")
        else:
            print("[ERROR] Ni PaddleOCR ni Tesseract disponibles")
            return self._empty_result()

        # PASO 2: Fallback por confianza baja
        print(f"\n[PASO 2] Aplicando fallback para bloques con confianza < {self.confidence_threshold}...")
        bloques_fallback = 0

        for bloque in bloques:
            if bloque['confianza'] < self.confidence_threshold and self.tesseract_available:
                texto_fallback = self._extract_bloque_with_tesseract(clean_image, bloque['coordenadas'])
                if texto_fallback:
                    bloque['texto_corregido'] = texto_fallback
                    bloque['motor'] = 'Tesseract (fallback)'
                    bloques_fallback += 1

        print(f"        Bloques con fallback: {bloques_fallback}")

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
                'motors_usados': list(set([b['motor'] for b in bloques]))
            }
        }

        # PASO 4: Imprimir resumen
        self._print_summary(result)

        return result

    def _extract_with_paddle(self, image):
        """Extrae texto con PaddleOCR"""
        bloques = []

        try:
            resultado = self.paddle.ocr(image, cls=True)

            if resultado and resultado[0]:
                for idx, linea in enumerate(resultado[0]):
                    # linea contiene: (puntos_poligono, (texto, confianza))
                    puntos, (texto, confianza) = linea

                    # Convertir puntos a lista de coordenadas
                    coords = [[float(p[0]), float(p[1])] for p in puntos]

                    bloque = {
                        'id': idx,
                        'texto_raw': texto.strip(),
                        'texto_corregido': texto.strip(),
                        'confianza': float(confianza),
                        'motor': 'PaddleOCR',
                        'coordenadas': coords,
                        'entidades': []  # Para future use con NER
                    }
                    bloques.append(bloque)

        except Exception as e:
            print(f"[ERROR] PaddleOCR falló: {e}")
            return []

        return bloques

    def _extract_with_tesseract_full(self, image):
        """Extrae texto con Tesseract en toda la imagen"""
        bloques = []

        try:
            # Convertir BGR a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Aplicar thresholding para mejorar OCR
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

            # Usar pytesseract con PSM 6
            data = self.tesseract.image_to_data(thresh, lang='spa', config='--psm 6', output_type='dict')

            bloque_id = 0
            for i in range(len(data['text'])):
                texto = data['text'][i].strip()

                if texto:  # Solo si hay texto
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    confianza = data['conf'][i] / 100.0

                    # Crear coordenadas del rectángulo (4 puntos)
                    coords = [
                        [x, y],
                        [x + w, y],
                        [x + w, y + h],
                        [x, y + h]
                    ]

                    bloque = {
                        'id': bloque_id,
                        'texto_raw': texto,
                        'texto_corregido': texto,
                        'confianza': float(confianza),
                        'motor': 'Tesseract',
                        'coordenadas': coords,
                        'entidades': []
                    }
                    bloques.append(bloque)
                    bloque_id += 1

        except Exception as e:
            print(f"[ERROR] Tesseract falló: {e}")
            return []

        return bloques

    def _extract_bloque_with_tesseract(self, image, coordenadas):
        """Extrae texto de una región específica con Tesseract"""
        try:
            # Convertir coordenadas a rect
            if coordenadas and len(coordenadas) >= 4:
                # Usar bounding box de las coordenadas
                x_coords = [c[0] for c in coordenadas]
                y_coords = [c[1] for c in coordenadas]

                x_min, x_max = int(min(x_coords)), int(max(x_coords))
                y_min, y_max = int(min(y_coords)), int(max(y_coords))

                # Recortar región
                roi = image[y_min:y_max, x_min:x_max]

                if roi.size == 0:
                    return None

                # Convertir a escala de grises y threshold
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

                # Extraer texto con PSM 6
                texto = self.tesseract.image_to_string(thresh, lang='spa', config='--psm 6')

                return texto.strip() if texto else None

        except Exception as e:
            print(f"[ERROR] Fallback Tesseract falló: {e}")
            return None

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
        print(f"Bloques con fallback: {metricas['bloques_fallback']}")
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
    ocr_pipeline = Phase4OCR(
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

    ocr_pipeline = Phase4OCR()
    ocr_pipeline.save_json(result_ocr, output_dir / "syn_0000_ocr.json")


if __name__ == "__main__":
    main()
