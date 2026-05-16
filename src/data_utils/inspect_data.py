import pandas as pd
import os

# Configuración de rutas
BASE_DIR = r'c:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project'
DATA_FILE = os.path.join(BASE_DIR, 'datos', 'data', 'train-00000-of-00024.parquet')

def inspect_parquet():
    print(f"--- Inspeccionando archivo: {os.path.basename(DATA_FILE)} ---")
    
    if not os.path.exists(DATA_FILE):
        print(f"Error: No se encuentra el archivo en {DATA_FILE}")
        return

    try:
        # Intentar leer el parquet
        # Nota: Requiere 'pip install pandas pyarrow'
        df = pd.read_parquet(DATA_FILE)
        
        print("\n[INFO] Dimensiones del DataFrame:", df.shape)
        print("\n[INFO] Columnas detectadas:")
        for col in df.columns:
            print(f" - {col} ({df[col].dtype})")
            
        print("\n[INFO] Primeras 5 filas:")
        print(df.head())
        
        # Guardar un resumen a texto para referencia rápida
        summary_path = os.path.join(BASE_DIR, 'datos', 'inspeccion_resumen.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"Resumen de inspección de {os.path.basename(DATA_FILE)}\n")
            f.write(f"Filas: {df.shape[0]}, Columnas: {df.shape[1]}\n\n")
            f.write("Columnas:\n" + "\n".join(df.columns))
            
        print(f"\n[OK] Resumen guardado en: {summary_path}")

    except Exception as e:
        print(f"\n[ERROR] Ocurrió un problema al leer el archivo: {e}")
        print("Asegúrate de tener instaladas las librerías: pip install pandas pyarrow")

if __name__ == "__main__":
    inspect_parquet()
