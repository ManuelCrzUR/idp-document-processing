import os
import shutil
import pandas as pd
import base64
from PIL import Image
import io
from tqdm import tqdm
import zipfile
import subprocess

# Configuración de rutas
BASE_DIR = r'c:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project'
DATOS_DIR = os.path.join(BASE_DIR, 'datos')

# Nuevas rutas estándar
SPANISH_OCR_DIR = os.path.join(DATOS_DIR, 'spanishocr')
STAVER_DIR = os.path.join(DATOS_DIR, 'staver')
STAMPS_SYNTH_DIR = os.path.join(DATOS_DIR, 'stamps_synthetic')
SROIE_V2_DIR = os.path.join(DATOS_DIR, 'sroie_v2')
SROIE_ORIG_DIR = os.path.join(DATOS_DIR, 'sroie_original')

def ensure_dirs():
    dirs = [
        os.path.join(SPANISH_OCR_DIR, 'raw'),
        os.path.join(SPANISH_OCR_DIR, 'images'),
        os.path.join(SPANISH_OCR_DIR, 'texts'),
        STAVER_DIR,
        os.path.join(STAMPS_SYNTH_DIR, 'images'),
        SROIE_V2_DIR,
        SROIE_ORIG_DIR
    ]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"[INFO] Creada carpeta: {d}")

def process_spanish_ocr():
    print("\n--- Procesando SpanishOCR ---")
    legacy_data_dir = os.path.join(DATOS_DIR, 'data')
    raw_dir = os.path.join(SPANISH_OCR_DIR, 'raw')
    img_dir = os.path.join(SPANISH_OCR_DIR, 'images')
    txt_dir = os.path.join(SPANISH_OCR_DIR, 'texts')

    if os.path.exists(legacy_data_dir):
        files = [f for f in os.listdir(legacy_data_dir) if f.endswith('.parquet')]
        for f in files:
            src = os.path.join(legacy_data_dir, f)
            dst = os.path.join(raw_dir, f)
            if not os.path.exists(dst):
                shutil.move(src, dst)
        print(f"[OK] Movidos {len(files)} parquets a {raw_dir}")

    # Extracción de imágenes
    parquets = [f for f in os.listdir(raw_dir) if f.endswith('.parquet')]
    for p in parquets:
        p_path = os.path.join(raw_dir, p)
        print(f" Extrayendo de {p}...")
        df = pd.read_parquet(p_path)
        for i, row in tqdm(df.iterrows(), total=len(df), desc=f"Extrayendo {p}"):
            img_name = f"{p.replace('.parquet', '')}_{i}.png"
            txt_name = f"{p.replace('.parquet', '')}_{i}.txt"
            
            img_path = os.path.join(img_dir, img_name)
            txt_path = os.path.join(txt_dir, txt_name)
            
            if not os.path.exists(img_path):
                img_data = base64.b64decode(row['image'])
                img = Image.open(io.BytesIO(img_data))
                img.save(img_path)
            
            if not os.path.exists(txt_path):
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(row['text'])

def download_kaggle(dataset_id, target_dir):
    print(f"\n--- Descargando de Kaggle: {dataset_id} ---")
    try:
        subprocess.run(['kaggle', 'datasets', 'download', '-d', dataset_id, '-p', target_dir, '--unzip'], check=True)
        print(f"[OK] {dataset_id} descargado y descomprimido en {target_dir}")
    except Exception as e:
        print(f"[ERROR] No se pudo descargar {dataset_id}: {e}")
        print("Asegúrate de tener configurada la Kaggle API (kaggle.json)")

def reorganize_stamps():
    print("\n--- Reorganizando Stamps Mendeley ---")
    legacy_stamps = os.path.join(DATOS_DIR, 'stamps_dataset', 'Stapms Dataset')
    target_img = os.path.join(STAMPS_SYNTH_DIR, 'images')
    
    if os.path.exists(legacy_stamps):
        files = os.listdir(legacy_stamps)
        for f in tqdm(files, desc="Moviendo sellos"):
            shutil.copy2(os.path.join(legacy_stamps, f), os.path.join(target_img, f))
        print(f"[OK] Movidos {len(files)} sellos a {target_img}")

def main():
    ensure_dirs()
    process_spanish_ocr()
    # reorganize_stamps()
    
    # Kaggle downloads (Deshabilitados por ahora a petición del usuario)
    # download_kaggle('rtatman/stamp-verification-staver-dataset', STAVER_DIR)
    # download_kaggle('urbikn/sroie-datasetv2', SROIE_V2_DIR)
    # download_kaggle('dattrinh12/sroie-dataset', SROIE_ORIG_DIR)
    
    print("\n[FINALIZADO] El dataset SpanishOCR ha sido re-procesado.")
    print("Corre 'python data_registry.py' para ver el resumen.")

if __name__ == "__main__":
    main()
