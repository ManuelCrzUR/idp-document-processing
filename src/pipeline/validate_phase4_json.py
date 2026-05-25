# -*- coding: utf-8 -*-
"""
Validador de esquema JSON para Phase 4 OCR enriquecido
Verifica que todos los campos necesarios estén presentes
"""
import json
from typing import Dict, List, Tuple
from pathlib import Path


class Phase4JSONValidator:
    """Valida estructura del JSON de Phase 4"""

    # Campos requeridos por bloque
    REQUIRED_BLOQUE_FIELDS = {
        'id': int,
        'texto_raw': str,
        'texto_corregido': str,
        'confianza': float,
        'baja_confianza': bool,
        'motor': str,
        'coordenadas': list,
        'en_zona_sello': bool,
        'overlap_sello': float,
        'palabras_parciales': list,
        'fue_corregido': bool,
        'distancia_correccion': float,
        'entidades': list
    }

    # Campos requeridos en metricas
    REQUIRED_METRICAS_FIELDS = {
        'total_bloques': int,
        'bloques_baja_confianza': int,
        'bloques_en_zona_sello': int,
        'confianza_promedio': float,
        'palabras_corregidas': int,
        'entidades_detectadas': int,
        'confidence_threshold': float,
        'motors_usados': list,
        'procesadores_usados': list
    }

    @staticmethod
    def validate(ocr_json: Dict) -> Tuple[bool, List[str]]:
        """
        Valida JSON de Phase 4.
        Retorna (es_válido, lista_de_errores)
        """
        errores = []

        # Validar campos principales
        if 'timestamp' not in ocr_json:
            errores.append("❌ Falta campo: timestamp")
        if 'imagen_size' not in ocr_json:
            errores.append("❌ Falta campo: imagen_size")
        if 'seal_bbox' not in ocr_json:
            errores.append("❌ Falta campo: seal_bbox")
        if 'texto_completo' not in ocr_json:
            errores.append("❌ Falta campo: texto_completo")
        if 'bloques' not in ocr_json:
            errores.append("❌ Falta campo: bloques")
            return False, errores

        # Validar métricas
        if 'metricas' not in ocr_json:
            errores.append("❌ Falta campo: metricas")
        else:
            metricas_errores = Phase4JSONValidator._validate_metricas(ocr_json['metricas'])
            errores.extend(metricas_errores)

        # Validar bloques
        bloques = ocr_json['bloques']
        if not isinstance(bloques, list):
            errores.append("❌ 'bloques' debe ser una lista")
            return False, errores

        for idx, bloque in enumerate(bloques):
            bloque_errores = Phase4JSONValidator._validate_bloque(bloque, idx)
            errores.extend(bloque_errores)

        es_válido = len(errores) == 0
        return es_válido, errores

    @staticmethod
    def _validate_metricas(metricas: Dict) -> List[str]:
        """Valida sección de métricas"""
        errores = []

        for campo, tipo_esperado in Phase4JSONValidator.REQUIRED_METRICAS_FIELDS.items():
            if campo not in metricas:
                errores.append(f"❌ Métrica faltante: {campo}")
            else:
                if not isinstance(metricas[campo], tipo_esperado):
                    errores.append(f"❌ Métrica '{campo}' tiene tipo incorrecto. "
                                 f"Esperado: {tipo_esperado.__name__}, "
                                 f"Obtenido: {type(metricas[campo]).__name__}")

        return errores

    @staticmethod
    def _validate_bloque(bloque: Dict, idx: int) -> List[str]:
        """Valida estructura de un bloque"""
        errores = []

        for campo, tipo_esperado in Phase4JSONValidator.REQUIRED_BLOQUE_FIELDS.items():
            if campo not in bloque:
                errores.append(f"❌ Bloque #{idx}: Falta campo '{campo}'")
            else:
                valor = bloque[campo]
                if tipo_esperado == list:
                    if not isinstance(valor, list):
                        errores.append(f"❌ Bloque #{idx}: '{campo}' debe ser lista, "
                                     f"pero es {type(valor).__name__}")
                elif not isinstance(valor, tipo_esperado):
                    errores.append(f"❌ Bloque #{idx}: '{campo}' tiene tipo incorrecto. "
                                 f"Esperado: {tipo_esperado.__name__}, "
                                 f"Obtenido: {type(valor).__name__}")

        # Validación especial de palabras_parciales
        if 'palabras_parciales' in bloque:
            palabras_parciales = bloque['palabras_parciales']
            for p_idx, palabra_info in enumerate(palabras_parciales):
                if not isinstance(palabra_info, dict):
                    errores.append(f"❌ Bloque #{idx}: palabras_parciales[{p_idx}] "
                                 f"debe ser dict")
                else:
                    campos_requeridos = ['indice', 'original', 'corregida', 'distancia']
                    for campo_req in campos_requeridos:
                        if campo_req not in palabra_info:
                            errores.append(f"❌ Bloque #{idx}: palabras_parciales[{p_idx}] "
                                         f"falta campo '{campo_req}'")

        return errores

    @staticmethod
    def print_validation_report(ocr_json: Dict):
        """Imprime reporte de validación en consola"""
        es_válido, errores = Phase4JSONValidator.validate(ocr_json)

        print("\n" + "="*80)
        print("VALIDACIÓN JSON PHASE 4 - ENRIQUECIDO")
        print("="*80)

        if es_válido:
            print("✅ JSON VÁLIDO - Todos los campos están presentes y correctos")
            print("\n📊 Estructura verificada:")
            print(f"   - Timestamp: {ocr_json.get('timestamp')}")
            print(f"   - Imagen: {ocr_json.get('imagen_size')}")
            print(f"   - Bloques totales: {len(ocr_json.get('bloques', []))}")
            print(f"   - Bloques baja confianza: {ocr_json['metricas'].get('bloques_baja_confianza', 0)}")
            print(f"   - Bloques en zona sello: {ocr_json['metricas'].get('bloques_en_zona_sello', 0)}")
        else:
            print("❌ JSON INVÁLIDO - Se encontraron los siguientes errores:\n")
            for error in errores:
                print(f"   {error}")

        print("\n" + "="*80)

        return es_válido

    @staticmethod
    def print_bloque_sample(ocr_json: Dict, bloque_idx: int = 0):
        """Muestra un bloque de ejemplo con estructura completa"""
        bloques = ocr_json.get('bloques', [])
        if not bloques or bloque_idx >= len(bloques):
            print(f"No hay bloque #{bloque_idx}")
            return

        bloque = bloques[bloque_idx]
        print("\n" + "="*80)
        print(f"EJEMPLO DE BLOQUE #{bloque_idx}")
        print("="*80)
        print(json.dumps(bloque, ensure_ascii=False, indent=2))
        print("="*80)


def validate_json_file(json_path: str) -> bool:
    """Valida un archivo JSON"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            ocr_json = json.load(f)

        is_valid = Phase4JSONValidator.print_validation_report(ocr_json)

        if is_valid and len(ocr_json.get('bloques', [])) > 0:
            Phase4JSONValidator.print_bloque_sample(ocr_json, 0)

        return is_valid
    except Exception as e:
        print(f"❌ Error al leer archivo JSON: {e}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        json_path = sys.argv[1]
        validate_json_file(json_path)
    else:
        print("Uso: python validate_phase4_json.py <ruta_al_json>")
