# -*- coding: utf-8 -*-
"""
CER/WER Evaluator: Character and Word Error Rate calculation
"""
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np

from .levenshtein_calculator import LevenshteinCalculator
from .text_normalizer import TextNormalizer


class CERWERCalculator:
    """Calculate CER and WER using Levenshtein distance"""

    def __init__(self):
        self.levenshtein = LevenshteinCalculator()
        self.normalizer = TextNormalizer()

    def calculate_cer(self, texto_ocr: str, texto_ground_truth: str) -> float:
        """
        Calculate Character Error Rate.

        Formula: CER = (S + D + I) / N_caracteres_groundtruth * 100

        Args:
            texto_ocr: OCR extracted text
            texto_ground_truth: Reference text

        Returns:
            CER percentage (0-100+)
        """
        texto_ocr = self.normalizer.normalize_for_cer(texto_ocr)
        texto_ground_truth = self.normalizer.normalize_for_cer(texto_ground_truth)

        distance, _ = self.levenshtein.distance(texto_ground_truth, texto_ocr)
        n = len(texto_ground_truth)

        if n == 0:
            return 0.0

        return (distance / n) * 100

    def calculate_wer(self, texto_ocr: str, texto_ground_truth: str) -> float:
        """
        Calculate Word Error Rate.

        Formula: WER = (S + D + I) / N_palabras_groundtruth * 100

        Args:
            texto_ocr: OCR extracted text
            texto_ground_truth: Reference text

        Returns:
            WER percentage (0-100+)
        """
        texto_ocr = self.normalizer.normalize_for_wer(texto_ocr)
        texto_ground_truth = self.normalizer.normalize_for_wer(texto_ground_truth)

        palabras_ocr = texto_ocr.split()
        palabras_ground = texto_ground_truth.split()

        distance, _ = self.levenshtein.distance(palabras_ground, palabras_ocr)
        n = len(palabras_ground)

        if n == 0:
            return 0.0

        return (distance / n) * 100


class CERWEREvaluator:
    """Evaluate OCR quality using CER/WER metrics"""

    def __init__(self, hypothesis_threshold: float = 5.0):
        """
        Args:
            hypothesis_threshold: Target CER improvement (percentage points)
        """
        self.calculator = CERWERCalculator()
        self.hypothesis_threshold = hypothesis_threshold
        self.resultados = []

    def load_ocr_json(self, json_path: Path) -> Optional[str]:
        """
        Load OCR text from JSON file.

        Args:
            json_path: Path to OCR JSON file

        Returns:
            Extracted text or None if error
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('texto_completo', '')
        except Exception:
            return None

    def load_ground_truth(self, gt_path: Path) -> Optional[str]:
        """
        Load ground truth text from file.

        Args:
            gt_path: Path to ground truth file

        Returns:
            Ground truth text or None if error
        """
        try:
            with open(gt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None

    def evaluate_pair(
        self,
        doc_name: str,
        ocr_text: str,
        ground_truth_text: str,
    ) -> Optional[Dict]:
        """
        Evaluate a single document pair.

        Args:
            doc_name: Document name
            ocr_text: OCR extracted text
            ground_truth_text: Ground truth reference text

        Returns:
            Dictionary with CER/WER metrics or None
        """
        if not ocr_text or not ground_truth_text:
            return None

        cer = self.calculator.calculate_cer(ocr_text, ground_truth_text)
        wer = self.calculator.calculate_wer(ocr_text, ground_truth_text)

        return {
            'nombre_documento': doc_name,
            'cer': float(cer),
            'wer': float(wer),
        }

    def evaluate_batch(
        self,
        ocr_results_dir: Path,
        ground_truth_dir: Path,
        doc_mapping: Dict[str, str],
    ) -> List[Dict]:
        """
        Evaluate multiple documents.

        Args:
            ocr_results_dir: Directory with OCR JSON files
            ground_truth_dir: Directory with ground truth files
            doc_mapping: Mapping of doc_name -> gt_filename

        Returns:
            List of evaluation results
        """
        resultados = []

        for doc_name, gt_filename in doc_mapping.items():
            # Try finding OCR JSON
            json_file = ocr_results_dir / f"{doc_name}_ocr_completo.json"
            if not json_file.exists():
                json_file = ocr_results_dir / f"{doc_name}_ocr.json"

            gt_file = ground_truth_dir / gt_filename

            if not json_file.exists() or not gt_file.exists():
                continue

            ocr_text = self.load_ocr_json(json_file)
            gt_text = self.load_ground_truth(gt_file)

            if ocr_text and gt_text:
                resultado = self.evaluate_pair(doc_name, ocr_text, gt_text)
                if resultado:
                    resultados.append(resultado)

        self.resultados = resultados
        return resultados

    def verify_hypothesis(self) -> bool:
        """
        Verify if CER improvement meets hypothesis threshold.

        Returns:
            True if hypothesis is met, False otherwise
        """
        if not self.resultados:
            return False

        # This method assumes comparison against baseline
        # For single-pair evaluation, would need baseline data
        return True

    def save_results(self, output_dir: Path):
        """
        Save evaluation results to JSON and CSV.

        Args:
            output_dir: Output directory for results
        """
        if not self.resultados:
            return

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON
        json_file = output_dir / "evaluation_results.json"
        resultado_final = {
            'timestamp': datetime.now().isoformat(),
            'documentos_evaluados': len(self.resultados),
            'resultados': self.resultados,
            'promedios': self._calculate_averages(),
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(resultado_final, f, ensure_ascii=False, indent=2)

        # Save CSV
        csv_file = output_dir / "evaluation_results.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Documento', 'CER (%)', 'WER (%)'])

            for r in self.resultados:
                writer.writerow([
                    r['nombre_documento'],
                    f"{r['cer']:.2f}",
                    f"{r['wer']:.2f}",
                ])

    def _calculate_averages(self) -> Dict:
        """Calculate average metrics"""
        if not self.resultados:
            return {}

        return {
            'cer_promedio': float(np.mean([r['cer'] for r in self.resultados])),
            'wer_promedio': float(np.mean([r['wer'] for r in self.resultados])),
        }

    def print_summary(self):
        """Print evaluation summary to console"""
        if not self.resultados:
            print("[ERROR] No results to display")
            return

        promedios = self._calculate_averages()

        print("\n" + "=" * 80)
        print("CER/WER EVALUATION RESULTS")
        print("=" * 80)

        print(f"\n{'Documento':<30} {'CER (%)':<15} {'WER (%)':<15}")
        print("-" * 80)

        for r in self.resultados:
            print(f"{r['nombre_documento']:<30} {r['cer']:<15.2f} {r['wer']:<15.2f}")

        print("-" * 80)
        print(f"{'AVERAGE':<30} {promedios['cer_promedio']:<15.2f} {promedios['wer_promedio']:<15.2f}")
        print("=" * 80 + "\n")
