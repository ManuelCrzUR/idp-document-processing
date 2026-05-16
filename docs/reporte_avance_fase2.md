# Reporte de Avance: Sistema de Limpieza y Detección de Sellos (Fase 1 & 2)
## Manuel Cruz Garrote - Proyecto de Grado
### Fecha: 8 de Abril de 2026

---

## ESTRUCTURA DE LA PRESENTACIÓN (Slide by Slide)

### Slide 1: Portada y Contexto
*   **Título:** Optimización del Pipeline de Procesamiento Inteligente de Documentos (IDP).
*   **Subtítulo:** Fase 2: Detección Robusta de Sellos mediante Deep Learning (YOLOv8).
*   **Contenido:**
    *   Nombre del Autor.
    *   Estado del Proyecto: Transición de Métodos Heurísticos a Deep Learning.
    *   Objetivo: Garantizar la eliminación precisa de elementos obstructivos (sellos) para mejorar el OCR downstream.

### Slide 2: El Problema - Limitaciones de la Heurística (Fase 0)
*   **Título:** El Desafío de la Variabilidad Cromática.
*   **Contenido:**
    *   **Metodología Anterior:** Basada en Umbralización HSV (Espacio de Color).
    *   **Puntos de Falla Detectados:** 
        *   Falla en sellos con baja saturación (grises o deslavados).
        *   Falsos positivos en fondos con ruido o texturas similares.
        *   Dificultad para manejar fondos no blancos (documentos escaneados con sombras).
    *   **Estadística de Error Inicial:** ~6% de fallas críticas en la extracción de máscaras (92/1557 muestras).

### Slide 3: Solución Implementada - El Pipeline Híbrido de Limpieza
*   **Título:** Refinamiento de Datos: "Prepare Stamps".
*   **Contenido:**
    *   **Innovación:** Implementación de un filtro doble (Luminancia + Saturación HSV).
    *   **Técnica:** Operaciones morfológicas de "Opening" para eliminar ruido de bordes.
    *   **Resultado:** Reducción del error del 6% al **0.5%** (solo 9 fallas en 1,557 imágenes).
    *   **Visual:** Mostrar el proceso de convertir un sello escaneado sucio a una base RGBA transparente perfecta.

### Slide 4: Generación de Dataset Sintético (Fase 1)
*   **Título:** Superando la Escasez de Datos Etiquetados.
*   **Contenido:**
    *   **Estrategia:** Composición programática de documentos reales (SpanishOCR) + Sellos Limpios.
    *   **Aumentación en Vuelo:**
        *   Rotación aleatoria (-45° a 45°).
        *   Opacidad variable (45% a 90%) para simular tintas reales.
        *   Escalado dinámico.
    *   **Producto Final:** Generación de 200 tripletes (Imagen, Etiqueta YOLO, Máscara de Inpainting).

### Slide 5: Entrenamiento en la Nube (Fase 2)
*   **Título:** Potencia de Cómputo y Eficiencia.
*   **Contenido:**
    *   **Infraestructura:** Migración a Google Colab (Tesla T4 GPU).
    *   **Modelo:** YOLOv8-Nano (Ligero y de alta velocidad).
    *   **Configuración:** 50 épocas de entrenamiento.
    *   **Resolución de Conflictos:** Ajuste de sistemas de archivos (Windows -> Linux) y normalización de rutas YAML.

### Slide 6: Resultados del Modelo (Métricas en Tiempo Real)
*   **Título:** Análisis de Performance del Detector.
*   **Contenido:**
    *   **mAP50:** **0.98 (98%)** — Precisión casi perfecta en localización.
    *   **Precisión (P):** **0.99** — Prácticamente cero falsos positivos.
    *   **Recall (R):** **0.97** — El modelo encuentra el 97% de los sellos presentes.
    *   **Conclusión:** El modelo es altamente robusto para entornos controlados de documentos administrativos españoles.

### Slide 7: Análisis de Metodología Académica
*   **Título:** Alineación con el Plan Técnico.
*   **Contenido:**
    *   **Cumplimiento:** Se ha cumplido rigurosamente el pipeline secuencial propuesto inicialmente.
    *   **Ajuste Metodológico:** Se decidió reemplazar la detección puramente basada en color por una detección basada en **Deep Learning (YOLO)** debido a la superioridad en la generalización de formas.
    *   **Impacto esperado:** La precisión del 98% en detección garantiza que la siguiente fase (Inpainting/Borrado) no afecte zonas de texto limpio.

### Slide 8: Próximos Pasos (Fase 3 & 4)
*   **Título:** Hacia la Restauración Total del Documento.
*   **Contenido:**
    *   **Inmediato:** Implementación del pipeline de **Inpainting Selectivo** usando las coordenadas de YOLO.
    *   **Siguiente:** Testeo de OCR (PaddleOCR) comparando: 
        1. Documento Original (con sello).
        2. Documento Restaurado (sin sello).
    *   **Meta Final:** Lograr la mejora del >5% en la lectura de campos clave obstruidos.

---

## NOTAS TÉCNICAS PARA LA PRESENTACIÓN

1.  **Enfoque en el Cambio de Estrategia:** Es vital mencionar cómo el análisis de los 92 fallos iniciales nos llevó a mejorar el script `prepare_stamps.py`, lo cual fue el "combustible" de alta calidad para el éxito del modelo YOLO.
2.  **Métricas de Tiempo:** El entrenamiento tomó solo ~9 minutos en GPU frente a la estimación original de >2 horas en CPU local.
3.  **Arquitectura:** El uso de YOLOv8n asegura que el sistema pueda ejecutarse en servidores modestos o incluso navegadores en el futuro.
