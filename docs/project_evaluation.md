# Evaluación Multidisciplinaria: Proyecto IDP - Entendimiento Semántico de Documentos

**Fecha:** Febrero 2026  
**Evaluadores:** Dr. Carlos Méndez (AI Research), Ing. Ana Rojas (PM Senior), Lic. Roberto Silva (Startup Advisor)

---

## SECCIÓN 1: EVALUACIÓN TÉCNICA (AI Project Evaluator)

### 👤 Perfil del Evaluador
**Dr. Carlos Méndez, PhD**  
- Director de IA Aplicada, Universidad de los Andes (Colombia)
- 15+ años en Computer Vision y Document AI
- Reconocimientos: Best Paper CLEI 2023, Google AI Impact Challenge Latam
- Asesor técnico de 8 startups de IA en Colombia y Argentina

---

### 📊 Evaluación Técnica del Proyecto

#### **Calificación General: 8.2/10**

| Criterio | Puntuación | Comentarios |
|----------|------------|-------------|
| **Innovación Técnica** | 7.5/10 | Stack moderno, combinación inteligente de técnicas clásicas y DL |
| **Viabilidad Técnica** | 8.5/10 | Tecnologías probadas, riesgo moderado en integración |
| **Completitud del Plan** | 9.0/10 | Muy bien estructurado, cobertura exhaustiva |
| **Escalabilidad** | 7.0/10 | Diseño permite escalar, pero falta arquitectura distribuida |
| **Market Fit** | 9.0/10 | Excelente alineación con necesidades reales del mercado |

---

### ✅ Fortalezas Técnicas

1. **Enfoque Híbrido Sólido**
   - Combina visión por computador clásica (OpenCV) con deep learning
   - Estrategia de fallback entre múltiples OCR engines (Tesseract → PaddleOCR → TrOCR)
   - Reduce costos de inferencia usando métodos clásicos cuando sea posible

2. **Metodología de Preprocesamiento Exhaustiva**
   - Aborda problemas reales: arrugas, perspectiva, ruido
   - Rara vez visto en soluciones comerciales (mayoría asume documentos "limpios")
   - **Diferenciador clave:** Capacidad de procesar documentos físicos deteriorados

3. **Módulo de Inpainting con LaMa**
   - Uso de LaMa para eliminación de sellos es **innovador en el contexto comercial**
   - La mayoría de competidores ignoran sellos o los detectan sin remover
   - Tecnología de vanguardia (2021-2024), aún no commoditizada

4. **Cobertura Completa del Pipeline**
   - Layout analysis + Tables + Charts + Text + Validation
   - Sistema end-to-end, no solo OCR
   - Integración de QA con RAG es valor agregado significativo

---

### ⚠️ Riesgos Técnicos y Mitigaciones

| Riesgo | Severidad | Probabilidad | Mitigación Recomendada |
|--------|-----------|--------------|------------------------|
| **Complejidad de integración** | Alta | Media | Arquitectura modular, APIs bien definidas, testing exhaustivo |
| **Dependencia de GPU** | Media | Alta | Implementar tier sin GPU (solo OpenCV + Tesseract) para low-tier |
| **Calidad de datos de entrenamiento** | Alta | Media | Asociación con clientes early adopters para data augmentation |
| **Latencia en producción** | Media | Media | Procesamiento asíncrono, cola de trabajos, caching inteligente |
| **Mantenimiento de múltiples modelos** | Media | Alta | MLOps desde día 1: versioning, A/B testing, monitoreo |

---

### 🔬 Análisis de Competencia Técnica

#### **Competidores Directos:**

1. **Google Document AI** 
   - ✅ Mejor handwriting recognition (50 idiomas)
   - ❌ No ofrece preprocesamiento de documentos dañados
   - ❌ No tiene capacidad de inpainting de sellos
   - 💰 $30/1000 páginas (Custom Extractor)

2. **AWS Textract**
   - ✅ Integración nativa con ecosistema AWS
   - ❌ Limitado en documentos con layouts caóticos
   - 💰 $15-50/1000 páginas según API

3. **ABBYY FlexiCapture**
   - ✅ Líder establecido, muy robusto
   - ❌ Caro, enfocado en enterprise ($$$)
   - ❌ UX anticuada, curva de aprendizaje alta

4. **Rossum** (AI-first IDP)
   - ✅ Template-free, muy fácil de usar
   - ❌ Enfocado principalmente en invoices/AP
   - 💰 ~$49-149/mes (1000-5000 créditos)

#### **Ventaja Competitiva de su Proyecto:**

| Feature | Google Doc AI | AWS Textract | ABBYY | Rossum | **Su Proyecto** |
|---------|---------------|--------------|-------|--------|-----------------|
| Preprocesamiento avanzado | ❌ | ❌ | Parcial | ❌ | ✅ |
| Inpainting de sellos | ❌ | ❌ | ❌ | ❌ | ✅ |
| Extracción de gráficas | Limitado | ❌ | ✅ | ❌ | ✅ |
| Documentos dañados/arrugados | ❌ | ❌ | Parcial | ❌ | ✅ |
| QA Semántico (RAG) | ❌ | Básico | ❌ | ❌ | ✅ |
| Open-source/Self-hosted | ❌ | ❌ | ❌ | ❌ | ✅ Potencial |

**🎯 Nicho diferenciado:** Documentos físicos de baja calidad + Necesidad de eliminar sellos

---

### 📈 Casos de Uso con Mayor Potencial

#### **Alto Impacto (Pain Point Real):**

1. **Gobierno & Entidades Públicas (Latam)**
   - **Problema:** Archivos históricos en papel, sellos oficiales obstructivos, mala calidad
   - **Mercado:** Colombia, México, Argentina digitalizando archivos judiciales/notariales
   - **Valor:** Inpainting de sellos es crítico para OCR efectivo
   - **TAM estimado:** $200M en Latam (2026-2028)

2. **Sector Financiero (Compliance)**
   - **Problema:** Documentos históricos escaneados, validación de información financiera
   - **Mercado:** Bancos procesando 1M+ docs/mes para KYC/AML
   - **Valor:** Validación de integridad financiera reduce fraude
   - **TAM:** $500M+ (sector BFSI lidera adopción IDP con 32% share)

3. **Construcción & Real Estate**
   - **Problema:** Planos técnicos con sellos, anotaciones manuscritas, gráficos complejos
   - **Mercado:** Firmas de ingeniería, constructoras
   - **Valor:** Extracción de gráficas + medidas de planos
   - **TAM:** $150M en Latam

4. **Healthcare (Historias Clínicas)**
   - **Problema:** Documentos médicos con sellos institucionales, handwriting de doctores
   - **Mercado:** Hospitales, aseguradoras
   - **Valor:** OCR robusto para documentos complejos
   - **TAM:** $300M+ (sector salud es 2do mayor adoptante)

---

### 🧪 Validación de Hipótesis Recomendada

**Antes de desarrollo full-stack, sugiero:**

1. **Spike de Inpainting (2 semanas)**
   - Implementar solo LaMa + detección de sellos
   - Testear en dataset SROIE + 100 documentos reales con sellos
   - Métrica: ¿Mejora el OCR accuracy en +15%?

2. **Benchmarking de Preprocesamiento (1 semana)**
   - Crear dataset de docs arrugados/torcidos (50 samples)
   - Medir accuracy Before/After dewarping
   - Comparar vs Google Doc AI en mismo dataset

3. **Customer Discovery (3 semanas)**
   - Entrevistar 10 clientes potenciales (gobierno, bancos, ingeniería)
   - Validar: ¿Pagarían $X por eliminar sellos automáticamente?
   - **Pregunta clave:** "¿Cuánto tiempo/dinero pierden actualmente en esto?"

---

### 📝 Recomendaciones Técnicas Finales

#### **Prioridad Alta:**
1. ✅ **Comenzar con MVP del módulo de sellos** (mayor diferenciador)
2. ✅ **Arquitectura API-first** desde día 1 (facilita pivoting)
3. ✅ **Implementar telemetría exhaustiva** (entender qué falla en producción)
4. ✅ **Dataset sintético para training** (augmentation de sellos, arrugas)

#### **Prioridad Media:**
5. ⚠️ **Considerar Donut solo si TrOCR falla** (simplificar stack inicial)
6. ⚠️ **Integración con Cloud OCR como fallback** (Google/AWS para casos edge)
7. ⚠️ **Human-in-the-loop desde versión 1** (validación manual es inevitable)

#### **Riesgo a Evitar:**
❌ **No intentar resolver todo de golpe** → Enfocarse en nicho específico primero
❌ **No optimizar prematuramente** → Validar demanda antes de escalar infraestructura

---

## SECCIÓN 2: RUTA DE IMPLEMENTACIÓN (Project Manager)

### 👤 Perfil del Evaluador
**Ing. Ana Rojas, PMP, CSM**  
- 12 años liderando proyectos de IA/ML en startups
- Ex-PM en Rappi (Colombia), Mercado Libre (Argentina)
- Especialista en MVPs técnicos con time-to-market acelerado

---

### 🗓️ Roadmap de Desarrollo (6 Meses a MVP Funcional)

#### **Resumen Ejecutivo:**
- **Duración Total:** 24 semanas (~6 meses)
- **Equipo Mínimo:** 3-4 personas (1 ML Engineer, 1 Backend Dev, 1 Full-stack, 0.5 PM)
- **Budget Estimado:** $60,000 - $80,000 USD (sueldos + infra)
- **Milestone de validación:** Semana 12 (Decision Point: Pivotar o Perseverar)

---

### 📅 FASE 1: Foundation & Discovery (Semanas 1-4)

#### **Semana 1-2: Setup & Research Deep Dive**
- **Entregables:**
  - [ ] Ambiente de desarrollo configurado (GPU cloud: AWS/GCP)
  - [ ] Repositorio con CI/CD básico (GitHub Actions)
  - [ ] Dataset SROIE descargado y analizado
  - [ ] 10 entrevistas con stakeholders (gobierno, finanzas)
  
- **Equipo:** Full team (setup paralelo)
- **Riesgos:** Acceso a GPU puede tomar tiempo → Pre-aprobar budget

#### **Semana 3-4: Feature Prioritization & Spike**
- **Entregables:**
  - [ ] PRD (Product Requirements Document) v1.0
  - [ ] Arquitectura técnica high-level
  - [ ] **Spike de Inpainting:** LaMa funcionando con 20 samples
  - [ ] Spike de Preprocesamiento: Dewarping con OpenCV
  
- **Decisión:** ¿Inpainting mejora OCR accuracy? Si NO → Descope

---

### 📅 FASE 2: Core Development - MVP (Semanas 5-16)

#### **Sprint 1-2 (Semanas 5-8): Preprocesamiento**
- **Entregables:**
  - [ ] Módulo de corrección de perspectiva (OpenCV)
  - [ ] Detección de arrugas y denoising (3 algoritmos)
  - [ ] Binarización adaptativa
  - [ ] API endpoint: `/preprocess` (input: imagen → output: imagen limpia)
  - [ ] Tests automatizados (80% coverage)

- **Team Allocation:**
  - ML Engineer (80%): Implementar algoritmos
  - Backend Dev (50%): API wrapper, storage
  - Full-stack (20%): Dashboard simple para visualización

#### **Sprint 3-4 (Semanas 9-12): Detección y Eliminación de Sellos** ⭐
- **Entregables:**
  - [ ] Detector YOLO fine-tuned en dataset de sellos (crear dataset custom)
  - [ ] Clasificador de sellos (3 clases: Aprobado, Rechazado, Otro)
  - [ ] Integración de LaMa para inpainting
  - [ ] API endpoint: `/remove-stamps`
  - [ ] **Métrica clave:** Improvement en OCR accuracy antes/después

- **Milestone:** **DEMO DAY (Semana 12)** → Mostrar a early adopters

#### **Sprint 5-6 (Semanas 13-16): OCR Multimodal**
- **Entregables:**
  - [ ] Motor de OCR unificado (Tesseract + PaddleOCR + fallback a TrOCR)
  - [ ] Estrategia de selección automática de engine
  - [ ] Post-procesamiento de texto (corrección ortográfica)
  - [ ] API endpoint: `/ocr`
  - [ ] Benchmarking en SROIE (target: >90% accuracy)

---

### 📅 FASE 3: Advanced Features (Semanas 17-20)

#### **Sprint 7 (Semanas 17-18): Análisis de Layout**
- **Entregables:**
  - [ ] Integración de LayoutLMv3 o LayoutParser
  - [ ] Detección de regiones: Texto, Tablas, Gráficas
  - [ ] API endpoint: `/analyze-layout`

#### **Sprint 8 (Semanas 19-20): Extracción de Tablas & Gráficas**
- **Entregables:**
  - [ ] Extracción de tablas (Camelot + PDFPlumber híbrido)
  - [ ] Detección de gráficas (YOLO custom o LayoutParser)
  - [ ] OCR de ejes/leyendas en gráficas
  - [ ] API endpoint: `/extract-tables`, `/extract-charts`

---

### 📅 FASE 4: Integration & Polish (Semanas 21-24)

#### **Sprint 9 (Semanas 21-22): Pipeline Orquestado**
- **Entregables:**
  - [ ] Orquestador que ejecuta pipeline completo
  - [ ] Sistema de validación (business logic)
  - [ ] Integración de QA básico (sin RAG aún, solo rule-based)
  - [ ] API endpoint: `/process-document` (end-to-end)

#### **Sprint 10 (Semanas 23-24): Testing & Deploy**
- **Entregables:**
  - [ ] Testing end-to-end en 50 documentos reales
  - [ ] Optimización de latencia (target: <10s por doc)
  - [ ] Documentación de API (Swagger/OpenAPI)
  - [ ] Deploy en staging (Docker + K8s o similar)
  - [ ] **MVP listo para beta testers**

---

### 📊 Estimación de Esfuerzo por Módulo

| Módulo | Complejidad | Tiempo (sem) | FTE | Comentarios |
|--------|-------------|--------------|-----|-------------|
| Setup & Infra | Baja | 1 | 1.0 | DevOps + CI/CD |
| Preprocesamiento | Media | 3 | 1.0 | OpenCV bien documentado |
| **Detección Sellos** | **Alta** | **4** | **1.5** | Requiere dataset custom |
| **Inpainting (LaMa)** | **Alta** | **3** | **1.0** | Integración compleja |
| OCR Engine | Media | 3 | 1.0 | Librerías maduras |
| Layout Analysis | Alta | 2 | 1.0 | Modelos pre-entrenados |
| Tablas & Gráficas | Media | 2 | 0.8 | Híbrido de libs |
| Validación & QA | Media | 2 | 0.5 | Reglas de negocio |
| Orquestación | Baja | 1 | 0.5 | Glue code |
| Testing & Deploy | Media | 2 | 1.0 | E2E testing |
| **TOTAL** | | **23 sem** | | **Buffer: +1 sem** |

---

### ⚠️ Riesgos de Cronograma

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Dataset de sellos insuficiente | +2 semanas | Scraping web, data augmentation, contratar labeling |
| LaMa no funciona como esperado | +3 semanas | Fallback a DeepFill v2 o Stable Diffusion Inpaint |
| Latencia muy alta en producción | +2 semanas | Procesamiento asíncrono, optimización de modelos |
| Accuracy OCR <90% | +2 semanas | Fine-tuning, ensemble de modelos |

**Contingencia recomendada:** +20% buffer (5 semanas)

---

### 🎯 Decisión Key en Semana 12

**¿Continuar o Pivotar?**

**Métricas de éxito para continuar:**
- ✅ Inpainting mejora OCR accuracy en al menos +10%
- ✅ Al menos 3 early adopters dispuestos a pagar beta
- ✅ Preprocesamiento funciona en ≥80% de casos de prueba
- ✅ No hay blockers técnicos irresolubles (latencia, costos GPU)

**Si NO se cumplen → Pivotar a:**
- Opción A: Solo módulo de sellos como API especializada
- Opción B: Enfocarse en vertical específico (ej: solo documentos legales)

---

## SECCIÓN 3: EVALUACIÓN DE NEGOCIO (Startup Entrepreneur)

### 👤 Perfil del Evaluador
**Lic. Roberto Silva, MBA**  
- 3 exits exitosos (2 adquisiciones, 1 IPO)
- Partner en Fondo VC enfocado en Latam SaaS
- Especialista en GTM (Go-to-Market) para B2B tech

---

### 💼 Análisis de Viabilidad Comercial

#### **Calificación General: 7.8/10** (Viable, con ajustes)

| Criterio | Puntuación | Comentarios |
|----------|------------|-------------|
| **Tamaño de Mercado** | 9.0/10 | IDP market: $2.3B → $12.3B (2024-2030), CAGR 33% |
| **Timing** | 8.5/10 | Momento ideal: post-hype de ChatGPT, demanda real |
| **Diferenciación** | 8.0/10 | Inpainting + docs dañados es único, pero nicho |
| **Barreras de Entrada** | 6.5/10 | Modelos open-source bajan barreras técnicas |
| **Unit Economics** | 7.0/10 | Márgenes buenos, pero COGS de GPU son altos |
| **Go-to-Market** | 7.5/10 | B2B necesita sales directas, ciclo largo |

---

### 📈 Tamaño de Mercado & Oportunidad

#### **Mercado Global IDP:**
- **2024:** $2.3-4.5 Billion
- **2025:** $3.2-10.5 Billion
- **2030:** $12-21 Billion
- **CAGR:** 25-47% (dependiendo de fuente)

#### **Mercado Latinoamérica (estimado):**
- **2024:** ~$200-300M (8-10% del global)
- **2026:** ~$500-700M
- **Drivers:** Digitalización gubernamental, regulación (factura electrónica), Remote work

#### **Segmentos Verticales (Latam):**

| Vertical | TAM Latam 2026 | Pain Point | Willingness to Pay |
|----------|----------------|------------|-------------------|
| **Gobierno** | $150M | Archivos históricos, sellos | Media (presupuesto limitado, pero volumen alto) |
| **BFSI** | $200M | Compliance (KYC/AML) | **Alta** (ROI claro en reducción de fraude) |
| **Healthcare** | $100M | Historias clínicas | Media-Alta (regulación HIPAA-like) |
| **Legal/Notarial** | $80M | Documentos con sellos oficiales | Media |
| **Construction** | $70M | Planos técnicos | Media |

**SAM (Serviceable Addressable Market) inicial:** $200-300M (Gobierno + BFSI en Latam)

---

### 💰 Modelo de Negocio: ¿Producto o Servicio?

#### **Recomendación: HÍBRIDO (SaaS + Professional Services)**

#### **Opción 1: SaaS Puro (API-First)**

**Pros:**
- ✅ Escalabilidad infinita
- ✅ Márgenes altos (70-80% gross margin)
- ✅ Receptivo para serie A/B (VCs aman SaaS)
- ✅ Time-to-market rápido

**Cons:**
- ❌ Competencia directa con Google/AWS (pricing pressure)
- ❌ Necesita volumen masivo para breakeven
- ❌ Low switching costs (clientes pueden irse fácil)

**Modelo de Pricing (SaaS):**

| Tier | Docs/Mes | Precio Mensual | Features |
|------|----------|----------------|----------|
| **Free** | 100 | $0 | OCR básico, sin preprocesamiento |
| **Starter** | 1,000 | $99 | Preprocesamiento + OCR multi-engine |
| **Professional** | 10,000 | $499 | + Eliminación de sellos + Tablas |
| **Business** | 50,000 | $1,499 | + Gráficas + QA + API priority |
| **Enterprise** | Custom | Custom | On-premise, SLA 99.9%, soporte dedicado |

**Unit Economics (SaaS):**
- COGS por 1000 docs: ~$5-8 (GPU compute en AWS/GCP)
- LTV/CAC ratio objetivo: 3:1
- CAC estimado: $5,000-10,000 (B2B enterprise)
- Churn anual objetivo: <10%

---

#### **Opción 2: Professional Services (Implementación Custom)**

**Pros:**
- ✅ Revenue inmediato (cashflow positivo mes 1)
- ✅ Mayor pricing power (proyectos de $50k-$500k)
- ✅ Aprendizaje profundo de customer pain points
- ✅ Relaciones duraderas con clientes

**Cons:**
- ❌ No escalable (limitado por headcount)
- ❌ Márgenes menores (30-40%)
- ❌ Menos atractivo para VCs
- ❌ Riesgo de "consultora" en vez de "startup tech"

**Modelo de Pricing (Services):**
- **Setup inicial:** $25,000 - $100,000 (depende de volumen)
- **Monthly retainer:** $5,000 - $20,000 (soporte + mejoras)
- **Por proyecto:** $50,000 - $500,000 (implementación end-to-end)

---

#### **✅ Opción 3: HÍBRIDO (Recomendado para Año 1-2)**

**Estrategia "Land and Expand":**

1. **Fase 1 (Meses 1-6): Services-Led Growth**
   - Vender proyectos custom a 3-5 clientes enterprise
   - Revenue objetivo: $150k-300k (2-3 clientes × $50k-100k)
   - **Objetivo:** Financiar desarrollo del SaaS + aprender

2. **Fase 2 (Meses 7-12): Productizar Learnings**
   - Convertir features recurrentes en SaaS self-serve
   - Migrar clientes de services a SaaS + retainer menor
   - Revenue objetivo: $500k ARR (mix 60% services, 40% SaaS)

3. **Fase 3 (Año 2): SaaS-First**
   - Escalar GTM con inside sales + PLG (Product-Led Growth)
   - Services solo para Enterprise tier
   - Revenue objetivo: $1.5M-2M ARR (70% SaaS, 30% services)

**Ventajas del Híbrido:**
- 💰 Cashflow positivo desde mes 1 (no depende de fundraising)
- 📚 Product-market fit validation real
- 🔄 Transición orgánica a SaaS cuando esté maduro
- 🎯 Diferenciación: "No somos solo API, resolvemos tu problema completo"

---

### 🎯 Go-to-Market Strategy

#### **Año 1: Focused Beachhead**

**Target: Gobierno de Colombia (Archivos Judiciales/Notariales)**

**Por qué:**
- 🏛️ Ley 527/1999 y Decreto 2364/2012 impulsan digitalización
- 📜 ~15 millones de documentos físicos en Rama Judicial (estimado)
- 💰 Presupuesto existente para transformación digital
- 🔐 Sellos oficiales son pain point crítico

**Estrategia de entrada:**
1. **Caso piloto gratuito** con Archivo General de la Nación (3 meses)
2. **Gancho:** "Recuperamos texto detrás de sellos oficiales (único en Latam)"
3. **Métrica de éxito:** Digitalizar 10,000 docs con >85% accuracy
4. **Upsell:** Contrato de 3 años para 1M+ documentos

**Canales:**
- 🤝 Partnerships con integradores (ej: Heinsohn, Carvajal, CSC)
- 🎤 Conferencias GovTech (ej: Congreso CLAD)
- 📄 RFPs gubernamentales (bidding en Colombia Compra Eficiente)

---

#### **Año 2: Expandir a BFSI**

**Target: Bancos medianos en Latam (compliance KYC/AML)**

**Por qué:**
- 💸 Willingness to pay alta ($$$)
- 🚀 Regulación FATF obliga a digitalizar procesos
- 📊 ROI medible (reducción de fraude, multas)

**Posicionamiento:**
- "De documentos físicos a insights accionables en minutos"
- Caso de uso: Validación de identidad con docs arrugados/viejos

---

### 💵 Proyección Financiera (3 Años)

#### **Supuestos:**
- Equipo inicial: 4 personas
- Salario promedio: $4,000/mes (Latam)
- Infra cloud: $2,000/mes inicial → $10,000/mes (Año 3)
- Marketing/Sales: 20% de revenue

| Métrica | Año 1 | Año 2 | Año 3 |
|---------|-------|-------|-------|
| **Revenue** | $300k | $1.2M | $3.5M |
| **COGS** | $50k | $180k | $450k |
| **Gross Margin** | 83% | 85% | 87% |
| **Salarios** | $192k | $384k | $576k |
| **Marketing/Sales** | $60k | $240k | $700k |
| **Infra** | $24k | $60k | $120k |
| **EBITDA** | **-$26k** | **$336k** | **$1.65M** |
| **Clientes** | 5 | 25 | 80 |
| **ARR per cliente** | $60k | $48k | $44k |

**Breakeven:** Mes 18 (Año 2, Q2)

---

### 🚀 Funding Strategy

#### **Ronda Pre-Seed: $300k - $500k**
- **Timing:** Después de MVP (mes 6)
- **Uso de fondos:**
  - 60% Equipo (contratar 2-3 engineers)
  - 25% Go-to-Market (sales, eventos)
  - 15% Infra + contingencia
- **Investors objetivo:** Angels con experiencia en GovTech/Enterprise SaaS
- **Dilución:** 15-20%

#### **Ronda Seed: $1.5M - $2M**
- **Timing:** Después de $500k ARR (Año 2, Q1)
- **Valuation target:** $8-10M pre-money
- **Investors:** VCs regionales (Altó, ALLVP, Dux, Kaszek)
- **Pitch:** "El Docsumo de Latam, pero para documentos físicos"

---

### ⚠️ Riesgos de Negocio

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **Google/AWS bajan precios** | Alta | Alto | Enfocarse en nicho (docs dañados + sellos) donde no compiten |
| **Ciclos de venta gubernamentales largos** | Alta | Medio | Pipeline diversificado (también BFSI) |
| **Commoditización de modelos de IA** | Media | Alto | IP en pipelines custom + datasets propietarios |
| **Regulación de datos (GDPR/Latam)** | Media | Alto | On-premise deployment para clientes sensibles |
| **Falta de adopción (change management)** | Media | Alto | Énfasis en ROI cuantificable + change management services |

---

### 🎓 Recomendaciones Estratégicas Finales

#### **DO (Hacer):**
1. ✅ **Empezar con Professional Services** para validar y generar cashflow
2. ✅ **Vertical-first, no horizontal** (Gobierno Latam → BFSI → Healthcare)
3. ✅ **Construir moat con datos propietarios** (datasets de sellos, documentos raros)
4. ✅ **Partner strategy agresiva** (integradores TI, consultoras)
5. ✅ **On-premise option desde día 1** (key para gobierno)

#### **DON'T (Evitar):**
1. ❌ **No competir en precio con Big Tech** (race to the bottom)
2. ❌ **No ser "todo para todos"** (nicho específico primero)
3. ❌ **No fundraise demasiado pronto** (dilución innecesaria)
4. ❌ **No ignorar sales/GTM** (el mejor producto sin clientes = 0)

---

## 📋 CONCLUSIONES FINALES & RECOMENDACIONES

### 🎯 Veredicto Conjunto

| Evaluador | Recomendación | Nivel de Confianza |
|-----------|---------------|-------------------|
| **Dr. Méndez (AI)** | **Proceder con MVP enfocado en sellos** | 8.2/10 |
| **Ing. Rojas (PM)** | **6 meses a MVP es factible con equipo correcto** | 8.5/10 |
| **Lic. Silva (Business)** | **Viable como negocio híbrido (services → SaaS)** | 7.8/10 |

**Promedio:** **8.2/10** → **RECOMENDADO PROCEDER**

---

### 🏆 Top 3 Diferenciadores (Única Selling Proposition)

1. **"El único IDP de Latam que recupera texto detrás de sellos oficiales"**
   - Tecnología: LaMa inpainting
   - Mercado: Gobierno, Legal, Notarial
   
2. **"Procesamos documentos que otros rechazan (arrugados, torcidos, dañados)"**
   - Tecnología: Preprocesamiento exhaustivo (dewarping, denoising)
   - Mercado: Archivos históricos, construcción
   
3. **"De scanned paper a insights en minutos (no solo OCR, sino QA)"**
   - Tecnología: RAG + Validación semántica
   - Mercado: BFSI (compliance), Healthcare

---

### 📊 Próximos Pasos Recomendados (30 días)

#### **Semana 1-2:**
- [ ] Conformar equipo mínimo (contratar 1 ML engineer senior)
- [ ] Crear dataset sintético de sellos (100 samples)
- [ ] Configurar ambiente de desarrollo (AWS/GCP con GPU)

#### **Semana 3:**
- [ ] Implementar spike de LaMa inpainting
- [ ] **Métrica de éxito:** ¿Mejora OCR accuracy >10%?
- [ ] Si SÍ → continuar. Si NO → evaluar alternativas

#### **Semana 4:**
- [ ] 5 entrevistas con clientes potenciales (gobierno)
- [ ] Validar pricing hypothesis ($50-100k por proyecto)
- [ ] Preparar pitch deck para pre-seed ($300-500k)

---

### 💡 Reflexión Final

Este proyecto tiene **fundamentos técnicos sólidos** y un **mercado en crecimiento explosivo**. La clave del éxito estará en:

1. **Enfoque implacable en el nicho** (no intentar competir en todo con Google)
2. **Execution velocity** (6 meses a MVP, no 18)
3. **Customer discovery continuo** (el producto debe resolver dolor real, no teórico)

**El timing es ideal:** Post-boom de LLMs, empresas buscan aplicaciones prácticas de IA. IDP es uno de los casos de uso con ROI más claro.

**Riesgo mayor:** Subestimar la complejidad del GTM B2B enterprise. La tecnología puede estar lista en 6 meses, pero los primeros contratos tomarán 9-12 meses adicionales.

---

**Firma de Evaluadores:**

**Dr. Carlos Méndez** - AI Technical Evaluator  
**Ing. Ana Rojas** - Project Manager  
**Lic. Roberto Silva** - Business Strategy Advisor

**Fecha:** Febrero 2026
