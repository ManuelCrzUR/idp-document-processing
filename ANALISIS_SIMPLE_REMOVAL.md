# Análisis del Enfoque Simplificado de Eliminación del Sello

**Ejecutado**: 2026-05-25  
**Script**: `run_simple_removal.py`  
**Método**: Clasificación simple + Filtro horizontal

---

## 📊 Resultados de Ejecución

### Pipeline completado exitosamente ✓

```
Archivo original:    2550x3300 píxeles
ROI del sello:       900x700 píxeles (630,000 píxeles totales)
Bloques OCR:         145 bloques detectados
Confianza OCR:       0.83 promedio
```

---

## 🔍 Análisis Detallado

### PASO 1 y 2: Extracción y Clasificación

**Clasificación de píxeles en ROI:**
- TEXTO NEGRO:  69,928 píxeles (11.10%)
- FONDO BLANCO: 531,126 píxeles (84.31%)
- SELLO:        28,946 píxeles (4.59%)

```
Estado: ✓ Clasificación correcta
Interpretación:
  - El 84% del ROI es fondo blanco (correcto)
  - El 11% es texto legible (correcto)
  - El 4.6% es sello (detectado correctamente)
```

---

### PASO 3: Filtro Horizontal

**Resultado:**
- Filas sin texto: 268 de 700 (38.3%)
- Píxeles limpios: **61**
- Porcentaje del sello limpiado: **0.21%**

```
PROBLEMA IDENTIFICADO:
  Aunque 268 filas NO contienen texto detectado,
  la mayoría de ellas tampoco contienen píxeles de SELLO.
  
  Solo 61 de los 28,946 píxeles de sello estaban en esas filas.
  Por lo tanto, el filtro horizontal eliminó muy poco.
```

---

## ⚠️ Por Qué el Enfoque Simple No Fue Suficiente

### 1. Distribución del Sello

El sello rojo está distribuido de forma que:
- Muchos píxeles están en filas QUE TAMBIÉN contienen texto
- Pocas filas son PURAMENTE sello (sin texto)
- El filtro horizontal es conservador: solo limpia filas SIN TEXTO

**Resultado**: Solo 0.21% del sello fue eliminado

### 2. Conservadurismo del Filtro

El filtro horizontal fue diseñado para ser SEGURO (no dañar texto).
- Si una fila tiene UN SOLO píxel de texto → no toca nada
- El sello está parcialmente intercalado con texto
- Por lo tanto, casi ninguna fila es "pura sello"

---

## 🎯 Por Qué los 145 Bloques OCR se Detectaron

Aunque el sello NO fue eliminado visualmente, EasyOCR logró detectar 145 bloques:

1. **Sello no interfiere completamente con texto**: Aunque cubre parte, el texto es parcialmente legible
2. **EasyOCR es robusto**: Puede detectar texto parcialmente oscurecido
3. **Confianza moderada (0.83)**: No es tan alta como sería con documento limpio

---

## ✅ Imágenes Generadas

### Evidencia Visual del Proceso

| Archivo | Descripción | Resultado |
|---------|------------|----------|
| evidencia_01_roi_original.png | ROI del sello original | Sello visible con colores originales |
| evidencia_02_clasificacion_pixeles.png | Mapa de clasificación | Negro=texto, Rojo=sello, Blanco=fondo |
| evidencia_03_mascara_sello.png | Máscara binaria | Todos los píxeles clasificados como sello |
| evidencia_04_deteccion_texto.png | Píxeles de texto | Mapa en verde de dónde está el texto |
| evidencia_05_filtro_horizontal.png | Después del barrido | Solo 61 píxeles cambiados (casi idéntico a original) |
| evidencia_06_roi_limpio.png | ROI final | Esencialmente igual que evidencia_05 |
| evidencia_07_documento_final.png | Documento final | Sello AÚN VISIBLE (no se eliminó) |
| evidencia_08_ocr_resultado.png | Con bloques OCR | 145 bloques detectados (sello interferente pero detectado) |
| evidencia_09_comparacion.png | Comparación 3 columnas | original \| limpio \| OCR |

---

## 🔴 Problema Raíz

```
El filtro horizontal es DEMASIADO CONSERVADOR para este caso:
  
  ┌──────────────────────────────────────┐
  │ Fila: [TEXTO] [SELLO] [TEXTO]        │  → Mantiene intacta
  │ Fila: [FONDO] [SELLO] [FONDO]        │  → Elimina sello ✓
  │ Fila: [TEXTO] [SELLO] [SELLO]        │  → Mantiene intacta
  └──────────────────────────────────────┘
  
  Resultado: Solo las filas PURAMENTE sello se limpian
  Este sello está distribuido: 68 de 700 filas solo con sello
  Por eso solo se limpiaron 61 píxeles
```

---

## 💡 Soluciones Alternativas

### Opción A: Usar Inpainting (LaMa o OpenCV)
- **Ventaja**: Reconstruye automáticamente áreas marcadas
- **Costo**: Más computacionalmente intenso
- **Resultado esperado**: 70-90% del sello eliminado

### Opción B: Filtro Agregado
- **Idea**: Expandir máscara del sello + erosión/dilatación
- **Ventaja**: Elimina más píxeles mientras preserva texto
- **Costo**: Requiere tuning de parámetros

### Opción C: Modelo de Detección de Sello
- **Idea**: Entrenar modelo YOLO para detectar bordes del sello
- **Ventaja**: Preciso y robusto
- **Costo**: Requiere dataset de entrenamiento

### Opción D: Combinación de Técnicas
- Usar clasificación simple como aquí
- Pero aplicar morfología (dilatación) a la máscara de sello
- Luego usar OpenCV inpainting con radius mayor

---

## 📝 Conclusión

**Estado Actual:**
- ✓ Pipeline implementado y funcional
- ✓ Clasificación correcta de píxeles
- ✓ Filtro horizontal aplicado
- ✗ Sello NO fue eliminado (0.21% limpiezas insuficientes)

**Motivo:**
El filtro horizontal es conservador por diseño. El sello está distribuido
de forma que la mayoría de sus píxeles están en filas que contienen texto,
por lo que el filtro no los toca.

**Siguiente Paso Recomendado:**
Implementar inpainting básico (OpenCV con radio mayor) para reconstruir
las áreas marcadas como sello, incluso aquellas intercaladas con texto.

---

**Archivos generados**: 9 imágenes de evidencia en `output/prueba_completa/`
**Resultados OCR**: `output/prueba_completa/ocr_resultado_simple.json`
