# 📊 Phase 4 OCR - Enriquecimiento del JSON

## ✅ CAMBIOS IMPLEMENTADOS

Se han implementado exitosamente los **3 cambios principales** en `phase_4_ocr_complete.py` para enriquecer el JSON de salida con información crítica para recuperación de texto.

---

## 🔄 CAMBIO 1: Cálculo de Overlap con Sello

**Archivo:** `src/pipeline/phase_4_ocr_complete.py`

**Métodos agregados:**
- `_bbox_normalized_to_pixels()`: Convierte bounding box normalizado a píxeles
- `_calculate_overlap()`: Calcula porcentaje de overlap entre dos bboxes

**En `_extract_with_easyocr()`:**
```python
# Ahora recibe: seal_bbox, h, w
def _extract_with_easyocr(self, image, seal_bbox, h, w):
    # Convierte seal_bbox a píxeles
    seal_x1, seal_y1, seal_x2, seal_y2 = self._bbox_normalized_to_pixels(seal_bbox, h, w)
    
    # Para cada bloque OCR:
    overlap = self._calculate_overlap(
        (bloque_x1, bloque_y1, bloque_x2, bloque_y2),
        (seal_x1, seal_y1, seal_x2, seal_y2)
    )
    
    # Agregar campos al bloque:
    bloque['baja_confianza'] = confianza < 0.6
    bloque['en_zona_sello'] = overlap > 0.0
    bloque['overlap_sello'] = overlap  # 0-1
```

**Nuevos campos en cada bloque:**
- `baja_confianza`: bool - True si confianza < 0.6
- `en_zona_sello`: bool - True si hay overlap con sello
- `overlap_sello`: float - Porcentaje de overlap (0-1)

---

## 🔄 CAMBIO 2: Distancia Levenshtein en Correcciones

**Método `_corregir_palabra()` modificado:**

```python
def _corregir_palabra(self, palabra):
    """Ahora retorna tupla (palabra_corregida, distancia)"""
    if palabra in self.diccionario:
        return palabra, 0.0
    
    # Busca y retorna (palabra, distancia)
    # Si no se corrige: retorna (palabra_original, inf)
```

**Cambio de retorno:**
- Antes: `return palabra_corregida`
- Ahora: `return palabra_corregida, distancia_levenshtein`

---

## 🔄 CAMBIO 3: Metadata de Correcciones por Bloque

**En el loop de corrección (PASO 2):**

```python
for bloque in bloques:
    texto_original = bloque['texto_raw']
    palabras_parciales = []  # Registro de correcciones
    distancia_total = 0.0
    
    for idx_palabra, palabra in enumerate(palabras):
        palabra_corregida, distancia = self._corregir_palabra(palabra)
        
        if palabra_corregida != palabra:
            # Registrar si está en zona problemática
            if bloque['baja_confianza'] or bloque['en_zona_sello']:
                palabras_parciales.append({
                    'indice': idx_palabra,
                    'original': palabra,
                    'corregida': palabra_corregida,
                    'distancia': distancia
                })
```

**Nuevos campos por bloque:**
- `palabras_parciales`: list - Palabras corregidas en zonas problemáticas
- `fue_corregido`: bool - ¿El bloque fue modificado?
- `distancia_correccion`: float - Suma de distancias Levenshtein

---

## 📋 ESTRUCTURA COMPLETA DEL JSON ENRIQUECIDO

```json
{
  "timestamp": "2026-05-25T14:30:45.123456",
  "imagen_size": {"width": 1200, "height": 1800},
  "seal_bbox": [0.5, 0.3, 0.2, 0.15],
  "texto_completo": "Ministerio de Economía...",
  
  "bloques": [
    {
      "id": 0,
      "texto_raw": "Ministeri",              // ← Original intacto
      "texto_corregido": "Ministerio",      // ← Corregido
      "confianza": 0.45,
      "baja_confianza": true,               // ✨ NUEVO
      "motor": "EasyOCR",
      "coordenadas": [[10, 20], [110, 20], [110, 50], [10, 50]],
      "en_zona_sello": true,                // ✨ NUEVO
      "overlap_sello": 0.75,                // ✨ NUEVO (0-1)
      "fue_corregido": true,                // ✨ NUEVO
      "distancia_correccion": 1.0,          // ✨ NUEVO
      "palabras_parciales": [               // ✨ NUEVO
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
    "bloques_baja_confianza": 5,            // ✨ NUEVO
    "bloques_en_zona_sello": 8,             // ✨ NUEVO
    "confianza_promedio": 0.8745,
    "palabras_corregidas": 3,
    "entidades_detectadas": 12,
    "confidence_threshold": 0.6,
    "motors_usados": ["EasyOCR"],
    "procesadores_usados": ["Levenshtein", "spaCy"]
  }
}
```

---

## 🧪 VALIDACIÓN DEL JSON

Se proporciona **`validate_phase4_json.py`** para validar la estructura:

```bash
python src/pipeline/validate_phase4_json.py ocr_results/syn_0000_ocr_completo.json
```

**Salida esperada:**
```
✅ JSON VÁLIDO - Todos los campos están presentes y correctos

📊 Estructura verificada:
   - Timestamp: 2026-05-25T14:30:45.123456
   - Imagen: {'width': 1200, 'height': 1800}
   - Bloques totales: 45
   - Bloques baja confianza: 5
   - Bloques en zona sello: 8
```

---

## 🚀 PHASE 4B - TEXT RECOVERY

### Módulo: `phase_4b_text_recovery.py`

Implementa recuperación de texto usando:

#### 1️⃣ BETO (dccuchile/bert-base-spanish-wwm-cased)
**Para:** Palabras parciales en zona de sello con confianza 0.3-0.6

**Estrategia:**
- Marca palabra dañada con `[MASK]`
- BETO predice palabra más probable del contexto
- Mantiene coherencia lingüística

```python
# Ejemplo:
Texto: "Ministeri de Econom[MASK]a"
BETO predice: "Economía"
```

#### 2️⃣ GPT-4o-mini
**Para:** Huecos completos (sin texto) en zona de sello con confianza < 0.3

**Estrategia:**
- Proporciona contexto del párrafo completo
- Sistema prompt indica documento legal español
- GPT predice contenido más probable

```python
# Ejemplo:
Contexto: "En cumplimiento de lo establecido por la ley [HUECO]..."
GPT predice: "22/2015"
```

### Uso:

```python
from src.pipeline.phase_4_ocr_complete import phase_4_ocr_complete
from src.pipeline.phase_4b_text_recovery import phase_4b_text_recovery

# Phase 4: OCR
ocr_json = phase_4_ocr_complete(clean_image, seal_bbox)

# Phase 4B: Recuperación
recovered_json = phase_4b_text_recovery(
    ocr_json,
    confidence_partial=0.6,  # Threshold para BETO
    confidence_empty=0.3      # Threshold para GPT
)

# Resultado tiene:
# - bloque['texto_recuperado']: Texto recuperado
# - bloque['metodo_recuperacion']: 'BETO' o 'GPT-4o-mini'
# - bloque['recuperaciones']: Detalles de cambios
```

---

## 📊 CAMPOS NUEVOS EN JSON RECUPERADO

```json
{
  "bloques": [
    {
      // ... campos anteriores ...
      
      // ✨ Phase 4B
      "texto_recuperado": "Ministerio de Economía",  // NUEVO
      "metodo_recuperacion": "BETO",                 // NUEVO
      "recuperaciones": [                            // NUEVO
        {
          "original": "Ministeri",
          "recuperada": "Ministerio",
          "confidence": 0.92,
          "metodo": "BETO"
        }
      ]
    }
  ],
  
  "metricas": {
    // ... campos anteriores ...
    "bloques_recuperados_beto": 3,      // ✨ NUEVO
    "bloques_recuperados_gpt": 2        // ✨ NUEVO
  }
}
```

---

## 📈 FLUJO COMPLETO

```
Imagen OCR Original (con sello)
        ↓
┌─────────────────────────────┐
│ Phase 3A: Removedor Sellos  │
│ (chromatic + inpainting)    │
└─────────────────────────────┘
        ↓
Imagen Limpia
        ↓
┌─────────────────────────────┐
│ Phase 4: OCR + Corrección   │
│ (EasyOCR + Levenshtein)     │
├─────────────────────────────┤
│ JSON ENRIQUECIDO CON:       │
│ - baja_confianza            │
│ - en_zona_sello             │
│ - overlap_sello             │
│ - palabras_parciales        │
│ - fue_corregido             │
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│ Phase 4B: Recuperación      │
│ - BETO (palabras parciales) │
│ - GPT-4o-mini (huecos)      │
└─────────────────────────────┘
        ↓
JSON FINAL CON TEXTO RECUPERADO
```

---

## ✨ VENTAJAS DEL ENRIQUECIMIENTO

✅ **Identificación Clara** de bloques problemáticos  
✅ **Trazabilidad Completa** de qué se corrigió y por qué  
✅ **Información de Ubicación** respecto al sello  
✅ **Confianza por Corrección** para validar recuperaciones  
✅ **Contexto para IA** (BETO/GPT) para predicciones mejores  
✅ **Métricas de Éxito** para medir efectividad de recuperación  

---

## 🔍 TESTING

Para validar los cambios:

```python
# 1. Ejecutar Phase 4
result = phase_4_ocr_complete(clean_image, seal_bbox)

# 2. Validar JSON enriquecido
from src.pipeline.validate_phase4_json import Phase4JSONValidator
es_válido = Phase4JSONValidator.print_validation_report(result)

# 3. Ejecutar Phase 4B
if es_válido:
    recovered = phase_4b_text_recovery(result)
    print(f"Bloques recuperados: {recovered['metricas']['bloques_recuperados_beto']}")
```

---

## 📝 RESUMEN DE CAMBIOS

| Aspecto | Antes | Ahora |
|--------|-------|-------|
| Identificación baja confianza | No había | Flag `baja_confianza` |
| Zona de sello identificada | No se usaba | Flags `en_zona_sello` + `overlap_sello` |
| Distancia de corrección | No registrada | Campo `distancia_correccion` |
| Palabras parciales | No se registraban | Lista `palabras_parciales` |
| Campos por bloque | 8 | **13** (+5 nuevos) |
| Capacidad de recuperación | No | Sí (BETO + GPT) |

---

**Status:** ✅ Listo para Phase 4B  
**Próximo Paso:** Implementar y validar recuperación de textos en imágenes de prueba
