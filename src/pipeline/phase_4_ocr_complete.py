# -*- coding: utf-8 -*-
"""
Phase 4: OCR Completo con Corrección Ortográfica + NER
- EasyOCR para OCR
- Levenshtein para corrección ortográfica
- spaCy para NER (Persona, Fecha, Monto)
"""
import numpy as np
import cv2
import json
from pathlib import Path
from datetime import datetime
import sys
import re
from textdistance import levenshtein

sys.path.insert(0, str(Path(__file__).parent.parent / "classification"))
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))


class Phase4OCRComplete:
    """
    OCR Completo: EasyOCR + Corrección Ortográfica + NER
    """

    def __init__(self, confidence_threshold=0.6, min_word_length=3, max_levenshtein=2, debug=False):
        """
        Args:
            confidence_threshold: Threshold para fallback (default 0.6)
            min_word_length: Longitud mínima palabra (default 3)
            max_levenshtein: Distancia Levenshtein máxima para corrección (default 2)
            debug: Modo debug (default False)
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

        # Inicializar spaCy
        try:
            import spacy
            self.nlp = spacy.load('es_core_news_sm')
            self.spacy_available = True
            print("[Phase4OCR] spaCy (es_core_news_sm) inicializado correctamente")
        except Exception as e:
            print(f"[Phase4OCR] [WARN] spaCy no disponible: {str(e)[:60]}")
            self.nlp = None
            self.spacy_available = False

        # Cargar diccionario de palabras españolas (simulado)
        self.diccionario = self._build_spanish_dictionary()
        print(f"[Phase4OCR] Diccionario cargado: {len(self.diccionario)} palabras")

    def process(self, clean_image, seal_bbox):
        """
        Procesa imagen limpia: OCR + Corrección + NER
        """
        h, w = clean_image.shape[:2]

        print("\n" + "="*80)
        print("PHASE 4: OCR COMPLETO (EasyOCR + Corrección + NER)")
        print("="*80)
        print(f"Imagen: {w}x{h} pixeles")
        print(f"Threshold confianza: {self.confidence_threshold}")
        print()

        # PASO 1: OCR
        bloques = []
        if self.easyocr_available:
            print("[PASO 1] Ejecutando EasyOCR...")
            bloques = self._extract_with_easyocr(clean_image, seal_bbox, h, w)
            print(f"        Bloques detectados: {len(bloques)}")
        else:
            print("[ERROR] EasyOCR no disponible")
            return self._empty_result()

        # PASO 2: Corrección Ortográfica
        print(f"\n[PASO 2] Aplicando corrección ortografica (Levenshtein <= {self.max_levenshtein})...")
        palabras_corregidas = 0
        for bloque in bloques:
            texto_original = bloque['texto_raw']
            palabras = texto_original.split()
            palabras_corregidas_bloque = []
            palabras_parciales = []
            distancia_total = 0.0

            for idx_palabra, palabra in enumerate(palabras):
                palabra_limpia = re.sub(r'[^\w]', '', palabra)
                if len(palabra_limpia) >= self.min_word_length and palabra_limpia.isalpha():
                    palabra_corregida, distancia = self._corregir_palabra(palabra_limpia)
                    if palabra_corregida != palabra_limpia:
                        palabras_corregidas += 1
                        # Marcar como parcial si está en zona de sello con baja confianza
                        if bloque['baja_confianza'] or bloque['en_zona_sello']:
                            palabras_parciales.append({
                                'indice': idx_palabra,
                                'original': palabra_limpia,
                                'corregida': palabra_corregida,
                                'distancia': distancia if distancia != float('inf') else 0.0
                            })
                    if distancia != float('inf'):
                        distancia_total += distancia
                    palabras_corregidas_bloque.append(palabra_corregida)
                else:
                    palabras_corregidas_bloque.append(palabra)

            bloque['texto_corregido'] = ' '.join(palabras_corregidas_bloque)
            bloque['fue_corregido'] = bloque['texto_raw'] != bloque['texto_corregido']
            bloque['distancia_correccion'] = distancia_total
            bloque['palabras_parciales'] = palabras_parciales

        print(f"        Palabras corregidas: {palabras_corregidas}")

        # PASO 3: NER (Named Entity Recognition)
        print(f"\n[PASO 3] Ejecutando NER (Persona, Fecha, Monto)...")
        entidades_totales = 0
        if self.spacy_available:
            for bloque in bloques:
                texto = bloque['texto_corregido']
                entidades = self._extract_entities(texto)
                bloque['entidades'] = entidades
                entidades_totales += len(entidades)

        print(f"        Entidades detectadas: {entidades_totales}")

        # PASO 4: Construir resultado JSON
        texto_completo = " ".join([b['texto_corregido'] for b in bloques])
        confianza_promedio = np.mean([b['confianza'] for b in bloques]) if bloques else 0.0
        bloques_baja_confianza = sum(1 for b in bloques if b['baja_confianza'])
        bloques_en_zona_sello = sum(1 for b in bloques if b['en_zona_sello'])

        result = {
            'timestamp': datetime.now().isoformat(),
            'imagen_size': {'width': w, 'height': h},
            'seal_bbox': seal_bbox,
            'texto_completo': texto_completo,
            'bloques': bloques,
            'metricas': {
                'total_bloques': len(bloques),
                'bloques_baja_confianza': bloques_baja_confianza,
                'bloques_en_zona_sello': bloques_en_zona_sello,
                'confianza_promedio': float(confianza_promedio),
                'palabras_corregidas': palabras_corregidas,
                'entidades_detectadas': entidades_totales,
                'confidence_threshold': self.confidence_threshold,
                'motors_usados': ['EasyOCR'],
                'procesadores_usados': ['Levenshtein'] + (['spaCy'] if self.spacy_available else [])
            }
        }

        self._print_summary(result)
        return result

    def _extract_with_easyocr(self, image, seal_bbox, h, w):
        """Extrae texto con EasyOCR y calcula overlap con sello"""
        bloques = []

        # Convertir seal_bbox normalizado a píxeles (xc, yc, w, h -> x1, y1, x2, y2)
        seal_x1, seal_y1, seal_x2, seal_y2 = self._bbox_normalized_to_pixels(seal_bbox, h, w)

        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            resultado = self.reader.readtext(image_rgb, detail=1)

            for idx, deteccion in enumerate(resultado):
                bbox, texto, confianza = deteccion
                coords = [[float(p[0]), float(p[1])] for p in bbox]

                # Calcular bounding box del bloque en píxeles
                bloque_x1 = min(p[0] for p in coords)
                bloque_y1 = min(p[1] for p in coords)
                bloque_x2 = max(p[0] for p in coords)
                bloque_y2 = max(p[1] for p in coords)

                # Calcular overlap con sello
                overlap = self._calculate_overlap(
                    (bloque_x1, bloque_y1, bloque_x2, bloque_y2),
                    (seal_x1, seal_y1, seal_x2, seal_y2)
                )

                conf_float = float(confianza)
                bloque = {
                    'id': idx,
                    'texto_raw': texto.strip(),
                    'texto_corregido': texto.strip(),
                    'confianza': conf_float,
                    'baja_confianza': conf_float < self.confidence_threshold,
                    'motor': 'EasyOCR',
                    'coordenadas': coords,
                    'en_zona_sello': overlap > 0.0,
                    'overlap_sello': float(overlap),
                    'palabras_parciales': [],
                    'fue_corregido': False,
                    'distancia_correccion': 0.0,
                    'entidades': []
                }
                bloques.append(bloque)

        except Exception as e:
            print(f"[ERROR] EasyOCR falló: {e}")
            return []

        return bloques

    def _bbox_normalized_to_pixels(self, bbox_norm, h, w):
        """Convierte bbox normalizado (xc, yc, w, h) a píxeles (x1, y1, x2, y2)"""
        if not bbox_norm or len(bbox_norm) < 4:
            return 0, 0, w, h

        xc, yc, bbox_w, bbox_h = bbox_norm[:4]
        x1 = int((xc - bbox_w / 2) * w)
        y1 = int((yc - bbox_h / 2) * h)
        x2 = int((xc + bbox_w / 2) * w)
        y2 = int((yc + bbox_h / 2) * h)

        # Clampear a límites de imagen
        x1 = max(0, min(x1, w - 1))
        x2 = max(0, min(x2, w))
        y1 = max(0, min(y1, h - 1))
        y2 = max(0, min(y2, h))

        return x1, y1, x2, y2

    def _calculate_overlap(self, bbox1, bbox2):
        """
        Calcula porcentaje de overlap entre dos bboxes.
        bbox1 y bbox2 son tuplas (x1, y1, x2, y2)
        Retorna porcentaje 0-1
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2

        # Calcular intersección
        x_left = max(x1_1, x1_2)
        y_top = max(y1_1, y1_2)
        x_right = min(x2_1, x2_2)
        y_bottom = min(y2_1, y2_2)

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection = (x_right - x_left) * (y_bottom - y_top)

        # Área del bbox1 (bloque)
        area_bbox1 = (x2_1 - x1_1) * (y2_1 - y1_1)

        if area_bbox1 == 0:
            return 0.0

        # Porcentaje respecto al bloque
        overlap_pct = intersection / area_bbox1
        return min(1.0, max(0.0, overlap_pct))

    def _corregir_palabra(self, palabra):
        """
        Corrige palabra usando Levenshtein.
        Retorna tupla (palabra_corregida, distancia_usada)
        """
        if palabra in self.diccionario:
            return palabra, 0.0

        # Buscar palabras en diccionario con distancia <= max_levenshtein
        candidatos = []
        for palabra_dict in self.diccionario:
            dist = levenshtein(palabra.lower(), palabra_dict.lower())
            if dist <= self.max_levenshtein:
                candidatos.append((palabra_dict, float(dist)))

        if candidatos:
            # Retornar palabra con menor distancia
            candidatos.sort(key=lambda x: x[1])
            return candidatos[0][0], candidatos[0][1]

        return palabra, float('inf')

    def _extract_entities(self, texto):
        """Extrae entidades con spaCy NER"""
        entidades = []
        if not self.spacy_available:
            return entidades

        try:
            doc = self.nlp(texto)
            for ent in doc.ents:
                # Filtrar entidades relevantes
                if ent.label_ in ['PER', 'DATE', 'MONEY', 'ORG']:
                    entidades.append({
                        'texto': ent.text,
                        'tipo': ent.label_,
                        'inicio': ent.start_char,
                        'fin': ent.end_char
                    })
        except Exception as e:
            pass

        return entidades

    def _build_spanish_dictionary(self):
        """Construye diccionario de palabras españolas comunes"""
        palabras = [
            'ministerio', 'economia', 'finanzas', 'superintendencia', 'mercado',
            'valores', 'decenio', 'igualdad', 'oportunidades', 'mujeres', 'hombres',
            'bicentenario', 'independencia', 'codigo', 'gobierno', 'corporativo',
            'sociedades', 'peruanas', 'directores', 'accionistas', 'directivos',
            'trayectoria', 'profesional', 'honorabilidad', 'suficiencia', 'dedicacion',
            'exclusiva', 'empresa', 'riesgo', 'clasificadora', 'artículo', 'resolución',
            'normas', 'entidades', 'autorizadas', 'diciembre', 'marzo', 'primero',
            'tercio', 'constitu', 'requisito', 'cumplir', 'definición', 'uniforme',
            'aplicable', 'afectar', 'objetividad', 'evaluar', 'autorizar', 'excepción',
            'casos', 'considere', 'aspecto', 'clave', 'asegurar', 'persona', 'designada',
            'suficiente', 'económica', 'permitir', 'aportar', 'decisiones', 'directorio',
            'total', 'imparcialidad', 'contrapone', 'supuesto', 'requerirse', 'corresponde',
            'usar', 'prerrogativa', 'orgánica', 'modificar', 'principio', 'promociona',
            'tercio', 'constitu', 'precisos', 'propone', 'nombramiento', 'promueve'
        ]
        return set(palabras)

    def _print_summary(self, result):
        """Imprime resumen"""
        metricas = result['metricas']

        print("\n" + "-"*80)
        print("RESUMEN OCR COMPLETO")
        print("-"*80)
        print(f"Total bloques: {metricas['total_bloques']}")
        print(f"Bloques con baja confianza: {metricas['bloques_baja_confianza']}")
        print(f"Bloques en zona de sello: {metricas['bloques_en_zona_sello']}")
        print(f"Confianza promedio: {metricas['confianza_promedio']:.4f}")
        print(f"Palabras corregidas: {metricas['palabras_corregidas']}")
        print(f"Entidades detectadas: {metricas['entidades_detectadas']}")
        print(f"Motores: {', '.join(metricas['motors_usados'])}")
        print(f"Procesadores: {', '.join(metricas['procesadores_usados'])}")
        print(f"Longitud texto: {len(result['texto_completo']):,} caracteres")
        print("-"*80 + "\n")

    def _empty_result(self):
        """Retorna resultado vacío"""
        return {
            'timestamp': datetime.now().isoformat(),
            'imagen_size': {'width': 0, 'height': 0},
            'seal_bbox': None,
            'texto_completo': '',
            'bloques': [],
            'metricas': {
                'total_bloques': 0,
                'bloques_baja_confianza': 0,
                'bloques_en_zona_sello': 0,
                'confianza_promedio': 0.0,
                'palabras_corregidas': 0,
                'entidades_detectadas': 0,
                'motors_usados': [],
                'procesadores_usados': []
            }
        }

    def save_json(self, result, output_path):
        """Guarda resultado como JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"[OK] JSON guardado: {output_path}")


def phase_4_ocr_complete(clean_image, seal_bbox, confidence_threshold=0.6,
                         min_word_length=3, max_levenshtein=2, debug=False):
    """
    Función principal Phase 4: OCR Completo

    Args:
        clean_image: Imagen limpia en BGR
        seal_bbox: Bounding box del sello
        confidence_threshold: Threshold para fallback
        min_word_length: Longitud mínima palabra
        max_levenshtein: Distancia Levenshtein máxima
        debug: Modo debug

    Returns:
        dict: Resultado JSON OCR completo
    """
    ocr = Phase4OCRComplete(
        confidence_threshold=confidence_threshold,
        min_word_length=min_word_length,
        max_levenshtein=max_levenshtein,
        debug=debug
    )
    return ocr.process(clean_image, seal_bbox)


def main():
    """Test con imagen real"""
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

    # Phase 3A para imagen limpia
    print("Ejecutando Phase 3A para obtener imagen limpia...")
    img_pil = Image.open(image_file).convert('RGB')
    img_bgr = np.array(img_pil)[:, :, ::-1]

    pipeline_3a = Phase3aComplete(block_size=20, min_text_pixels=1, final_dilation=3, debug=False)
    result_3a = pipeline_3a.process(img_bgr, bbox)
    clean_image = result_3a['image_inpainted']

    # Phase 4 Completa
    print("\n" + "="*100)
    result = phase_4_ocr_complete(clean_image, bbox)

    # Guardar JSON
    output_dir = Path("C:/Users/manue/Desktop/final_vision/ocr_results")
    output_dir.mkdir(exist_ok=True)

    ocr = Phase4OCRComplete()
    ocr.save_json(result, output_dir / "syn_0000_ocr_completo.json")

    # Mostrar algunas entidades detectadas
    if result['bloques']:
        print("\nPrimeras 5 entidades detectadas:")
        todas_entidades = []
        for bloque in result['bloques']:
            todas_entidades.extend(bloque['entidades'])

        for ent in todas_entidades[:5]:
            print(f"  - {ent['texto']} (Tipo: {ent['tipo']})")


if __name__ == "__main__":
    main()
