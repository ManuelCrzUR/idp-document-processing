# 📅 Proyecto IDP - Versión Reducida (Estudiante que Trabaja)
## Universidad del Rosario - Proyecto de Grado

**Estudiante:** Manuel Cruz  
**Contexto:** Estudio + Trabajo  
**Tiempo disponible:** 15-18 horas/semana  
**Duración:** 16 semanas (Feb 5 - May 30)  
**Meta realista:** **7.5/10** (Muy Bueno) ✅

---

## 🎯 FILOSOFÍA DEL PROYECTO REDUCIDO

### **Cambios vs Plan Original:**

| Aspecto | Plan Original | Plan Reducido |
|---------|---------------|---------------|
| **Horas/semana** | 29h | **15-18h** ✅ |
| **Horas/día** | 5-6h | **2-3h** ✅ |
| **Nota objetivo** | 9.0-10.0 | **7.5** ✅ |
| **Checkpoints** | 5 (CP0-CP4) | **3 esenciales** (CP0-CP2) + CP3 |
| **Dataset sellos** | 100+ | **50** ✅ |
| **Features** | Todas | **Solo core** ✅ |
| **Fin de semana** | 4h | **0h** (descanso total) ✅ |

### **Principio clave:**
> **"Mejor un 7.5 bien hecho que un 9.0 mediocre por burnout"**

---

## 📊 ESTRUCTURA DE CHECKPOINTS REDUCIDA

| CP | Semanas | Horas Total | Entregable | Nota Acum. |
|----|---------|-------------|-----------|------------|
| **CP0** | 1-2 | 30h | Dataset + Setup | 1.0 |
| **CP1** | 3-5 | 48h | Preprocesamiento + OCR básico | **3.5** ✅ APROBADO |
| **CP2** | 6-9 | 64h | Inpainting funcional | **6.0** |
| **CP3** | 10-12 | 45h | Validación y resultados | **7.5** ⭐ MUY BUENO |
| **BUFFER** | 13-14 | 30h | Documentación final | - |
| **CIERRE** | 15-16 | 30h | Presentación | - |
| **TOTAL** | **16 sem** | **~247h** | | **7.5** |

**Promedio: 15.4 horas/semana** ✅ Sostenible

---

## 🔥 LO QUE SE DESCARTÓ (Para Ahorrar Tiempo)

### ❌ **NO haremos:**
1. Layout Analysis (ahorra ~25h)
2. Extracción de Tablas (ahorra ~30h)
3. Extracción de Gráficas (ahorra ~30h)
4. QA Semántico con RAG (ahorra ~20h)
5. Paper IEEE completo (solo informe académico)
6. Demo en cloud (solo demo local)

### ✅ **SÍ haremos (esencial):**
1. Preprocesamiento robusto
2. OCR dual (Tesseract + PaddleOCR)
3. **Detección + Inpainting de Sellos** (diferenciador)
4. Validación en SROIE
5. Documentación académica completa

---

## 📅 CRONOGRAMA REDUCIDO (16 SEMANAS)

---

# CHECKPOINT 0: SETUP (1.0 punto)

## 🗓️ SEMANAS 1-2: Feb 5-18 (30 horas total)

### **Objetivo:** Dataset mínimo + infraestructura

### **Semana 1: Feb 5-11 (15 horas)**

#### **Lunes 5 Feb (HOY) - 2h:**
- [ ] **17:00-19:00** (después del trabajo)
  - Crear repo GitHub
  - Leer evaluación del proyecto
  - Escribir email para acceso GPU

#### **Martes 6 Feb - 2h:**
- [ ] **19:00-21:00**
  - Descargar SROIE dataset
  - Setup Python + virtualenv

#### **Miércoles 7 Feb - 3h:**
- [ ] **18:00-21:00**
  - Investigar 5 papers clave (solo abstract + intro)
  - Crear documento de "Problema" (1-2 páginas, no 4)

#### **Jueves 8 Feb - 2h:**
- [ ] **10:00-11:00** 🎤 Reunión con asesor
- [ ] **19:00-20:00** Análisis exploratorio SROIE (básico)

#### **Viernes 9 Feb - 3h:**
- [ ] **18:00-21:00**
  - Web scraping: 25 imágenes con sellos (no 50)
  - Commit semanal

#### **Fin de semana: OFF** 🏖️

---

### **Semana 2: Feb 12-18 (15 horas)**

#### **Lunes 12 Feb - 3h:**
- [ ] **18:00-21:00**
  - Instalar LabelImg
  - Anotar 10 sellos

#### **Martes 13 Feb - 3h:**
- [ ] **19:00-22:00**
  - Anotar 15 sellos más (total: 25)

#### **Miércoles 14 Feb - 2h:**
- [ ] **19:00-21:00**
  - Data augmentation simple (rotación, flip)
  - 25 reales → 50 totales

#### **Jueves 15 Feb - 2h:**
- [ ] **10:00-11:00** 🎤 Reunión con asesor
- [ ] **19:00-20:00** Documentar dataset

#### **Viernes 16 Feb - 3h:**
- [ ] **18:00-21:00**
  - Split: train/val/test
  - Confirmar GPU access
  - 🎯 **ENTREGA CP0**

#### **Fin de semana: OFF** 🏖️

---

### ✅ **ENTREGABLES CP0 (antes del 18 Feb):**
- [x] Repo GitHub básico
- [x] Dataset: 50 sellos anotados (no 100)
- [x] SROIE descargado
- [x] GPU access confirmado
- [x] Documento de problema (1-2 pág)

**Nota acumulada: 1.0/10**

---

# CHECKPOINT 1: MVP BÁSICO (2.5 puntos)

## 🗓️ SEMANAS 3-5: Feb 19 - Mar 11 (48 horas total)

### **Objetivo:** Preprocesamiento + OCR funcional

### **Alcance REDUCIDO:**
- ✅ Corrección de rotación (OpenCV)
- ✅ Binarización (Otsu)
- ✅ OCR dual (Tesseract + PaddleOCR)
- ❌ NO: Corrección de perspectiva (ahorra 8h)
- ❌ NO: Denoising avanzado (solo básico)

---

### **Semana 3: Feb 19-25 (16 horas)**

**Lunes a Viernes (3h/día × 5 = 15h):**
- Implementar rotación + binarización
- Wrapper de Tesseract
- Tests básicos

**Viernes - Checkpoint:**
- [ ] **19:00-20:00** Commit + revisión semanal

---

### **Semana 4: Feb 26 - Mar 4 (16 horas)**

**Lunes a Viernes (3h/día × 5 = 15h):**
- Wrapper de PaddleOCR
- Estrategia de fallback
- Benchmarking en 50 muestras SROIE (no 100)

**Jueves - Reunión:**
- [ ] **10:00-11:00** 🎤 Asesor: Demo preprocesamiento

---

### **Semana 5: Mar 5-11 (16 horas)**

**Lunes a Viernes (3h/día × 5 = 15h):**
- Integrar preprocesamiento + OCR
- Pipeline v1 (simple, sin Docker por ahora)
- Documentación básica

**Viernes - Entrega:**
- [ ] **20:00-21:00** 🎯 **ENTREGA CP1**

---

### ✅ **ENTREGABLES CP1 (antes del 11 Mar):**
- [x] Rotación + Binarización funcional
- [x] OCR dual (Tesseract + Paddle)
- [x] Pipeline v1 (script Python simple)
- [x] Accuracy >70% en SROIE (subset 50 muestras)
- [x] Código en GitHub con README

**Nota acumulada: 3.5/10** ✅ **APROBADO**

---

# CHECKPOINT 2: INPAINTING (2.5 puntos)

## 🗓️ SEMANAS 6-9: Mar 12 - Apr 8 (64 horas total)

### **Objetivo:** Detección + Inpainting de sellos validado

### **Alcance REDUCIDO:**
- ✅ Detector simple (color-based, no YOLO fine-tuning)
- ✅ LaMa inpainting (pre-trained, no custom training)
- ✅ Validación en 30 imágenes (no 50)

---

### **Semana 6: Mar 12-18 (16 horas)**

**Tareas (3h/día × 5):**
- Implementar detector basado en HSV
- Crear máscaras de sellos
- Tests en 10 imágenes

**Jueves:**
- [ ] **10:00-11:00** 🎤 Asesor: Validar enfoque

---

### **Semana 7: Mar 19-25 (16 horas)**

**Tareas:**
- Instalar LaMa (usar repo oficial)
- Implementar wrapper básico
- Testear inpainting en 5 ejemplos

---

### **Semana 8: Mar 26 - Apr 1 (16 horas)**

**Tareas:**
- Integrar detector + inpainting
- Pipeline v2 completo
- **Experimento crítico:** OCR Before/After en 30 imágenes

**Jueves:**
- [ ] **10:00-11:00** 🎤 Asesor: Mostrar resultados

---

### **Semana 9: Apr 2-8 (16 horas)**

**Tareas:**
- Análisis de resultados (¿mejora >5%?)
- Documentar experimento
- Refinar código

**Viernes - Entrega:**
- [ ] **20:00-21:00** 🎯 **ENTREGA CP2**

---

### ✅ **ENTREGABLES CP2 (antes del 8 Apr):**
- [x] Detector de sellos (method simple, color-based)
- [x] LaMa inpainting integrado
- [x] Pipeline v2 funcional
- [x] **Mejora OCR >5%** validada en 30 samples
- [x] Reporte de experimento (3-5 páginas)

**Nota acumulada: 6.0/10** ✅ **BUENO**

---

# CHECKPOINT 3: VALIDACIÓN (1.5 puntos)

## 🗓️ SEMANAS 10-12: Apr 9 - Apr 29 (45 horas total)

### **Objetivo:** Validación científica + Documentación

### **Alcance REDUCIDO:**
- ✅ Benchmark en SROIE (subset 100 imágenes, no completo)
- ✅ Comparar con 1 baseline (solo Tesseract)
- ✅ Documentación académica esencial

---

### **Semana 10: Apr 9-15 (15 horas)**

**Tareas (3h/día × 5):**
- Correr pipeline en 100 muestras SROIE
- Calcular métricas (CER, WER, F1)
- Comparar con Tesseract solo

---

### **Semana 11: Apr 16-22 (15 horas)**

**Tareas:**
- Análisis de errores (cualitativo)
- Redactar Metodología (5-7 páginas)
- Empezar Estado del Arte (5-7 páginas)

**Jueves:**
- [ ] **10:00-11:00** 🎤 Asesor: Revisar resultados

---

### **Semana 12: Apr 23-29 (15 horas)**

**Tareas:**
- Completar Estado del Arte
- Integrar todo en documento único
- Preparar presentación (10 slides)

**Viernes - Entrega:**
- [ ] **20:00-21:00** 🎯 **ENTREGA CP3**

---

### ✅ **ENTREGABLES CP3 (antes del 29 Apr):**
- [x] Resultados en SROIE (100 samples)
- [x] Comparativa con baseline
- [x] Documento académico (20-25 páginas):
  - Introducción
  - Estado del Arte
  - Metodología
  - Resultados
  - Conclusiones
- [x] Presentación (10 slides)

**Nota acumulada: 7.5/10** ⭐ **MUY BUENO**

---

# FASE FINAL: DOCUMENTACIÓN (Semanas 13-16)

## 🗓️ SEMANAS 13-16: Apr 30 - May 30 (60 horas total)

### **Objetivo:** Pulir y entregar

### **Semana 13-14: Buffer (30h):**
- Revisar documento completo
- Correcciones de asesor
- Preparar código final (limpio, comentado)

### **Semana 15: May 21-27 (15h):**
- Crear demo simple (Jupyter Notebook interactivo)
- Video explicativo (3-5 min)
- README completo

**Jueves 22 May:**
- [ ] **10:00-11:30** 🎤 Asesor: Revisión pre-final

### **Semana 16: May 28-30 (15h):**
- Ensayo de presentación
- Ajustes finales

**Viernes 30 May:**
- [ ] **14:00-15:30** 🎤 **SUSTENTACIÓN FINAL**
- [ ] **18:00** 🎉 **CELEBRAR!**

---

## 📊 DISTRIBUCIÓN SEMANAL DE TIEMPO

### **Horario Típico (Lunes a Viernes):**

| Día | Horario | Actividad | Horas |
|-----|---------|-----------|-------|
| **Lun-Mié** | 18:00-21:00 | Implementación/Programación | 3h |
| **Jueves** | 10:00-11:00 | Reunión con asesor | 1h |
| **Jueves** | 19:00-21:00 | Follow-up de reunión | 2h |
| **Viernes** | 18:00-21:00 | Testing + Commit semanal | 3h |
| **Sábado** | - | **DESCANSO** | 0h |
| **Domingo** | - | **DESCANSO** | 0h |
| **TOTAL** | - | - | **15h** |

### **Flexibilidad:**
- Si un día solo tienes 2h → compensar otro día con 4h
- Meta: **15-18h/semana** (no menos de 12, no más de 20)

---

## 🎯 FECHAS CRÍTICAS (Guardar en Calendario)

| Fecha | Checkpoint | Nota | Qué entregar |
|-------|-----------|------|--------------|
| **18 Feb** | CP0 | 1.0 | Dataset + Setup |
| **11 Mar** | CP1 | **3.5** ✅ | **Pipeline básico (APROBADO)** |
| **8 Abr** | CP2 | 6.0 | Inpainting validado |
| **29 Abr** | CP3 | **7.5** ⭐ | **Documento completo (MUY BUENO)** |
| **30 May** | FINAL | 7.5 | Sustentación |

---

## 💡 TIPS PARA ESTUDIANTES QUE TRABAJAN

### **Gestión de Tiempo:**

1. **🔥 Prioridad 1:** Proyecto (15h/semana)
2. **📚 Prioridad 2:** Trabajo (lo que necesites para vivir)
3. **🎓 Prioridad 3:** Otras materias (si las hay)

### **Cuándo trabajar en el proyecto:**

**✅ MEJORES MOMENTOS:**
- 🌙 Noches (18:00-21:00) → 3h después del trabajo
- ☕ Madrugadas (si eres búho): 22:00-01:00
- 🌅 Mañanas de fin de semana (si tienes energía)

**❌ EVITAR:**
- Después de las 11 PM (baja productividad)
- Domingos (necesitas descanso total)

### **Micro-sesiones:**
Si solo tienes 1 hora:
- ✅ Leer un paper
- ✅ Correr experimentos (dejar corriendo)
- ✅ Documentar código
- ❌ NO: Implementar features complejas (frustración)

### **Automatización:**
- ⏰ Scripts que corran overnight (training, benchmarking)
- 📝 Templates para documentación (copia-pega)
- 🤖 GitHub Actions para tests (automatizar QA)

---

## ⚠️ SEÑALES DE ALARMA (Cuándo Pedir Ayuda)

### **🚨 Si esto pasa, habla con tu asesor:**

1. **Vas 2+ semanas atrasado** → Renegociar alcance
2. **Trabajas >20h/semana en el proyecto** → Burnout incoming
3. **Te sientes abrumado** → Puede que 7.0 sea mejor meta que 7.5
4. **Problemas técnicos >1 semana** → Descope esa feature

### **Plan B (Si las cosas se complican):**

**Meta mínima: 6.0 (Bueno)**
- Llegar solo hasta CP2 (semana 9)
- Documentar bien lo que hiciste
- Explicar limitaciones de tiempo honestamente
- **Esto SIGUE siendo un buen proyecto**

---

## 🎯 QUÉ HACER HOY (Miércoles 5 Feb)

### **Noche (19:00-21:00) - 2 horas:**

**Prioridad absoluta:**
1. [ ] **19:00-19:30** Leer este plan completo
2. [ ] **19:30-20:00** Crear repo GitHub básico
3. [ ] **20:00-20:30** Descargar SROIE (dejar descargando si es pesado)
4. [ ] **20:30-21:00** Agregar fechas críticas a tu calendario
5. [ ] **21:00** Commit + ir a descansar

**NO MÁS DE 2 HORAS HOY** → Empezamos suave

---

## 📈 FILOSOFÍA FINAL

### **Mantra del proyecto:**
> "Consistencia > Intensidad"
> 
> **15 horas/semana × 16 semanas = 240 horas**
> 
> Es suficiente para un 7.5 (Muy Bueno)

### **Recordatorios:**
1. ✅ **7.5 es MUY BUENO** (no es "solo aprobar")
2. ✅ **Tu salud mental > tu nota**
3. ✅ **Mejor terminar con 7.0 que abandonar agotado**
4. ✅ **Este proyecto te enseñará mucho, independiente de la nota**

---

**¿Listo para empezar con este plan más realista?** 🚀

Tienes 2 horas hoy para arrancar. Nada de presión, solo lo básico.
