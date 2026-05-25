# 🔄 FLUJO COMPLETO DEL PIPELINE: INICIO A FIN

**Versión**: 1.0  
**Fecha**: 2026-05-25  
**Estado**: Documentado y funcional

---

## 📋 TABLA DE CONTENIDOS

1. [Flujo Visual](#flujo-visual)
2. [Fase 1: Entrada](#fase-1-entrada)
3. [Fase 2: Eliminación del Sello (Phase 3A)](#fase-2-eliminación-del-sello-phase-3a)
4. [Fase 3: Extracción OCR (Phase 4)](#fase-3-extracción-ocr-phase-4)
5. [Fase 4: Evaluación (Phase 5)](#fase-4-evaluación-phase-5)
6. [Fase 5: Salida Final](#fase-5-salida-final)
7. [Ejecución del Pipeline](#ejecución-del-pipeline)

---

## 🎯 FLUJO VISUAL

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          ENTRADA: IMAGEN ORIGINAL                        │
│              Documento con sello rojo (2550×3300 píxeles)                │
│         output/prueba_completa/01_imagen_original.png                   │
└──────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                    PHASE 3A: ELIMINACIÓN DEL SELLO                       │
│                  (Clasificación cromática + Filtros)                     │
└──────────────────────────────────────────────────────────────────────────┘
    ├─ Paso 1: Clasificar píxeles (5 categorías)
    │   └─ TEXTO, SELLO_SATURADO, MIXTO, FONDO, SELLO_TRANSLUCIDO
    │   └─ Generar: 01_pixel_classification.png
    │
    ├─ Paso 2: Filtro horizontal por filas
    │   └─ Remover sello en filas sin texto
    │   └─ Generar: 02_after_hsweep_classification.png
    │
    ├─ Paso 3: Filtro de bloques 20×20
    │   └─ Remover sello en bloques sin texto
    │   └─ Generar: 03_after_bsweep_classification.png
    │
    ├─ Paso 4: Construir máscara final
    │   └─ 220,494 píxeles para inpaint (2.63%)
    │   └─ Generar: 04_final_inpaint_mask.png
    │
    └─ Paso 5: Aplicar inpainting
        └─ OpenCV Telea reconstruye píxeles
        └─ Generar: cleaned_image.png (IMAGEN LIMPIA)
                    05_comparison_before_after.png
                                    ↓
┌──────────────────────────────────────────────────────────────────────────┐
│               PHASE 4: EXTRACCIÓN OCR Y POST-PROCESAMIENTO               │
│      (EasyOCR + Corrección ortográfica + Análisis de entidades)         │
└──────────────────────────────────────────────────────────────────────────┘
    ├─ Cargar: cleaned_image.png (imagen limpia)
    │
    ├─ Paso 1: Extracción OCR
    │   └─ Motor: EasyOCR (español)
    │   └─ Detectar: 152 bloques de texto
    │   └─ Confianza promedio: 83.12%
    │
    ├─ Paso 2: Corrección ortográfica
    │   └─ Levenshtein distance
    │   └─ Corregir: 55 palabras
    │
    ├─ Paso 3: Extracción de entidades (NER)
    │   └─ spaCy Named Entity Recognition
    │   └─ Detectar: 17 entidades
    │
    └─ Paso 4: Guardar resultados
        └─ ocr_results.json (152 bloques + metadatos)
                                    ↓
┌──────────────────────────────────────────────────────────────────────────┐
│          CONSOLIDACIÓN: GENERAR SALIDAS FINALES PARA ANÁLISIS            │
│              (TXT + JSON con métricas consolidadas)                      │
└──────────────────────────────────────────────────────────────────────────┘
    ├─ Extraer texto completo
    │   └─ ocr_extracted_text.txt (3,546 caracteres, 534 palabras)
    │
    ├─ Calcular métricas internas
    │   └─ Caracteres, palabras, bloques, confianza
    │   └─ Distribución de confianza
    │   └─ Tasas de corrección y entidades
    │
    └─ Generar JSON de métricas
        └─ ocr_metrics.json (text, confidence, post-processing)
                                    ↓
┌──────────────────────────────────────────────────────────────────────────┐
│           PHASE 5 (OPCIONAL): EVALUACIÓN CON GROUND TRUTH                │
│                   (Cálculo de CER, WER, accuracy)                        │
└──────────────────────────────────────────────────────────────────────────┘
    ├─ Cargar: ocr_extracted_text.txt
    │
    ├─ Cargar: Ground truth (texto de referencia)
    │
    ├─ Calcular métricas:
    │   ├─ CER (Character Error Rate)
    │   ├─ WER (Word Error Rate)
    │   ├─ Character Accuracy
    │   └─ Word Accuracy
    │
    └─ Generar: ocr_evaluation_metrics.json
                ocr_evaluation_report.txt
                                    ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                        SALIDAS FINALES DEL PIPELINE                      │
│                  (Documentos listos para análisis)                       │
└──────────────────────────────────────────────────────────────────────────┘
    ├─ Imagen limpia (sin sello)
    │   └─ pipeline_results/phase_3a/cleaned_image.png
    │
    ├─ Texto extraído
    │   └─ pipeline_results/consolidated/ocr_extracted_text.txt
    │
    ├─ Métricas de rendimiento
    │   ├─ pipeline_results/consolidated/ocr_metrics.json
    │   └─ pipeline_results/consolidated/ocr_evaluation_metrics.json (opcional)
    │
    └─ Reportes y documentación
        ├─ PIPELINE_COMPLETE_REPORT.md
        ├─ ANALISIS_OCR_EVALUATION.md
        └─ Multiple visualization images (10 de Phase 3A)
```

---

## FASE 1: ENTRADA

### Archivo de entrada
```
C:\Users\manue\Desktop\final_vision\output\prueba_completa\01_imagen_original.png
├─ Tamaño: 2550 × 3300 píxeles
├─ Formato: PNG
├─ Contenido: Documento legal con sello rojo visible
└─ Problema: Sello oscurece ~2% del documento
```

### Configuración inicial
```python
# Rutas
input_image = "output/prueba_completa/01_imagen_original.png"
output_base_dir = "pipeline_results"

# Parámetros
block_size = 20                    # Tamaño de bloques para filtro
inpainting_method = "hybrid"       # OpenCV/LaMa
language = "es"                    # OCR en español
confidence_threshold = 0.6         # Mínima confianza OCR
```

---

## FASE 2: ELIMINACIÓN DEL SELLO (PHASE 3A)

### Entrada
```
Imagen original: 2550×3300 píxeles con sello rojo
```

### Paso 1: Clasificación cromática

**Técnica**: Analizar cada píxel por:
- Mean RGB (promedio de canales)
- Dominance (max-min de canales)

**Categorías generadas**:
```
TEXTO (0):              593,527 píxeles (7.08%)
SELLO_SATURADO (1):      67,879 píxeles (0.81%)
MIXTO (2):              357,741 píxeles (4.26%)
FONDO (3):            7,350,048 píxeles (87.50%)
SELLO_TRANSLUCIDO (4):   45,805 píxeles (0.55%)
```

**Salidas**:
- `01_pixel_classification.png` - Mapa de colores
- `01_initial_mask.png` - Máscara binaria

### Paso 2: Filtro horizontal

**Técnica**: Para cada fila:
- Si NO tiene píxeles TEXTO → convertir SELLO a FONDO
- Si SÍ tiene píxeles TEXTO → mantener intacto

**Resultado**:
```
Píxeles reclasificados:    27,293
SELLO_SATURADO:    67,879 → 63,172 (↓ 4,707)
MIXTO:            357,741 → 350,570 (↓ 7,171)
SELLO_TRANSLUCIDO: 45,805 → 30,390 (↓ 15,415)
```

**Salidas**:
- `02_after_hsweep_classification.png`
- `02_after_hsweep_mask.png`

### Paso 3: Filtro de bloques

**Técnica**: Dividir imagen en bloques 20×20:
- Bloques sin TEXTO → remover SELLO
- Bloques con TEXTO → mantener

**Estadísticas**:
```
Total bloques:             21,120
Con texto (mantener):       7,240 (34.3%)
Sin texto (limpiar):       13,880 (65.7%)
Píxeles reclasificados:    223,638
```

**Resultado final**:
```
SELLO_SATURADO:       63,172 →  2,120 (↓ 96.6%)
MIXTO:               350,570 → 210,019 (↓ 40.1%)
SELLO_TRANSLUCIDO:    30,390 →  8,355 (↓ 72.5%)
```

**Salidas**:
- `03_after_bsweep_classification.png`
- `03_after_bsweep_mask.png`
- `03_block_grid_overlay.png` (rojo=limpiados, verde=mantenidos)

### Paso 4: Máscara final

**Construcción**: Combinar SELLO + MIXTO + TRANSLUCIDO de máscara anterior

**Resultado**:
```
Píxeles para inpaint:      220,494 píxeles
Porcentaje imagen:         2.63%
```

**Salida**:
- `04_final_inpaint_mask.png`

### Paso 5: Inpainting

**Técnica**: OpenCV Telea (fallback de LaMa)
- Reconstruir píxeles marcados usando contexto circundante
- Radius: 3 píxeles

**Salidas**:
- `cleaned_image.png` - ⭐ IMAGEN FINAL SIN SELLO
- `05_comparison_before_after.png` - Comparación visual

---

## FASE 3: EXTRACCIÓN OCR (PHASE 4)

### Entrada
```
cleaned_image.png (imagen limpia sin sello)
Tamaño: 2550×3300 píxeles
```

### Paso 1: Inicialización OCR

```python
ocr_engine = EasyOCREngine(
    language="es",                    # Español
    confidence_threshold=0.6,         # Mínimo 60%
    max_levenshtein=2                 # Distancia máxima para corrección
)
```

### Paso 2: Extracción de bloques

**Motor**: EasyOCR
- Detectar bloques de texto con bounding boxes
- Calcular confianza para cada bloque
- Extraer texto

**Resultado**:
```
Bloques detectados:        152
Texto total extraído:      3,546 caracteres
Palabras extraídas:        534 palabras
```

**Distribución de confianza**:
```
0.0-0.2:   2 bloques
0.2-0.4:   3 bloques
0.4-0.6:  10 bloques
0.6-0.8:  38 bloques
0.8-1.0:  98 bloques (64.5%) ← ALTA CONFIANZA
```

**Confianza promedio**: 83.12%

### Paso 3: Corrección ortográfica

**Técnica**: Levenshtein distance
- Comparar palabras OCR con diccionario
- Si distancia < 2 → corregir automáticamente

**Resultado**:
```
Palabras corregidas:       55 (10.3% de 534 palabras)
Diccionario utilizado:     Español
```

### Paso 4: Extracción de entidades (NER)

**Técnica**: spaCy Named Entity Recognition
- Detectar nombres, organizaciones, localizaciones, etc.

**Resultado**:
```
Entidades detectadas:      17
Tipos: PERSON, ORG, LOC, MISC
```

### Paso 5: Guardar resultados

**Salida**:
```json
{
  "texto_completo": "PERÚ Ministerio SMV de economia...",
  "bloques": [
    {
      "bbox": [[x1, y1], [x2, y1], [x2, y2], [x1, y2]],
      "texto": "PERÚ",
      "confianza": 0.98
    },
    ...
  ],
  "metricas": {
    "total_bloques": 152,
    "confianza_promedio": 0.8312,
    "palabras_corregidas": 55,
    "entidades_detectadas": 17,
    "motores_usados": ["EasyOCR"],
    "procesadores_usados": ["Levenshtein", "spaCy"]
  }
}
```

**Archivo generado**:
- `ocr_results.json` (108 KB)

---

## FASE 4: CONSOLIDACIÓN DE RESULTADOS

### Entrada
```
ocr_results.json (resultados OCR completos)
```

### Paso 1: Extracción de texto

**Operación**: Extraer campo `texto_completo`

**Salida**:
- `ocr_extracted_text.txt` (3,546 caracteres)

### Paso 2: Cálculo de métricas internas

**Métricas calculadas**:
```
text_metrics:
  - total_characters: 3,546
  - total_words: 534
  - total_blocks: 152
  - unique_words: 240
  - average_word_length: 6.64
  - character_per_block: 23.33

ocr_confidence_metrics:
  - average: 0.8312 (83.12%)
  - min: 0.0561
  - max: 1.0
  - distribution: { "0.8-1.0": 98, ... }

post_processing_metrics:
  - words_corrected: 55
  - entities_detected: 17
  - correction_rate: 10.3%
  - entity_rate: 11.18%
```

**Salida**:
- `ocr_metrics.json`

---

## FASE 5: EVALUACIÓN (PHASE 5 - OPCIONAL)

### Entrada
```
ocr_extracted_text.txt (OCR extraído)
ground_truth.txt (texto de referencia)
```

### Paso 1: Normalización

Ambos textos se normalizan a minúsculas y se eliminan espacios

### Paso 2: Cálculo de distancia

**Levenshtein distance**: Operaciones mínimas (inserción, eliminación, substitución)

### Paso 3: Cálculo de métricas

```
CER = distancia / len(reference)
WER = distancia_palabras / len(reference_words)
Accuracy = (1 - error_rate) * 100
```

### Paso 4: Análisis de errores

- Palabras que no coinciden
- Caracteres faltantes/extra
- Palabras insertadas/eliminadas

**Salidas**:
- `ocr_evaluation_metrics.json`
- `ocr_evaluation_report.txt`

---

## FASE 5: SALIDA FINAL

### Archivos generados

```
pipeline_results/
│
├── phase_3a/                          (10 imágenes)
│   ├── 01_pixel_classification.png
│   ├── 01_initial_mask.png
│   ├── 02_after_hsweep_classification.png
│   ├── 02_after_hsweep_mask.png
│   ├── 03_after_bsweep_classification.png
│   ├── 03_after_bsweep_mask.png
│   ├── 03_block_grid_overlay.png
│   ├── 04_final_inpaint_mask.png
│   ├── 05_comparison_before_after.png
│   └── cleaned_image.png              ⭐ IMAGEN LIMPIA
│
├── phase_4/                           (1 JSON)
│   └── ocr_results.json               (152 bloques OCR)
│
├── consolidated/                      (2 archivos principales)
│   ├── ocr_extracted_text.txt         (TEXTO: 3,546 caracteres)
│   ├── ocr_metrics.json               (MÉTRICAS: confianza, etc)
│   ├── ocr_evaluation_metrics.json    (EVALUACIÓN: CER, WER - opcional)
│   └── ocr_evaluation_report.txt      (REPORTE: análisis - opcional)
│
└── pipeline_results_final.json         (Resumen ejecución)
```

---

## 🚀 EJECUCIÓN DEL PIPELINE

### Opción 1: Pipeline Completo (recomendado)

```bash
python execute_full_pipeline.py
```

**Qué hace**:
1. Ejecuta Phase 3A (eliminación del sello)
2. Ejecuta Phase 4 (extracción OCR)
3. Ejecuta Phase 5 (evaluación - si ground truth disponible)

### Opción 2: Paso a paso

```bash
# Solo Phase 3A
python pipeline/run_phase_3a.py --input imagen.png --output output_dir

# Solo Phase 4
python pipeline/run_phase_4.py --input imagen.png --output output_dir

# Consolidar resultados
python consolidate_results.py

# Evaluar OCR (opcional)
python calculate_ocr_evaluation.py
```

### Opción 3: Componentes individuales

```python
# Desde Python
from src.phase_3a import ChromaticSeparator, InpainterHybrid
from src.phase_4 import EasyOCREngine

# Phase 3A
separator = ChromaticSeparator()
pixel_map = separator.classify_pixels(image)
mask = separator.construct_final_mask(pixel_map)
inpainter = InpainterHybrid()
cleaned = inpainter.inpaint(image, mask)

# Phase 4
ocr_engine = EasyOCREngine(language="es")
result = ocr_engine.extract_text(cleaned)
```

---

## 📊 RESUMEN DE TRANSFORMACIÓN

```
ENTRADA
  └─ Documento con sello rojo (2550×3300 píxeles)

AFTER PHASE 3A
  ├─ Sello eliminado completamente
  ├─ 220,494 píxeles inpaintados
  └─ Documento limpio, listo para OCR

AFTER PHASE 4
  ├─ 152 bloques de texto detectados
  ├─ 3,546 caracteres extraídos
  ├─ 83.12% confianza promedio
  ├─ 55 palabras corregidas
  └─ 17 entidades detectadas

AFTER CONSOLIDACIÓN
  ├─ ocr_extracted_text.txt (texto limpio)
  └─ ocr_metrics.json (métricas de rendimiento)

AFTER EVALUACIÓN (OPCIONAL)
  ├─ CER / WER calculados
  └─ ocr_evaluation_metrics.json (con ground truth)

SALIDA FINAL
  ├─ Imagen limpia sin sello
  ├─ Texto extraído en TXT
  ├─ Métricas en JSON
  └─ 10 imágenes de proceso para documentación
```

---

## ⏱️ TIEMPO ESTIMADO

| Fase | Componente | Tiempo |
|------|-----------|--------|
| Entrada | Lectura imagen | ~1 segundo |
| Phase 3A | Clasificación | ~5 segundos |
| | Filtros | ~10 segundos |
| | Inpainting | ~5 segundos |
| Phase 4 | Inicialización OCR | ~30 segundos |
| | Extracción | ~20 segundos |
| | Post-procesamiento | ~5 segundos |
| Consolidación | Cálculo métricas | ~2 segundos |
| Evaluación | CER/WER | ~5 segundos |
| **TOTAL** | | **~83 segundos (~1.4 minutos)** |

---

## ✅ VERIFICACIÓN FINAL

Después de ejecutar el pipeline, verifica:

```bash
# Archivos generados
ls -lh pipeline_results/phase_3a/            # 10 imágenes
ls -lh pipeline_results/phase_4/             # 1 JSON
ls -lh pipeline_results/consolidated/        # 2 archivos principales

# Contenido de salidas
head -50 pipeline_results/consolidated/ocr_extracted_text.txt
cat pipeline_results/consolidated/ocr_metrics.json | python -m json.tool
```

---

## 🎯 CONCLUSIÓN

El pipeline es una solución integral que:

1. **Limpia documentos** eliminando sellos automáticamente
2. **Extrae texto** con alta confianza (83.12%)
3. **Corrige errores** automáticamente (55 palabras)
4. **Detecta entidades** para análisis (17 entidades)
5. **Calcula métricas** de rendimiento (CER, WER, accuracy)
6. **Genera evidencia visual** de cada paso

**Tiempo total**: ~1.4 minutos por documento  
**Salidas**: Imagen limpia + texto extraído + métricas JSON  
**Calidad**: EXCELENTE (83.12% confianza OCR)

---

**Status**: ✅ Pipeline completo y documentado
