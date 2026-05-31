# Batch Pipeline Processing - 200+ Images

**Script**: `batch_process_pipeline.py`

Procesa **201 imágenes sintéticas** en paralelo con:
- ✅ Paralelización (N workers simultáneos)
- ✅ Batch mode (procesamiento + cleanup incremental)
- ✅ Guardado inmediato de cada resultado
- ✅ Métricas detalladas de timing y RAM
- ✅ Error handling con fallback

---

## 📊 Arquitectura

### Estrategia de Memoria
```
Batch 1 (5 imágenes)
├─ Worker 1: Image 1 → Phase 3A → Phase 4 → Consolidate → SAVE
├─ Worker 2: Image 2 → Phase 3A → Phase 4 → Consolidate → SAVE
├─ Worker 3: Image 3 → Phase 3A → Phase 4 → Consolidate → SAVE
├─ Worker 4: Image 4 → Phase 3A → Phase 4 → Consolidate → SAVE
└─ Worker 1: Image 5 → Phase 3A → Phase 4 → Consolidate → SAVE
    ↓ [gc.collect() + cleanup]
Batch 2 (5 imágenes) — RAM cleared from Batch 1
```

**Ventajas**:
- ✅ 4 imágenes procesando simultáneamente (no 201 en RAM)
- ✅ Cada imagen se guarda inmediatamente (no pierde trabajo)
- ✅ Cleanup entre batches (RAM no crece indefinidamente)
- ✅ Si falla una imagen, las demás continúan

---

## 🚀 Uso

### Opción 1: Ejecutar con parámetros por defecto
```bash
python batch_process_pipeline.py
```

**Configuración por defecto**:
- NUM_WORKERS = 4 (parallelismo)
- BATCH_SIZE = 5 (cleanup después de 5 imágenes)
- Salida en: `batch_results/TIMESTAMP/`

### Opción 2: Ajustar parámetros antes de ejecutar

Edit `batch_process_pipeline.py` líneas 40-41:
```python
NUM_WORKERS = 4  # ← Cambiar según RAM (3-6 recomendado)
BATCH_SIZE = 5   # ← Cambiar si quieres cleanup más frecuente
```

**Recomendaciones por RAM disponible**:
| RAM | NUM_WORKERS | BATCH_SIZE | Notas |
|-----|-------------|-----------|-------|
| 8GB | 3 | 3 | Conservador |
| 16GB | 4 | 5 | Recomendado |
| 32GB | 6 | 8 | Agresivo |

---

## 📈 Qué esperar

### Tiempo estimado
Con 201 imágenes (381MB total, ~1.9MB c/u):

| Configuración | Tiempo estimado | Notas |
|---------------|-----------------|-------|
| NUM_WORKERS=4, BATCH_SIZE=5 | 45-60 min | **Recomendado** |
| NUM_WORKERS=3, BATCH_SIZE=3 | 60-75 min | Más conservador |
| NUM_WORKERS=6, BATCH_SIZE=8 | 30-40 min | Si tienes 32GB RAM |

**Tiempo promedio por imagen**: ~15-20 segundos (Phase 3A + Phase 4)

### Output en tiempo real
```
[BATCH 1] Processing images 1-5/201
  Progress: |████░░░░░░| 20%
  [OK] synthetic_image_001.png  16.23s | Conf: 85.2% | Blocks: 42
  [OK] synthetic_image_002.png  17.15s | Conf: 88.1% | Blocks: 38
  [OK] synthetic_image_003.png  15.89s | Conf: 82.3% | Blocks: 45
  [FAIL] synthetic_image_004.png  18.45s [phase 4 timeout]
  [OK] synthetic_image_005.png  16.67s | Conf: 86.7% | Blocks: 40
  [Memory] After batch: 45.3% used (8.5GB available)
```

---

## 📁 Estructura de resultados

```
batch_results/20260525_143022/
├── phase_3a/
│   ├── synthetic_image_001/
│   │   └── cleaned_image.png        [Imagen sin sello]
│   ├── synthetic_image_002/
│   │   └── cleaned_image.png
│   └── ...
│
├── phase_4/
│   ├── synthetic_image_001/
│   │   └── ocr_results.json         [JSON con bloques, coords, confianza]
│   ├── synthetic_image_002/
│   │   └── ocr_results.json
│   └── ...
│
├── consolidated/
│   ├── synthetic_image_001/
│   │   ├── ocr_extracted_text.txt   [Texto extraído puro]
│   │   └── ocr_metrics.json         [Métricas per-imagen]
│   ├── synthetic_image_002/
│   │   ├── ocr_extracted_text.txt
│   │   └── ocr_metrics.json
│   └── ...
│
├── logs/
│   ├── synthetic_image_001_result.json   [Result dict de worker]
│   ├── synthetic_image_002_result.json
│   └── ...
│
├── summary.json                     [MÉTRICAS GLOBALES]
├── ERRORS.txt                       [Errores de imágenes fallidas]
└── TIMESTAMP.log                    [Execution log]
```

---

## 📊 Métricas generadas

### `summary.json` - Estadísticas globales
```json
{
  "start_time": "2026-05-25T14:30:22",
  "total_images": 201,
  "images_processed": 198,
  "images_failed": 3,
  "summary": {
    "total_time_seconds": 3247.5,
    "avg_time_per_image_seconds": 16.4,
    "throughput_images_per_minute": 3.66,
    "success_rate_percent": 98.5,
    "avg_phase_timing": {
      "phase_3a": 8.2,
      "phase_4": 7.1,
      "consolidate": 1.1
    }
  },
  "image_timings": [
    {
      "image": "synthetic_image_001.png",
      "total_seconds": 16.23,
      "size_mb": 1.85,
      "throughput_mb_per_sec": 0.114
    },
    ...
  ],
  "errors_log": [
    {
      "image": "synthetic_image_045.png",
      "errors": ["Phase 4 timeout", "EasyOCR worker crash"]
    }
  ]
}
```

### Por imagen: `logs/synthetic_image_001_result.json`
```json
{
  "image_name": "synthetic_image_001.png",
  "success": true,
  "phases_completed": ["3a", "4", "consolidate"],
  "timing": {
    "phase_3a": 8.23,
    "phase_4": 7.15,
    "consolidate": 1.02,
    "total": 16.40,
    "image_size_mb": 1.85
  },
  "memory_delta_mb": 245.3,
  "ocr_blocks": 42,
  "ocr_confidence": 0.852,
  "ocr_text_length": 3847,
  "metrics": {
    "total_characters": 3847,
    "total_words": 534,
    "total_blocks": 42,
    "avg_confidence": 85.2,
    "words_corrected": 3,
    "entities_detected": 8
  }
}
```

---

## 🎯 Interpretación de métricas

### **avg_time_per_image_seconds**
- **15-20s** = Normal (OCR descargado)
- **20-30s** = Primera ejecución (EasyOCR descarga modelos)
- **>30s** = Posible bottleneck (GPU no disponible, disco lento)

### **throughput_images_per_minute**
- **4+ img/min** = Excelente
- **2-4 img/min** = Bueno
- **<2 img/min** = Revisar recursos

### **success_rate_percent**
- **>95%** = Pipeline robusto ✅
- **85-95%** = Aceptable (ver ERRORS.txt)
- **<85%** = Problema en configuración

### **avg_phase_timing**
Desglose de cuánto tarda cada fase:
- **phase_3a**: Detección + inpainting
- **phase_4**: OCR (tipicamente más lenta)
- **consolidate**: Post-processing

---

## ⚙️ Ajustes si hay problemas

### Problema: RAM se llena rápidamente
```python
NUM_WORKERS = 3   # Reducir de 4 a 3
BATCH_SIZE = 3    # Reducir de 5 a 3
```

### Problema: Algunas imágenes fallan en Phase 4
- Es normal (EasyOCR a veces timeout en imágenes difíciles)
- Revisar `ERRORS.txt` para detalles
- El script continúa con las demás

### Problema: Muy lento (>25s por imagen)
```python
NUM_WORKERS = 6   # Aumentar paralelismo
BATCH_SIZE = 8    # Aumentar batch
```
(Solo si tienes 16GB+ RAM disponible)

---

## 📝 Análisis post-procesamiento

Después que termina, puedes analizar:

```bash
# Ver resumen rápido
cat batch_results/*/summary.json | python -m json.tool | head -50

# Contar imágenes exitosas
cat batch_results/*/summary.json | grep success_rate_percent

# Ver errores
cat batch_results/*/ERRORS.txt

# Estadísticas de timing
python -c "
import json
with open('batch_results/*/summary.json') as f:
    data = json.load(f)
    timings = [t['total_seconds'] for t in data['image_timings']]
    print(f'Min: {min(timings):.2f}s')
    print(f'Max: {max(timings):.2f}s')
    print(f'Avg: {sum(timings)/len(timings):.2f}s')
"
```

---

## 🔄 Recuperación de fallos

Si el script se interrumpe:

1. **Identifica último batch procesado** → Ver `batch_results/*/logs/`
2. **Crea lista de imágenes restantes**:
   ```python
   import json
   with open('batch_results/*/summary.json') as f:
       processed = {img['image'] for img in json.load(f)['image_timings']}
   remaining = [img for img in IMAGES_DIR.glob("*.png") 
                if img.name not in processed]
   ```
3. **Ejecuta script de nuevo** → Detecta imágenes existentes y continúa

---

## 📊 Script complementario: Análisis de resultados

Para analizar los 198 resultados procesados, crearé un script que:
- Genera reportes de cobertura
- Estadísticas de confidence
- Correlación entre tamaño imagen y tiempo
- Histogramas de distribución

¿Quieres que lo cree después de ejecutar el batch? 📈
