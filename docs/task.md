# Proyecto IDP - Manuel Cruz Garrote
## Universidad del Rosario - Proyecto de Grado

**Alcance:** Versión reducida enfocada en core features  
**Meta:** 7.5/10 (Muy Bueno)  
**Periodo:** Febrero - Mayo 2026

---

## CHECKPOINT 0: Fundamentos y Setup (Nota: 1.0)
**Deadline:** 18 Febrero 2026

- [ ] **Dataset y Preparación de Datos**
    - [ ] Descargar y analizar SROIE dataset
    - [ ] Recolectar 25 imágenes con sellos (web scraping)
    - [ ] Anotar 25 sellos con LabelImg
    - [ ] Aplicar data augmentation → 50 imágenes totales
    - [ ] Crear splits: train (70%), val (15%), test (15%)
    - [ ] Documentar metodología de dataset

- [ ] **Infraestructura Técnica**
    - [ ] Configurar repositorio GitHub
    - [ ] Setup ambiente Python (virtualenv)
    - [ ] Confirmar acceso a GPU (universidad/Colab/AWS)
    - [ ] Instalar dependencias base (OpenCV, PyTorch)
    - [ ] Crear estructura de proyecto modular

- [ ] **Documentación Inicial**
    - [ ] Documento de planteamiento del problema (1-2 pág)
    - [ ] Análisis exploratorio de datos (notebook)
    - [ ] README con instrucciones de setup

---

## CHECKPOINT 1: MVP Básico - Pipeline Core (Nota: 3.5 ✅ APROBADO)
**Deadline:** 11 Marzo 2026

- [ ] **Módulo de Preprocesamiento**
    - [ ] Implementar corrección de rotación (Hough transform)
    - [ ] Implementar binarización adaptativa (Otsu)
    - [ ] Tests unitarios básicos con pytest
    - [ ] API unificada: `preprocess_image(img)`

- [ ] **Motor de OCR**
    - [ ] Wrapper para Tesseract OCR
    - [ ] Wrapper para PaddleOCR
    - [ ] Estrategia de fallback automático
    - [ ] Benchmarking en subset SROIE (50 muestras)

- [ ] **Integración del Pipeline v1**
    - [ ] Script unificado: preprocesamiento → OCR
    - [ ] Validar accuracy >70% en SROIE
    - [ ] Documentación de API
    - [ ] Código limpio y comentado

---

## CHECKPOINT 2: Diferenciador - Inpainting de Sellos (Nota: 6.0)
**Deadline:** 8 Abril 2026

- [ ] **Detección de Sellos (Enfoque Simplificado)**
    - [ ] Implementar detector basado en color HSV
    - [ ] Generación de máscaras binarias
    - [ ] Validación en dataset de 50 sellos
    - [ ] Análisis de precisión del detector

- [ ] **Inpainting con LaMa**
    - [ ] Clonar e instalar LaMa (repo oficial)
    - [ ] Descargar weights pre-entrenados
    - [ ] Implementar wrapper en Python
    - [ ] Testear inpainting en 10 ejemplos iniciales
    - [ ] Optimizar parámetros de inpainting

- [ ] **Pipeline v2 - Integración Completa**
    - [ ] Integrar: detector → inpainting → OCR
    - [ ] Flujo end-to-end automatizado
    - [ ] Manejo de errores y casos edge

- [ ] **Experimento Crítico de Validación**
    - [ ] Seleccionar 30 documentos con sellos
    - [ ] Medir OCR accuracy ANTES de inpainting
    - [ ] Medir OCR accuracy DESPUÉS de inpainting
    - [ ] Análisis estadístico (¿mejora >5%?)
    - [ ] Documentar resultados con visualizaciones

---

## CHECKPOINT 3: Validación y Resultados (Nota: 7.5 ⭐ MUY BUENO)
**Deadline:** 29 Abril 2026

- [ ] **Evaluación en SROIE**
    - [ ] Benchmark en 100 muestras del test set
    - [ ] Calcular métricas: CER, WER, F1-score
    - [ ] Comparar con baseline (solo Tesseract)
    - [ ] Análisis cualitativo de errores

- [ ] **Documentación Académica**
    - [ ] Redactar sección de Metodología (5-7 pág)
    - [ ] Redactar Estado del Arte (5-7 pág)
    - [ ] Sección de Resultados con gráficos
    - [ ] Introducción y Conclusiones
    - [ ] Referencias bibliográficas (formato IEEE)

- [ ] **Preparación de Entregables**
    - [ ] Documento académico completo (20-25 pág)
    - [ ] Presentación de resultados (10 slides)
    - [ ] Código limpio y bien documentado
    - [ ] README con instrucciones de reproducción

---

## FASE FINAL: Cierre del Proyecto
**Deadline:** 30 Mayo 2026

- [ ] **Refinamiento y Pulido**
    - [ ] Implementar feedback del asesor
    - [ ] Refactorizar código (eliminar duplicación)
    - [ ] Completar tests unitarios pendientes
    - [ ] Revisar y corregir documentación

- [ ] **Demo y Presentación**
    - [ ] Crear demo simple (Jupyter Notebook)
    - [ ] Video explicativo del proyecto (3-5 min)
    - [ ] Preparar presentación final (15-20 slides)
    - [ ] Ensayo de sustentación

- [ ] **Entrega Final**
    - [ ] Subir todo a repositorio (tag final)
    - [ ] Entregar documento en plataforma
    - [ ] Sustentación ante jurado

---

## NOTAS Y DECISIONES

### Alcance Descartado (por tiempo):
- ❌ Layout Analysis (LayoutLMv3)
- ❌ Extracción de Tablas (Camelot)
- ❌ Extracción de Gráficas (PlotDigitizer)
- ❌ QA Semántico con RAG
- ❌ Fine-tuning de YOLO (usar detector simple)
- ❌ Paper IEEE completo (solo informe académico)

### Decisiones Técnicas:
- ✅ Detector de sellos: Color-based (HSV) en lugar de YOLO
- ✅ Dataset reducido: 50 sellos en lugar de 100+
- ✅ Benchmark parcial: 100 muestras SROIE en lugar de completo
- ✅ Enfoque en calidad sobre cantidad

### Puntos de Validación con Asesor:
- 18 Feb: Aprobar CP0
- 11 Mar: Aprobar CP1 (crítico: si falla, proyecto no aprueba)
- 8 Abr: Validar CP2 (experimento de inpainting)
- 29 Abr: Aprobar CP3 (documento académico)
- 22 May: Revisión pre-final
- 30 May: Sustentación
