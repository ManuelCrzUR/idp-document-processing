# -*- coding: utf-8 -*-
"""
Phase 5: Base utilities para evaluación y métricas
Contiene funciones compartidas para CER/WER, normalización de texto, etc.
"""
import re
import numpy as np
from typing import Tuple, List, Dict
from pathlib import Path


class TextNormalizer:
    """Normaliza texto para comparación justa"""

    @staticmethod
    def normalize(text: str) -> str:
        """
        Normaliza texto:
        - Convierte a minúsculas
        - Elimina puntuación no significativa
        - Elimina espacios extra
        - Elimina saltos de línea múltiples
        """
        if not text:
            return ""

        # Convertir a minúsculas
        text = text.lower()

        # Eliminar saltos de línea múltiples
        text = re.sub(r'\n+', ' ', text)

        # Eliminar puntuación no significativa (mantener apóstrofos, guiones en palabras)
        # Pero eliminar: . , ; : ! ? " ' - al final/inicio
        text = re.sub(r'[,;:!?"\']', '', text)

        # Eliminar espacios múltiples
        text = re.sub(r'\s+', ' ', text)

        # Strip espacios al inicio y final
        text = text.strip()

        return text

    @staticmethod
    def normalize_for_comparison(text: str) -> List[str]:
        """
        Normaliza y divide en palabras para WER
        """
        text = TextNormalizer.normalize(text)
        # Dividir en palabras
        words = text.split()
        return words


class LevenshteinCalculator:
    """Calcula distancia de Levenshtein desde cero"""

    @staticmethod
    def distance(s1: str, s2: str) -> int:
        """
        Calcula distancia de Levenshtein entre dos strings.
        Implementación dinámica sin dependencias externas.
        """
        if len(s1) < len(s2):
            return LevenshteinCalculator.distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        # Crear matriz de DP
        previous_row = range(len(s2) + 1)

        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # j+1 en lugar de j porque ranged previo tiene tamaño len(s2)+1
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))

            previous_row = current_row

        return previous_row[-1]


class MetricsCalculator:
    """Calcula CER y WER"""

    @staticmethod
    def calculate_cer(reference: str, hypothesis: str) -> float:
        """
        Calcula Character Error Rate (CER).
        CER = (S + D + I) / N
        donde S=sustituciones, D=deletions, I=insertions, N=caracteres referencia
        """
        reference = TextNormalizer.normalize(reference)
        hypothesis = TextNormalizer.normalize(hypothesis)

        if len(reference) == 0:
            return 0.0 if len(hypothesis) == 0 else 100.0

        distance = LevenshteinCalculator.distance(reference, hypothesis)
        cer = (distance / len(reference)) * 100.0

        return min(100.0, cer)  # Clamear a 100%

    @staticmethod
    def calculate_wer(reference: str, hypothesis: str) -> float:
        """
        Calcula Word Error Rate (WER).
        WER = (S + D + I) / N
        donde S=sustituciones, D=deletions, I=insertions, N=palabras referencia
        """
        ref_words = TextNormalizer.normalize_for_comparison(reference)
        hyp_words = TextNormalizer.normalize_for_comparison(hypothesis)

        if len(ref_words) == 0:
            return 0.0 if len(hyp_words) == 0 else 100.0

        distance = LevenshteinCalculator.distance(
            ' '.join(ref_words),
            ' '.join(hyp_words)
        )
        wer = (distance / len(ref_words)) * 100.0

        return min(100.0, wer)  # Clamear a 100%

    @staticmethod
    def calculate_both(reference: str, hypothesis: str) -> Tuple[float, float]:
        """Calcula CER y WER en una sola pasada"""
        cer = MetricsCalculator.calculate_cer(reference, hypothesis)
        wer = MetricsCalculator.calculate_wer(reference, hypothesis)
        return cer, wer


class FileHelper:
    """Helpers para manejo de archivos"""

    @staticmethod
    def find_ground_truth_pairs(gt_dir: str, results_dir: str, ext: str = '.txt') -> List[Tuple[Path, Path]]:
        """
        Encuentra pares de archivo de ground truth y resultado emparejando por nombre.

        Args:
            gt_dir: Directorio con ground truth
            results_dir: Directorio con resultados
            ext: Extensión de archivo (.txt, .json, etc)

        Returns:
            Lista de tuplas (ruta_gt, ruta_resultado)
        """
        gt_path = Path(gt_dir)
        results_path = Path(results_dir)

        if not gt_path.exists():
            raise FileNotFoundError(f"Directorio ground truth no existe: {gt_dir}")
        if not results_path.exists():
            raise FileNotFoundError(f"Directorio resultados no existe: {results_dir}")

        pairs = []
        for gt_file in gt_path.glob(f"*{ext}"):
            # Buscar resultado con mismo nombre
            result_file = results_path / gt_file.name
            if result_file.exists():
                pairs.append((gt_file, result_file))

        return sorted(pairs)

    @staticmethod
    def read_text_file(file_path: Path) -> str:
        """Lee archivo de texto de forma segura"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Error leyendo {file_path}: {e}")

    @staticmethod
    def read_image_file(file_path: Path):
        """Lee archivo de imagen usando cv2"""
        import cv2
        try:
            img = cv2.imread(str(file_path))
            if img is None:
                raise ValueError(f"Imagen no se pudo cargar: {file_path}")
            return img
        except Exception as e:
            raise IOError(f"Error leyendo imagen {file_path}: {e}")


class ResultsWriter:
    """Escribe resultados en JSON y CSV"""

    @staticmethod
    def write_json(data: Dict, output_path: Path):
        """Escribe resultados a JSON"""
        import json
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON guardado: {output_path}")

    @staticmethod
    def write_csv(data: List[Dict], output_path: Path):
        """Escribe resultados a CSV"""
        import csv
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not data:
            print(f"⚠️ No hay datos para escribir CSV: {output_path}")
            return

        # Obtener todos los campos
        fieldnames = set()
        for row in data:
            fieldnames.update(row.keys())
        fieldnames = sorted(list(fieldnames))

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

        print(f"✅ CSV guardado: {output_path}")


if __name__ == "__main__":
    # Test de normalización
    text = "Ministerio  de  Economía.\n\nAcuerdo 123-456!"
    normalized = TextNormalizer.normalize(text)
    print(f"Original: {repr(text)}")
    print(f"Normalizado: {repr(normalized)}")

    # Test de Levenshtein
    dist = LevenshteinCalculator.distance("ministerio", "ministério")
    print(f"\nDistancia 'ministerio' -> 'ministério': {dist}")

    # Test de CER/WER
    ref = "Ministerio de Economía"
    hyp = "Ministério de Economiá"
    cer, wer = MetricsCalculator.calculate_both(ref, hyp)
    print(f"\nReferencia: {ref}")
    print(f"Hipótesis: {hyp}")
    print(f"CER: {cer:.2f}%")
    print(f"WER: {wer:.2f}%")
