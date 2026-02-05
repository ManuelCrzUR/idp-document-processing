# Plan de Implementación - Proyecto IDP
## Manuel Cruz Garrote - Universidad del Rosario

**Versión:** Alcance Reducido (Versión Realista)  
**Fecha:** Febrero 2026  
**Meta:** 7.5/10 - Muy Bueno

---

# Resumen Ejecutivo

Este plan define la implementación de un sistema de Procesamiento Inteligente de Documentos (IDP) enfocado en el **diferenciador clave**: eliminación de sellos mediante inpainting para mejorar la extracción de texto por OCR.

Dado que trabajo y estudio simultáneamente, he priorizado las funcionalidades **esenciales** que demuestran innovación técnica y tienen aplicabilidad real, descartando features avanzadas que consumirían tiempo sin agregar valor proporcional al objetivo académico.

---

# Problema a Resolver

## Contexto

Los sistemas de OCR comerciales (Google Doc AI, AWS Textract, ABBYY) funcionan bien con documentos digitales limpios, pero **fallan significativamente** cuando procesan:

1. **Documentos físicos escaneados** con arrugas, manchas, o perspectiva incorrecta
2. **Documentos con sellos oficiales** que obstruyen el texto subyacente
3. **Documentos históricos** con degradación de calidad

## Caso de Uso Específico

**Target:** Archivos gubernamentales y notariales en Colombia

- Millones de documentos físicos pendientes de digitalización
- Sellos oficiales obligatorios que cubren información crítica
- Necesidad de extraer texto completo para índice de búsqueda

## Propuesta de Valor

> **"Recuperar texto que otros sistemas ignoran mediante inpainting inteligente de sellos"**

Ningún competidor comercial ofrece esta funcionalidad de forma integrada.

---

# Arquitectura del Sistema (Versión Reducida)

## Pipeline Simplificado

```
Input: Imagen de documento
    ↓
[1] Preprocesamiento
    - Corrección de rotación
    - Binarización adaptativa
   ↓
[2] Detección de Sellos
    - Método basado en color HSV
    ↓
[3] Inpainting (LaMa)
    - Eliminación inteligente de sellos
    ↓
[4] OCR Multimodal
    - PaddleOCR (primario)
    - Tesseract (fallback)
    ↓
Output: Texto extraído + Métricas
```

## Módulos del Sistema

### `preprocessing/`
- `rotation.py` - Corrección de rotación con Hough Transform
- `binarization.py` - Binarización adaptativa (Otsu)

### `stamps/`
- `detector.py` - Detección por color en espacio HSV
- `inpainting.py` - Wrapper para LaMa

### `ocr/`
- `paddle_engine.py` - Motor principal (PaddleOCR)
- `tesseract_engine.py` - Fallback
- `ocr_engine.py` - Orquestador con estrategia de fallback

### `utils/`
- `metrics.py` - Cálculo de CER, WER, F1
- `visualization.py` - Gráficos y comparativas

---

# Stack Tecnológico

## Lenguaje Base
- **Python 3.10+** (compatibilidad con todas las librerías modernas)

## Preprocesamiento
- **OpenCV 4.8+** - Procesamiento de imágenes
  - Por qué: Maduro, rápido, bien documentado
  - Uso: Rotación, binarización, detección de color

## OCR
- **PaddleOCR v2.7** - Motor principal
  - Por qué: Excelente accuracy en múltiples idiomas
  - GPU/CPU automático
  - Lightweight
  
- **Tesseract 5.0** - Fallback
  - Por qué: Baseline confiable, open-source

## Inpainting
- **LaMa (Large Mask Inpainting)** - Samsung AI 2021
  - Por qué: Estado del arte en inpainting
  - Funciona bien con máscaras grandes (sellos)
  - Modelo pre-entrenado disponible

## Infrastructure
- **PyTorch 2.0+** - Framework para LaMa
- **NumPy / PIL** - Manipulación de imágenes
- **Pytest** - Testing
- **Jupyter** - Experimentación

## Datasets
- **SROIE** (Scanned Receipts OCR and IE) - Benchmark público
- **Custom Stamp Dataset** - 50 imágenes anotadas manualmente

---

# Fases de Implementación

## FASE 1: MVP Core (CP0 + CP1)
**Objetivo:** Sistema funcional básico de preprocesamiento + OCR

### Entregables:
1. **Dataset preparado**
   - 50 sellos anotados
   - SROIE descargado y organizado
   
2. **Módulo de Preprocesamiento**
   ```python
   def preprocess_image(img):
       img = correct_rotation(img)
       img = apply_binarization(img)
       return img
   ```

3. **Motor de OCR Dual**
   ```python
   def extract_text(img):
       try:
           return paddle_ocr(img)
       except:
           return tesseract_ocr(img)
   ```

4. **Pipeline v1**
   ```python
   text = extract_text(preprocess_image(input_img))
   ```

### Criterio de Éxito:
- ✅ Accuracy >70% en subset SROIE (50 muestras)
- ✅ Pipeline ejecuta sin errores
- ✅ Código modularizado y testeado

---

## FASE 2: Diferenciador - Inpainting (CP2)
**Objetivo:** Validar que el inpainting mejora significativamente el OCR

### Entregables:

1. **Detector de Sellos (Simplificado)**
   ```python
   def detect_stamps_hsv(img):
       hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
       # Define rangos de color típicos de sellos (azul, rojo)
       mask = cv2.inRange(hsv, lower_bound, upper_bound)
       contours = find_contours(mask)
       return filter_valid_stamps(contours)
   ```

2. **Inpainting Integration**
   ```python
   def remove_stamps(img, stamp_masks):
       model = load_lama_model()
       inpainted = model.inpaint(img, stamp_masks)
       return inpainted
   ```

3. **Pipeline v2**
   ```python
   stamps = detect_stamps(img)
   img_clean = remove_stamps(img, stamps)
   text = extract_text(preprocess_image(img_clean))
   ```

4. **Experimento de Validación**
   - 30 documentos con sellos
   - Métrica Before: OCR sin inpainting
   - Métrica After: OCR con inpainting
   - **Hipótesis:** Mejora >5% en CER/WER

### Criterio de Éxito:
- ✅ Detector identifica >80% de sellos
- ✅ Inpainting genera resultados visualmente coherentes
- ✅ **Mejora estadísticamente significativa en OCR (>5%)**

---

## FASE 3: Validación y Documentación (CP3)
**Objetivo:** Resultados científicos reproducibles + documento académico

### Entregables:

1. **Benchmark en SROIE**
   - Correr pipeline en 100 muestras
   - Métricas completas: CER, WER, F1-score
   - Comparativa con baseline (solo Tesseract)

2. **Análisis de Resultados**
   - Gráficos de comparación
   - Análisis cualitativo de errores
   - Identificación de casos donde falla el sistema

3. **Documento Académico (20-25 páginas)**
   - Introducción y contexto
   - **Estado del Arte** (5-7 pág)
     - Revisión de soluciones IDP comerciales
     - Papers de OCR (TrOCR, PaddleOCR)
     - Papers de Inpainting (LaMa, DeepFill)
   - **Metodología** (5-7 pág)
     - Arquitectura del sistema
     - Descripción de algoritmos
     - Dataset y métricas
   - **Resultados** (4-5 pág)
     - Tablas de métricas
     - Gráficos comparativos
     - Análisis de experimento de inpainting
   - **Conclusiones** (2-3 pág)
     - Logros alcanzados
     - Limitaciones
     - Trabajo futuro

4. **Presentación**
   - 10 slides para sustentación
   - Demo en vivo (Jupyter Notebook)
   - Video explicativo (3-5 min)

### Criterio de Éxito:
- ✅ Resultados reproducibles
- ✅ Documento bien estructurado y referenciado
- ✅ Presentación clara y concisa

---

# Plan de Verificación

## Métricas de Evaluación

### Accuracy de OCR
- **CER (Character Error Rate)**: % de caracteres incorrectos
- **WER (Word Error Rate)**: % de palabras incorrectas
- **F1-score**: Para entidades específicas (si aplica)

### Validación de Inpainting
- **LPIPS (Learned Perceptual Image Patch Similarity)**: Calidad perceptual
- **Comparativa Before/After**: Mejora en CER/WER

### Calidad de Código
- **Test Coverage**: >70% (pytest)
- **Linting**: Pasar flake8 sin warnings críticos

## Proceso de Testing

### 1. Tests Unitarios
```python
def test_rotation_correction():
    rotated_img = generate_rotated_image(angle=15)
    corrected = correct_rotation(rotated_img)
    assert get_rotation_angle(corrected) < 2  # tolerance
```

### 2. Tests de Integración
```python
def test_pipeline_end_to_end():
    img = load_test_image()
    text = pipeline_v2(img)
    assert len(text) > 0
    assert calculate_cer(text, ground_truth) < 0.3
```

### 3. Benchmarking
- Correr pipeline en SROIE test set
- Guardar resultados en CSV
- Generar reporte automático con métricas

---

# Decisiones de Alcance

## ✅ Lo que SÍ haremos

1. **Preprocesamiento robusto** (rotación + binarización)
2. **OCR dual** con fallback inteligente
3. **Detección de sellos** (método simple pero efectivo)
4. **Inpainting con LaMa** (diferenciador clave)
5. **Validación científica** en dataset público
6. **Documentación académica completa**

## ❌ Lo que NO haremos (descartado por tiempo)

1. **Layout Analysis** - Detección de regiones con LayoutLMv3
   - Razón: Complejidad alta, valor agregado marginal
   - Ahorro: ~25 horas

2. **Extracción de Tablas** - Camelot/Tabula
   - Razón: Requiere fine-tuning extenso
   - Ahorro: ~30 horas

3. **Extracción de Gráficas** - PlotDigitizer
   - Razón: Caso de uso muy específico
   - Ahorro: ~30 horas

4. **QA Semántico con RAG** 
   - Razón: Complejidad de implementar LLMs + vector DB
   - Ahorro: ~20 horas

5. **Fine-tuning de YOLO**
   - Razón: Detector HSV es suficiente para demostrar concepto
   - Ahorro: ~15 horas

6. **Dockerización**
   - Razón: Ejecución local es suficiente para proyecto académico
   - Ahorro: ~8 horas

7. **Demo en cloud**
   - Razón: Jupyter Notebook local es suficiente
   - Ahorro: ~10 horas

**Total ahorrado: ~138 horas** → Hace el proyecto factible

---

# Limitaciones Reconocidas

## Técnicas

1. **Detector de sellos simplificado**
   - Basado en color, no en forma/contexto
   - Puede tener falsos positivos con elementos rojos/azules
   - Mejora futura: YOLO fine-tuned

2. **Sin manejo de layouts complejos**
   - No reordena texto según lectura visual
   - Asume orden secuencial
   - Mejora futura: LayoutParser

3. **Evaluación en subset de SROIE**
   - 100 muestras, no dataset completo
   - Suficiente para validación académica
   - Mejora futura: Benchmark completo

## De Alcance

1. **No es un producto de producción**
   - Es un prototipo académico
   - No tiene consideraciones de escalabilidad
   - No tiene manejo de errores exhaustivo

2. **Enfoque en documentos con sellos**
   - No generaliza a todos los tipos de documentos
   - Optimizado para caso de uso específico

---

# Checkpoints y Validación con Asesor

## CP0 (18 Feb): Setup
- **Mostrar:** Dataset anotado + infraestructura
- **Validar:** ¿Es suficiente calidad de dataset?

## CP1 (11 Mar): MVP
- **Mostrar:** Demo de pipeline v1 en vivo
- **Validar:** ¿OCR >70% accuracy?
- **Crítico:** Si falla, proyecto no aprueba

## CP2 (8 Abr): Inpainting
- **Mostrar:** Resultados Before/After en 30 muestras
- **Validar:** ¿Mejora >5% es estadísticamente significativa?
- **Decisión:** Si NO mejora, documentar por qué y ajustar enfoque

## CP3 (29 Abr): Resultados
- **Mostrar:** Documento académico completo
- **Validar:** ¿Metodología es clara? ¿Resultados son reproducibles?

## Final (30 May): Sustentación
- **Presentar:** Proyecto completo ante jurado
- **Defender:** Decisiones técnicas y resultados

---

# Recursos Necesarios

## Computacionales
- **GPU:** NVIDIA con >=8GB VRAM (para LaMa)
  - Opción 1: Lab de universidad
  - Opción 2: Google Colab Pro ($10/mes)
  - Opción 3: AWS credits (educate)

## Humanos
- **Asesor académico:** Reuniones semanales (30-60 min)
- **Yo:** 15-18 horas/semana dedicadas

## Bibliográficos
- Papers de referencia (acceso vía universidad)
- Documentación oficial de librerías

---

# Conclusión

Este plan de implementación prioriza **calidad sobre cantidad**, enfocándose en demostrar un concepto innovador (inpainting para mejorar OCR) de forma científicamente rigurosa.

La meta de **7.5/10** es realista y **muy buena** académicamente, reconociendo las limitaciones de tiempo de un estudiante que trabaja.

**Próximo paso:** Iniciar CP0 - Setup del proyecto.

---

**Manuel Cruz Garrote**  
Universidad del Rosario  
Febrero 2026
