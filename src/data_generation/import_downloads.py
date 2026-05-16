import os
import zipfile
import shutil
import subprocess
from tqdm import tqdm

# Configuración de rutas
BASE_DIR = r'c:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project'
DATOS_DIR = os.path.join(BASE_DIR, 'datos')
DOWNLOADS_DIR = os.path.join(os.environ['USERPROFILE'], 'Downloads')

# Rutas de origen (Downloads)
STAMPS_RAR = os.path.join(DOWNLOADS_DIR, 'Stapms Dataset.rar')
STAVER_ZIP = os.path.join(DOWNLOADS_DIR, 'archive (2).zip')
SROIE_V2_ZIP = os.path.join(DOWNLOADS_DIR, 'archive (3).zip')
SROIE_ORIG_ZIP = os.path.join(DOWNLOADS_DIR, 'archive (4).zip')

# Rutas de destino
STAMPS_DEST = os.path.join(DATOS_DIR, 'stamps_synthetic', 'images')
STAVER_DEST = os.path.join(DATOS_DIR, 'staver')
SROIE_V2_DEST = os.path.join(DATOS_DIR, 'sroie_v2')
SROIE_ORIG_DEST = os.path.join(DATOS_DIR, 'sroie_original')

def get_winrar_path():
    paths = [
        r"C:\Program Files\WinRAR\UnRAR.exe",
        r"C:\Program Files (x86)\WinRAR\UnRAR.exe"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def flatten_folder(src, dest, extensions=None):
    """Copia archivos de src a dest recursivamente eliminando la estructura de carpetas."""
    if not os.path.exists(dest):
        os.makedirs(dest)
    
    count = 0
    for root, dirs, files in os.walk(src):
        for f in files:
            if extensions and not any(f.lower().endswith(ext) for ext in extensions):
                continue
            shutil.move(os.path.join(root, f), os.path.join(dest, f))
            count += 1
    return count

def import_stamps():
    print(f"\n--- Importando Stamps Mendeley ---")
    if not os.path.exists(STAMPS_RAR):
        print(f"[SKIP] No se encontró {STAMPS_RAR}")
        return

    unrar = get_winrar_path()
    if not unrar:
        print("[ERROR] No se encontró WinRAR/UnRAR.exe. Por favor extrae el RAR manualmente a stamps_synthetic/images.")
        return

    temp_dir = os.path.join(DATOS_DIR, 'temp_stamps')
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f" Extrayendo {STAMPS_RAR}...")
    try:
        subprocess.run([unrar, 'x', STAMPS_RAR, temp_dir], check=True, stdout=subprocess.DEVNULL)
        count = flatten_folder(temp_dir, STAMPS_DEST, extensions=['.bmp', '.png', '.jpg'])
        print(f"[OK] Importados {count} sellos a {STAMPS_DEST}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def import_zip_dataset(zip_path, dest_path, name):
    print(f"\n--- Importando {name} ---")
    if not os.path.exists(zip_path):
        print(f"[SKIP] No se encontró {zip_path}")
        return

    temp_dir = os.path.join(DATOS_DIR, f'temp_{name.lower().replace(" ", "_")}')
    os.makedirs(temp_dir, exist_ok=True)

    print(f" Extrayendo {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # Kaggle ZIPs suelen tener una subcarpeta con el mismo nombre o "archive"
    # Aplanamos un nivel si detectamos que todo está dentro de una sola carpeta
    subdirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
    
    # Mover archivos al destino final
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    
    # Si hay subcarpetas críticas como 'scans', 'ground-truth', etc., las movemos tal cual
    for item in os.listdir(temp_dir):
        src_item = os.path.join(temp_dir, item)
        dst_item = os.path.join(dest_path, item)
        if os.path.exists(dst_item):
            if os.path.isdir(dst_item): shutil.rmtree(dst_item)
            else: os.remove(dst_item)
        shutil.move(src_item, dst_item)
    
    print(f"[OK] {name} importado correctamente en {dest_path}")
    shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    import_stamps()
    import_zip_dataset(STAVER_ZIP, STAVER_DEST, "StaVer")
    import_zip_dataset(SROIE_V2_ZIP, SROIE_V2_DEST, "SROIE v2")
    import_zip_dataset(SROIE_ORIG_ZIP, SROIE_ORIG_DEST, "SROIE Original")
    
    print("\n[FINALIZADO] Proceso de importación completo.")

if __name__ == "__main__":
    main()
