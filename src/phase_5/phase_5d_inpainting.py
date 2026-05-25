# -*- coding: utf-8 -*-
"""
Phase 5D: Evaluación de inpainting - SSIM y FID
Compara imágenes restauradas por LaMa contra imágenes limpias originales
"""
import json
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime

from phase_5_base import FileHelper, ResultsWriter


class Phase5dInpainting:
    """Evaluación de inpainting con SSIM y FID"""

    def __init__(self, ssim_window_size: int = 11, debug: bool = False):
        """
        Args:
            ssim_window_size: Tamaño de ventana para SSIM
            debug: Modo debug
        """
        self.ssim_window_size = ssim_window_size
        self.debug = debug
        self.results = []

    def evaluate(
        self,
        clean_images_dir: str,
        restored_images_dir: str,
        results_dir: str,
        roi_masks_dir: str = None
    ) -> Dict:
        """
        Evalúa inpainting con SSIM (local en ROI) y FID (global).

        Args:
            clean_images_dir: Directorio con imágenes limpias originales
            restored_images_dir: Directorio con imágenes restauradas por LaMa
            results_dir: Directorio para guardar resultados
            roi_masks_dir: (Opcional) Directorio con máscaras ROI de sello

        Returns:
            dict: Resultados con SSIM y FID
        """
        print("\n" + "="*80)
        print("PHASE 5D: EVALUACIÓN DE INPAINTING - SSIM y FID")
        print("="*80)

        clean_dir = Path(clean_images_dir)
        restored_dir = Path(restored_images_dir)
        res_dir = Path(results_dir)
        res_dir.mkdir(parents=True, exist_ok=True)

        # Encontrar pares
        try:
            clean_files = sorted(clean_dir.glob("*.png"))
            print(f"✓ Encontradas {len(clean_files)} imágenes limpias")
        except Exception as e:
            print(f"❌ Error: {e}")
            return self._empty_result()

        if not clean_files:
            print("⚠️ No se encontraron imágenes limpias")
            return self._empty_result()

        # Procesar cada par
        self.results = []
        ssim_scores = []

        for idx, clean_file in enumerate(clean_files, 1):
            restored_file = restored_dir / clean_file.name
            roi_mask_file = None

            if roi_masks_dir:
                roi_mask_file = Path(roi_masks_dir) / clean_file.name

            if restored_file.exists():
                print(f"\n[{idx}/{len(clean_files)}] Evaluando: {clean_file.name}")
                ssim = self._process_pair(clean_file, restored_file, roi_mask_file)
                if ssim is not None:
                    ssim_scores.append(ssim)
            else:
                print(f"\n[{idx}/{len(clean_files)}] ⚠️ Falta imagen restaurada para: {clean_file.name}")

        # Calcular FID (si es posible)
        fid_score = None
        try:
            fid_score = self._calculate_fid(clean_dir, restored_dir)
            print(f"\n✓ FID calculado: {fid_score:.4f}")
        except Exception as e:
            print(f"\n⚠️ No se pudo calcular FID: {e}")

        # Consolidar
        consolidado = self._consolidate_results(ssim_scores, fid_score)

        # Guardar
        output_json = res_dir / "resultados_5d.json"
        output_csv = res_dir / "resultados_5d.csv"

        ResultsWriter.write_json(consolidado, output_json)
        if self.results:
            ResultsWriter.write_csv(self.results, output_csv)

        # Imprimir resumen
        self._print_summary(consolidado)

        return consolidado

    def _process_pair(
        self,
        clean_file: Path,
        restored_file: Path,
        roi_mask_file: Path = None
    ) -> float:
        """Procesa un par imagen limpia/restaurada"""
        try:
            import cv2
            from skimage.metrics import structural_similarity as ssim

            # Cargar imágenes
            img_clean = FileHelper.read_image_file(clean_file)
            img_restored = FileHelper.read_image_file(restored_file)

            # Convertir a escala de grises
            gray_clean = cv2.cvtColor(img_clean, cv2.COLOR_BGR2GRAY)
            gray_restored = cv2.cvtColor(img_restored, cv2.COLOR_BGR2GRAY)

            # Si hay máscara ROI, calcular SSIM solo en esa región
            if roi_mask_file and roi_mask_file.exists():
                roi_mask = FileHelper.read_image_file(roi_mask_file)
                roi_mask_bin = (roi_mask > 127).astype(np.uint8)

                # SSIM solo en ROI
                ssim_score = ssim(
                    gray_clean * roi_mask_bin,
                    gray_restored * roi_mask_bin,
                    win_size=self.ssim_window_size,
                    data_range=255
                )
            else:
                # SSIM global
                ssim_score = ssim(
                    gray_clean,
                    gray_restored,
                    win_size=self.ssim_window_size,
                    data_range=255
                )

            # Registrar
            self.results.append({
                'documento': clean_file.stem,
                'ssim': round(float(ssim_score), 4),
                'ssim_type': 'ROI' if roi_mask_file and roi_mask_file.exists() else 'Global'
            })

            print(f"  SSIM: {ssim_score:.4f} ({'ROI' if roi_mask_file else 'Global'})")

            return float(ssim_score)

        except Exception as e:
            print(f"  ❌ Error procesando imágenes: {e}")
            if self.debug:
                raise
            return None

    def _calculate_fid(self, clean_dir: Path, restored_dir: Path) -> float:
        """
        Calcula Fréchet Inception Distance (FID).
        Requiere pytorch_fid instalado.
        """
        try:
            import subprocess
            import tempfile

            # Crear archivos temporales con las rutas
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                fid_output = f.name

            # Ejecutar pytorch_fid
            cmd = [
                'fid',
                str(clean_dir),
                str(restored_dir),
                '--output', fid_output
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # Parsear output
                with open(fid_output, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if 'FID' in line:
                            fid_value = float(line.split()[-1])
                            return fid_value

        except Exception as e:
            if self.debug:
                print(f"[DEBUG] FID calculation failed: {e}")
            # Retornar None si falla (pytorch_fid puede no estar instalado)
            return None

        return None

    def _consolidate_results(self, ssim_scores: list, fid_score: float) -> Dict:
        """Consolida resultados"""
        ssim_mean = 0
        ssim_std = 0
        ssim_min = 0
        ssim_max = 0

        if ssim_scores:
            ssim_mean = sum(ssim_scores) / len(ssim_scores)
            ssim_std = (sum((x - ssim_mean) ** 2 for x in ssim_scores) / len(ssim_scores)) ** 0.5
            ssim_min = min(ssim_scores)
            ssim_max = max(ssim_scores)

        return {
            'timestamp': datetime.now().isoformat(),
            'total_imagenes': len(self.results),
            'ssim_window_size': self.ssim_window_size,
            'ssim': {
                'media': round(ssim_mean, 4),
                'std': round(ssim_std, 4),
                'min': round(ssim_min, 4),
                'max': round(ssim_max, 4),
                'interpretacion': self._interpret_ssim(ssim_mean)
            },
            'fid': {
                'score': round(fid_score, 4) if fid_score is not None else None,
                'interpretacion': self._interpret_fid(fid_score) if fid_score else 'N/A (pytorch_fid no instalado)'
            },
            'documentos': self.results
        }

    @staticmethod
    def _interpret_ssim(ssim: float) -> str:
        """Interpreta valor SSIM"""
        if ssim >= 0.95:
            return 'Excelente - Restauración casi perfecta'
        elif ssim >= 0.85:
            return 'Muy buena - Restauración muy coherente'
        elif ssim >= 0.70:
            return 'Buena - Restauración visible pero aceptable'
        elif ssim >= 0.50:
            return 'Aceptable - Diferencias notables'
        else:
            return 'Pobre - Restauración con artefactos significativos'

    @staticmethod
    def _interpret_fid(fid: float) -> str:
        """Interpreta valor FID"""
        if fid is None:
            return 'N/A'
        elif fid < 10:
            return 'Excelente - Distribuciones muy similares'
        elif fid < 25:
            return 'Muy buena - Distribuciones similares'
        elif fid < 50:
            return 'Buena - Diferencias moderadas'
        else:
            return 'Pobre - Diferencias significativas'

    def _empty_result(self) -> Dict:
        """Retorna resultado vacío"""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_imagenes': 0,
            'ssim_window_size': self.ssim_window_size,
            'ssim': {
                'media': 0,
                'std': 0,
                'min': 0,
                'max': 0,
                'interpretacion': 'N/A'
            },
            'fid': {
                'score': None,
                'interpretacion': 'N/A'
            },
            'documentos': []
        }

    def _print_summary(self, result: Dict):
        """Imprime resumen"""
        ssim = result['ssim']
        fid = result['fid']

        print("\n" + "-"*80)
        print("RESUMEN PHASE 5D - EVALUACIÓN DE INPAINTING")
        print("-"*80)
        print(f"Total imágenes: {result['total_imagenes']}")
        print(f"\nSSIM (Structural Similarity Index):")
        print(f"  Media:         {ssim['media']:.4f}")
        print(f"  Std Dev:       {ssim['std']:.4f}")
        print(f"  Rango:         {ssim['min']:.4f} - {ssim['max']:.4f}")
        print(f"  Interpretación: {ssim['interpretacion']}")
        if fid['score'] is not None:
            print(f"\nFID (Fréchet Inception Distance):")
            print(f"  Score:         {fid['score']:.4f}")
            print(f"  Interpretación: {fid['interpretacion']}")
        else:
            print(f"\nFID (Fréchet Inception Distance):")
            print(f"  {fid['interpretacion']}")
        print("-"*80 + "\n")


def phase_5d_inpainting(
    clean_images_dir: str,
    restored_images_dir: str,
    results_dir: str,
    roi_masks_dir: str = None,
    ssim_window_size: int = 11,
    debug: bool = False
) -> Dict:
    """
    Función principal Phase 5D.

    Args:
        clean_images_dir: Directorio con imágenes limpias
        restored_images_dir: Directorio con imágenes restauradas
        results_dir: Directorio para guardar resultados
        roi_masks_dir: (Opcional) Directorio con máscaras ROI
        ssim_window_size: Tamaño de ventana para SSIM
        debug: Modo debug

    Returns:
        dict: Resultados con SSIM y FID
    """
    inpainter = Phase5dInpainting(ssim_window_size=ssim_window_size, debug=debug)
    return inpainter.evaluate(clean_images_dir, restored_images_dir, results_dir, roi_masks_dir)


if __name__ == "__main__":
    print("Phase 5D: Módulo de evaluación SSIM/FID para inpainting")
