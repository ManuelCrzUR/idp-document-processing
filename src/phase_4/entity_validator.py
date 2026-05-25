# -*- coding: utf-8 -*-
"""
Entity Validator: spaCy-based Named Entity Recognition
"""
from typing import List, Dict, Tuple, Optional
import spacy
import re


class EntityValidator:
    """Named Entity Recognition using spaCy"""

    def __init__(self, model_name: str = "es_core_news_sm"):
        """
        Args:
            model_name: spaCy model name (Spanish: es_core_news_sm)
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            print(f"Model {model_name} not found. Install with: python -m spacy download {model_name}")
            self.nlp = None

    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities from text.

        Args:
            text: Text to process

        Returns:
            List of entities with:
            - 'texto': Entity text
            - 'tipo': Entity type (PERSON, DATE, MONEY, etc.)
            - 'confianza': Confidence score
        """
        if not self.nlp or not text:
            return []

        doc = self.nlp(text)
        entities = []

        for ent in doc.ents:
            entities.append({
                'texto': ent.text,
                'tipo': ent.label_,
                'inicio': ent.start_char,
                'fin': ent.end_char,
            })

        return entities

    def validate_text(self, text: str) -> Dict:
        """
        Validate text and extract entities.

        Args:
            text: Text to validate

        Returns:
            Dictionary with:
            - 'texto_validado': Original text
            - 'entidades': List of detected entities
            - 'entidades_persona': Person entities
            - 'entidades_fecha': Date entities
            - 'entidades_monto': Money entities
        """
        if not self.nlp:
            return {
                'texto_validado': text,
                'entidades': [],
                'entidades_persona': [],
                'entidades_fecha': [],
                'entidades_monto': [],
            }

        entities = self.extract_entities(text)

        persona_entities = [e for e in entities if e['tipo'] in ['PERSON', 'PER']]
        fecha_entities = [e for e in entities if e['tipo'] in ['DATE', 'FECHA']]
        monto_entities = [e for e in entities if e['tipo'] in ['MONEY', 'QUANTITY', 'MONTO']]

        return {
            'texto_validado': text,
            'entidades': entities,
            'entidades_persona': persona_entities,
            'entidades_fecha': fecha_entities,
            'entidades_monto': monto_entities,
        }

    def validate_blocks(self, blocks: List[Dict]) -> List[Dict]:
        """
        Validate OCR blocks and extract entities.

        Args:
            blocks: List of OCR blocks

        Returns:
            Blocks with entity annotations
        """
        validated_blocks = []

        for block in blocks:
            validated_block = block.copy()

            if 'texto' in block:
                validation = self.validate_text(block['texto'])
                validated_block['entidades'] = validation['entidades']

            validated_blocks.append(validated_block)

        return validated_blocks

    def extract_key_entities(self, text: str) -> Dict:
        """
        Extract key entity types from text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with extracted key information
        """
        validation = self.validate_text(text)

        return {
            'personas': [e['texto'] for e in validation['entidades_persona']],
            'fechas': [e['texto'] for e in validation['entidades_fecha']],
            'montos': [e['texto'] for e in validation['entidades_monto']],
            'todas_entidades': [e['texto'] for e in validation['entidades']],
        }
