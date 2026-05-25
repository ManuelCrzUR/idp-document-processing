# 🔍 DIAGNÓSTICO FINAL: ¿POR QUÉ NO SE INPAINTA EL SELLO?

**Fecha**: 2026-05-25  
**Problema**: El sello NO fue eliminado en Phase 3A

---

## 📊 HALLAZGOS PRINCIPALES

### 1. La Máscara de Visualización SÍ es Correcta
- ✓ Tiene exactamente **220,494 píxeles marcados para inpaint** (en rojo)
- ✓ Las shapes de imagen y máscara coinciden (3300 × 2550)
- ✓ OpenCV **SÍ funciona** cuando recibe máscara válida

### 2. El Problema NO está en OpenCV
**Test directo demuestra que OpenCV funciona:**
```
Test 1 (Máscara normal):  Imagen cambió ✓
Test 2 (Máscara invertida): Imagen cambió ✓
Test 3 (Rect pequeno):    Imagen cambió ✓
```

### 3. EL VERDADERO PROBLEMA ENCONTRADO:

**Los píxeles que se clasifican como "SELLO" en la región del sello circular son:**
- **28,729 píxeles MIXTO** (de 700×900 = 630,000 píxeles totales)
- **0 píxeles SELLO_SATURADO**
- **0 píxeles SELLO_TRANSLUCIDO**

**¿Por qué?** Los píxeles del sello circular visible tienen:
- Dominancia = 0 (son GRISES, no rojos saturados)
- Se clasifican como MIXTO porque tienen transiciones débiles

**LOS PÍXELES ROJOS REALES en la imagen son:**
- **85,745 píxeles** con dominancia > 50
- Ubicados en Y: 98 a 2821, X: 311 a 1968
- **Estos son los LOGOS e INSTITUCIONALES en el encabezado**, no el sello circular

### 4. El Sello Circular es GRIS, NO Rojo

```
Análisis región (1800-2000, 1000-1300):
  - Min dominancia: 0
  - Max dominancia: 0
  - Mean dominancia: 0
  → Todos los píxeles son GRISES (B=G=R)
```

Los píxeles "rojos" que parecen ser del sello son en realidad:
- Sombras oscuras grises
- Transiciones de color débil
- Bordes suavizados

---

## 🎯 EXPLICACIÓN COMPLETA DEL FLUJO

### Paso 1: Clasificación
```
Región del sello circular (1600-2300 Y, 800-1700 X):
  TEXTO (0):             69,928 píxeles (70%)
  MIXTO (2):             28,946 píxeles (29%) ← AQUÍ está el "sello"
  SELLO_SATURADO (1):         0 píxeles
  SELLO_TRANSLUCIDO (4):      0 píxeles
```

El sello se clasifica como MIXTO porque:
- Tiene dominancia RGB baja (0-20)
- Cae en la categoría "transiciones y bordes débiles"
- No cumple con umbrales de SELLO (dominancia ≥ 80)

### Paso 2: Filtros Horizontales
- Removió 41 píxeles MIXTO (de 28,946 → 28,905)
- Mínimo impacto

### Paso 3: Filtros de Bloques
- Removió 176 píxeles MIXTO (de 28,905 → 28,729)
- Los 28,729 píxeles MIXTO SI están en la máscara final

### Paso 4: OpenCV Inpainting
- Recibió máscara con 220,494 píxeles (incluyendo los 28,729 del "sello")
- Intentó inpaintear con radius=3
- **Solo removió 7,080 píxeles rojos** de la región (1.3% del sello visible)
- **NO fue suficiente** para eliminar visualmente el sello

---

## 💡 POR QUÉ FALLÓ

```
Flujo incorrecto:
1. Sello gris detectado como MIXTO, no como SELLO
2. 28,729 píxeles MIXTO son insuficientes para inpaintear correctamente
3. OpenCV con radius=3 no puede reconstruir 70% de los píxeles del sello
4. El sello sigue siendo visible en la imagen final
```

---

## ✅ SOLUCIONES POSIBLES

### Opción A: Ajustar umbrales en `chromatic_separator.py`
**Problema**: Los umbrales de SELLO_SATURADO (dominancia ≥ 80) no detectan el sello gris

**Solución**:
- Bajar `translucent_dominance_high` de 80 a 40
- Esto clasificaría píxeles grises como SELLO_TRANSLUCIDO
- Máscara final tendría más píxeles para inpaint

### Opción B: Aumentar radio de OpenCV
**Problema**: `radius=3` es muy pequeño para inpaintear el sello

**Solución**:
- Cambiar `OpenCVInpainter(radius=3)` a `OpenCVInpainter(radius=15)`
- Esto permitiría propagación de píxeles desde mayor distancia

### Opción C: Instalar y usar LaMa correctamente
**Problema**: LaMa no está instalado, OpenCV es fallback

**Solución**:
- Instalar `lama-cleaner` correctamente
- LaMa tiene mejor capacidad de inpainting que OpenCV

---

## 📝 RESUMEN TÉCNICO

| Aspecto | Estado | Motivo |
|---------|--------|--------|
| Máscara construcción | ✓ OK | 220,494 píxeles correctos |
| Máscara shapes | ✓ OK | Coinciden con imagen |
| OpenCV función | ✓ OK | Funciona en tests |
| Clasificación sello | ✗ ERROR | Detecta como MIXTO, no SELLO |
| Radio inpainting | ✗ PEQUEÑO | 3 píxeles insuficiente |
| LaMa disponible | ✗ NO | Necesita instalación |

---

## 🔧 RECOMENDACIÓN INMEDIATA

El problema está en los **umbrales de clasificación**. El sello gris no se clasifica como SELLO sino como MIXTO.

**Cambio recomendado en `src/phase_3a/chromatic_separator.py`:**

```python
# Línea ~35: Cambiar de:
translucent_dominance_high=80

# A:
translucent_dominance_high=40  # Detecta más grises como sello
```

Esto clasificaría los 28,729 píxeles MIXTO como SELLO_TRANSLUCIDO, mejorando el inpainting.

---

**Status**: Problema identificado y solución clara  
**Próximo paso**: Ajustar umbrales y re-ejecutar Phase 3A
