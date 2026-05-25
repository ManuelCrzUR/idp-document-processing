# -*- coding: utf-8 -*-
"""
Phase 5: Pipeline completo de evaluación y métricas
Orquesta los 4 experimentos (5A, 5B, 5C, 5D) y genera reporte consolidado
"""
import json
from pathlib import Path
from typing import Dict
from datetime import datetime

from phase_5a_evaluation import phase_5a_evaluation
from phase_5b_evaluation import phase_5b_evaluation
from phase_5c_detection import phase_5c_detection
from phase_5d_inpainting import phase_5d_inpainting
from phase_5_base import ResultsWriter


class Phase5Complete:
    """Orquestador completo de Phase 5"""

    def __init__(
        self,
        confidence_threshold: float = 0.6,
        iou_threshold: float = 0.5,
        ssim_window_size: int = 11,
        debug: bool = False
    ):
        """
        Args:
            confidence_threshold: Threshold para OCR
            iou_threshold: Threshold para IoU
            ssim_window_size: Tamaño ventana SSIM
            debug: Modo debug
        """
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.ssim_window_size = ssim_window_size
        self.debug = debug

    def evaluate(
        self,
        ground_truth_dir: str,
        manual_gt_dir: str,
        masks_gt_dir: str,
        hsv_masks_dir: str,
        yolo_masks_dir: str,
        clean_images_dir: str,
        restored_images_dir: str,
        results_dir: str,
        roi_masks_dir: str = None
    ) -> Dict:
        """
        Ejecuta los 4 experimentos y genera reporte consolidado.

        Args:
            ground_truth_dir: Ground truth Grupo A (sintético)
            manual_gt_dir: Transcripciones manuales Grupo B (real)
            masks_gt_dir: Máscaras ground truth para IoU
            hsv_masks_dir: Máscaras HSV predichas
            yolo_masks_dir: Máscaras YOLO predichas
            clean_images_dir: Imágenes limpias originales
            restored_images_dir: Imágenes restauradas por LaMa
            results_dir: Directorio para guardar resultados
            roi_masks_dir: (Opcional) Máscaras ROI para SSIM

        Returns:
            dict: Reporte consolidado de los 4 experimentos
        """
        print("\n" + "="*100)
        print("PHASE 5: EVALUACIÓN Y MÉTRICAS - PIPELINE COMPLETO")
        print("="*100)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Parámetros:")
        print(f"  - Confidence threshold: {self.confidence_threshold}")
        print(f"  - IoU threshold: {self.iou_threshold}")
        print(f"  - SSIM window size: {self.ssim_window_size}")

        res_dir = Path(results_dir)
        res_dir.mkdir(parents=True, exist_ok=True)

        # Ejecutar los 4 experimentos
        print("\n" + "-"*100)
        print("EJECUTANDO EXPERIMENTOS...")
        print("-"*100)

        # Experimento 5A: CER/WER Automático
        print("\n▶ EXPERIMENTO 5A: CER/WER Automático (Grupo A - Sintético)")
        try:
            result_5a = phase_5a_evaluation(ground_truth_dir, str(res_dir / "5a"))
        except Exception as e:
            print(f"❌ Error en 5A: {e}")
            result_5a = None

        # Experimento 5B: CER/WER Manual
        print("\n▶ EXPERIMENTO 5B: CER/WER Manual (Grupo B - Real con validación humana)")
        try:
            result_5b = phase_5b_evaluation(manual_gt_dir, str(res_dir / "5b"))
        except Exception as e:
            print(f"❌ Error en 5B: {e}")
            result_5b = None

        # Experimento 5C: IoU Detección
        print("\n▶ EXPERIMENTO 5C: IoU Detección (HSV vs YOLO)")
        try:
            result_5c = phase_5c_detection(
                masks_gt_dir,
                hsv_masks_dir,
                yolo_masks_dir,
                str(res_dir / "5c"),
                iou_threshold=self.iou_threshold
            )
        except Exception as e:
            print(f"❌ Error en 5C: {e}")
            result_5c = None

        # Experimento 5D: SSIM/FID Inpainting
        print("\n▶ EXPERIMENTO 5D: SSIM/FID Inpainting (LaMa)")
        try:
            result_5d = phase_5d_inpainting(
                clean_images_dir,
                restored_images_dir,
                str(res_dir / "5d"),
                roi_masks_dir=roi_masks_dir,
                ssim_window_size=self.ssim_window_size
            )
        except Exception as e:
            print(f"❌ Error en 5D: {e}")
            result_5d = None

        # Consolidar reporte
        reporte = self._consolidate_report(result_5a, result_5b, result_5c, result_5d)

        # Guardar reporte
        output_json = res_dir / "reporte_final_fase5.json"
        output_csv = res_dir / "reporte_final_fase5.csv"
        output_md = res_dir / "reporte_final_fase5.md"

        ResultsWriter.write_json(reporte, output_json)

        # Escribir CSV con resumen
        if reporte.get('documentos'):
            ResultsWriter.write_csv(reporte['documentos'], output_csv)

        # Escribir Markdown
        self._write_markdown_report(reporte, output_md)

        # Imprimir resumen final
        self._print_final_summary(reporte)

        return reporte

    def _consolidate_report(
        self,
        result_5a: Dict,
        result_5b: Dict,
        result_5c: Dict,
        result_5d: Dict
    ) -> Dict:
        """Consolida los 4 experimentos en un reporte único"""
        return {
            'timestamp': datetime.now().isoformat(),
            'pipeline': 'OCR con Detección y Eliminación de Sellos',
            'experimentos': {
                '5a_ocr_automatico': result_5a or {'status': 'error'},
                '5b_ocr_manual': result_5b or {'status': 'error'},
                '5c_deteccion_iou': result_5c or {'status': 'error'},
                '5d_inpainting_ssim_fid': result_5d or {'status': 'error'}
            },
            'hipotesis_central': {
                'condicion': 'Reducción de CER >= 5 puntos porcentuales respecto baseline',
                'resultado_5a': result_5a.get('hipotesis', {}).get('cumplida') if result_5a else None,
                'resultado_5b': result_5b.get('hipotesis', {}).get('cumplida') if result_5b else None,
                'delta_cer_5a': result_5a.get('hipotesis', {}).get('delta_cer_respecto_baseline') if result_5a else None,
                'delta_cer_5b': result_5b.get('hipotesis', {}).get('delta_cer_respecto_baseline') if result_5b else None
            },
            'resumen_ejecutivo': self._generate_executive_summary(result_5a, result_5b, result_5c, result_5d),
            'documentos': []
        }

    def _generate_executive_summary(
        self,
        result_5a: Dict,
        result_5b: Dict,
        result_5c: Dict,
        result_5d: Dict
    ) -> Dict:
        """Genera resumen ejecutivo de los 4 experimentos"""
        summary = {}

        if result_5a:
            summary['ocr_automatico'] = {
                'total_docs': result_5a.get('total_documentos', 0),
                'cer_media': result_5a.get('cer', {}).get('media', 0),
                'wer_media': result_5a.get('wer', {}).get('media', 0),
                'status': '✅' if result_5a.get('hipotesis', {}).get('cumplida') else '❌'
            }

        if result_5b:
            summary['ocr_manual'] = {
                'total_docs': result_5b.get('total_documentos', 0),
                'cer_media': result_5b.get('cer', {}).get('media', 0),
                'wer_media': result_5b.get('wer', {}).get('media', 0),
                'validador': 'Humano',
                'status': '✅' if result_5b.get('hipotesis', {}).get('cumplida') else '❌'
            }

        if result_5c:
            summary['deteccion_iou'] = {
                'total_imagenes': result_5c.get('total_imagenes', 0),
                'iou_hsv': result_5c.get('hsv', {}).get('iou_media', 0),
                'iou_yolo': result_5c.get('yolo', {}).get('iou_media', 0),
                'winner': result_5c.get('comparativa', {}).get('winner', 'N/A')
            }

        if result_5d:
            summary['inpainting_calidad'] = {
                'total_imagenes': result_5d.get('total_imagenes', 0),
                'ssim_media': result_5d.get('ssim', {}).get('media', 0),
                'fid_score': result_5d.get('fid', {}).get('score'),
                'ssim_interpretacion': result_5d.get('ssim', {}).get('interpretacion', 'N/A')
            }

        return summary

    def _write_markdown_report(self, reporte: Dict, output_path: Path):
        """Escribe reporte en Markdown"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        md_content = f"""# Fase 5: Evaluación y Métricas del Pipeline OCR

**Timestamp:** {reporte['timestamp']}

## Resumen Ejecutivo

{self._generate_markdown_summary(reporte)}

## Experimento 5A: CER/WER Automático (Grupo A - Sintético)

{self._generate_markdown_5a(reporte.get('experimentos', {}).get('5a_ocr_automatico'))}

## Experimento 5B: CER/WER Manual (Grupo B - Real)

{self._generate_markdown_5b(reporte.get('experimentos', {}).get('5b_ocr_manual'))}

## Experimento 5C: Evaluación de Detección (IoU)

{self._generate_markdown_5c(reporte.get('experimentos', {}).get('5c_deteccion_iou'))}

## Experimento 5D: Evaluación de Inpainting (SSIM/FID)

{self._generate_markdown_5d(reporte.get('experimentos', {}).get('5d_inpainting_ssim_fid'))}

## Hipótesis Central

**Condición:** Reducción de CER >= 5 puntos porcentuales respecto baseline

- **5A (Sintético):** {'✅ Cumplida' if reporte.get('hipotesis_central', {}).get('resultado_5a') else '❌ No cumplida'}
- **5B (Real):** {'✅ Cumplida' if reporte.get('hipotesis_central', {}).get('resultado_5b') else '❌ No cumplida'}

---
*Generado automáticamente por Phase 5 - Pipeline de OCR*
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"✅ Markdown reportgenerado: {output_path}")

    @staticmethod
    def _generate_markdown_summary(reporte: Dict) -> str:
        """Genera sección de resumen en Markdown"""
        summary = reporte.get('resumen_ejecutivo', {})
        text = "\n"

        if 'ocr_automatico' in summary:
            ocr_a = summary['ocr_automatico']
            text += f"### OCR Automático (Grupo A)\n"
            text += f"- Documentos: {ocr_a['total_docs']}\n"
            text += f"- CER Media: {ocr_a['cer_media']:.2f}%\n"
            text += f"- WER Media: {ocr_a['wer_media']:.2f}%\n"
            text += f"- Status: {ocr_a['status']}\n\n"

        if 'ocr_manual' in summary:
            ocr_b = summary['ocr_manual']
            text += f"### OCR Manual (Grupo B - Real)\n"
            text += f"- Documentos: {ocr_b['total_docs']}\n"
            text += f"- CER Media: {ocr_b['cer_media']:.2f}%\n"
            text += f"- WER Media: {ocr_b['wer_media']:.2f}%\n"
            text += f"- Validador: {ocr_b['validador']}\n"
            text += f"- Status: {ocr_b['status']}\n\n"

        if 'deteccion_iou' in summary:
            det = summary['deteccion_iou']
            text += f"### Detección de Sellos (IoU)\n"
            text += f"- Imágenes: {det['total_imagenes']}\n"
            text += f"- IoU HSV: {det['iou_hsv']:.4f}\n"
            text += f"- IoU YOLO: {det['iou_yolo']:.4f}\n"
            text += f"- Ganador: **{det['winner']}**\n\n"

        if 'inpainting_calidad' in summary:
            inp = summary['inpainting_calidad']
            text += f"### Inpainting (SSIM/FID)\n"
            text += f"- Imágenes: {inp['total_imagenes']}\n"
            text += f"- SSIM Media: {inp['ssim_media']:.4f}\n"
            text += f"- FID: {inp['fid_score'] if inp['fid_score'] else 'N/A'}\n"
            text += f"- Interpretación: {inp['ssim_interpretacion']}\n"

        return text

    @staticmethod
    def _generate_markdown_5a(result: Dict) -> str:
        """Genera sección 5A en Markdown"""
        if not result or result.get('status') == 'error':
            return "❌ Error en ejecución de Experimento 5A\n"

        cer = result.get('cer', {})
        wer = result.get('wer', {})

        return f"""| Métrica | Media | Std Dev | Rango |
|---------|-------|---------|-------|
| CER | {cer.get('media', 0):.2f}% | {cer.get('std', 0):.2f}% | {cer.get('min', 0):.2f}% - {cer.get('max', 0):.2f}% |
| WER | {wer.get('media', 0):.2f}% | {wer.get('std', 0):.2f}% | {wer.get('min', 0):.2f}% - {wer.get('max', 0):.2f}% |

**Documentos:** {result.get('total_documentos', 0)}
"""

    @staticmethod
    def _generate_markdown_5b(result: Dict) -> str:
        """Genera sección 5B en Markdown"""
        if not result or result.get('status') == 'error':
            return "❌ Error en ejecución de Experimento 5B\n"

        cer = result.get('cer', {})
        wer = result.get('wer', {})

        return f"""| Métrica | Media | Std Dev | Rango |
|---------|-------|---------|-------|
| CER | {cer.get('media', 0):.2f}% | {cer.get('std', 0):.2f}% | {cer.get('min', 0):.2f}% - {cer.get('max', 0):.2f}% |
| WER | {wer.get('media', 0):.2f}% | {wer.get('std', 0):.2f}% | {wer.get('min', 0):.2f}% - {wer.get('max', 0):.2f}% |

**Documentos:** {result.get('total_documentos', 0)}
**Validador:** Humano (Transcripciones manuales)
"""

    @staticmethod
    def _generate_markdown_5c(result: Dict) -> str:
        """Genera sección 5C en Markdown"""
        if not result or result.get('status') == 'error':
            return "❌ Error en ejecución de Experimento 5C\n"

        hsv = result.get('hsv', {})
        yolo = result.get('yolo', {})

        return f"""| Método | IoU Media | Std Dev | Rango |
|--------|-----------|---------|-------|
| HSV | {hsv.get('iou_media', 0):.4f} | {hsv.get('iou_std', 0):.4f} | {hsv.get('iou_min', 0):.4f} - {hsv.get('iou_max', 0):.4f} |
| YOLO | {yolo.get('iou_media', 0):.4f} | {yolo.get('iou_std', 0):.4f} | {yolo.get('iou_min', 0):.4f} - {yolo.get('iou_max', 0):.4f} |

**Ganador:** {result.get('comparativa', {}).get('winner', 'N/A')}
**Diferencia:** {result.get('comparativa', {}).get('diferencia_iou', 0):.4f}
"""

    @staticmethod
    def _generate_markdown_5d(result: Dict) -> str:
        """Genera sección 5D en Markdown"""
        if not result or result.get('status') == 'error':
            return "❌ Error en ejecución de Experimento 5D\n"

        ssim = result.get('ssim', {})
        fid = result.get('fid', {})

        return f"""| Métrica | Valor | Interpretación |
|---------|-------|-----------------|
| SSIM Media | {ssim.get('media', 0):.4f} | {ssim.get('interpretacion', 'N/A')} |
| SSIM Std Dev | {ssim.get('std', 0):.4f} | - |
| SSIM Rango | {ssim.get('min', 0):.4f} - {ssim.get('max', 0):.4f} | - |
| FID | {fid.get('score', 'N/A')} | {fid.get('interpretacion', 'N/A')} |
"""

    def _print_final_summary(self, reporte: Dict):
        """Imprime resumen final en consola"""
        print("\n" + "="*100)
        print("RESUMEN FINAL - PHASE 5 COMPLETA")
        print("="*100)

        summary = reporte.get('resumen_ejecutivo', {})

        if 'ocr_automatico' in summary:
            print("\n✓ Experimento 5A (CER/WER Automático):")
            print(f"  - Documentos: {summary['ocr_automatico']['total_docs']}")
            print(f"  - CER Media: {summary['ocr_automatico']['cer_media']:.2f}%")

        if 'ocr_manual' in summary:
            print("\n✓ Experimento 5B (CER/WER Manual):")
            print(f"  - Documentos: {summary['ocr_manual']['total_docs']}")
            print(f"  - CER Media: {summary['ocr_manual']['cer_media']:.2f}%")

        if 'deteccion_iou' in summary:
            print("\n✓ Experimento 5C (IoU Detección):")
            print(f"  - Ganador: {summary['deteccion_iou']['winner']}")

        if 'inpainting_calidad' in summary:
            print("\n✓ Experimento 5D (SSIM/FID Inpainting):")
            print(f"  - SSIM Media: {summary['inpainting_calidad']['ssim_media']:.4f}")

        print("\n" + "="*100)


def phase_5_complete(
    ground_truth_dir: str,
    manual_gt_dir: str,
    masks_gt_dir: str,
    hsv_masks_dir: str,
    yolo_masks_dir: str,
    clean_images_dir: str,
    restored_images_dir: str,
    results_dir: str,
    roi_masks_dir: str = None,
    confidence_threshold: float = 0.6,
    iou_threshold: float = 0.5,
    ssim_window_size: int = 11,
    debug: bool = False
) -> Dict:
    """
    Función principal Phase 5 - Pipeline completo.

    Ejecuta los 4 experimentos y genera reporte consolidado final.
    """
    phase5 = Phase5Complete(
        confidence_threshold=confidence_threshold,
        iou_threshold=iou_threshold,
        ssim_window_size=ssim_window_size,
        debug=debug
    )

    return phase5.evaluate(
        ground_truth_dir,
        manual_gt_dir,
        masks_gt_dir,
        hsv_masks_dir,
        yolo_masks_dir,
        clean_images_dir,
        restored_images_dir,
        results_dir,
        roi_masks_dir
    )


if __name__ == "__main__":
    print("Phase 5: Módulo de evaluación y métricas completo")
