# Batch Processing 200+ Synthetic Images - Complete Workflow

## 🎯 Overview

Este workflow procesa **201 imágenes sintéticas** a través del pipeline completo con:

- ✅ **Paralelización inteligente** (4 workers simultáneos)
- ✅ **Batch processing** (procesar + limpiar RAM incrementalmente)
- ✅ **Guardado inmediato** (cada imagen se guarda al terminar)
- ✅ **Métricas detalladas** (timing, confidence, throughput)
- ✅ **Análisis automático** (reportes + gráficas)

**Tiempo estimado**: 45-60 minutos  
**Imágenes procesadas**: 201  
**Salida**: ~800MB de resultados (fase por fase)

---

## 📋 Paso a Paso

### **Paso 1: Pre-flight Check** (2 min)
```bash
python batch_preflight_check.py
```

Verifica:
- ✓ 201 imágenes encontradas (381MB)
- ✓ Dependencias instaladas
- ✓ Pipeline functions importan correctamente
- ✓ RAM disponible (recomendado 4GB)
- ✓ Disco con espacio (600MB requerido)

**Si todo pasa**: Procede a Paso 2

**Si falla algo**: 
- Sigue las instrucciones del script
- Instala dependencias si falta algo
- Reduce NUM_WORKERS si falta RAM

---

### **Paso 2: Ejecutar Batch Processing** (45-60 min)

```bash
python batch_process_pipeline.py
```

El script:
1. Descubre las 201 imágenes
2. Las procesa en paralelo (4 workers)
3. Guarda resultados incrementalmente
4. Limpia RAM cada 5 imágenes
5. Reporta progreso en tiempo real
6. Genera `summary.json` con todas las métricas

**Output en consola**:
```
[BATCH 1] Processing images 1-5/201
  Progress: |████░░░░░░| 20%
  [OK] synthetic_image_001.png  16.23s | Conf: 85.2% | Blocks: 42
  [OK] synthetic_image_002.png  17.15s | Conf: 88.1% | Blocks: 38
  ...
  [Memory] After batch: 45.3% used (8.5GB available)

[BATCH 2] Processing images 6-10/201
  ...
```

**Resultado**: Carpeta `batch_results/TIMESTAMP/` con todos los resultados

---

### **Paso 3: Analizar Resultados** (2 min)

```bash
python batch_analyze_results.py batch_results/TIMESTAMP
```

O automaticamente después de la más reciente:
```bash
python batch_analyze_results.py $(ls -t batch_results/ | head -1 | xargs -I {} echo batch_results/{})
```

El script genera:
- **ANALYSIS_REPORT.txt** - Reporte en texto
- **analysis_visualization.png** - Gráficas (4 plots)
- Estadísticas en consola

---

## 📊 Estructura de Resultados

```
batch_results/20260525_143022/
├── phase_3a/                          [Imágenes limpias]
│   ├── synthetic_image_001/
│   │   └── cleaned_image.png          [Sello removido]
│   ├── synthetic_image_002/
│   │   └── cleaned_image.png
│   └── ... (201 carpetas)
│
├── phase_4/                           [OCR JSON]
│   ├── synthetic_image_001/
│   │   └── ocr_results.json           [Bloques, coords, confianza]
│   ├── synthetic_image_002/
│   │   └── ocr_results.json
│   └── ... (201 carpetas)
│
├── consolidated/                      [Texto extraído + métricas]
│   ├── synthetic_image_001/
│   │   ├── ocr_extracted_text.txt     [Texto puro]
│   │   └── ocr_metrics.json           [Confidence, words, entities]
│   ├── synthetic_image_002/
│   │   ├── ocr_extracted_text.txt
│   │   └── ocr_metrics.json
│   └── ... (201 carpetas)
│
├── logs/                              [Resultados individuales por imagen]
│   ├── synthetic_image_001_result.json
│   ├── synthetic_image_002_result.json
│   └── ... (201 archivos)
│
├── summary.json                       [MÉTRICAS GLOBALES]
│   ├── images_processed: 198
│   ├── images_failed: 3
│   ├── avg_time_per_image: 16.4s
│   ├── throughput: 3.66 img/min
│   ├── phase_timing:
│   │   ├── phase_3a: 8.2s (avg)
│   │   ├── phase_4: 7.1s (avg)
│   │   └── consolidate: 1.1s (avg)
│   └── ...
│
├── ERRORS.txt                         [Imágenes fallidas]
├── ANALYSIS_REPORT.txt                [Reporte de análisis]
└── analysis_visualization.png         [Gráficas]
```

---

## 📈 Métricas que obtendrás

### Timing
```
Total time: 3247.5 seconds (54.1 min)
Average per image: 16.4 seconds
Throughput: 3.66 images/min
Success rate: 98.5% (198/201 imágenes exitosas)
```

### Por Fase
```
Phase 3A (Stamp Removal): 8.2s promedio
  - Detección chromática
  - Horizontal sweep filter
  - Inpainting

Phase 4 (OCR Extraction): 7.1s promedio
  - EasyOCR detección
  - Spell correction (Levenshtein)
  - NER (Named Entity Recognition)

Consolidate: 1.1s promedio
  - Extracción a TXT
  - Cálculo de métricas
```

### Calidad OCR
```
Average confidence: 85.2%
  - High (≥80%): 142 imágenes (70.6%)
  - Medium (50-80%): 45 imágenes (22.4%)
  - Low (<50%): 12 imágenes (6.0%)

Average blocks detected: 41.3 per image
Average text extracted: 3,847 characters per image
```

---

## 🎛️ Ajustar Configuración

Edit `batch_process_pipeline.py` líneas 40-41:

```python
NUM_WORKERS = 4  # Cambiar según tu sistema
BATCH_SIZE = 5   # Cambiar si quieres cleanup más frecuente
```

### Recomendaciones
| Sistema | NUM_WORKERS | BATCH_SIZE | Notas |
|---------|-------------|-----------|-------|
| 8GB RAM | 3 | 3 | Conservador (80 min total) |
| 16GB RAM | 4 | 5 | **Recomendado** (50-60 min) |
| 32GB RAM | 6 | 8 | Agresivo (30-40 min) |

---

## ⚠️ Troubleshooting

### Problema: "RAM se llena rápidamente"
```python
NUM_WORKERS = 2  # Reducir paralelismo
BATCH_SIZE = 3   # Cleanup más frecuente
```

### Problema: "Algunas imágenes fallan"
Normal - OCR a veces falla en imágenes difíciles. Ver `ERRORS.txt` para detalles. El script continúa.

### Problema: "Muy lento (>25s por imagen)"
```python
NUM_WORKERS = 6   # Aumentar paralelismo
BATCH_SIZE = 8    # Batch más grande
```
(Solo si tienes 32GB+ RAM)

### Problema: "First run is taking forever"
Primera ejecución descarga modelo de EasyOCR (~5-10 min). Subsecuentes ejecutarán es más rápido.

---

## 🔄 Reanudar si se interrumpe

Si el script se detiene a mitad:

1. **Identifica último batch procesado**:
   ```bash
   ls -t batch_results/TIMESTAMP/logs/ | head -1
   ```

2. **El script detectará imágenes existentes y continuará automáticamente**

3. **Ejecuta de nuevo**:
   ```bash
   python batch_process_pipeline.py
   ```

---

## 📊 Analizar resultados

### Ver resumen rápido
```bash
cat batch_results/*/summary.json | python -m json.tool | head -50
```

### Estadísticas de timing
```bash
python -c "
import json
with open('batch_results/*/summary.json') as f:
    data = json.load(f)
    timings = [t['total_seconds'] for t in data['image_timings']]
    print(f'Min: {min(timings):.2f}s')
    print(f'Max: {max(timings):.2f}s')
    print(f'Avg: {sum(timings)/len(timings):.2f}s')
    print(f'Total: {sum(timings)/60:.1f} min')
"
```

### Ver errores
```bash
cat batch_results/*/ERRORS.txt | head -20
```

---

## 📁 Después: Procesar Resultados

Con los 201 conjuntos de resultados, puedes:

### 1. Extraer estadísticas globales
```python
import json
from pathlib import Path

results_dir = Path("batch_results/TIMESTAMP")
all_metrics = []

for metric_file in results_dir.glob("consolidated/*/ocr_metrics.json"):
    with open(metric_file) as f:
        all_metrics.append(json.load(f))

# Ahora tienes 201 diccionarios de métricas
avg_confidence = sum(m.get('average_percent', 0) for m in all_metrics) / len(all_metrics)
total_chars = sum(m.get('total_characters', 0) for m in all_metrics)
```

### 2. Generar dataset de ground truth
Las imágenes limpias en `phase_3a/` ahora puedes usarlas como conjunto de entrenamiento

### 3. Análisis de confianza
Los `phase_4/*/ocr_results.json` tienen `bloques` con coordenadas y confianza para análisis espacial

### 4. Reportar cobertura
`summary.json` tiene todo para un reporte técnico

---

## 🚀 Flujo Completo (Resumen)

```
1. python batch_preflight_check.py     [2 min - Verifica prerequisitos]
   ↓
2. python batch_process_pipeline.py    [45-60 min - Procesa 201 imágenes]
   ↓
3. python batch_analyze_results.py ... [2 min - Genera reportes]
   ↓
4. Resultados en batch_results/TIMESTAMP/
   ├── 201 imágenes limpias (phase_3a/)
   ├── 201 OCR JSON (phase_4/)
   ├── 201 textos extraídos (consolidated/)
   ├── 201 métricas por imagen (logs/)
   ├── summary.json (estadísticas globales)
   ├── ERRORS.txt (imágenes fallidas)
   ├── ANALYSIS_REPORT.txt (reporte)
   └── analysis_visualization.png (gráficas)
```

---

## 💾 Requisitos Mínimos

- **Python**: 3.8+
- **RAM**: 8GB (recomendado 16GB)
- **Disco**: 1GB libre (para resultados)
- **CPU**: Multi-core (4+ recomendado)
- **Dependencies**: opencv-python-headless, easyocr, spacy, numpy, tqdm

Verificar todo con:
```bash
python batch_preflight_check.py
```

---

## 📝 Documentación Relacionada

- **BATCH_PROCESSING_GUIDE.md** - Detalles técnicos del batch processing
- **batch_process_pipeline.py** - Script principal (editable)
- **batch_preflight_check.py** - Verificaciones pre-ejecución
- **batch_analyze_results.py** - Análisis post-procesamiento

---

## ❓ Preguntas Frecuentes

**P: ¿Cuánto tiempo tarda?**  
A: 45-60 minutos para 201 imágenes (~16.4s/imagen promedio)

**P: ¿Puedo detener e reanudar?**  
A: Sí, el script detecta imágenes procesadas y continúa donde se detuvo

**P: ¿Qué pasa si una imagen falla?**  
A: El script continúa con las demás. Ver ERRORS.txt para detalles.

**P: ¿Necesito GPU?**  
A: No, funciona perfectamente en CPU. GPU solo acelera Phase 4.

**P: ¿Cuánto espacio en disco?**  
A: ~600MB para los 201 resultados

**P: ¿Puedo procesar más de 201?**  
A: Sí, el script detecta automáticamente todas las imágenes en el directorio

---

**Status**: ✅ Ready to run. Start with `python batch_preflight_check.py`

