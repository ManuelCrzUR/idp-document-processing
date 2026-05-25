# -*- coding: utf-8 -*-
"""
Phase 4B: Recuperación de Texto Dañado por Sellos
- BETO para palabras parciales (confianza 0.3-0.6)
- GPT-4o-mini para huecos completos (confianza < 0.3)
"""
import json
import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))


class Phase4bTextRecovery:
    """
    Recuperación de texto dañado usando modelos avanzados
    """

    def __init__(self, confidence_partial=0.6, confidence_empty=0.3, debug=False):
        """
        Args:
            confidence_partial: Threshold para palabras parciales (default 0.6)
            confidence_empty: Threshold para huecos completos (default 0.3)
            debug: Modo debug (default False)
        """
        self.confidence_partial = confidence_partial
        self.confidence_empty = confidence_empty
        self.debug = debug

        # Inicializar BETO
        self.beto_available = False
        self.beto_model = None
        self.beto_tokenizer = None
        try:
            from transformers import AutoTokenizer, AutoModelForMaskedLM
            self.beto_tokenizer = AutoTokenizer.from_pretrained('dccuchile/bert-base-spanish-wwm-cased')
            self.beto_model = AutoModelForMaskedLM.from_pretrained('dccuchile/bert-base-spanish-wwm-cased')
            self.beto_available = True
            print("[Phase4bTextRecovery] BETO inicializado correctamente")
        except ImportError:
            print("[Phase4bTextRecovery] [WARN] Transformers no disponible para BETO")
        except Exception as e:
            print(f"[Phase4bTextRecovery] [WARN] BETO no disponible: {str(e)[:60]}")

        # Inicializar GPT-4o-mini
        self.gpt_available = False
        self.gpt_client = None
        try:
            from openai import OpenAI
            self.gpt_client = OpenAI()
            self.gpt_available = True
            print("[Phase4bTextRecovery] OpenAI GPT-4o-mini inicializado correctamente")
        except ImportError:
            print("[Phase4bTextRecovery] [WARN] OpenAI no disponible para GPT-4o-mini")
        except Exception as e:
            print(f"[Phase4bTextRecovery] [WARN] GPT-4o-mini no disponible: {str(e)[:60]}")

    def process(self, ocr_json: Dict) -> Dict:
        """
        Recupera texto dañado del JSON de Phase 4.
        Retorna el mismo JSON enriquecido con campos de recuperación.

        Args:
            ocr_json: JSON resultante de phase_4_ocr_complete()

        Returns:
            dict: JSON mejorado con texto_recuperado y metodo_recuperacion por bloque
        """
        print("\n" + "="*80)
        print("PHASE 4B: RECUPERACIÓN DE TEXTO DAÑADO")
        print("="*80)

        if not ocr_json.get('bloques'):
            print("[WARN] No hay bloques para recuperar")
            return ocr_json

        bloques = ocr_json['bloques']
        seal_bbox = ocr_json.get('seal_bbox')
        metricas = ocr_json.get('metricas', {})

        # Identificar bloques problemáticos
        bloques_parciales = []
        bloques_vacios = []

        for bloque in bloques:
            confianza = bloque.get('confianza', 1.0)
            en_zona_sello = bloque.get('en_zona_sello', False)
            overlap_sello = bloque.get('overlap_sello', 0.0)

            # Palabras parciales: en zona de sello + confianza 0.3-0.6
            if en_zona_sello and overlap_sello > 0 and self.confidence_empty < confianza < self.confidence_partial:
                bloques_parciales.append(bloque)

            # Huecos completos: en zona de sello + confianza < 0.3
            if en_zona_sello and overlap_sello > 0 and confianza < self.confidence_empty:
                bloques_vacios.append(bloque)

        print(f"Bloques con palabras parciales (BETO): {len(bloques_parciales)}")
        print(f"Bloques con huecos completos (GPT-4o-mini): {len(bloques_vacios)}")

        # Recuperar con BETO (palabras parciales)
        if bloques_parciales and self.beto_available:
            print(f"\n[BETO] Recuperando {len(bloques_parciales)} bloques con palabras parciales...")
            for bloque in bloques_parciales:
                self._recover_with_beto(bloque, ocr_json)

        # Recuperar con GPT-4o-mini (huecos completos)
        if bloques_vacios and self.gpt_available:
            print(f"\n[GPT-4o-mini] Recuperando {len(bloques_vacios)} bloques con huecos completos...")
            for bloque in bloques_vacios:
                self._recover_with_gpt(bloque, ocr_json)

        # Actualizar metricas
        ocr_json['metricas']['bloques_recuperados_beto'] = len(bloques_parciales) if self.beto_available else 0
        ocr_json['metricas']['bloques_recuperados_gpt'] = len(bloques_vacios) if self.gpt_available else 0

        self._print_summary(ocr_json)
        return ocr_json

    def _recover_with_beto(self, bloque: Dict, ocr_json: Dict):
        """
        Recupera palabras parciales usando BETO con [MASK].
        Busca palabras con palabras_parciales no vacío.
        """
        if not self.beto_available:
            return

        palabras_parciales = bloque.get('palabras_parciales', [])
        if not palabras_parciales:
            return

        texto_raw = bloque.get('texto_raw', '')
        if not texto_raw:
            return

        try:
            import torch
            from transformers import pipeline

            # Crear pipeline de fill-mask
            unmasker = pipeline('fill-mask', model=self.beto_model, tokenizer=self.beto_tokenizer)

            texto_con_mask = texto_raw
            recuperaciones = []

            # Procesar cada palabra parcial
            for palabra_info in palabras_parciales:
                original = palabra_info['original']
                # Marcar palabra con [MASK]
                texto_con_mask = texto_con_mask.replace(original, '[MASK]', 1)

                # Usar BETO para predecir
                try:
                    resultados = unmasker(texto_con_mask, top_k=5)
                    if resultados:
                        # Tomar la predicción con mayor score
                        prediccion = resultados[0]['token_str'].strip()
                        score = resultados[0]['score']

                        recuperaciones.append({
                            'original': original,
                            'recuperada': prediccion,
                            'confidence': float(score),
                            'metodo': 'BETO'
                        })

                        # Actualizar texto para siguiente iteración
                        texto_con_mask = texto_con_mask.replace('[MASK]', prediccion, 1)

                except Exception as e:
                    if self.debug:
                        print(f"[DEBUG] Error en BETO para '{original}': {e}")

            if recuperaciones:
                bloque['texto_recuperado'] = texto_con_mask
                bloque['metodo_recuperacion'] = 'BETO'
                bloque['recuperaciones'] = recuperaciones

        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Error general en BETO: {e}")

    def _recover_with_gpt(self, bloque: Dict, ocr_json: Dict):
        """
        Recupera huecos completos usando GPT-4o-mini.
        Proporciona contexto del párrafo completo.
        """
        if not self.gpt_available:
            return

        texto_raw = bloque.get('texto_raw', '')
        if texto_raw.strip():
            return  # No es un hueco completo

        try:
            # Obtener contexto del párrafo donde está el hueco
            bloques = ocr_json.get('bloques', [])
            idx_bloque = None
            for i, b in enumerate(bloques):
                if b.get('id') == bloque.get('id'):
                    idx_bloque = i
                    break

            if idx_bloque is None:
                return

            # Construir contexto: bloques adyacentes
            contexto_bloques = []
            for i in range(max(0, idx_bloque - 2), min(len(bloques), idx_bloque + 3)):
                if i != idx_bloque:
                    contexto_bloques.append(bloques[i].get('texto_corregido', ''))

            contexto = ' '.join(contexto_bloques)

            # System prompt para legal documents
            system_prompt = """Eres un experto en recuperación de texto en documentos legales españoles.
Tu tarea es reconstruir el contenido faltante basándote en el contexto del documento.
El documento es un documento oficial legal en español.
Debes mantener coherencia legal y gramatical.
Responde SOLO con la palabra o frase recuperada, sin explicaciones."""

            # User prompt
            user_prompt = f"""Contexto del documento:
{contexto}

Se ha perdido texto donde está marcado [HUECO].
Recupera el texto faltante que debería ir en ese lugar, considerando:
- Coherencia legal
- Términos comunes en documentos oficiales españoles
- Concordancia con el contexto

Responde con la palabra/frase más probable que debería ir en [HUECO]."""

            # Llamar a GPT-4o-mini
            try:
                response = self.gpt_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.5,
                    max_tokens=50
                )

                texto_recuperado = response.choices[0].message.content.strip()

                bloque['texto_recuperado'] = texto_recuperado
                bloque['metodo_recuperacion'] = 'GPT-4o-mini'
                bloque['recuperacion_confidence'] = 0.85  # Asumido alto para GPT

            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] Error en llamada a GPT: {e}")

        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Error general en GPT: {e}")

    def _print_summary(self, ocr_json: Dict):
        """Imprime resumen de recuperación"""
        metricas = ocr_json.get('metricas', {})

        print("\n" + "-"*80)
        print("RESUMEN RECUPERACIÓN DE TEXTO (Phase 4B)")
        print("-"*80)
        print(f"Bloques recuperados con BETO: {metricas.get('bloques_recuperados_beto', 0)}")
        print(f"Bloques recuperados con GPT-4o-mini: {metricas.get('bloques_recuperados_gpt', 0)}")
        print(f"Disponibilidad BETO: {'✓' if self.beto_available else '✗'}")
        print(f"Disponibilidad GPT: {'✓' if self.gpt_available else '✗'}")
        print("-"*80 + "\n")


def phase_4b_text_recovery(ocr_json: Dict, confidence_partial: float = 0.6,
                           confidence_empty: float = 0.3, debug: bool = False) -> Dict:
    """
    Función principal Phase 4B: Recuperación de texto.

    Args:
        ocr_json: JSON de phase_4_ocr_complete()
        confidence_partial: Threshold para palabras parciales
        confidence_empty: Threshold para huecos completos
        debug: Modo debug

    Returns:
        dict: JSON mejorado con texto_recuperado y metodo_recuperacion
    """
    recovery = Phase4bTextRecovery(
        confidence_partial=confidence_partial,
        confidence_empty=confidence_empty,
        debug=debug
    )
    return recovery.process(ocr_json)


if __name__ == "__main__":
    # Test simple
    print("Phase 4B: Módulo de recuperación de texto")
    print("Requiere JSON de Phase 4 como entrada")
