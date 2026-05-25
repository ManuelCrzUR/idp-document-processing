import os
import json
import pandas as pd
from PIL import Image
from tabulate import tabulate
from datetime import datetime

# BASE_DIR can be set via IDP_DATA_ROOT environment variable
BASE_DIR = os.environ.get(
    'IDP_DATA_ROOT',
    r'c:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project'
)
DATOS_DIR = os.path.join(BASE_DIR, 'datos')

def get_dir_size(path):
    total_size = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)  # MB

def count_files(path, extensions=None):
    count = 0
    found_exts = set()
    for root, dirs, files in os.walk(path):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if extensions is None or ext in extensions:
                count += 1
                found_exts.add(ext)
    return count, list(found_exts)

def get_avg_resolution(path, n=10):
    resolutions = []
    count = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')):
                try:
                    with Image.open(os.path.join(root, f)) as img:
                        resolutions.append(img.size)
                        count += 1
                    if count >= n: break
                except: continue
        if count >= n: break
    
    if not resolutions: return "N/A"
    avg_w = sum(r[0] for r in resolutions) / len(resolutions)
    avg_h = sum(r[1] for r in resolutions) / len(resolutions)
    return f"{int(avg_w)}x{int(avg_h)}"

def register_data():
    print("--- Generando Registro de Datos ---")
    datasets = {
        "SpanishOCR": os.path.join(DATOS_DIR, 'spanishocr'),
        "StaVer": os.path.join(DATOS_DIR, 'staver'),
        "Stamps Synthetic": os.path.join(DATOS_DIR, 'stamps_synthetic'),
        "SROIE v2": os.path.join(DATOS_DIR, 'sroie_v2'),
        "SROIE Original": os.path.join(DATOS_DIR, 'sroie_original')
    }

    report = []
    json_data = {}

    for name, path in datasets.items():
        if not os.path.exists(path):
            report.append([name, 0, 0, 0, "No encontrado", "N/A"])
            continue

        size_mb = get_dir_size(path)
        img_count, img_exts = count_files(path, ['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'])
        txt_count, _ = count_files(path, ['.txt', '.json', '.csv', '.xml'])
        res = get_avg_resolution(path)

        report.append([
            name, 
            img_count, 
            txt_count, 
            f"{size_mb:.2f}", 
            ", ".join(img_exts),
            res
        ])
        
        json_data[name] = {
            "images": img_count,
            "texts": txt_count,
            "size_mb": size_mb,
            "formats": img_exts,
            "avg_resolution": res,
            "path": path,
            "last_updated": datetime.now().isoformat()
        }

    # Totales
    total_imgs = sum(r[1] for r in report)
    total_txts = sum(r[2] for r in report)
    total_size = sum(float(r[3]) if r[3] != "0" and isinstance(r[3], str) else 0 for r in report)
    
    headers = ["Dataset", "Imágenes", "Textos", "Tamaño (MB)", "Formatos", "Res. Promedio"]
    table = tabulate(report, headers=headers, tablefmt="github")

    # Guardar Markdown
    md_path = os.path.join(DATOS_DIR, 'DATA_REGISTRY.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Registro de Datos - IDP\n")
        f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(table)
        f.write(f"\n\n**TOTAL:** {total_imgs} imágenes, {total_txts} anotaciones, {total_size:.2f} MB")

    # Guardar JSON
    json_path = os.path.join(DATOS_DIR, 'data_registry.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4)

    print(f"[OK] Reporte generado en: {md_path}")
    print(table)

if __name__ == "__main__":
    register_data()
