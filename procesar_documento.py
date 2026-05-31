# -*- coding: utf-8 -*-
"""
Procesador de documento individual.

Uso:
    python procesar_documento.py ruta/a/tu/imagen.png
    python procesar_documento.py ruta/a/tu/imagen.png --salida carpeta/salida
"""

import sys
import json
import argparse
import time
from pathlib import Path
import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")  # sin ventana grafica
import matplotlib.pyplot as plt

# === Rutas ===
REPO_ROOT = Path(__file__).parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline import run_phase_3a, run_phase_4, consolidate_ocr_results


# ===========================================================================
# VISUALIZACION
# ===========================================================================

def guardar_grid_evidencias(phase_3a_dir, output_path):
    """Guarda cuadricula 2x3 con imagenes intermedias de fase 3A."""
    etiquetas = {
        "01": "Original",
        "02": "Clasificacion cromatica",
        "03": "H-Sweep",
        "04": "Block Grid Overlay",
        "05": "Mascara final",
        "06": "Antes vs Despues",
    }
    imgs_inter = sorted(Path(phase_3a_dir).glob("0*.png"))[:6]
    evidencias, labels = [], []
    for p in imgs_inter:
        img = cv2.imread(str(p))
        if img is not None:
            evidencias.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            labels.append(etiquetas.get(p.stem[:2], p.stem))

    if len(evidencias) < 2:
        return

    cols = min(3, len(evidencias))
    rows = -(-len(evidencias) // cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 6, rows * 4.5))
    axes = np.array(axes).flatten()
    for i, (img, lbl) in enumerate(zip(evidencias, labels)):
        axes[i].imshow(img); axes[i].set_title(lbl, fontsize=11, fontweight="bold"); axes[i].axis("off")
    for i in range(len(evidencias), len(axes)):
        axes[i].axis("off")
    plt.suptitle("Fase 3A - Evidencias de Deteccion de Sello", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close()


def guardar_detecciones_ocr(cleaned_image_path, ocr_json_path, output_path):
    """Guarda imagen con bounding boxes color-coded por confianza."""
    with open(ocr_json_path, encoding="utf-8") as f:
        ocr_data = json.load(f)

    bloques = ocr_data.get("bloques", [])
    img_bgr = cv2.imread(str(cleaned_image_path))
    img_vis = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).copy()
    counts = {"alta": 0, "media": 0, "baja": 0}

    for bloque in bloques:
        coords    = bloque.get("coordenadas", [])
        confianza = bloque.get("confianza", 0)
        if len(coords) != 4:
            continue
        if confianza >= 0.8:
            color, cat = (34, 197, 94),  "alta"
        elif confianza >= 0.5:
            color, cat = (251, 191, 36), "media"
        else:
            color, cat = (239, 68, 68),  "baja"
        counts[cat] += 1
        pts = np.array(coords, dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(img_vis, [pts], True, color, 2)
        x0, y0 = int(coords[0][0]), max(int(coords[0][1]) - 5, 12)
        cv2.putText(img_vis, f"{confianza:.0%}", (x0, y0),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)

    leyenda = [
        ((34, 197, 94),  f"Alta (>=80%): {counts['alta']}"),
        ((251, 191, 36), f"Media (50-80%): {counts['media']}"),
        ((239, 68, 68),  f"Baja (<50%): {counts['baja']}"),
    ]
    for i, (col, txt) in enumerate(leyenda):
        y = 30 + i * 28
        cv2.rectangle(img_vis, (10, y - 14), (26, y + 4), col, -1)
        cv2.putText(img_vis, txt, (32, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (20, 20, 20), 1, cv2.LINE_AA)

    fig, ax = plt.subplots(figsize=(16, 12))
    ax.imshow(img_vis)
    total = len(bloques)
    ax.set_title(
        f"Detecciones OCR — {total} bloques  |  "
        f"Alta: {counts['alta']}  Media: {counts['media']}  Baja: {counts['baja']}",
        fontsize=13, fontweight="bold"
    )
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close()


def guardar_dashboard_metricas(ocr_json_path, metrics, output_path):
    """Guarda dashboard de 4 paneles con metricas OCR."""
    with open(ocr_json_path, encoding="utf-8") as f:
        ocr_data = json.load(f)
    confs = [b.get("confianza", 0) for b in ocr_data.get("bloques", [])]

    tm = metrics.get("text_metrics", {})
    cm = metrics.get("ocr_confidence_metrics", {})
    pm = metrics.get("post_processing_metrics", {})
    avg_conf = cm.get("average_percent", 0) / 100

    if avg_conf >= 0.85:   quality, qcolor = "EXCELENTE", "#16a34a"
    elif avg_conf >= 0.75: quality, qcolor = "MUY BUENO", "#2563eb"
    elif avg_conf >= 0.60: quality, qcolor = "BUENO",     "#d97706"
    else:                  quality, qcolor = "MEJORABLE", "#dc2626"

    fig = plt.figure(figsize=(16, 10))
    gs  = fig.add_gridspec(3, 2, hspace=0.38, wspace=0.28)

    # Panel 1 — Histograma
    ax1 = fig.add_subplot(gs[0, 0])
    if confs:
        bin_colors = ["#ef4444","#f97316","#facc15","#4ade80","#16a34a"]
        hist, _ = np.histogram(confs, bins=[0, 0.4, 0.6, 0.8, 0.9, 1.01])
        for i, (h, c) in enumerate(zip(hist, bin_colors)):
            ax1.bar(i, h, color=c, edgecolor="white", width=0.7)
        ax1.set_xticks(range(5))
        ax1.set_xticklabels(["<40%","40-60%","60-80%","80-90%",">90%"], fontsize=8)
        ax1.set_ylabel("Bloques", fontweight="bold")
        ax1.set_title("Distribucion de Confianza", fontweight="bold")
        ax1.grid(axis="y", alpha=0.3)
        for i, h in enumerate(hist):
            if h: ax1.text(i, h + 0.3, str(h), ha="center", fontsize=9, fontweight="bold")

    # Panel 2 — Pie
    ax2 = fig.add_subplot(gs[0, 1])
    alta  = sum(1 for c in confs if c >= 0.8)
    media = sum(1 for c in confs if 0.5 <= c < 0.8)
    baja  = sum(1 for c in confs if c < 0.5)
    sizes = [alta, media, baja]
    if sum(sizes) > 0:
        ax2.pie(sizes,
                labels=[f"Alta\n{alta}", f"Media\n{media}", f"Baja\n{baja}"],
                colors=["#16a34a","#d97706","#dc2626"],
                autopct="%1.0f%%", startangle=90, textprops={"fontsize": 9})
        ax2.set_title("Alta / Media / Baja confianza", fontweight="bold")

    # Panel 3 — Tabla
    ax3 = fig.add_subplot(gs[1, :])
    ax3.axis("off")
    rows = [
        ["Caracteres totales",        f"{tm.get('total_characters',0):,}"],
        ["Palabras totales",           f"{tm.get('total_words',0):,}"],
        ["Palabras unicas",            f"{tm.get('unique_words',0):,}"],
        ["Bloques de texto",           f"{tm.get('total_blocks',0)}"],
        ["Confianza promedio",         f"{cm.get('average_percent',0):.2f}%"],
        ["Bloques alta confianza",     f"{cm.get('blocks_with_high_confidence',0)}"],
        ["Palabras corregidas",        f"{pm.get('words_corrected',0)}"],
        ["Entidades NER detectadas",   f"{pm.get('entities_detected',0)}"],
    ]
    tbl = ax3.table(cellText=rows, colLabels=["Metrica","Valor"],
                    cellLoc="left", loc="center", colWidths=[0.58, 0.28])
    tbl.auto_set_font_size(False); tbl.set_fontsize(10); tbl.scale(1, 2.0)
    for (r, c), cell in tbl.get_celld().items():
        if r == 0:   cell.set_facecolor("#1e40af"); cell.set_text_props(color="white", fontweight="bold")
        elif r%2==0: cell.set_facecolor("#f0f9ff")
        else:        cell.set_facecolor("#ffffff")

    # Panel 4 — Calidad
    ax4 = fig.add_subplot(gs[2, :])
    ax4.axis("off")
    ax4.text(0.5, 0.5,
             f"Calidad OCR: {quality}    ({cm.get('average_percent',0):.2f}% confianza promedio)",
             fontsize=17, fontweight="bold", ha="center", va="center",
             bbox=dict(boxstyle="round,pad=0.9", facecolor=qcolor, alpha=0.15,
                       edgecolor=qcolor, linewidth=3),
             color=qcolor, transform=ax4.transAxes)

    plt.suptitle("Dashboard de Metricas OCR", fontsize=14, fontweight="bold")
    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close()


# ===========================================================================
# PIPELINE PRINCIPAL
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Procesa un documento: elimina sello + OCR + metricas"
    )
    parser.add_argument("imagen", help="Ruta a la imagen (PNG, JPG, BMP, TIFF)")
    parser.add_argument("--salida", default=None,
                        help="Carpeta de salida (default: output/NOMBRE_IMAGEN/)")
    args = parser.parse_args()

    imagen_path = Path(args.imagen)
    if not imagen_path.exists():
        print(f"[ERROR] Imagen no encontrada: {imagen_path}")
        sys.exit(1)

    if args.salida:
        output_dir = Path(args.salida)
    else:
        output_dir = REPO_ROOT / "output" / imagen_path.stem

    output_dir.mkdir(parents=True, exist_ok=True)

    print()
    print("=" * 65)
    print("  PIPELINE OCR - PROCESAMIENTO DE DOCUMENTO")
    print("=" * 65)
    print(f"  Imagen  : {imagen_path.name}")
    print(f"  Salida  : {output_dir}")
    print("=" * 65)

    t_total = time.time()

    # ------------------------------------------------------------------
    # FASE 3A — Eliminacion de sello
    # ------------------------------------------------------------------
    print("\n[1/3] Fase 3A - Deteccion y eliminacion de sello...")
    t0 = time.time()
    result_3a = run_phase_3a(
        input_image_path=str(imagen_path),
        output_dir=str(output_dir / "fase_3a"),
        block_size=20,
        inpainting_method="hybrid",
        save_intermediate=True,
    )
    t3a = time.time() - t0

    if result_3a["success"]:
        cleaned_image = result_3a["output_image"]
        px = result_3a.get("pixels_inpainted", "N/A")
        print(f"     [OK] {t3a:.1f}s  |  Pixeles inpainted: {px}")
        guardar_grid_evidencias(output_dir / "fase_3a", output_dir / "evidencias_fase3a.png")
        print(f"     [OK] Cuadricula de evidencias guardada")
    else:
        print(f"     [!!] Fase 3A fallo: {result_3a.get('error','?')} — usando imagen original")
        cleaned_image = str(imagen_path)

    # ------------------------------------------------------------------
    # FASE 4 — OCR
    # ------------------------------------------------------------------
    print("\n[2/3] Fase 4 - OCR + correccion ortografica...")
    print("      (Primera ejecucion descarga modelo EasyOCR ~100MB)")
    t0 = time.time()
    result_4 = run_phase_4(
        input_image_path=cleaned_image,
        output_dir=str(output_dir / "fase_4"),
        language="es",
        confidence_threshold=0.6,
        levenshtein_threshold=2,
    )
    t4 = time.time() - t0

    ocr_json = None
    if result_4["success"]:
        ocr_json = result_4["output_json"]
        bloques  = result_4.get("text_blocks", 0)
        conf     = result_4.get("confidence", 0)
        chars    = result_4.get("text_length", 0)
        print(f"     [OK] {t4:.1f}s  |  Bloques: {bloques}  |  Conf: {conf:.1%}  |  Chars: {chars:,}")
        guardar_detecciones_ocr(cleaned_image, ocr_json, output_dir / "detecciones_ocr.png")
        print(f"     [OK] Imagen con bounding boxes guardada")
    else:
        print(f"     [!!] Fase 4 fallo: {result_4.get('error','?')}")

    # ------------------------------------------------------------------
    # CONSOLIDAR
    # ------------------------------------------------------------------
    print("\n[3/3] Consolidando resultados...")
    metrics = {}
    if ocr_json and Path(ocr_json).exists():
        metrics = consolidate_ocr_results(
            ocr_json_path=ocr_json,
            output_dir=str(output_dir / "consolidated"),
        )
        guardar_dashboard_metricas(ocr_json, metrics, output_dir / "dashboard_metricas.png")
        print(f"     [OK] Dashboard de metricas guardado")

    # ------------------------------------------------------------------
    # RESUMEN
    # ------------------------------------------------------------------
    t_fin = time.time() - t_total
    tm = metrics.get("text_metrics", {})
    cm = metrics.get("ocr_confidence_metrics", {})

    print()
    print("=" * 65)
    print("  RESULTADO FINAL")
    print("=" * 65)
    print(f"  Tiempo total    : {t_fin:.1f}s ({t_fin/60:.1f} min)")
    print(f"  Fase 3A         : {t3a:.1f}s")
    print(f"  Fase 4 (OCR)    : {t4:.1f}s")
    print(f"  Bloques OCR     : {tm.get('total_blocks', 'N/A')}")
    print(f"  Palabras        : {tm.get('total_words', 'N/A')}")
    print(f"  Confianza prom. : {cm.get('average_percent', 0):.2f}%")
    print()
    print("  Archivos generados:")
    archivos = {
        "evidencias_fase3a.png" : "Cuadricula de evidencias (deteccion sello)",
        "detecciones_ocr.png"   : "Bounding boxes color-coded por confianza",
        "dashboard_metricas.png": "Dashboard con histograma + tabla + calidad",
        "fase_3a/"              : "Imagen limpia sin sello",
        "fase_4/"               : "JSON con bloques OCR y coordenadas",
        "consolidated/"         : "Texto plano + metricas JSON",
    }
    for nombre, desc in archivos.items():
        ruta = output_dir / nombre
        existe = ruta.exists()
        print(f"  {'[OK]' if existe else '[ ] '} {nombre:30} {desc}")
    print()
    print(f"  Carpeta: {output_dir}")
    print("=" * 65)

    # Texto extraido — preview
    txt_file = output_dir / "consolidated" / "ocr_extracted_text.txt"
    if txt_file.exists():
        print("\n  TEXTO EXTRAIDO (primeros 600 caracteres):")
        print("  " + "-" * 63)
        with open(txt_file, encoding="utf-8") as f:
            preview = f.read(600)
        for linea in preview.splitlines():
            print(f"  {linea}")
        print("  " + "-" * 63)


if __name__ == "__main__":
    main()
