# 🚀 Hoja de Ruta: Proyecto IDP
## Manuel Cruz Garrote - Proyecto de Grado
### Universidad del Rosario

**Meta:** Desarrollar un sistema funcional de IDP con inpainting de sellos.
**Periodo:** 16 semanas (Febrero - Mayo 2026)

---

## 🎯 RESUMEN DE CHECKPOINTS (Hitos de Desarrollo)

| Hito | Fase | Fecha Objetivo | Entregable Clave |
|------|------|----------------|------------------|
| **CP0** | Fundamentos | 18 Feb | Dataset de 50 sellos anotados + Repo. |
| **CP1** | MVP Core | 11 Mar | Pipeline Preprocesamiento + OCR. |
| **CP2** | Innovación | 8 Abr | Detector + Inpainting de sellos. |
| **CP3** | Validación | 29 Abr | Documento Académico + Benchmark SROIE. |
| **FINAL** | Cierre | 30 May | Sustentación ante jurado. |

---

## 📅 PLAN DE DESARROLLO SEMANAL

---

### FASE 0: FUNDAMENTOS (CP0)

**Semana 1: Configuración e Investigación**
- [ ] Inicialización técnica: Repositorio GitHub y ambiente virtual.
- [ ] Investigación: Lectura de 5 papers clave (TrOCR, LaMa, PaddleOCR).
- [ ] Definición: Documento de Planteamiento del Problema.
- [ ] Exploración: Análisis del dataset SROIE.

**Semana 2: Construcción del Dataset**
- [ ] Recolección: Web scraping de 25 imágenes reales con sellos.
- [ ] Anotación: Uso de LabelImg para delimitar sellos oficiales.
- [ ] Aumento de Datos: Generación de 25 imágenes sintéticas adicionales.
- [ ] Estructura: Organización de carpetas `data/raw`, `data/processed`.

**Semana 3: Cierre de Infraestructura**
- [ ] GPU: Confirmación de recursos computacionales (Colab Pro / AWS).
- [ ] Split: División de datos en Train/Val/Test.
- [ ] **Hito CP0:** Presentar dataset y setup inicial al asesor.

---

### FASE 1: MVP CORE - PIPELINE BASE (CP1)

**Semana 4: Preprocesamiento Geométrico**
- [ ] Implementación: Algoritmo de corrección de rotación (Hough).
- [ ] Implementación: Binarización adaptativa para mejorar claridad.
- [ ] Validación: Visualización de resultados Before/After.

**Semana 5: Motores de OCR**
- [ ] Integración: Entorno funcional para PaddleOCR y Tesseract.
- [ ] Lógica: Sistema de fallback (si Paddle falla, usar Tesseract).
- [ ] Benchmarking: Medición inicial de precisión en documentos limpios.

**Semana 6: Integración v1**
- [ ] Orquestación: Script `pipeline_v1.py` unificando procesos.
- [ ] Pruebas: Ejecución en 50 muestras de SROIE.
- [ ] **Hito CP1:** Demo funcional del sistema básico (OCR aprobado).

---

### FASE 2: EL DIFERENCIADOR - INPAINTING (CP2)

**Semana 7: Detección de Sellos**
- [ ] Desarrollo: Detector basado en espacio de color HSV (rojos/azules).
- [ ] Máscaras: Generación automática de máscaras para inpainting.
- [ ] Testing: Validación de detección en el dataset propio de 50 sellos.

**Semana 8: Integración de LaMa**
- [ ] Setup: Instalación de pesos pre-entrenados del modelo LaMa.
- [ ] Inpainting: Ejecución de limpieza de sellos en imágenes de prueba.
- [ ] Ajustes: Refinamiento de la dilatación de máscaras para mejor borrado.

**Semana 9: Experimento Crítico**
- [ ] Comparativa: OCR con sellos vs. OCR post-inpainting.
- [ ] Validación: Medición de mejora en CER (Character Error Rate).
- [ ] **Hito CP2:** Resultados del inpainting demostrando mejora >5%.

---

### FASE 3: VALIDACIÓN Y ACADEMIA (CP3)

**Semana 10: Rigurosidad Científica**
- [ ] Benchmark: Evaluación completa en 100 documentos SROIE.
- [ ] Análisis: Identificación de casos de falla y falsos positivos.
- [ ] Gráficos: Generación de tablas visuales de rendimiento.

**Semana 11: Documentación Académica**
- [ ] Redacción I: Sección de Metodología y Estado del Arte.
- [ ] Redacción II: Discusión de resultados y comparativa con baselines.
- [ ] Referencias: Organización de bibliografía en formato IEEE.

**Semana 12: Cierre Académico**
- [ ] Consolidación: Documento final de 25 páginas listo para revisión.
- [ ] Presentación: Diseño de las 10 diapositivas clave de resultados.
- [ ] **Hito CP3:** Entrega del documento académico completo.

---

### FASE FINAL: SUSTENTACIÓN Y CIERRE

**Semana 13-14: Refinamiento**
- [ ] Ajustes: Implementación de sugerencias finales del asesor.
- [ ] Código: Limpieza de repositorio, eliminación de archivos temporales.
- [ ] Documentación: README exhaustivo e instrucciones de uso.

**Semana 15: Preparación Final**
- [ ] Demo: Creación de un Notebook de prueba interactivo.
- [ ] Video: Grabación de demo técnica (3 min).
- [ ] Ensayo: Práctica de la sustentación frente a espejo/amigos.

**Semana 16: Entrega y Sustentación**
- [ ] **30 MAYO:** Sustentación final del proyecto IDP.
- [ ] Cierre del repositorio con tag `v1.0-final`.

---

## 🛠️ DECISIONES TÉCNICAS (Esperadas)

1. **Stack:** Python 3.10, OpenCV, PyTorch, PaddleOCR.
2. **Detección Sellos:** Se prioriza detector HSV sobre YOLO por eficiencia de tiempo.
3. **Inpainting:** Uso de modelo LaMa (Samsung AI) por su capacidad de reconstrucción global.
4. **Validación:** El éxito se mide por la mejora del OCR en documentos "sucios".

---

## 🚦 PUNTOS DE CONTROL CON ASESOR (Jueves 10 AM)

- **Feb 18:** Validación de Dataset.
- **Mar 11:** Demo Pipeline v1.
- **Abr 8:** Resultados experimento Inpainting.
- **Abr 29:** Revisión Documento Académico.
- **May 22:** Pre-sustentación.

---

**Manuel Cruz Garrote**  
"Consistencia > Intensidad"
