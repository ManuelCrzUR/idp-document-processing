# Criterios de Evaluación y Checkpoints
## Proyecto IDP - Manuel Cruz Garrote
### Universidad del Rosario

---

## 🎯 FILOSOFÍA DE EVALUACIÓN

El proyecto se evalúa mediante un sistema de **Checkpoints Incrementales**. Cada hito alcanzado asegura una base de calificación y construye el camino hacia la excelencia. El enfoque principal es la **calidad técnica** y la **validación experimental**.

---

## 📊 ESTRUCTURA DE CALIFICACIÓN

| Checkpoint | Entregable Clave | Nota Acumulada | Objetivo de Calidad |
|-----------|------------------|----------------|---------------------|
| **CP0** | Dataset + Setup | 1.0 | Rigurosidad en la recolección y anotación. |
| **CP1** | MVP Core (Pipeline) | 3.5 ✅ | Funcionalidad básica y robustez del OCR. |
| **CP2** | Inpainting (Innovación) | 6.0 | Mejora cuantificable mediante limpieza de sellos. |
| **CP3** | Validación Académica | 7.5 ⭐ | Rigor científico y documentación de resultados. |
| **FINAL** | Sustentación | 7.5+ | Defensa técnica y calidad de presentación. |

---

## 📋 DETALLE DE ENTREGABLES POR HITO

### **CHECKPOINT 0: Fundamentos (Hasta 18 Feb)**
- **Dataset SROIE:** Estructurado y analizado mediante EDA.
- **Dataset de Sellos:** 50 imágenes (25 reales, 25 aumentadas) con anotaciones precisas.
- **Infraestructura:** Repositorio en GitHub con README y ambiente virtual configurado.
- **Documentación:** Planteamiento del problema claro y conciso.

### **CHECKPOINT 1: MVP Básico (Hasta 11 Mar)**
- **Módulo de Preprocesamiento:** Algoritmos de rotación y binarización funcionando en diversos documentos.
- **Motor OCR:** Integración de PaddleOCR + Tesseract con lógica de fallback.
- **Pipeline v1:** Ejecución automática de "Imagen -> Texto" con precisión >70%.

### **CHECKPOINT 2: Diferenciador Innovador (Hasta 8 Abr)**
- **Detector de Sellos:** Identificación precisa de regiones de sellos basada en color/forma.
- **Inpainting LaMa:** Eliminación de sellos sin degradar el texto subyacente.
- **Validación Crítica:** Experimento de comparación Before/After inpainting demostrando una mejora de al menos 5% en el OCR.

### **CHECKPOINT 3: Rigurosidad y Academia (Hasta 29 Abr)**
- **Benchmark Completo:** Evaluación en 100 documentos con métricas CER, WER y F1.
- **Documento Académico:** Informe de 20-25 páginas con Estado del Arte, Metodología y Resultados.
- **Análisis de Error:** Documentación de limitaciones y casos de éxito del sistema.

### **FASE FINAL: Sustentación (Hasta 30 May)**
- **Código Final:** Repositorio limpio, modular y documentado.
- **Presentación:** 10-15 diapositivas enfocadas en el aporte técnico y resultados.
- **Demo Técnica:** Ejecución del sistema en vivo o video demo profesional.

---

## 🚦 RÚBRICA DE EXCELENCIA TÉCNICA

| Criterio | Expectativa para 7.5+ |
|----------|-----------------------|
| **Código** | Modular, uso de clases/funciones, sin hard-coding. |
| **Validación** | Uso de métricas estándar (CER/WER), no solo visual. |
| **Innovación** | Implementación exitosa de inpainting (LaMa). |
| **Documentación** | Redacción técnica clara, referencias IEEE. |

---

## 🔄 PLAN DE CONTINGENCIA

- **Riesgo:** Si el inpainting no mejora el OCR en los tiempos previstos.
- **Solución:** Reforzar el módulo de preprocesamiento avanzado (denoising, corrección de perspectiva) para asegurar la calidad del entregable base (Checkpoint 1 revisado).

---

**Manuel Cruz Garrote**  
"Calidad sobre cantidad"
