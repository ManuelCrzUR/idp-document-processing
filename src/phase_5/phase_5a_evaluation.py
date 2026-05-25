# -*- coding: utf-8 -*-
"""
Phase 5A: Evaluación automática CER/WER
Compara resultados OCR contra ground truth en documentos sintéticos
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

from phase_5_base import (
    TextNormalizer,
    MetricsCalculator,
    FileHelper,
    ResultsWriter
)


class Phase5aEvaluation:
    """Evaluación automática CER/WER en Grupo A (documentos sintéticos)"""

    def __init__(self, confidence_threshold: float = 0.6, debug: bool = False):
        """
        Args:
            confidence_threshold: Threshold para baja confianza
            debug: Modo debug
        """
        self.confidence_threshold = confidence_threshold
        self.debug = debug
        self.results = []

    def evaluate(self, ground_truth_dir: str, results_dir: str) -> Dict:
        """
        Evalúa CER/WER en 5 condiciones.

        Args:
            ground_truth_dir: Directorio con textos ground truth
            results_dir: Directorio donde guardar resultados

        Returns:
            dict: Resultados consolidados
        """
        print("\n" + "="*80)
        print("PHASE 5A: EVALUACIÓN AUTOMÁTICA CER/WER (Grupo A - Sintético)")
        print("="*80)

        gt_dir = Path(ground_truth_dir)
        res_dir = Path(results_dir)
        res_dir.mkdir(parents=True, exist_ok=True)

        # Encontrar pares
        try:
            pairs = FileHelper.find_ground_truth_pairs(gt_dir, res_dir)
            print(f"✓ Encontrados {len(pairs)} pares documento/ground truth")
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            return self._empty_result()

        if not pairs:
            print("❌ No se encontraron pares")
            return self._empty_result()

        # Procesar cada par
        self.results = []
        for idx, (gt_file, result_file) in enumerate(pairs, 1):
            print(f"\n[{idx}/{len(pairs)}] Procesando: {gt_file.name}")
            self._process_pair(gt_file, result_file)

        # Consolidar resultados
        consolidado = self._consolidate_results()

        # Guardar
        output_json = res_dir / "resultados_5a.json"
        output_csv = res_dir / "resultados_5a.csv"

        ResultsWriter.write_json(consolidado, output_json)
        ResultsWriter.write_csv(self.results, output_csv)

        # Imprimir resumen
        self._print_summary(consolidado)

        return consolidado

    def _process_pair(self, gt_file: Path, result_file: Path):
        """Procesa un par documento/ground truth"""
        try:
            # Leer textos
            gt_text = FileHelper.read_text_file(gt_file)
            result_text = FileHelper.read_text_file(result_file)

            # Calcular métricas
            cer, wer = MetricsCalculator.calculate_both(gt_text, result_text)

            # Registrar
            self.results.append({
                'documento': gt_file.stem,
                'cer': round(cer, 2),
                'wer': round(wer, 2),
                'gt_length': len(TextNormalizer.normalize(gt_text)),
                'result_length': len(TextNormalizer.normalize(result_text))
            })

            print(f"  CER: {cer:.2f}% | WER: {wer:.2f}%")

        except Exception as e:
            print(f"  ❌ Error procesando {gt_file.name}: {e}")
            if self.debug:
                raise

    def _consolidate_results(self) -> Dict:
        """Consolida resultados y calcula estadísticas"""
        if not self.results:
            return self._empty_result()

        cers = [r['cer'] for r in self.results]
        wers = [r['wer'] for r in self.results]

        # Calcular estadísticas
        cer_mean = sum(cers) / len(cers)
        cer_std = (sum((x - cer_mean) ** 2 for x in cers) / len(cers)) ** 0.5
        cer_min = min(cers)
        cer_max = max(cers)

        wer_mean = sum(wers) / len(wers)
        wer_std = (sum((x - wer_mean) ** 2 for x in wers) / len(wers)) ** 0.5
        wer_min = min(wers)
        wer_max = max(wers)

        # Hipótesis central: CER se reduce >= 5 puntos
        hypothesis_met = False  # En producc ión, compararía contra baseline
        delta_cer = 0.0  # Sería diferencia respecto baseline

        return {
            'timestamp': datetime.now().isoformat(),
            'tipo': 'Automática',
            'grupo': 'A (Sintético)',
            'total_documentos': len(self.results),
            'validador_humano': False,
            'condiciones': [
                'Baseline crudo',
                'Pipeline HSV',
                'Pipeline YOLO',
                'Pipeline + Post-corrección',
                'Pipeline + Recuperación BETO+GPT'
            ],
            'cer': {
                'media': round(cer_mean, 2),
                'std': round(cer_std, 2),
                'min': round(cer_min, 2),
                'max': round(cer_max, 2)
            },
            'wer': {
                'media': round(wer_mean, 2),
                'std': round(wer_std, 2),
                'min': round(wer_min, 2),
                'max': round(wer_max, 2)
            },
            'hipotesis': {
                'condicion': 'CER debe reducirse >= 5 puntos respecto baseline',
                'cumplida': hypothesis_met,
                'delta_cer_respecto_baseline': delta_cer
            },
            'documentos': self.results
        }

    def _empty_result(self) -> Dict:
        """Retorna resultado vacío"""
        return {
            'timestamp': datetime.now().isoformat(),
            'tipo': 'Automática',
            'grupo': 'A (Sintético)',
            'total_documentos': 0,
            'validador_humano': False,
            'condiciones': [],
            'cer': {'media': 0, 'std': 0, 'min': 0, 'max': 0},
            'wer': {'media': 0, 'std': 0, 'min': 0, 'max': 0},
            'hipotesis': {
                'condicion': 'CER debe reducirse >= 5 puntos respecto baseline',
                'cumplida': False,
                'delta_cer_respecto_baseline': 0
            },
            'documentos': []
        }

    def _print_summary(self, result: Dict):
        """Imprime resumen"""
        cer = result['cer']
        wer = result['wer']

        print("\n" + "-"*80)
        print("RESUMEN PHASE 5A")
        print("-"*80)
        print(f"Total documentos: {result['total_documentos']}")
        print(f"\nCER (Character Error Rate):")
        print(f"  Media:     {cer['media']:.2f}%")
        print(f"  Std Dev:   {cer['std']:.2f}%")
        print(f"  Rango:     {cer['min']:.2f}% - {cer['max']:.2f}%")
        print(f"\nWER (Word Error Rate):")
        print(f"  Media:     {wer['media']:.2f}%")
        print(f"  Std Dev:   {wer['std']:.2f}%")
        print(f"  Rango:     {wer['min']:.2f}% - {wer['max']:.2f}%")
        print(f"\nHipótesis central: {result['hipotesis']['condicion']}")
        print(f"  Cumplida: {'✅' if result['hipotesis']['cumplida'] else '❌'}")
        print("-"*80 + "\n")


def phase_5a_evaluation(
    ground_truth_dir: str,
    results_dir: str,
    confidence_threshold: float = 0.6,
    debug: bool = False
) -> Dict:
    """
    Función principal Phase 5A.

    Args:
        ground_truth_dir: Directorio con ground truth
        results_dir: Directorio para guardar resultados
        confidence_threshold: Threshold para confianza
        debug: Modo debug

    Returns:
        dict: Resultados consolidados
    """
    evaluator = Phase5aEvaluation(confidence_threshold=confidence_threshold, debug=debug)
    return evaluator.evaluate(ground_truth_dir, results_dir)


if __name__ == "__main__":
    # Test
    gt_dir = "C:/Users/manue/Documents/Desktop_Archive_2026-03-14/Folders/PR_COMPUTER_VISION/idp-project/datos/spanishocr/texts/"
    res_dir = "results/phase_5a/"

    result = phase_5a_evaluation(gt_dir, res_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
