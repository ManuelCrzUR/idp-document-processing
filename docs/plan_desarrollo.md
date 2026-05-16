# Hoja de Ruta y Tareas: Proyecto IDP
## Manuel Cruz Garrote - Proyecto de Grado
### Universidad del Rosario

**Meta Academica:** 7.5/10 (Muy Bueno)
**Periodo:** Febrero - Mayo 2026
**Ultima actualizacion:** 17 de marzo de 2026

---

## RESUMEN DE HITOS (Checkpoints)

| Hito | Fase | Fecha Objetivo | Entregable Clave | Estado |
|------|------|----------------|------------------|--------|
| **CP0** | Fundamentos | 18 Feb | Dataset (50 sellos) + Infraestructura | Completado (nota: 1.0) |
| **CP1** | MVP Core | 11 Mar -> **24 Mar** | Pipeline Preprocesamiento + OCR | Retrasado ~2 semanas |
| **CP2** | Innovacion | 8 Abr -> **15 Abr** | Deteccion + Inpainting de sellos | Pendiente |
| **CP3** | Validacion | 29 Abr -> **6 May** | Documento Academico + Resultados | Pendiente |
| **FINAL** | Cierre | 30 May | Sustentacion ante jurado | Pendiente |

> [!WARNING]
> **Estado al 17 de marzo:** El proyecto tiene ~1 semana de retraso respecto al plan original.
> La estructura de datos esta lista pero falta implementar codigo. Se ajustaron las fechas
> dando 1 semana extra a cada checkpoint. **Es critico empezar la implementacion esta semana.**

---

## ESTADO ACTUAL DE DATOS

| Dataset | Fuente | Estado | Accion Pendiente |
|---------|--------|--------|------------------|
| MultiFinBen-SpanishOCR | Hugging Face | 24 parquets (~13K muestras) | Extraer imagenes PNG |
| Stamps Dataset | Mendeley | 174+ BMPs | Listo |
| StaVer | Kaggle | Parcial (metadata) | Descargar scans completos |
| SROIE v2 | Kaggle | No descargado | Descargar con kaggle CLI |
| SROIE Original | Kaggle | No descargado | Descargar con kaggle CLI |

---

## PLAN DE EJECUCION SEMANAL (REVISADO)

### FASE 0: FUNDAMENTOS (CP0) - COMPLETADO
**Feb 5 - Feb 18**

- [x] **Semana 1-2: Configuracion y Datos**
    - [x] Setup de repositorio y estructura de carpetas
    - [x] Lectura de papers base (TrOCR, LaMa, PaddleOCR)
    - [x] Documento inicial de Planteamiento del Problema
    - [x] Recoleccion de datasets (SpanishOCR, Stamps, StaVer parcial)
    - [x] Scripts de inspeccion y extraccion de muestras
    - [x] **Hito CP0:** Dataset inicial presentado al asesor

### FASE 1: MVP - PIPELINE CORE (CP1) - EN PROGRESO
**Feb 19 - Mar 24** (ajustado: +2 semanas)

- [ ] **Semana 3 (Mar 17-21): Datos + Preprocesamiento** <-- AHORA
    - [ ] Completar descarga de todos los datasets (SROIE, StaVer completo)
    - [ ] Reorganizar datos en estructura estandar
    - [ ] Extraer imagenes PNG del SpanishOCR
    - [ ] Implementar src/preprocessing/cleaner.py (rotacion, binarizacion, denoising)
    - [ ] Tests unitarios del preprocesamiento
- [ ] **Semana 4 (Mar 22-28): Motor OCR**
    - [ ] Integrar PaddleOCR (lang='es') + Tesseract (lang='spa')
    - [ ] Post-procesamiento de texto
    - [ ] Baseline: medir CER/WER en SpanishOCR sin preprocesamiento
    - [ ] **Hito CP1:** Demo funcional (Imagen -> Texto) con metricas

### FASE 2: EL DIFERENCIADOR - INPAINTING (CP2)
**Mar 25 - Abr 15** (ajustado: +1 semana)

- [ ] **Semana 5-6 (Mar 25 - Abr 7): Deteccion de Sellos**
    - [ ] Implementar detector HSV (rojo + azul) con morfologia
    - [ ] Generacion de mascara binaria para inpainting
    - [ ] Validacion en StaVer y Stamps Dataset (IoU > 0.7)
    - [ ] Notebook de visualizacion de detecciones
- [ ] **Semana 7-8 (Abr 7 - Abr 15): Borrado Inteligente (LaMa)**
    - [ ] Integrar modelo LaMa pre-entrenado
    - [ ] Fallback con cv2.inpaint (TELEA)
    - [ ] Pipeline completo: deteccion -> mascara -> inpainting -> OCR
    - [ ] **Hito CP2:** Experimento validado (Mejora OCR >5% post-inpainting)

### FASE 3: VALIDACION Y ACADEMIA (CP3)
**Abr 16 - May 6** (ajustado: +1 semana)

- [ ] **Semana 9 (Abr 16 - Abr 22): Benchmark Cientifico**
    - [ ] Evaluacion completa: CER/WER en 100+ documentos
    - [ ] Experimento principal: con sellos vs sin sellos (post-inpainting)
    - [ ] Benchmark comparativo en SROIE
    - [ ] Generar tablas y graficas de resultados
- [ ] **Semana 10-11 (Abr 23 - May 6): Documentacion Final**
    - [ ] Estado del Arte (5-7 paginas)
    - [ ] Metodologia con diagramas (5-7 paginas)
    - [ ] Resultados con tablas/graficas (5-7 paginas)
    - [ ] Conclusiones y Trabajo Futuro
    - [ ] **Hito CP3:** Entrega de documento academico (20-25 paginas)

### FASE FINAL: SUSTENTACION
**May 7 - May 30**

- [ ] **Semana 12-13: Preparativos**
    - [ ] Refinamiento de codigo y pipeline.py completo
    - [ ] Demo interactiva reproducible
    - [ ] Diapositivas (15-20 slides)
    - [ ] Video tecnico de demo
- [ ] **Semana 14-15: Ensayo y Cierre**
    - [ ] Ensayo de presentacion (2-3 veces)
    - [ ] Revision final del documento
    - [ ] **30 MAYO:** Sustentacion final del proyecto

---

## NOTAS DE DESARROLLO

**Decisiones Tecnicas Confirmadas:**
- Detector HSV sobre YOLO (simplicidad + tiempo)
- LaMa pre-entrenado para inpainting (no entrenar desde cero)
- PaddleOCR como motor principal, Tesseract como fallback
- SpanishOCR como dataset principal (espanol, financiero)
- SROIE como benchmark internacional comparativo
- Validacion basada en mejora medible del OCR (CER/WER)

**Alcance Descartado (confirmado):**
- Layout Analysis avanzado (LayoutLMv3, Detectron2)
- Extraccion de Tablas y Graficas
- NLP / RAG / Resumenes
- Paper IEEE (se entrega Informe Academico detallado)
- Despliegue en Cloud (se ejecuta local/notebook)
- Clasificacion de sellos (solo deteccion + eliminacion)

**Riesgos Identificados:**
- LaMa requiere GPU -- si no hay GPU disponible, usar cv2.inpaint como plan B
- PaddleOCR en espanol puede tener menor precision que en chino/ingles -- validar temprano
- StaVer dataset incompleto -- puede afectar la evaluacion de deteccion de sellos