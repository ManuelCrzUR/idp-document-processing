# Metodología y Plan Técnico - IDP
## Manuel Cruz Garrote - Proyecto de Grado

Este documento detalla la lógica algorítmica y la estrategia de implementación para el sistema de Procesamiento Inteligente de Documentos.

---

## 1. ARQUITECTURA DEL SISTEMA

El sistema opera como un pipeline secuencial modular:

1. **Preprocesamiento:** Corrección de rotación (Hough Transform) y binarización (Otsu).
2. **Detección de Sellos:** Localización basada en espacio de color HSV y morfología.
3. **Inpainting (LaMa):** Eliminación del sello y reconstrucción del fondo/texto.
4. **OCR Multimodal:** Extracción de texto usando PaddleOCR con fallback a Tesseract.

---

## 2. METODOLOGÍA TÉCNICA

### 2.1 Preprocesamiento Geométrico
- **Rotación:** Se detectan líneas dominantes mediante la **Transformada de Hough**. El ángulo promedio de estas líneas indica la inclinación del documento, permitiendo aplicar una matriz de rotación afín para enderezarlo.
- **Binarización:** Se utiliza **Thresholding Adaptativo** para separar el texto del fondo, compensando variaciones de iluminación y sombras.

### 2.2 Detección de Sellos (Enfoque HSV)
En lugar de entrenar un modelo complejo (YOLO), se aprovecha el contraste cromático:
- Se convierte la imagen a espacio **HSV**.
- Se definen umbrales para colores típicos de sellos (Azul y Rojo).
- Se aplican operaciones morfológicas (dilatación/cierre) para consolidar la máscara del sello.

### 2.3 Borrado Inteligente (LaMa)
Para el inpainting se utiliza **LaMa (Large Mask Inpainting)**:
- Utiliza **Convoluciones de Fourier** que permiten un campo de visión global.
- Esto es crítico para "adivinar" el texto que está debajo del sello basándose en el contexto del resto del documento.

### 2.4 Reconocimiento de Texto (OCR)
- **PaddleOCR:** Utiliza modelos basados en Transformers que ofrecen alta precisión en español.
- **Fallback:** Si el motor principal falla o tiene baja confianza, se utiliza **Tesseract 5.0** (LSTM) como respaldo.

---

## 3. STACK TECNOLÓGICO

- **Lenguaje:** Python 3.10+
- **Visión Artificial:** OpenCV 4.8.
- **Deep Learning:** PyTorch (para Inpainting).
- **OCR:** PaddleOCR, Tesseract.
- **Validación:** Pytest para calidad, métricas CER/WER para precisión.

---

## 4. PLAN DE VERIFICACIÓN

El éxito del desarrollo se validará mediante dos experimentos clave:

1. **Benchmark SROIE:** Evaluación del pipeline en 100 muestras del dataset público para obtener un baseline de precisión.
2. **Experimento de Inpainting:** Comparación directa del OCR en documentos con sellos, midiendo la mejora porcentual en la extracción de texto tras aplicar el borrado inteligente (Meta: >5% de mejora).

---

## 5. RECURSOS Y LIMITACIONES

- El desarrollo se realizará en ambiente local con soporte de GPU (necesaria para LaMa).
- El sistema asume layouts de documentos relativamente simples (no se procesarán tablas complejas o gráficas en esta versión).

---

**Manuel Cruz Garrote**  
Febrero 2026
