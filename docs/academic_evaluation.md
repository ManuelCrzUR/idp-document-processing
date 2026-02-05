# Proyecto IDP - Sistema de Checkpoints Incrementales
## Universidad del Rosario - Ingeniería de Sistemas

### 👨‍🏫 Diseñado por: Dr. Andrés Parra Rojas, PhD
**Modalidad:** Proyecto de Grado / Trabajo de Investigación  
**Duración:** 16-18 semanas (1 semestre académico)  
**Créditos:** 6-8 créditos académicos

---

## 🎯 FILOSOFÍA DEL SISTEMA DE CHECKPOINTS

### **Concepto: "Escalera de Valor Incremental"**

Cada checkpoint representa un **entregable funcional completo** que:
- ✅ Tiene valor académico independiente
- ✅ Es evaluable objetivamente
- ✅ Construye sobre el checkpoint anterior
- ✅ Permite detener el proyecto en cualquier punto sin "fracaso"

**Analogía:** Es como construir un edificio piso por piso. Cada piso es habitable, pero más pisos = más valor.

---

## 📊 ESTRUCTURA DE CALIFICACIÓN POR CHECKPOINTS

| Checkpoint | Entregable | Nota Máxima | % del Total | Acumulado |
|-----------|-----------|-------------|-------------|-----------|
| **CP0: Setup** | Infraestructura + Dataset | 1.0 | 10% | 1.0 |
| **CP1: MVP Core** | Preprocesamiento + OCR | 2.5 | 25% | 3.5 |
| **CP2: Diferenciador** | Detección + Inpainting Sellos | 2.5 | 25% | 6.0 |
| **CP3: Validación** | Experimentos + Resultados | 1.5 | 15% | 7.5 |
| **CP4: Features Avanzadas** | Layout + Tablas | 1.5 | 15% | 9.0 |
| **CP5: Excelencia** | Paper + Demo + Código Prod | 1.0 | 10% | **10.0** ✨ |

### **Interpretación de Notas:**

- **3.5 (CP0+CP1):** Aprobado - Sistema funcional básico
- **6.0 (hasta CP2):** Bueno - Con diferenciador innovador
- **7.5 (hasta CP3):** Muy Bueno - Validación rigurosa
- **9.0 (hasta CP4):** Sobresaliente - Sistema completo
- **10.0 (CP5):** Excelencia - Contribución científica

---

## 🗓️ CRONOGRAMA DE 16 SEMANAS

### **CHECKPOINT 0: Fundamentos (Semanas 1-3)** → Nota: 1.0/10

#### **Objetivo:** Preparar el terreno técnico y teórico

#### **Semana 1: Investigación Inicial**
**Actividades:**
- [ ] Lectura de 10 papers core (OCR, Inpainting, IDP)
- [ ] Análisis del problema (documentos con sellos)
- [ ] Definición de objetivos SMART del proyecto
- [ ] Setup de ambiente (Python, PyTorch, GPU)

**Entregables:**
- 📄 Documento "Planteamiento del Problema" (3-4 páginas)
- 📚 Tabla comparativa de 3 soluciones existentes
- ✅ Repositorio GitHub inicializado

**Tiempo:** 25 horas

---

#### **Semana 2: Dataset - Parte 1**
**Actividades:**
- [ ] Descargar SROIE dataset
- [ ] Análisis exploratorio de datos (EDA)
- [ ] Definir estrategia de anotación de sellos
- [ ] Scrapar 50 imágenes con sellos (web scraping)

**Entregables:**
- 💾 SROIE descargado y organizado
- 📊 Notebook de EDA (estadísticas del dataset)
- 🖼️ 50 imágenes con sellos recolectadas

**Tiempo:** 20 horas

---

#### **Semana 3: Dataset - Parte 2**
**Actividades:**
- [ ] Anotar 100 sellos con LabelImg/CVAT
- [ ] Data augmentation (rotación, ruido, blur)
- [ ] Split: Train 70% / Val 15% / Test 15%
- [ ] Documentar proceso de anotación

**Entregables:**
- 💾 **Dataset de Sellos Anotado** (100+ imágenes)
- 📄 Documento de "Metodología de Dataset" (2-3 páginas)
- ✅ Scripts de augmentation

**Tiempo:** 25 horas

---

#### **📋 Evaluación CP0 (3.0 puntos totales):**

| Criterio | Puntos |
|----------|--------|
| Repositorio configurado correctamente | 0.2 |
| Dataset SROIE descargado y analizado | 0.2 |
| Dataset de sellos anotado (mín 80 samples) | 0.3 |
| Documentación de metodología | 0.2 |
| EDA con visualizaciones | 0.1 |
| **TOTAL CP0** | **1.0** |

**Nota acumulada hasta aquí: 1.0/10**

---

### **CHECKPOINT 1: MVP Core - Sistema Base (Semanas 4-7)** → Nota: +2.5/10

#### **Objetivo:** Pipeline funcional de preprocesamiento + OCR

#### **Semana 4: Preprocesamiento - Parte 1**
**Actividades:**
- [ ] Implementar corrección de rotación (Hough transform)
- [ ] Implementar corrección de perspectiva (4-point transform)
- [ ] Tests unitarios con pytest
- [ ] Notebook de demostración visual

**Entregables:**
- 💻 `preprocessing/rotation.py`
- 💻 `preprocessing/perspective.py`
- 📊 Notebook "Demo_Preprocessing_1.ipynb"
- ✅ Tests unitarios (>70% coverage)

**Tiempo:** 25 horas

---

#### **Semana 5: Preprocesamiento - Parte 2**
**Actividades:**
- [ ] Implementar denoising (3 métodos)
- [ ] Implementar binarización adaptativa
- [ ] Benchmarking de métodos (PSNR, SSIM)
- [ ] Módulo unificado de preprocesamiento

**Entregables:**
- 💻 `preprocessing/denoising.py`
- 💻 `preprocessing/binarization.py`
- 📊 Tabla comparativa de métodos
- ✅ API unificada `preprocess_image()`

**Tiempo:** 25 horas

---

#### **Semana 6: OCR Engine**
**Actividades:**
- [ ] Wrapper para Tesseract
- [ ] Wrapper para PaddleOCR
- [ ] Estrategia de fallback automático
- [ ] Medición de accuracy en SROIE (subset)

**Entregables:**
- 💻 `ocr/ocr_engine.py`
- 📊 Benchmark: Tesseract vs PaddleOCR
- 📈 Accuracy en 100 muestras de SROIE
- ✅ API `extract_text(image)`

**Tiempo:** 30 horas

---

#### **Semana 7: Pipeline v1 + Integración**
**Actividades:**
- [ ] Integrar preprocesamiento + OCR
- [ ] Script end-to-end `pipeline_v1.py`
- [ ] Dockerizar aplicación
- [ ] Documentación de API

**Entregables:**
- 💻 `pipeline_v1.py` (completo)
- 🐳 `Dockerfile` funcional
- 📄 README con instrucciones de uso
- 🎥 Video demo (2 min)

**Tiempo:** 25 horas

---

#### **📋 Evaluación CP1 (2.5 puntos):**

| Criterio | Puntos |
|----------|--------|
| Preprocesamiento funcional (3+ métodos) | 0.6 |
| OCR con 2+ engines | 0.5 |
| Pipeline integrado end-to-end | 0.6 |
| Código limpio + tests (>70% coverage) | 0.3 |
| Dockerizado y documentado | 0.3 |
| Accuracy OCR >70% en subset SROIE | 0.2 |
| **TOTAL CP1** | **2.5** |

**Nota acumulada hasta aquí: 3.5/10** ✅ **APROBADO**

**🎓 Decisión académica:** Si el estudiante detiene aquí, tiene un proyecto aprobado con sistema funcional básico.

---

### **CHECKPOINT 2: Diferenciador Innovador (Semanas 8-11)** → Nota: +2.5/10

#### **Objetivo:** Implementar la feature única (Inpainting de Sellos)

#### **Semana 8: Detección de Sellos - Enfoque Clásico**
**Actividades:**
- [ ] Implementar detección por color (HSV thresholding)
- [ ] Implementar detección por forma (Hough circles)
- [ ] Benchmarking en dataset de sellos
- [ ] Análisis de falsos positivos/negativos

**Entregables:**
- 💻 `stamps/detector_classic.py`
- 📊 Métricas: Precision, Recall, F1-score
- 📈 Confusion matrix
- ✅ Visualización de detecciones

**Tiempo:** 25 horas

---

#### **Semana 9: Detección de Sellos - Deep Learning**
**Actividades:**
- [ ] Fine-tune YOLOv8 en dataset de sellos
- [ ] Training (50 epochs mínimo)
- [ ] Evaluación en test set
- [ ] Comparar YOLO vs métodos clásicos

**Entregables:**
- 💻 `stamps/detector_yolo.py`
- 🤖 Modelo entrenado `.pt` file
- 📊 Curvas de entrenamiento (loss, mAP)
- 📈 Tabla comparativa: Classic vs YOLO

**Tiempo:** 30 horas

---

#### **Semana 10: Inpainting con LaMa**
**Actividades:**
- [ ] Integrar LaMa (clonar repo, download weights)
- [ ] Implementar wrapper en Python
- [ ] Testear en 30 imágenes con sellos
- [ ] Medir calidad de inpainting (LPIPS, FID)

**Entregables:**
- 💻 `stamps/inpainting.py`
- 📊 Métricas de calidad (PSNR, SSIM, LPIPS)
- 📷 Galería Before/After (20 ejemplos)
- ✅ Comparativa con cv2.inpaint (baseline)

**Tiempo:** 30 horas

---

#### **Semana 11: Pipeline v2 - Con Inpainting**
**Actividades:**
- [ ] Integrar detección + inpainting en pipeline
- [ ] **Experimento crítico:** OCR Before/After inpainting
- [ ] Análisis estadístico (paired t-test)
- [ ] Optimización de hiperparámetros

**Entregables:**
- 💻 `pipeline_v2.py` (con sellos)
- 📊 **Tabla de resultados:** CER Before vs After
- 📈 Análisis estadístico (p-value <0.05)
- 🎥 Video demo comparativo

**Tiempo:** 30 horas

---

#### **📋 Evaluación CP2 (2.5 puntos):**

| Criterio | Puntos |
|----------|--------|
| Detector de sellos funcional (mAP >0.6) | 0.6 |
| Inpainting integrado correctamente | 0.5 |
| **Mejora cuantificable en OCR (>5%)** | 0.8 |
| Análisis estadístico riguroso | 0.3 |
| Comparativa de enfoques (classic vs DL) | 0.2 |
| Documentación de experimento crítico | 0.1 |
| **TOTAL CP2** | **2.5** |

**Nota acumulada hasta aquí: 6.0/10** ✅ **BUENO**

**🎓 Decisión académica:** Si detiene aquí, tiene un proyecto bueno con aporte innovador validado.

---

### **CHECKPOINT 3: Validación Rigurosa (Semanas 12-13)** → Nota: +1.5/10

#### **Objetivo:** Demostrar resultados científicamente válidos

#### **Semana 12: Evaluación en SROIE Completo**
**Actividades:**
- [ ] Correr pipeline en SROIE test set completo
- [ ] Calcular métricas oficiales (F1 por entidad)
- [ ] Comparar con baselines (solo Tesseract, solo PaddleOCR)
- [ ] Análisis de errores (¿qué falla y por qué?)

**Entregables:**
- 📊 **Tabla de Resultados vs Baselines**
- 📈 Gráficos de comparación
- 📄 Sección "Resultados" del documento (5-7 páginas)
- 💾 Predicciones guardadas (para reproducibilidad)

**Tiempo:** 30 horas

---

#### **Semana 13: Ablation Study + Documentación**
**Actividades:**
- [ ] Ablation study: ¿Qué componente aporta más?
  - Pipeline sin preprocesamiento
  - Pipeline sin inpainting
  - Pipeline completo
- [ ] Redactar sección de Metodología
- [ ] Redactar Estado del Arte

**Entregables:**
- 📊 Tabla de Ablation Study
- 📄 Metodología (8-10 páginas)
- 📄 Estado del Arte (10-12 páginas)
- 📚 Referencias bibliográficas (mín 15 papers)

**Tiempo:** 35 horas

---

#### **📋 Evaluación CP3 (1.5 puntos):**

| Criterio | Puntos |
|----------|--------|
| Evaluación completa en SROIE | 0.4 |
| Comparativa con 2+ baselines | 0.3 |
| Ablation study riguroso | 0.4 |
| Documentación metodológica | 0.3 |
| Estado del arte bien fundamentado | 0.1 |
| **TOTAL CP3** | **1.5** |

**Nota acumulada hasta aquí: 7.5/10** ✅ **MUY BUENO**

**🎓 Decisión académica:** Proyecto muy bueno, cumple con estándares de tesis de grado.

---

### **CHECKPOINT 4: Features Avanzadas (Semanas 14-16)** → Nota: +1.5/10

#### **Objetivo:** Sistema completo de IDP

#### **Semana 14: Layout Analysis**
**Actividades:**
- [ ] Integrar LayoutParser o LayoutLMv3
- [ ] Detectar regiones: Texto, Tablas, Imágenes
- [ ] Benchmarking en PubLayNet (subset)
- [ ] Integrar en pipeline principal

**Entregables:**
- 💻 `layout/layout_analyzer.py`
- 📊 IoU por tipo de región
- 🎨 Visualizaciones de layout detectado
- ✅ API `analyze_layout(image)`

**Tiempo:** 30 horas

---

#### **Semana 15: Extracción de Tablas**
**Actividades:**
- [ ] Implementar Camelot (Lattice + Stream)
- [ ] Implementar PDFPlumber como fallback
- [ ] Estrategia híbrida automática
- [ ] Evaluación en dataset de tablas

**Entregables:**
- 💻 `tables/table_extractor.py`
- 📊 Tasa de extracción correcta (>75%)
- 📋 Ejemplos de tablas extraídas (CSV/JSON)
- ✅ API `extract_tables(document)`

**Tiempo:** 30 horas

---

#### **Semana 16: Pipeline v3 Final + Optimización**
**Actividades:**
- [ ] Integrar layout + tables en pipeline
- [ ] Optimización de latencia (<15s por doc)
- [ ] Refactoring de código
- [ ] Documentación de API completa

**Entregables:**
- 💻 `pipeline_v3.py` (sistema completo)
- 📊 Profiling de performance
- 📄 Swagger/OpenAPI documentation
- 🐳 Docker optimizado

**Tiempo:** 35 horas

---

#### **📋 Evaluación CP4 (1.5 puntos):**

| Criterio | Puntos |
|----------|--------|
| Layout analysis funcional | 0.4 |
| Extracción de tablas (>75% success rate) | 0.5 |
| Pipeline completo integrado | 0.3 |
| Optimización de latencia (<15s/doc) | 0.2 |
| Documentación de API | 0.1 |
| **TOTAL CP4** | **1.5** |

**Nota acumulada hasta aquí: 9.0/10** ⭐ **SOBRESALIENTE**

**🎓 Decisión académica:** Proyecto sobresaliente, supera expectativas de pregrado.

---

### **CHECKPOINT 5: Excelencia Académica (Semanas 17-18)** → Nota: +1.0/10

#### **Objetivo:** Contribución científica y profesionalización

#### **Semana 17: Paper Académico**
**Actividades:**
- [ ] Redactar paper (formato IEEE, 6-8 páginas)
  - Abstract
  - Introduction
  - Related Work
  - Methodology
  - Experiments
  - Results
  - Conclusion
- [ ] Generar figuras de calidad publicable
- [ ] Revisión con asesor

**Entregables:**
- 📄 **Paper en formato IEEE** (LaTeX)
- 📊 Figuras en alta resolución
- 📚 Referencias en BibTeX

**Tiempo:** 35 horas

---

#### **Semana 18: Demo Profesional + Código Producción**
**Actividades:**
- [ ] Crear demo interactiva (Streamlit/Gradio)
- [ ] Desplegar en cloud (Hugging Face Spaces / Railway)
- [ ] Código production-ready:
  - CI/CD con GitHub Actions
  - Tests automatizados (>80% coverage)
  - Logging estructurado
  - Error handling robusto
- [ ] Documentación completa (README, CONTRIBUTING, API docs)

**Entregables:**
- 🌐 **Demo en vivo** (URL pública)
- 💻 Repositorio production-ready
- 📄 Documentación exhaustiva
- 🎥 Video explicativo (5-7 min)

**Tiempo:** 35 horas

---

#### **📋 Evaluación CP5 (1.0 punto):**

| Criterio | Puntos |
|----------|--------|
| Paper en formato IEEE (completo) | 0.4 |
| Demo interactiva desplegada | 0.3 |
| Código production-ready (CI/CD, tests) | 0.2 |
| Video explicativo profesional | 0.1 |
| **TOTAL CP5** | **1.0** |

**Nota acumulada hasta aquí: 10.0/10** 🏆 **EXCELENCIA**

**🎓 Decisión académica:** Proyecto de excelencia, candidato a mejor proyecto del año.

---

## 📊 RESUMEN DE TIEMPOS POR CHECKPOINT

| Checkpoint | Semanas | Horas Totales | Horas/Semana | Nota Acum. |
|-----------|---------|---------------|--------------|------------|
| CP0 | 3 | 70 h | 23 | 1.0 |
| CP1 | 4 | 105 h | 26 | 3.5 ✅ |
| CP2 | 4 | 115 h | 29 | 6.0 |
| CP3 | 2 | 65 h | 33 | 7.5 |
| CP4 | 3 | 95 h | 32 | 9.0 ⭐ |
| CP5 | 2 | 70 h | 35 | 10.0 🏆 |
| **TOTAL** | **18** | **520 h** | **~29 h/sem** | |

**Nota:** El promedio de 29 horas/semana es intensivo pero manejable para un proyecto de grado full-time.

---

## 🎯 ESTRATEGIAS DE MITIGACIÓN DE RIESGOS

### **Si el estudiante va retrasado:**

#### **En Semana 8 (inicio CP2):**
- ❌ Si CP0+CP1 no están completos → **DETENER**
- ✅ Remedial: Completar CP1 antes de continuar
- ⏱️ Extensión: +2 semanas máximo

#### **En Semana 12 (inicio CP3):**
- ❌ Si inpainting NO mejora OCR >5% → **PIVOTAR**
- ✅ Plan B: Descope inpainting, enfocarse en preprocesamiento robusto
- 📊 Mantener nota de CP2 si detector de sellos funciona

#### **En Semana 14 (inicio CP4):**
- ⚠️ Si tiempo es limitado → **PRIORIZAR**
- ✅ Opción 1: Solo layout (sin tablas) → 9.0 es alcanzable
- ✅ Opción 2: Solo tablas (sin layout) → 9.0 es alcanzable

---

## 🔄 FLEXIBILIDAD DEL SISTEMA

### **Ventajas del Sistema de Checkpoints:**

1. ✅ **Evaluación Justa:**
   - Estudiante que llega a CP3 tiene 7.5 (muy bueno)
   - No es "todo o nada"

2. ✅ **Motivación Incremental:**
   - Cada checkpoint es un "win"
   - Gamificación del aprendizaje

3. ✅ **Adaptabilidad:**
   - Profesor puede ajustar pesos según contexto
   - Estudiante puede negociar prioridades

4. ✅ **Transparencia:**
   - Criterios claros desde el inicio
   - No hay sorpresas en la evaluación

---

## 📋 RÚBRICA DETALLADA POR CHECKPOINT

### **CP0: Fundamentos (1.0 punto)**

| Criterio | Excelente (1.0) | Bueno (0.7) | Suficiente (0.5) | Insuficiente (0.0) |
|----------|----------------|-------------|------------------|--------------------|
| **Dataset Anotado** | 100+ sellos, alta calidad | 80+ sellos, calidad media | 50+ sellos | <50 sellos |
| **Documentación** | Completa, profesional | Suficiente | Básica | Falta |
| **Infraestructura** | GPU + Docker + Git | GPU + Git | Solo local | No funciona |

---

### **CP1: MVP Core (2.5 puntos)**

| Criterio | Excelente (2.5) | Bueno (2.0) | Suficiente (1.5) | Insuficiente (<1.5) |
|----------|----------------|-------------|------------------|---------------------|
| **Preprocesamiento** | 3+ métodos, bien implementados | 2 métodos | 1 método funcional | No funciona |
| **OCR** | 2 engines + fallback | 1 engine robusto | 1 engine básico | No extrae texto |
| **Pipeline** | Dockerizado, documentado | Funcional | Funciona localmente | Errores frecuentes |
| **Accuracy** | >80% SROIE | 70-80% | 60-70% | <60% |

---

### **CP2: Diferenciador (2.5 puntos)**

| Criterio | Excelente (2.5) | Bueno (2.0) | Suficiente (1.5) | Insuficiente (<1.5) |
|----------|----------------|-------------|------------------|---------------------|
| **Detección Sellos** | YOLO mAP >0.8 | mAP 0.6-0.8 | Detector clásico funcional | No detecta |
| **Inpainting** | LaMa integrado | cv2.inpaint funcional | Inpainting básico | No implementado |
| **Mejora OCR** | >15% mejora | 10-15% | 5-10% | <5% |
| **Validación** | Análisis estadístico riguroso | Comparativa básica | Solo ejemplos visuales | Sin validación |

---

### **CP3: Validación (1.5 puntos)**

| Criterio | Excelente (1.5) | Bueno (1.2) | Suficiente (0.9) | Insuficiente (<0.9) |
|----------|----------------|-------------|------------------|---------------------|
| **Benchmark SROIE** | Test completo, múltiples métricas | Test parcial | Solo accuracy | Sin benchmark |
| **Ablation Study** | 3+ variantes comparadas | 2 variantes | Análisis superficial | No realizado |
| **Documentación** | Metodología + Estado del Arte | Solo metodología | Documentación básica | Incompleta |

---

### **CP4: Features Avanzadas (1.5 puntos)**

| Criterio | Excelente (1.5) | Bueno (1.2) | Suficiente (0.9) | Insuficiente (<0.9) |
|----------|----------------|-------------|------------------|---------------------|
| **Layout Analysis** | LayoutLMv3, IoU >0.75 | LayoutParser básico | Detección manual | No implementado |
| **Tablas** | Híbrido, >85% accuracy | Camelot solo | Extracción básica | No funciona |
| **Integración** | Pipeline unificado optimizado | Pipeline funcional | Módulos separados | Sin integración |

---

### **CP5: Excelencia (1.0 punto)**

| Criterio | Excelente (1.0) | Bueno (0.7) | Suficiente (0.5) | Insuficiente (0.0) |
|----------|----------------|-------------|------------------|---------------------|
| **Paper IEEE** | Completo, listo para submit | Draft sólido | Estructura básica | No escrito |
| **Demo** | Desplegada en cloud, UX profesional | Demo local funcional | Jupyter notebook | No hay demo |
| **Código Prod** | CI/CD, tests >80%, docs | Tests básicos | Código limpio | Sin tests |

---

## 🎓 RECOMENDACIONES PEDAGÓGICAS

### **Para el Estudiante:**

1. ✅ **No saltar checkpoints**
   - Cada CP es prerequisito del siguiente
   - Validar con profesor antes de avanzar

2. ✅ **Priorizar calidad sobre cantidad**
   - Mejor un CP3 excelente que CP4 mediocre
   - 7.5 muy bien hecho > 9.0 incompleto

3. ✅ **Checkpoints semanales con asesor**
   - Reunión de 30 min cada viernes
   - Demo de avance + planning próxima semana

4. ✅ **Documentar mientras desarrollas**
   - No dejar escritura para el final
   - Cada experimento → sección de Resultados

---

### **Para el Profesor:**

1. ✅ **Evaluación continua:**
   - Revisar entregables en <48 horas
   - Feedback específico y accionable

2. ✅ **Flexibilidad controlada:**
   - Permitir negociación de CP4 (layout vs tablas)
   - NO permitir saltar CP2 (es el core innovador)

3. ✅ **Puntos de decisión claros:**
   - Semana 11: ¿Continuar con CP3 o reforzar CP2?
   - Semana 14: ¿Ir por CP5 o perfeccionar CP4?

---

## 📈 CASOS DE USO DEL SISTEMA

### **Caso 1: Estudiante Ambicioso (Nota Objetivo: 10.0)**
- Semanas 1-11: CP0→CP2 sin problemas
- Semanas 12-13: CP3 con ablation study extenso
- Semanas 14-16: CP4 completo (layout + tablas)
- Semanas 17-18: CP5 (paper + demo cloud)
- **Resultado:** 10.0 + Mención de Honor

---

### **Caso 2: Estudiante Realista (Nota Objetivo: 8.0-9.0)**
- Semanas 1-11: CP0→CP2 (dedicar más tiempo a inpainting)
- Semanas 12-13: CP3 sólido
- Semanas 14-16: CP4 (solo tablas, descope layout)
- **Resultado:** 8.5-9.0 Sobresaliente

---

### **Caso 3: Estudiante con Contratiempos (Nota Objetivo: 7.0-7.5)**
- Semanas 1-7: CP0+CP1 (retrasado 1 semana)
- Semanas 8-13: CP2 (inpainting mejora solo 8%, acepta)
- Semanas 14-16: CP3 (validación básica)
- **Resultado:** 7.0-7.5 Muy Bueno (aprobado con mérito)

---

## 🏆 CONCLUSIONES

### **Por qué este sistema es mejor:**

1. ✅ **Reduce ansiedad:** Estudiante sabe exactamente dónde está
2. ✅ **Fomenta excelencia:** Cada CP es un reto alcanzable
3. ✅ **Evaluación justa:** No se penaliza por no llegar al final
4. ✅ **Escalable:** Profesor puede adaptar pesos según curso
5. ✅ **Calidad garantizada:** CP1 asegura proyecto funcional mínimo

### **Mejora sobre plan original:**

| Aspecto | Plan Original (8-10 meses) | Plan Checkpoints (16-18 sem) |
|---------|---------------------------|------------------------------|
| **Duración** | 32-40 semanas | 16-18 semanas ✅ |
| **Evaluación** | Final (todo o nada) | Incremental ✅ |
| **Calidad** | Alta | **Igual o mayor** ✅ |
| **Flexibilidad** | Baja | Alta ✅ |
| **Motivación** | Picos y valles | Constante ✅ |

---

**Firma:**

**Dr. Andrés Parra Rojas, PhD**  
Profesor Titular  
Universidad del Rosario  

**Fecha:** Febrero 2026
