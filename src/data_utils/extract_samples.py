import pandas as pd
import base64
import os
from PIL import Image
import io

# Configuración de rutas
BASE_DIR = r'c:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project'
DATA_FILE = os.path.join(BASE_DIR, 'datos', 'data', 'train-00000-of-00024.parquet')
OUTPUT_DIR = os.path.join(BASE_DIR, 'datos', 'muestras')

def extract_samples(n=5):
    print(f"--- Extrayendo {n} muestras de: {os.path.basename(DATA_FILE)} ---")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"[INFO] Carpeta de muestras creada: {OUTPUT_DIR}")

    try:
        # Leer el parquet
        df = pd.read_parquet(DATA_FILE)
        
        for i in range(min(n, len(df))):
            img_b64 = df.iloc[i]['image']
            img_text = df.iloc[i]['text']
            
            # Decodificar base64 a imagen
            img_data = base64.b64decode(img_b64)
            img = Image.open(io.BytesIO(img_data))
            
            # Guardar imagen
            img_path = os.path.join(OUTPUT_DIR, f'muestra_{i}.png')
            img.save(img_path)
            
            # Guardar texto asociado para referencia
            txt_path = os.path.join(OUTPUT_DIR, f'muestra_{i}_texto.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(img_text)
                
            print(f" - [OK] Muestra {i} guardada en: {os.path.basename(img_path)}")

        print(f"\n[FINALIZADO] Puedes ver las imágenes en: {OUTPUT_DIR}")

    except Exception as e:
        print(f"\n[ERROR] Ocurrió un problema: {e}")

if __name__ == "__main__":
    # Necesita: pip install pandas pyarrow Pillow
    extract_samples(5)
