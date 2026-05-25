# 📋 ANÁLISIS DEL FORMATO JSON - Phase 4 OCR

## Estructura Actual del JSON

```json
{
  "timestamp": "2026-05-25T10:30:45.123456",
  "imagen_size": {"width": 1200, "height": 1800},
  "seal_bbox": [0.5, 0.3, 0.2, 0.15],
  "texto_completo": "texto extraído...",
  "bloques": [
    {
      "id": 0,
      "texto_raw": "Ministerio",
      "texto_corregido": "Ministerio",
      "confianza": 0.9543,
      "motor": "EasyOCR",
      "coordenadas": [[10, 20], [110, 20], [110, 50], [10, 50]],
      "entidades": [
        {
          "texto": "Ministerio",
          "tipo": "ORG",
          "inicio": 0,
          "fin": 9
        }
      ]
    }
  ],
  "metricas": {
    "total_bloques": 45,
    "confianza_promedio": 0.8745,
    "palabras_corregidas": 3,
    "entidades_detectadas": 12,
    "motors_usados": ["EasyOCR"],
    "procesadores_usados": ["Levenshtein", "spaCy"]
  }
}
```

---

## 📊 RESPUESTAS A LAS PREGUNTAS

### 1️⃣ ¿Los bloques con baja confianza (< 0.6) están marcados?
**❌ NO** - Problema identificado

- El campo `confianza` existe pero **no hay flag que indique baja confianza**
- No hay forma de identificar rápidamente qué bloques son problemáticos
- Necesitamos agregar: `"baja_confianza": true/false` por bloque

### 2️⃣ ¿Se guardan confianza scores por bloque individual?
**✅ SÍ** - Esto está bien

```json
"confianza": 0.9543  // Por cada bloque
```

- Excelente para el análisis posterior
- Usaremos este campo para segmentar en recuperación

### 3️⃣ ¿Bloques en zona del sello están diferenciados?
**❌ NO** - Problema crítico

- El `seal_bbox` se almacena pero **nunca se usa para marcar bloques**
- No hay identificación de si el bloque está dentro del sello
- Necesitamos: `"en_zona_sello": true/false` y `"overlap_porcentaje": 0.45`

### 4️⃣ ¿texto_raw preserva palabras parciales sin modificar?
**✅ SÍ** - Esto está perfecto

```json
"texto_raw": "Ministeri",        // Original del OCR (puede estar dañado)
"texto_corregido": "Ministerio"  // Corregido por Levenshtein
```

- `texto_raw` es intacto (excelente para recuperación)
- `texto_corregido` tiene las correcciones
- Podemos detectar si hay diferencia: `texto_raw != texto_corregido` = fue corregido

---

## ⚠️ CONCLUSIÓN: FALTAN CAMPOS CRÍTICOS

El JSON actual **NO tiene todo lo necesario** para la recuperación inteligente. 

**Campos faltantes necesarios:**

| Campo | Dónde | Tipo | Propósito |
|-------|-------|------|-----------|
| `baja_confianza` | Por bloque | bool | Marcar confianza < 0.6 |
| `en_zona_sello` | Por bloque | bool | ¿Está en zona del sello? |
| `overlap_sello` | Por bloque | float | % de overlap con sello (0-1) |
| `palabras_parciales` | Por bloque | list | Índices de palabras con confianza baja |
| `fue_corregido` | Por bloque | bool | ¿Levenshtein modificó el texto? |
| `distancia_correccion` | Por bloque | float | Levenshtein distance usado |

---

## 🔧 CAMBIOS NECESARIOS A PHASE 4

### Cambio 1: Actualizar método `_extract_with_easyocr()`

Agregar cálculo de zona de sello:

```python
def _extract_with_easyocr(self, image, seal_bbox):
    """Extrae texto con EasyOCR"""
    h, w = image.shape[:2]
    bloques = []
    
    # Convertir seal_bbox normalizado a píxeles
    seal_x1, seal_y1, seal_x2, seal_y2 = self._bbox_normalized_to_pixels(seal_bbox, h, w)
    
    try:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        resultado = self.reader.readtext(image_rgb, detail=1)
        
        for idx, deteccion in enumerate(resultado):
            bbox, texto, confianza = deteccion
            coords = [[float(p[0]), float(p[1])] for p in bbox]
            
            # Calcular overlap con sello
            bloque_x1, bloque_y1 = min(p[0] for p in coords), min(p[1] for p in coords)
            bloque_x2, bloque_y2 = max(p[0] for p in coords), max(p[1] for p in coords)
            overlap = self._calculate_overlap(
                (bloque_x1, bloque_y1, bloque_x2, bloque_y2),
                (seal_x1, seal_y1, seal_x2, seal_y2)
            )
            
            bloque = {
                'id': idx,
                'texto_raw': texto.strip(),
                'texto_corregido': texto.strip(),
                'confianza': float(confianza),
                'baja_confianza': float(confianza) < self.confidence_threshold,
                'motor': 'EasyOCR',
                'coordenadas': coords,
                'en_zona_sello': overlap > 0,
                'overlap_sello': float(overlap),
                'entidades': [],
                'palabras_parciales': []  # Se llenará después
            }
            bloques.append(bloque)
    
    except Exception as e:
        print(f"[ERROR] EasyOCR falló: {e}")
        return []
    
    return bloques
```

### Cambio 2: Actualizar `_corregir_palabra()`

Registrar correcciones:

```python
def _corregir_palabra(self, palabra):
    """Corrige palabra y retorna (palabra_corregida, distancia_usada)"""
    if palabra in self.diccionario:
        return palabra, 0.0
    
    candidatos = []
    for palabra_dict in self.diccionario:
        dist = levenshtein(palabra.lower(), palabra_dict.lower())
        if dist <= self.max_levenshtein:
            candidatos.append((palabra_dict, float(dist)))
    
    if candidatos:
        candidatos.sort(key=lambda x: x[1])
        return candidatos[0][0], candidatos[0][1]  # palabra, distancia
    
    return palabra, float('inf')  # No se corrigió
```

### Cambio 3: Actualizar loop de corrección

Agregar metadata:

```python
for bloque in bloques:
    texto_original = bloque['texto_raw']
    palabras = texto_original.split()
    palabras_corregidas_bloque = []
    palabras_parciales = []
    distancia_total = 0.0
    
    for idx_palabra, palabra in enumerate(palabras):
        palabra_limpia = re.sub(r'[^\w]', '', palabra)
        
        if len(palabra_limpia) >= self.min_word_length and palabra_limpia.isalpha():
            palabra_corregida, distancia = self._corregir_palabra(palabra_limpia)
            
            if palabra_corregida != palabra_limpia:
                palabras_corregidas += 1
                # Si baja confianza, marcar como parcial
                if bloque['baja_confianza']:
                    palabras_parciales.append({
                        'indice': idx_palabra,
                        'original': palabra_limpia,
                        'corregida': palabra_corregida,
                        'distancia': distancia
                    })
            
            if distancia != float('inf'):
                distancia_total += distancia
            
            palabras_corregidas_bloque.append(palabra_corregida)
        else:
            palabras_corregidas_bloque.append(palabra)
    
    bloque['texto_corregido'] = ' '.join(palabras_corregidas_bloque)
    bloque['fue_corregido'] = bloque['texto_raw'] != bloque['texto_corregido']
    bloque['distancia_correccion'] = distancia_total
    bloque['palabras_parciales'] = palabras_parciales
```

---

## 📐 ESTRUCTURA JSON MEJORADA

```json
{
  "timestamp": "2026-05-25T10:30:45.123456",
  "imagen_size": {"width": 1200, "height": 1800},
  "seal_bbox": [0.5, 0.3, 0.2, 0.15],
  "texto_completo": "texto extraído...",
  "bloques": [
    {
      "id": 0,
      "texto_raw": "Ministeri",              // ← Original intacto
      "texto_corregido": "Ministerio",      // ← Corregido
      "confianza": 0.45,
      "baja_confianza": true,               // ← NUEVO: Fácil identificación
      "motor": "EasyOCR",
      "coordenadas": [[10, 20], [110, 20], [110, 50], [10, 50]],
      "en_zona_sello": true,                // ← NUEVO: ¿Está en sello?
      "overlap_sello": 0.75,                // ← NUEVO: % de overlap
      "fue_corregido": true,                // ← NUEVO: ¿Fue modificado?
      "distancia_correccion": 1.0,          // ← NUEVO: Levenshtein distance
      "palabras_parciales": [               // ← NUEVO: Para recuperación
        {
          "indice": 0,
          "original": "Ministeri",
          "corregida": "Ministerio",
          "distancia": 1.0
        }
      ],
      "entidades": [
        {"texto": "Ministerio", "tipo": "ORG", "inicio": 0, "fin": 9}
      ]
    }
  ],
  "metricas": {
    "total_bloques": 45,
    "bloques_baja_confianza": 5,            // ← NUEVO
    "bloques_en_zona_sello": 8,             // ← NUEVO
    "confianza_promedio": 0.8745,
    "palabras_corregidas": 3,
    "entidades_detectadas": 12,
    "motors_usados": ["EasyOCR"],
    "procesadores_usados": ["Levenshtein", "spaCy"]
  }
}
```

---

## ✅ RECOMENDACIÓN FINAL

**Implementar estos cambios ANTES de Phase 4B:**

1. ✅ Modificar `phase_4_ocr_complete.py` con los 3 cambios listados
2. ✅ Agregar helpers: `_bbox_normalized_to_pixels()` y `_calculate_overlap()`
3. ✅ Aumentar metadata en `metricas`
4. ✅ Agregar logging de bloques problemáticos
5. ✅ Validar que el JSON tenga todos los campos nuevos

**Después, implementar Phase 4B con:**
- Acceso directo a `bloques_baja_confianza` y `bloques_en_zona_sello`
- Iteración sobre `palabras_parciales` para BERT
- Identificación de huecos completos (confianza < 0.3)
- Llamadas a GPT-4o-mini para recuperación

---

**Costo de cambio:** ~50 líneas de código  
**Ganancia:** Información perfecta para Phase 4B text recovery  
**Status:** LISTO PARA IMPLEMENTAR
