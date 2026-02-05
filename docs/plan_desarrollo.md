# 🚀 Hoja de Ruta y Tareas: Proyecto IDP
## Manuel Cruz Garrote - Proyecto de Grado
### Universidad del Rosario

**Meta Académica:** 7.5/10 (Muy Bueno)  
**Periodo:** Febrero - Mayo 2026

---

## 🎯 RESUMEN DE HITOS (Checkpoints)

| Hito | Fase | Fecha Objetivo | Entregable Clave | Nota |
|------|------|----------------|------------------|------|
| **CP0** | Fundamentos | 18 Feb | Dataset (50 sellos) + Infraestructura. | 1.0 |
| **CP1** | MVP Core | 11 Mar | Pipeline Preprocesamiento + OCR. | 3.5 ✅ |
| **CP2** | Innovación | 8 Abr | Detección + Inpainting de sellos. | 6.0 |
| **CP3** | Validación | 29 Abr | Documento Académico + Resultados. | 7.5 ⭐ |
| **FINAL** | Cierre | 30 May | Sustentación ante jurado. | - |

---

## 📅 PLAN DE EJECUCIÓN SEMANAL

### FASE 0: FUNDAMENTOS (CP0)
**De Feb 5 a Feb 18**

- [ ] **Semana 1: Configuración**
    - [ ] Setup de repositorio GitHub y ambiente Python.
    - [ ] Lectura de papers base (TrOCR, LaMa, PaddleOCR).
    - [ ] Documento inicial de Planteamiento del Problema.
- [ ] **Semana 2: Dataset Inicial**
    - [ ] Recolección y anotación de 25 sellos reales.
    - [ ] Data augmentation para llegar a 50 muestras.
    - [ ] **Hito CP0:** Presentar dataset y setup inicial al asesor.

### FASE 1: MVP - PIPELINE CORE (CP1)
**De Feb 19 a Mar 11**

- [ ] **Semana 3: Preprocesamiento**
    - [ ] Implementar rotación (Hough) y binarización (Otsu).
    - [ ] Pruebas unitarias de calidad de imagen.
- [ ] **Semana 4-5: Motor OCR**
    - [ ] Integrar PaddleOCR con fallback a Tesseract.
    - [ ] **Hito CP1:** Demo funcional (Imagen -> Texto) con accuracy >70%.

### FASE 2: EL DIFERENCIADOR - INPAINTING (CP2)
**De Mar 12 a Abr 8**

- [ ] **Semana 6-7: Detección de Sellos**
    - [ ] Detector basado en color (HSV) y generación de máscaras.
    - [ ] Validación en el dataset de 50 sellos.
- [ ] **Semana 8-9: Borrado Inteligente (LaMa)**
    - [ ] Integrar modelo LaMa para eliminación de sellos.
    - [ ] **Hito CP2:** Experimento validado (Mejora OCR >5% post-inpainting).

### FASE 3: VALIDACIÓN Y ACADEMIA (CP3)
**De Abr 9 a Abr 29**

- [ ] **Semana 10: Benchmark Científico**
    - [ ] Evaluación completa en 100 documentos SROIE.
    - [ ] Comparativa de métricas CER/WER contra baselines.
- [ ] **Semana 11-12: Documentación Final**
    - [ ] Redacción de Metodología, Estado del Arte y Resultados.
    - [ ] **Hito CP3:** Entrega de documento académico (20-25 páginas).

### FASE FINAL: SUSTENTACIÓN
**De Abr 30 a May 30**

- [ ] **Semana 13-15: Preparativos**
    - [ ] Refinamiento de código y demo interactiva.
    - [ ] Grabación de video técnico y diseño de diapositivas.
- [ ] **30 MAYO:** Sustentación final del proyecto.

---

## 🛠️ NOTAS DE DESARROLLO

**Decisiones Técnicas:**
- Se prioriza detector HSV sobre YOLO por simplicidad y tiempo.
- Se utiliza LaMa pre-entrenado para el inpainting.
- Validación basada en mejora real del OCR en documentos "sucios".

**Alcance Descartado:**
- ❌ Layout Analysis avanzado, Extracción de Tablas y Gráficas.
- ❌ Paper IEEE (se entrega Informe Académico detallado).
- ❌ Despliegue en Cloud (se ejecuta local/notebook).
