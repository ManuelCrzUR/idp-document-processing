import os
import json
from datetime import datetime

BASE_DIR = r'c:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project'
DATOS_DIR = os.path.join(BASE_DIR, 'datos')

def get_dir_size(path):
    total_size = 0
    if not os.path.exists(path): return 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total_size += os.path.getsize(fp)
            except: continue
    return total_size / (1024 * 1024)  # MB

def count_files(path, extensions=None):
    count = 0
    found_exts = set()
    if not os.path.exists(path): return 0, []
    for root, dirs, files in os.walk(path):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if extensions is None or ext in extensions:
                count += 1
                found_exts.add(ext)
    return count, list(found_exts)

def register_data():
    print("--- Generando Registro de Datos (Versión Ligera) ---")
    datasets = {
        "SpanishOCR": os.path.join(DATOS_DIR, 'spanishocr'),
        "StaVer": os.path.join(DATOS_DIR, 'staver'),
        "Stamps Synthetic": os.path.join(DATOS_DIR, 'stamps_synthetic'),
        "SROIE v2": os.path.join(DATOS_DIR, 'sroie_v2'),
        "SROIE Original": os.path.join(DATOS_DIR, 'sroie_original')
    }

    report = []
    
    md_content = "# Registro de Datos - IDP\n"
    md_content += f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += "| Dataset | Imágenes | Textos | Tamaño (MB) | Formatos |\n"
    md_content += "|---------|----------|--------|-------------|----------|\n"

    total_imgs = 0
    total_txts = 0
    total_size = 0

    for name, path in datasets.items():
        if not os.path.exists(path):
            md_content += f"| {name} | 0 | 0 | 0.00 | No encontrado |\n"
            continue

        size_mb = get_dir_size(path)
        img_count, img_exts = count_files(path, ['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'])
        txt_count, _ = count_files(path, ['.txt', '.json', '.csv', '.xml', '.parquet'])

        md_content += f"| {name} | {img_count} | {txt_count} | {size_mb:.2f} | {', '.join(img_exts)} |\n"
        
        total_imgs += img_count
        total_txts += txt_count
        total_size += size_mb

    md_content += f"\n\n**TOTAL:** {total_imgs} imágenes, {total_txts} archivos, {total_size:.2f} MB"

    md_path = os.path.join(DATOS_DIR, 'DATA_REGISTRY.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"[OK] Reporte generado en: {md_path}")
    print(md_content)

if __name__ == "__main__":
    register_data()
