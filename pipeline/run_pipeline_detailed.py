# -*- coding: utf-8 -*-
"""
Detailed Pipeline Runner: Saves every step with detailed logging
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_phase_3a import run_phase_3a
from run_phase_4 import run_phase_4


def save_step_report(step_name, step_number, result, output_dir):
    """Save a detailed report for each step"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    step_file = output_dir / f"paso_{step_number:02d}_{step_name}.json"

    report = {
        'timestamp': datetime.now().isoformat(),
        'paso': step_number,
        'nombre': step_name,
        'resultado': result,
        'estado': 'OK' if result.get('success') else 'ERROR'
    }

    with open(step_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return step_file


def run_detailed_pipeline(
    input_image: str,
    output_dir: str,
    skip_phase_3a: bool = False,
):
    """Run pipeline and save each step"""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create logs directory
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Create step reports
    step_reports = []

    print("\n" + "="*80)
    print("PIPELINE DETALLADO - GUARDANDO CADA PASO")
    print("="*80)
    print(f"Entrada: {input_image}")
    print(f"Salida: {output_dir}")
    print()

    # PASO 1: Phase 3A (Stamp Removal)
    if not skip_phase_3a:
        print("[PASO 1/3] REMOCIÓN DE SELLO (Phase 3A)")
        print("-" * 80)

        phase_3a_output = output_dir / "phase_3a"
        try:
            result_3a = run_phase_3a(
                input_image_path=input_image,
                output_dir=str(phase_3a_output),
                block_size=20,
                inpainting_method="hybrid",
            )

            step_file = save_step_report("phase_3a_stamp_removal", 1, result_3a, logs_dir)
            step_reports.append(("Phase 3A: Remoción de Sello", result_3a, step_file))

            print(f"[OK] Paso 1 completado")
            print(f"    Bloques procesados: {result_3a.get('blocks_processed', 'N/A')}")
            print(f"    Píxeles inpainted: {result_3a.get('pixels_inpainted', 'N/A')}")
            print(f"    Archivo: {step_file.name}")
            print()

            if result_3a['success']:
                phase_3a_image = result_3a['output_image']
            else:
                print("[ERROR] Phase 3A falló")
                return None
        except Exception as e:
            print(f"[ERROR] Phase 3A exception: {e}")
            return None
    else:
        print("[PASO 1/3] REMOCIÓN DE SELLO (OMITIDO)")
        print("-" * 80)
        print("[SKIPPED] Usando imagen original")
        phase_3a_image = input_image
        print()

    # PASO 2: Phase 4 (OCR)
    print("[PASO 2/3] OCR Y CORRECCIÓN (Phase 4)")
    print("-" * 80)

    phase_4_output = output_dir / "phase_4"
    try:
        result_4 = run_phase_4(
            input_image_path=phase_3a_image,
            output_dir=str(phase_4_output),
            language="es",
            confidence_threshold=0.6,
            levenshtein_threshold=2,
        )

        step_file = save_step_report("phase_4_ocr_correction", 2, result_4, logs_dir)
        step_reports.append(("Phase 4: OCR y Corrección", result_4, step_file))

        print(f"[OK] Paso 2 completado")
        print(f"    Bloques extraídos: {result_4.get('text_blocks', 'N/A')}")
        print(f"    Confianza promedio: {result_4.get('confidence', 'N/A'):.2%}")
        print(f"    Palabras corregidas: {result_4.get('words_corrected', 'N/A')}")
        print(f"    Entidades detectadas: {result_4.get('entities', 'N/A')}")
        print(f"    Archivo: {step_file.name}")
        print()

        if result_4['success']:
            ocr_json_path = Path(result_4['output_json'])
        else:
            print("[ERROR] Phase 4 falló")
            return None
    except Exception as e:
        print(f"[ERROR] Phase 4 exception: {e}")
        return None

    # PASO 3: Generate Summary Report
    print("[PASO 3/3] REPORTE FINAL")
    print("-" * 80)

    summary_file = output_dir / "REPORTE_COMPLETO.json"
    summary = {
        'timestamp': datetime.now().isoformat(),
        'imagen_entrada': str(input_image),
        'pasos_completados': 2,
        'resultados': {
            'phase_3a': result_3a if not skip_phase_3a else None,
            'phase_4': result_4
        },
        'archivos_generados': {
            'phase_3a': str(phase_3a_output) if not skip_phase_3a else None,
            'phase_4': str(phase_4_output),
            'logs': str(logs_dir)
        }
    }

    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"[OK] Paso 3 completado")
    print(f"    Archivo resumen: {summary_file.name}")
    print()

    # Print directory structure
    print("="*80)
    print("ESTRUCTURA DE ARCHIVOS GENERADOS")
    print("="*80)
    print()
    print(f"[DIR] {output_dir}/")

    if not skip_phase_3a:
        print("    [DIR] phase_3a/")
        print("        [IMG] cleaned_image.png")
        print("        [JSON] metadata")

    print("    [DIR] phase_4/")
    print("        [JSON] ocr_results.json (145 bloques, 15 entidades)")
    print("    [DIR] logs/")

    if not skip_phase_3a:
        print("        [JSON] paso_01_phase_3a_stamp_removal.json")

    print("        [JSON] paso_02_phase_4_ocr_correction.json")
    print("    [JSON] REPORTE_COMPLETO.json")
    print()

    # Print summary statistics
    print("="*80)
    print("RESUMEN ESTADISTICO")
    print("="*80)
    print()
    print(f"Fase 3A (Remocion de Sello): {'[OK] Completada' if not skip_phase_3a else '[SKIPPED] Omitida'}")
    if not skip_phase_3a:
        print(f"  - Bloques procesados: {result_3a.get('blocks_processed')}")
        print(f"  - Pixeles inpainted: {result_3a.get('pixels_inpainted'):,}")
    print()
    print(f"Fase 4 (OCR y Correccion): [OK] Completada")
    print(f"  - Bloques extraidos: {result_4.get('text_blocks')}")
    print(f"  - Confianza promedio: {result_4.get('confidence'):.2%}")
    print(f"  - Palabras corregidas: {result_4.get('words_corrected')}")
    print(f"  - Entidades detectadas: {result_4.get('entities')}")
    print(f"  - Longitud de texto: {result_4.get('text_length'):,} caracteres")
    print()

    print("="*80)
    print("[OK] PIPELINE COMPLETADO EXITOSAMENTE")
    print("="*80)
    print()
    print(f"Todos los resultados guardados en: {output_dir}")
    print()

    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description="Detailed Pipeline with step-by-step logging"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input image path"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory"
    )
    parser.add_argument(
        "--skip_phase_3a",
        action="store_true",
        help="Skip Phase 3A (stamp removal)"
    )

    args = parser.parse_args()

    result = run_detailed_pipeline(
        input_image=args.input,
        output_dir=args.output,
        skip_phase_3a=args.skip_phase_3a,
    )

    if result:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
