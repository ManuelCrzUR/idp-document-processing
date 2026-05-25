# -*- coding: utf-8 -*-
"""
Phase 5C: Evaluación de detección - IoU (Intersection over Union)
Compara máscaras de detección HSV vs YOLO contra ground truth
"""
import json
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime

from phase_5_base import FileHelper, ResultsWriter


class Phase5cDetection:
    """Evaluación de detección con IoU"""

    def __init__(self, iou_threshold: float = 0.5, debug: bool = False):
        """
        Args:
            iou_threshold: Threshold para considerar detección válida
            debug: Modo debug
        """
        self.iou_threshold = iou_threshold
        self.debug = debug
        self.results = []

    def evaluate(
        self,
        masks_gt_dir: str,
        hsv_masks_dir: str,
        yolo_masks_dir: str,
        results_dir: str
    ) -> Dict:
        """
        Evalúa detección calculando IoU.

        Args:
            masks_gt_dir: Directorio con máscaras ground truth binarias
            hsv_masks_dir: Directorio con máscaras HSV predichas
            yolo_masks_dir: Directorio con máscaras YOLO predichas
            results_dir: Directorio para guardar resultados

        Returns:
            dict: Resultados consolidados con IoU medio por método
        """
        print("\n" + "="*80)
        print("PHASE 5C: EVALUACIÓN DE DETECCIÓN - IoU (HSV vs YOLO)")
        print("="*80)

        gt_dir = Path(masks_gt_dir)
        hsv_dir = Path(hsv_masks_dir)
        yolo_dir = Path(yolo_masks_dir)
        res_dir = Path(results_dir)
        res_dir.mkdir(parents=True, exist_ok=True)

        # Encontrar pares
        try:
            gt_files = sorted(gt_dir.glob("*.png"))
            print(f"✓ Encontradas {len(gt_files)} máscaras ground truth")
        except Exception as e:
            print(f"❌ Error: {e}")
            return self._empty_result()

        if not gt_files:
            print("⚠️ No se encontraron máscaras ground truth")
            return self._empty_result()

        # Procesar cada máscara
        self.results = []
        for idx, gt_file in enumerate(gt_files, 1):
            hsv_file = hsv_dir / gt_file.name
            yolo_file = yolo_dir / gt_file.name

            if hsv_file.exists() and yolo_file.exists():
                print(f"\n[{idx}/{len(gt_files)}] Evaluando: {gt_file.name}")
                self._process_masks(gt_file, hsv_file, yolo_file)
            else:
                print(f"\n[{idx}/{len(gt_files)}] ⚠️ Falta máscara para: {gt_file.name}")

        # Consolidar
        consolidado = self._consolidate_results()

        # Guardar
        output_json = res_dir / "resultados_5c.json"
        output_csv = res_dir / "resultados_5c.csv"

        ResultsWriter.write_json(consolidado, output_json)
        ResultsWriter.write_csv(self.results, output_csv)

        # Imprimir resumen
        self._print_summary(consolidado)

        return consolidado

    def _process_masks(self, gt_file: Path, hsv_file: Path, yolo_file: Path):
        """Procesa un trio de máscaras"""
        try:
            # Cargar máscaras binarias
            import cv2
            mask_gt = cv2.imread(str(gt_file), cv2.IMREAD_GRAYSCALE)
            mask_hsv = cv2.imread(str(hsv_file), cv2.IMREAD_GRAYSCALE)
            mask_yolo = cv2.imread(str(yolo_file), cv2.IMREAD_GRAYSCALE)

            if mask_gt is None or mask_hsv is None or mask_yolo is None:
                raise ValueError("No se pudieron cargar las máscaras")

            # Binarizar (blanco=255 es sello, negro=0 es fondo)
            mask_gt_bin = (mask_gt > 127).astype(np.uint8)
            mask_hsv_bin = (mask_hsv > 127).astype(np.uint8)
            mask_yolo_bin = (mask_yolo > 127).astype(np.uint8)

            # Calcular IoU
            iou_hsv = self._calculate_iou(mask_gt_bin, mask_hsv_bin)
            iou_yolo = self._calculate_iou(mask_gt_bin, mask_yolo_bin)

            # Registrar
            self.results.append({
                'documento': gt_file.stem,
                'iou_hsv': round(iou_hsv, 4),
                'iou_yolo': round(iou_yolo, 4),
                'winner': 'YOLO' if iou_yolo > iou_hsv else ('HSV' if iou_hsv > iou_yolo else 'Empate'),
                'gt_pixels': int(np.sum(mask_gt_bin)),
                'hsv_pixels': int(np.sum(mask_hsv_bin)),
                'yolo_pixels': int(np.sum(mask_yolo_bin))
            })

            print(f"  IoU HSV:  {iou_hsv:.4f}")
            print(f"  IoU YOLO: {iou_yolo:.4f}")
            print(f"  Winner: {self.results[-1]['winner']}")

        except Exception as e:
            print(f"  ❌ Error procesando máscaras: {e}")
            if self.debug:
                raise

    @staticmethod
    def _calculate_iou(mask_gt: np.ndarray, mask_pred: np.ndarray) -> float:
        """
        Calcula Intersection over Union.
        IoU = (A ∩ B) / (A ∪ B)
        """
        intersection = np.logical_and(mask_gt, mask_pred).sum()
        union = np.logical_or(mask_gt, mask_pred).sum()

        if union == 0:
            return 1.0 if intersection == 0 else 0.0

        iou = intersection / union
        return float(iou)

    def _consolidate_results(self) -> Dict:
        """Consolida resultados"""
        if not self.results:
            return self._empty_result()

        iou_hsv_list = [r['iou_hsv'] for r in self.results]
        iou_yolo_list = [r['iou_yolo'] for r in self.results]

        # Estadísticas HSV
        iou_hsv_mean = sum(iou_hsv_list) / len(iou_hsv_list)
        iou_hsv_std = (sum((x - iou_hsv_mean) ** 2 for x in iou_hsv_list) / len(iou_hsv_list)) ** 0.5

        # Estadísticas YOLO
        iou_yolo_mean = sum(iou_yolo_list) / len(iou_yolo_list)
        iou_yolo_std = (sum((x - iou_yolo_mean) ** 2 for x in iou_yolo_list) / len(iou_yolo_list)) ** 0.5

        # Ganador general
        winner = 'YOLO' if iou_yolo_mean > iou_hsv_mean else ('HSV' if iou_hsv_mean > iou_yolo_mean else 'Empate')

        return {
            'timestamp': datetime.now().isoformat(),
            'total_imagenes': len(self.results),
            'iou_threshold': self.iou_threshold,
            'hsv': {
                'iou_media': round(iou_hsv_mean, 4),
                'iou_std': round(iou_hsv_std, 4),
                'iou_min': round(min(iou_hsv_list), 4),
                'iou_max': round(max(iou_hsv_list), 4)
            },
            'yolo': {
                'iou_media': round(iou_yolo_mean, 4),
                'iou_std': round(iou_yolo_std, 4),
                'iou_min': round(min(iou_yolo_list), 4),
                'iou_max': round(max(iou_yolo_list), 4)
            },
            'comparativa': {
                'winner': winner,
                'diferencia_iou': round(iou_yolo_mean - iou_hsv_mean, 4)
            },
            'documentos': self.results
        }

    def _empty_result(self) -> Dict:
        """Retorna resultado vacío"""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_imagenes': 0,
            'iou_threshold': self.iou_threshold,
            'hsv': {'iou_media': 0, 'iou_std': 0, 'iou_min': 0, 'iou_max': 0},
            'yolo': {'iou_media': 0, 'iou_std': 0, 'iou_min': 0, 'iou_max': 0},
            'comparativa': {'winner': 'N/A', 'diferencia_iou': 0},
            'documentos': []
        }

    def _print_summary(self, result: Dict):
        """Imprime resumen"""
        hsv = result['hsv']
        yolo = result['yolo']
        comp = result['comparativa']

        print("\n" + "-"*80)
        print("RESUMEN PHASE 5C - EVALUACIÓN DE DETECCIÓN (IoU)")
        print("-"*80)
        print(f"Total imágenes: {result['total_imagenes']}")
        print(f"\nHSV Chromatic Separation:")
        print(f"  IoU Media:   {hsv['iou_media']:.4f}")
        print(f"  Std Dev:     {hsv['iou_std']:.4f}")
        print(f"  Rango:       {hsv['iou_min']:.4f} - {hsv['iou_max']:.4f}")
        print(f"\nYOLOv8 Detection:")
        print(f"  IoU Media:   {yolo['iou_media']:.4f}")
        print(f"  Std Dev:     {yolo['iou_std']:.4f}")
        print(f"  Rango:       {yolo['iou_min']:.4f} - {yolo['iou_max']:.4f}")
        print(f"\nGanador: {comp['winner']} 🏆")
        print(f"Diferencia: {comp['diferencia_iou']:.4f}")
        print("-"*80 + "\n")


def phase_5c_detection(
    masks_gt_dir: str,
    hsv_masks_dir: str,
    yolo_masks_dir: str,
    results_dir: str,
    iou_threshold: float = 0.5,
    debug: bool = False
) -> Dict:
    """
    Función principal Phase 5C.

    Args:
        masks_gt_dir: Directorio con máscaras ground truth
        hsv_masks_dir: Directorio con máscaras HSV
        yolo_masks_dir: Directorio con máscaras YOLO
        results_dir: Directorio para guardar resultados
        iou_threshold: Threshold para IoU
        debug: Modo debug

    Returns:
        dict: Resultados con comparativa HSV vs YOLO
    """
    detector = Phase5cDetection(iou_threshold=iou_threshold, debug=debug)
    return detector.evaluate(masks_gt_dir, hsv_masks_dir, yolo_masks_dir, results_dir)


if __name__ == "__main__":
    print("Phase 5C: Módulo de evaluación IoU para detección de sellos")
