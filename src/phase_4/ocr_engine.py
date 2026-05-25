# -*- coding: utf-8 -*-
"""
OCR Engine: EasyOCR wrapper with complete functionality
Based on proven Phase 4 implementation with:
- Overlap detection with seal regions
- Comprehensive spell correction
- Named Entity Recognition
"""
import cv2
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import re

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    from textdistance import levenshtein
    TEXTDISTANCE_AVAILABLE = True
except ImportError:
    TEXTDISTANCE_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class EasyOCREngine:
    """Complete EasyOCR-based text extraction with corrections and NER"""

    def __init__(
        self,
        language: str = "es",
        confidence_threshold: float = 0.6,
        min_word_length: int = 3,
        max_levenshtein: int = 2,
        debug: bool = False,
    ):
        """
        Args:
            language: OCR language code (default 'es')
            confidence_threshold: Minimum confidence for results
            min_word_length: Minimum word length for spell correction
            max_levenshtein: Max Levenshtein distance for corrections
            debug: Enable debug output
        """
        self.language = language
        self.confidence_threshold = confidence_threshold
        self.min_word_length = min_word_length
        self.max_levenshtein = max_levenshtein
        self.debug = debug

        # Initialize EasyOCR
        if EASYOCR_AVAILABLE:
            self.reader = easyocr.Reader([language], gpu=False)
        else:
            self.reader = None

        # Initialize spaCy
        try:
            self.nlp = spacy.load('es_core_news_sm')
        except Exception:
            self.nlp = None

        # Spanish dictionary
        self.diccionario = self._build_spanish_dictionary()

    def extract_text(
        self,
        image: np.ndarray,
        seal_bbox: Optional[Tuple] = None,
    ) -> Dict:
        """
        Extract and correct text from image.

        Args:
            image: Input image (BGR, uint8)
            seal_bbox: Optional seal bounding box (xc, yc, w, h) normalized

        Returns:
            Dictionary with text, blocks, entities, and metrics
        """
        if image.size == 0:
            return self._empty_result()

        if not EASYOCR_AVAILABLE:
            raise RuntimeError("EasyOCR not available. Install with: pip install easyocr")

        h, w = image.shape[:2]

        # STEP 1: Extract with EasyOCR
        bloques = self._extract_with_easyocr(image, seal_bbox, h, w)

        if not bloques:
            return self._empty_result()

        # STEP 2: Spell correction
        palabras_corregidas = self._apply_spell_correction(bloques)

        # STEP 3: NER
        entidades_totales = self._apply_ner(bloques)

        # STEP 4: Build result
        texto_completo = " ".join([b['texto_corregido'] for b in bloques])
        confianza_promedio = (
            np.mean([b['confianza'] for b in bloques]) if bloques else 0.0
        )

        result = {
            'timestamp': datetime.now().isoformat(),
            'imagen_size': {'width': w, 'height': h},
            'seal_bbox': seal_bbox,
            'texto_completo': texto_completo,
            'bloques': bloques,
            'metricas': {
                'total_bloques': len(bloques),
                'confianza_promedio': float(confianza_promedio),
                'palabras_corregidas': palabras_corregidas,
                'entidades_detectadas': entidades_totales,
                'confianza_threshold': self.confidence_threshold,
                'motores_usados': ['EasyOCR'],
                'procesadores_usados': (
                    ['Levenshtein'] + (['spaCy'] if self.nlp else [])
                ),
            },
        }

        return result

    def _extract_with_easyocr(
        self,
        image: np.ndarray,
        seal_bbox: Optional[Tuple],
        h: int,
        w: int,
    ) -> List[Dict]:
        """Extract text blocks with EasyOCR"""
        bloques = []

        # Convert seal_bbox if provided
        seal_x1, seal_y1, seal_x2, seal_y2 = (0, 0, 0, 0)
        if seal_bbox and len(seal_bbox) >= 4:
            seal_x1, seal_y1, seal_x2, seal_y2 = self._bbox_to_pixels(
                seal_bbox, h, w
            )

        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.reader.readtext(image_rgb, detail=1)

            for idx, (bbox, text, confidence) in enumerate(results):
                coords = [[float(p[0]), float(p[1])] for p in bbox]

                # Calculate block bbox in pixels
                bloque_x1 = min(p[0] for p in coords)
                bloque_y1 = min(p[1] for p in coords)
                bloque_x2 = max(p[0] for p in coords)
                bloque_y2 = max(p[1] for p in coords)

                # Calculate overlap with seal
                overlap = self._calculate_overlap(
                    (bloque_x1, bloque_y1, bloque_x2, bloque_y2),
                    (seal_x1, seal_y1, seal_x2, seal_y2),
                )

                conf_float = float(confidence)
                bloque = {
                    'id': idx,
                    'texto_raw': text.strip(),
                    'texto_corregido': text.strip(),
                    'confianza': conf_float,
                    'baja_confianza': conf_float < self.confidence_threshold,
                    'motor': 'EasyOCR',
                    'coordenadas': coords,
                    'en_zona_sello': overlap > 0.0,
                    'overlap_sello': float(overlap),
                    'palabras_parciales': [],
                    'fue_corregido': False,
                    'distancia_correccion': 0.0,
                    'entidades': [],
                }
                bloques.append(bloque)

        except Exception as e:
            if self.debug:
                print(f"[ERROR] EasyOCR failed: {e}")

        return bloques

    def _bbox_to_pixels(
        self,
        bbox_norm: Tuple,
        h: int,
        w: int,
    ) -> Tuple:
        """Convert normalized bbox (xc, yc, w, h) to pixels"""
        if not bbox_norm or len(bbox_norm) < 4:
            return 0, 0, w, h

        xc, yc, bbox_w, bbox_h = bbox_norm[:4]
        x1 = int(max(0, (xc - bbox_w / 2) * w))
        y1 = int(max(0, (yc - bbox_h / 2) * h))
        x2 = int(min(w, (xc + bbox_w / 2) * w))
        y2 = int(min(h, (yc + bbox_h / 2) * h))

        return x1, y1, x2, y2

    def _calculate_overlap(
        self,
        bbox1: Tuple,
        bbox2: Tuple,
    ) -> float:
        """Calculate overlap percentage between two bboxes"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2

        x_left = max(x1_1, x1_2)
        y_top = max(y1_1, y1_2)
        x_right = min(x2_1, x2_2)
        y_bottom = min(y2_1, y2_2)

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection = (x_right - x_left) * (y_bottom - y_top)
        area_bbox1 = (x2_1 - x1_1) * (y2_1 - y1_1)

        if area_bbox1 == 0:
            return 0.0

        return min(1.0, max(0.0, intersection / area_bbox1))

    def _apply_spell_correction(self, bloques: List[Dict]) -> int:
        """Apply spell correction to all blocks"""
        if not TEXTDISTANCE_AVAILABLE:
            return 0

        palabras_corregidas = 0

        for bloque in bloques:
            texto_original = bloque['texto_raw']
            palabras = texto_original.split()
            palabras_corregidas_bloque = []

            for palabra in palabras:
                palabra_limpia = re.sub(r'[^\w]', '', palabra)

                if (
                    len(palabra_limpia) >= self.min_word_length
                    and palabra_limpia.isalpha()
                ):
                    palabra_corregida = self._correct_word(palabra_limpia)
                    if palabra_corregida != palabra_limpia:
                        palabras_corregidas += 1
                    palabras_corregidas_bloque.append(palabra_corregida)
                else:
                    palabras_corregidas_bloque.append(palabra)

            bloque['texto_corregido'] = ' '.join(palabras_corregidas_bloque)
            bloque['fue_corregido'] = (
                bloque['texto_raw'] != bloque['texto_corregido']
            )

        return palabras_corregidas

    def _correct_word(self, palabra: str) -> str:
        """Correct single word using Levenshtein"""
        palabra_lower = palabra.lower()

        if palabra_lower in self.diccionario:
            return palabra

        if not TEXTDISTANCE_AVAILABLE:
            return palabra

        # Find best matching candidate
        best_match = None
        best_distance = self.max_levenshtein + 1

        for dict_word in self.diccionario:
            if abs(len(dict_word) - len(palabra_lower)) > self.max_levenshtein:
                continue

            dist = levenshtein(palabra_lower, dict_word)
            if dist <= self.max_levenshtein and dist < best_distance:
                best_match = dict_word
                best_distance = dist

        return best_match if best_match else palabra

    def _apply_ner(self, bloques: List[Dict]) -> int:
        """Apply Named Entity Recognition"""
        if not self.nlp:
            return 0

        entidades_totales = 0

        for bloque in bloques:
            try:
                doc = self.nlp(bloque['texto_corregido'])
                entidades = []

                for ent in doc.ents:
                    if ent.label_ in ['PER', 'DATE', 'MONEY', 'ORG']:
                        entidades.append({
                            'texto': ent.text,
                            'tipo': ent.label_,
                            'inicio': ent.start_char,
                            'fin': ent.end_char,
                        })

                bloque['entidades'] = entidades
                entidades_totales += len(entidades)
            except Exception:
                bloque['entidades'] = []

        return entidades_totales

    def _build_spanish_dictionary(self) -> set:
        """Build Spanish dictionary for spell correction"""
        palabras = [
            'ministerio', 'economia', 'finanzas', 'superintendencia', 'mercado',
            'valores', 'decenio', 'igualdad', 'oportunidades', 'mujeres', 'hombres',
            'bicentenario', 'independencia', 'codigo', 'gobierno', 'corporativo',
            'sociedades', 'peruanas', 'directores', 'accionistas', 'directivos',
            'trayectoria', 'profesional', 'honorabilidad', 'suficiencia', 'dedicacion',
            'exclusiva', 'empresa', 'riesgo', 'clasificadora', 'articulo', 'resolucion',
            'normas', 'entidades', 'autorizadas', 'diciembre', 'marzo', 'primero',
            'tercio', 'constituyente', 'requisito', 'cumplir', 'definicion', 'uniforme',
            'aplicable', 'afectar', 'objetividad', 'evaluar', 'autorizar', 'excepcion',
            'casos', 'considere', 'aspecto', 'clave', 'asegurar', 'persona',
            'suficiente', 'economica', 'permitir', 'aportar', 'decisiones', 'directorio',
            'total', 'imparcialidad', 'contrapone', 'supuesto', 'requerirse', 'corresponde',
            'usar', 'prerrogativa', 'organica', 'modificar', 'principio', 'promociona',
            'precisos', 'propone', 'nombramiento', 'promueve', 'fecha', 'numero',
            'documento', 'referencia', 'articulos', 'texto', 'pagina', 'folio',
        ]
        return set(palabras)

    def _empty_result(self) -> Dict:
        """Return empty result"""
        return {
            'timestamp': datetime.now().isoformat(),
            'imagen_size': {'width': 0, 'height': 0},
            'seal_bbox': None,
            'texto_completo': '',
            'bloques': [],
            'metricas': {
                'total_bloques': 0,
                'confianza_promedio': 0.0,
                'palabras_corregidas': 0,
                'entidades_detectadas': 0,
                'motores_usados': [],
                'procesadores_usados': [],
            },
        }
