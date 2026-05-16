# Reporte Técnico Consolidado: IDP - Limpieza y Detección de Sellos
## Fases 0 a 3
**Fecha:** 8 de abril de 2026
**Autor:** Manuel Cruz Garrote

Este documento detalla el progreso técnico, las metodologías implementadas y las métricas obtenidas desde la generación de datos hasta la prueba de concepto del borrado de sellos en documentos.

---

## FASE 0: Auditoría y Refinamiento de Datos (Extracción de Sellos)

**Objetivo:** Obtener sellos con fondo perfectamente transparente ("limpios") para usar como base del entrenamiento.

*   **Problema Inicial (Enfoque Clásico):** La segmentación inicial basada exclusivamente en umbrales de color fallaba en sellos con colores grises, beige o escaneos de baja calidad. Inicialmente tuvimos un **6% de error** (92 fallos sobre 1,557 muestras).
*   **Solución Implementada:** Se diseñó un **Pipeline Heurístico Híbrido** en visión artificial:
    1.  **Luminancia (Y en YCbCr / Escala de grises):** Filtrado de píxeles oscuros (umbral < 215).
    2.  **Saturación (S en HSV):** Filtrado de píxeles con pigmentación definida (umbral > 35).
    3.  **Morfología Matemática:** Uso de operaciones de _Opening_ (Apertura) y _Cierre_ para eliminar píxeles de ruido aislados alrededor de los bordes.
*   **Métricas de Éxito:**
    *   Total procesado: **1,557 imágenes**.
    *   Tasa de éxito final: **99.42%** (Los fallos se redujeron de 92 a solo 9 sellos).

---

## FASE 1: Generación de Dataset Sintético

**Objetivo:** Ante la falta de datos reales etiquetados, crear un banco de entrenamiento robusto combinando documentos y los sellos de la Fase 0.

*   **Metodología:** Superposición algorítmica (Alpha Blending) de sellos transparentes sobre el corpus `SpanishOCR` (facturas y documentos administrativos reales).
*   **Data Augmentation (Aumentación Programática):** Para evitar el sobreajuste (overfitting) y simular condiciones reales, a cada sello instanciado se le aplicó:
    *   **Rotación aleatoria:** Entre -45° y 45°.
    *   **Opacidad aleatoria:** Entre 45% y 90% (simulando "falta de tinta" o sellos deslavados).
    *   **Escalado dinámico:** Variación del tamaño según la resolución del documento base.
*   **Métricas de Producción:**
    *   Volumen generado: **200 tripletes de alta calidad**.
    *   Cada triplete consta de: `Imagen Compuesta (.png)`, `Etiqueta YOLO (.txt)` y `Máscara Binaria de Inpainting`.

---

## FASE 2: Detección con Deep Learning (YOLOv8)

**Objetivo:** Entrenar una red neuronal convolucional para localizar las coordenadas (Bounding Boxes) de los sellos en cualquier documento.

*   **Infraestructura:** Para evitar tiempos de entrenamiento insostenibles en CPU local (>2 horas), se empaquetó el dataset y se migró a **Google Colab utilizando una GPU Tesla T4**.
*   **Modelo Utilizado:** **YOLOv8-Nano** (`yolov8n.pt`). Se eligió la versión nano por su bajo peso computacional (inferencia en milisegundos), ideal para pipelines de procesamiento de documentos en masa. El modelo fue entrenado durante **50 épocas**.
*   **Métricas de Rendimiento (Resultados Finales):**
    *   **mAP50 (Mean Average Precision): 0.980 (98%)** — Capacidad casi perfecta para predecir correctamente la ubicación del sello.
    *   **Precisión (P): 0.995 (99.5%)** — Tasa extremadamente baja de falsos positivos (no confunde logos o texto denso con sellos).
    *   **Recall (R): 0.975 (97.5%)** — Localiza el 97.5% de todos los sellos presentes en la imagen.
    *   **Tiempo de Inferencia:** < 10ms por documento (GPU).

---

## FASE 3: Restauración de Documentos (Inpainting)

**Objetivo:** Dado el modelo YOLO entrenado, implementar el pipeline local capaz de inferir, generar máscaras en tiempo real y eliminar el sello del documento ("Borrado").

*   **Metodología de Inferencia:** Se cargó el peso `best.pt` localmente. El modelo predice las cajas y aplicamos un _padding_ (margen de seguridad) de 10 píxeles.
*   **Técnica de Computer Vision:** Se aplicó **Inpainting con el Algoritmo de Telea** (`cv2.INPAINT_TELEA`) provisto por OpenCV.
    *   _Cómo funciona:_ Es un método basado en gradientes (Fast Marching Method). El algoritmo analiza los píxeles en el límite exterior de la máscara (los píxeles limpios del fondo) y los propaga hacia adentro, rellenando la superficie del sello basándose en el color y la textura circundante.
*   **Experimento y Resultados:**
    *   Se probó con la imagen `syn_0001.png`.
    *   El modelo detectó el sello automáticamente.
    *   El algoritmo de Telea reconstruyó exitosamente la uniformidad del fondo (papel blanco).
    *   **Limitación Identificada:** Como Telea propaga información de los vecinos, si el sello está posicionado sobre una palabra, el sistema borra tanto el sello como la palabra (porque prioriza el blanco del papel circundante).

---

## CONCLUSIONES Y FASE 4 (Próximos Pasos)

El sistema base (Detección -> Limpieza) ha sido demostrado con éxito métrico y cualitativo. Para alcanzar la fiabilidad en producción y mejorar la lectura OCR:

1.  **Inpainting Consciente del Contexto (LaMa):** Reemplazar Telea por **Large Mask Inpainting** (basado en convoluciones de Fourier) para que el modelo "adivine" reconstrucciones de texto que hayan quedado parcialmente borradas.
2.  **Métricas Funcionales (CER/WER):** Someter los documentos a un motor OCR (PaddleOCR o Tesseract) y medir el _Character Error Rate (CER)_ **antes y después** de nuestro pipeline predictivo para cuantificar la mejora real de legibilidad.