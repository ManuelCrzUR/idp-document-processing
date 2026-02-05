# Metodología Técnica de Detección - IDP

Explicación detallada de cómo el computador detecta y procesa cada elemento del documento a nivel algorítmico.

---

## 0. PREPROCESAMIENTO: Limpieza y Corrección de Documentos Escaneados

### **Problema:** Documentos físicos escaneados tienen defectos (arrugas, rotación, perspectiva incorrecta, sombras)

---

### **0.1 Detección y Corrección de Rotación/Inclinación**

**Principio:** Detectar el ángulo de inclinación del texto para rotarlo y alinearlo horizontalmente.

**Proceso computacional:**

1. **Detección de Bordes:**
   ```python
   edges = cv2.Canny(gray_image, threshold1=50, threshold2=150)
   ```
   - Algoritmo Canny: Detecta cambios bruscos de intensidad (bordes de letras)
   - Salida: Imagen binaria con solo los contornos del texto

2. **Transformada de Hough para Líneas:**
   ```python
   lines = cv2.HoughLines(edges, rho=1, theta=np.pi/180, threshold=200)
   ```
   - Cada píxel de borde "vota" por líneas que pasan por él
   - Las líneas con más votos = líneas dominantes del documento (generalmente horizontales del texto)

3. **Cálculo del Ángulo de Inclinación:**
   - Promedio de ángulos (θ) de las líneas detectadas
   - Ángulo de rotación = θ - 0° (o θ - 90° para líneas verticales)
   - Ejemplo: Si θ = 5°, el documento está inclinado 5° a la derecha

4. **Rotación:**
   ```python
   rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale=1.0)
   rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
   ```
   - Matriz de transformación afín: Rota cada píxel alrededor del centro
   - Interpolación bilineal: Calcula valores de píxeles intermedios

**Por qué funciona:** El texto tiene líneas horizontales dominantes; al detectarlas y medir su ángulo, podemos enderezar el documento.

---

### **0.2 Corrección de Perspectiva (Dewarping)**

**Principio:** Documentos fotografiados o escaneados desde un ángulo tienen distorsión trapezoidal. Necesitamos "aplanarlos".

**Proceso computacional:**

1. **Detección de Bordes del Documento:**
   ```python
   contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   document_contour = max(contours, key=cv2.contourArea)  # Contorno más grande
   ```
   - Suposición: El borde del documento es el contorno más grande en la imagen

2. **Aproximación a Cuadrilátero:**
   ```python
   epsilon = 0.02 * cv2.arcLength(document_contour, True)
   corners = cv2.approxPolyDP(document_contour, epsilon, True)
   ```
   - Algoritmo Douglas-Peucker: Simplifica el contorno a un polígono de 4 esquinas
   - Salida: 4 puntos (x, y) de las esquinas del documento

3. **Ordenar Esquinas:**
   - Top-left, top-right, bottom-right, bottom-left
   - Criterio: Suma y diferencia de coordenadas
     - Top-left: mínima suma (x + y)
     - Bottom-right: máxima suma (x + y)

4. **Transformación de Perspectiva:**
   ```python
   src_points = corners  # Esquinas detectadas (trapecio)
   dst_points = [[0, 0], [width, 0], [width, height], [0, height]]  # Rectángulo destino
   
   matrix = cv2.getPerspectiveTransform(src_points, dst_points)
   warped = cv2.warpPerspective(image, matrix, (width, height))
   ```
   - Calcula matriz de transformación 3×3 que mapea trapecio → rectángulo
   - Cada píxel (x, y) se transforma según: `[x', y', w'] = matrix × [x, y, 1]`

**Por qué funciona:** La transformación de perspectiva es una función matemática que "deshace" la distorsión causada por el ángulo de la cámara.

---

### **0.3 Detección y Eliminación de Arrugas**

**Principio:** Las arrugas son deformaciones locales que crean sombras y distorsiones no uniformes.

**Enfoque 1: Filtros de Denoising (OpenCV, scikit-image)**

**Proceso computacional:**

1. **Detección de Sombras por Arrugas:**
   - Aplicar filtro Gaussian Blur para separar textura de sombras
   - Restar imagen difuminada de original: `shadows = original - blurred`
   - Las arrugas aparecen como líneas oscuras en la diferencia

2. **Inpainting de Sombras:**
   ```python
   mask = cv2.threshold(shadows, threshold=30, maxval=255, type=cv2.THRESH_BINARY)[1]
   clean = cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
   ```
   - Máscara: Marca regiones oscuras (arrugas)
   - INPAINT_TELEA: Algoritmo Fast Marching que propaga color desde bordes hacia dentro

3. **Non-Local Means Denoising:**
   ```python
   denoised = cv2.fastNlMeansDenoisingColored(image, h=10, templateWindowSize=7, searchWindowSize=21)
   ```
   - Busca patches similares en toda la imagen (no solo localmente)
   - Promedia píxeles de patches similares para reducir ruido
   - `h`: Fuerza del filtro (mayor = más suave pero puede perder detalles)

**Enfoque 2: Deep Learning (DocUNet, DewarpNet)**

**Proceso computacional:**

1. **Red U-Net para Estimación de Deformación:**
   - Input: Imagen arrugada (H × W × 3)
   - Output: Mapa de flujo óptico (H × W × 2) que indica cómo mover cada píxel

2. **Encoder:**
   - Capas convolucionales que reducen resolución pero aumentan features
   - Aprende patrones de arrugas (sombras, curvaturas)

3. **Decoder:**
   - Capas de upsampling que reconstruyen resolución original
   - Predice desplazamiento (Δx, Δy) para cada píxel

4. **Warping:**
   ```python
   grid = flow_map + original_coordinate_grid
   unwarped = cv2.remap(image, grid_x, grid_y, interpolation=cv2.INTER_CUBIC)
   ```
   - `remap`: Reubica cada píxel según el mapa de flujo predicho

**Por qué funciona:** El modelo aprende durante entrenamiento cómo se ven las arrugas y cómo "devolverlas" a su posición original.

---

### **0.4 Eliminación de Ruido (Salt-and-Pepper, Gaussian Noise)**

**Principio:** Ruido del escáner aparece como píxeles aleatorios oscuros/claros.

**Proceso computacional:**

1. **Median Filter:**
   ```python
   denoised = cv2.medianBlur(image, ksize=5)
   ```
   - Para cada píxel, reemplaza su valor con la **mediana** de sus vecinos en ventana 5×5
   - Robusto contra outliers (píxeles de ruido aislado)

2. **Bilateral Filter:**
   ```python
   smooth = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)
   ```
   - Suaviza pero **preserva bordes**
   - Ponderación: Píxeles similares en color Y cercanos en espacio tienen más peso
   - Útil para eliminar ruido sin desdibujar texto

**Por qué funciona:** El ruido es aleatorio e inconsistente; los filtros lo eliminan al promediar con píxeles vecinos consistentes.

---

### **0.5 Binarización Adaptativa (Thresholding)**

**Principio:** Separar texto (negro) de fondo (blanco) incluso con iluminación no uniforme.

**Proceso computacional:**

1. **Thresholding Global (Otsu):**
   ```python
   _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
   ```
   - Algoritmo Otsu: Calcula automáticamente el mejor umbral global minimizando varianza intra-clase
   - Problema: Falla con iluminación variable (sombras en una esquina)

2. **Thresholding Adaptativo:**
   ```python
   binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, blockSize=11, C=2)
   ```
   - Divide imagen en bloques pequeños (11×11)
   - Calcula umbral **local** para cada bloque basado en promedio de vecinos
   - `C`: Constante restada del promedio (ajuste fino)

**Por qué funciona:** El umbral local se adapta a variaciones de iluminación, permitiendo binarización correcta en toda la imagen.

---

## 1. Detección de Sellos

### **Enfoque 1: Análisis de Color (OpenCV)**

**Principio:** Los sellos suelen tener colores distintivos (rojo, azul) que contrastan con el fondo blanco/texto negro.

**Proceso computacional:**
1. **Conversión de espacio de color:** RGB → HSV (Hue, Saturation, Value)
   - HSV es más robusto que RGB para segmentación por color porque separa el tono del brillo
   - Ejemplo: Rojo en HSV = H: 0-10°/170-180°, S: 100-255, V: 100-255
   
2. **Thresholding (Umbralización):**
   ```python
   # Crear máscara binaria donde TRUE = píxeles rojos
   mask = cv2.inRange(hsv_image, lower_red, upper_red)
   ```
   - El computador compara **cada píxel** con el rango definido
   - Salida: Imagen binaria (0 = negro, 255 = sello detectado)

3. **Operaciones Morfológicas:**
   - **Dilatación:** Expande regiones blancas para conectar fragmentos del sello
   - **Erosión:** Elimina ruido pequeño (píxeles aislados)
   - **Closing:** Rellena huecos internos del sello

4. **Detección de Contornos:**
   ```python
   contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   ```
   - Algoritmo: Suzuki-Abe (traza bordes de regiones blancas)
   - Salida: Lista de coordenadas (x, y) que forman el perímetro del sello

5. **Filtrado por características geométricas:**
   - Área: `cv2.contourArea(contour)` → Elimina objetos muy pequeños/grandes
   - Circularidad: `4π × área / perímetro²` → Detecta formas redondas
   - Bounding box: `x, y, w, h = cv2.boundingRect(contour)`

**Por qué funciona:** Los sellos tienen propiedades únicas: color intenso + forma circular/rectangular + tamaño consistente.

---

### **Enfoque 2: Deep Learning (YOLO/Detectron2)**

**Principio:** Red neuronal entrenada para reconocer patrones visuales de sellos en imágenes.

**Proceso computacional:**
1. **División en Grid:** La imagen se divide en una cuadrícula (ej: 13×13 celdas)

2. **Extracción de Features (CNN):**
   - Capas convolucionales detectan patrones jerárquicos:
     - Capa 1: Bordes y líneas
     - Capa 2: Formas simples (círculos, rectángulos)
     - Capa 3: Patrones complejos (textura de tinta, símbolos)
   
3. **Predicción de Bounding Boxes:**
   - Cada celda predice N cajas con:
     - (x, y, w, h): Coordenadas y dimensiones
     - Confianza: Probabilidad de que contenga un sello (0-1)
     - Clase: "sello_aprobado", "sello_rechazado", etc.

4. **Non-Maximum Suppression (NMS):**
   - Elimina cajas duplicadas para el mismo objeto
   - Algoritmo: Calcula IoU (Intersection over Union) entre cajas
   - Mantiene solo la caja con mayor confianza si IoU > 0.5

**Por qué funciona:** La red aprende representaciones abstractas que capturan la "esencia visual" de un sello, incluso con variaciones de rotación, escala o iluminación.

---

## 2. Detección de Gráficas

### **Enfoque 1: Segmentación Basada en Contornos (OpenCV)**

**Principio:** Las gráficas tienen líneas continuas, ejes perpendiculares y áreas cerradas.

**Proceso computacional:**
1. **Preprocesamiento:**
   - Conversión a escala de grises
   - Binarización: `cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)`
   
2. **Detección de Líneas (Transformada de Hough):**
   ```python
   lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100)
   ```
   - **Cómo funciona:** Cada píxel "vota" por todas las líneas posibles que pasan por él
   - Espacio de parámetros: (ρ, θ) → distancia y ángulo desde el origen
   - Líneas con más votos = líneas reales en la imagen
   
3. **Identificación de Ejes:**
   - Filtrar líneas por orientación:
     - Eje X: θ ≈ 0° (horizontal)
     - Eje Y: θ ≈ 90° (vertical)
   - Verificar intersección perpendicular (esquina inferior izquierda típica)

4. **Detección de Región de Gráfica:**
   - Encontrar el rectángulo delimitador que engloba ejes + datos
   - `cv2.boundingRect()` sobre el conjunto de líneas detectadas

**Por qué funciona:** Las gráficas tienen geometría estructurada (ejes ortogonales) que las diferencia del texto o imágenes arbitrarias.

---

### **Enfoque 2: Deep Learning (LayoutParser/Detectron2)**

**Principio:** Modelo entrenado en datasets como PubLayNet o ICDAR que contienen documentos anotados con tipos de regiones.

**Proceso computacional:**
1. **Backbone (Feature Extractor):** ResNet-50/101
   - Procesa la imagen completa en múltiples escalas
   - Salida: Feature maps (mapas de activación) de diferentes resoluciones

2. **Region Proposal Network (RPN):**
   - Genera ~2000 regiones candidatas que podrían contener objetos
   - Para cada región, predice:
     - Probabilidad de ser "objeto" vs "fondo"
     - Ajuste de coordenadas (x, y, w, h)

3. **Classification Head:**
   - Para cada región candidata, clasifica en:
     - "chart", "table", "text", "figure", "title", etc.
   - Además refina las coordenadas del bounding box

4. **Post-procesamiento:**
   - NMS para eliminar duplicados
   - Filtrado por umbral de confianza (ej: mantener solo predicciones > 0.7)

**Por qué funciona:** El modelo aprende la "apariencia visual" de gráficas (líneas, puntos de datos, leyendas) durante el entrenamiento con miles de ejemplos anotados.

---

## 3. Extracción de Datos de Gráficas

### **PlotDigitizer/WebPlotDigitizer**

**Principio:** Transformar píxeles en valores numéricos mediante calibración de ejes.

**Proceso computacional:**
1. **Calibración de Ejes (Manual/Semi-automática):**
   - Usuario define 2 puntos en el eje X: (x₁_pixel, x₁_valor), (x₂_pixel, x₂_valor)
   - Usuario define 2 puntos en el eje Y: (y₁_pixel, y₁_valor), (y₂_pixel, y₂_valor)
   - Construye función de mapeo: `f: pixel → valor_real`

2. **Detección de Curvas (Autotracing):**
   - Binarización de la curva (thresholding por color)
   - Esqueletización: Reduce la curva a línea de 1 píxel de grosor
   - Algoritmo de seguimiento: Arranca en un extremo y sigue píxeles conectados

3. **Extracción de Coordenadas:**
   - Para cada píxel (px, py) de la curva:
     ```
     x_real = interpolate(px, x₁_pixel, x₁_valor, x₂_pixel, x₂_valor)
     y_real = interpolate(py, y₁_pixel, y₁_valor, y₂_pixel, y₂_valor)
     ```
   - Salida: Lista de pares (x, y) en valores reales

4. **OCR para Etiquetas:**
   - Detecta regiones de texto (título, leyendas) con Tesseract/PaddleOCR
   - Asocia etiquetas con series de datos por proximidad espacial

**Por qué funciona:** Usa la geometría cartesiana conocida de las gráficas para mapear píxeles a coordenadas del mundo real.

---

## 4. Detección de Tablas

### **Enfoque 1: Lattice (Camelot)**

**Principio:** Detecta líneas de separación explícitas (bordes de celdas).

**Proceso computacional:**
1. **Detección de Líneas Horizontales/Verticales:**
   ```python
   # Kernel horizontal: detecta líneas horizontales largas
   kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
   horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_h)
   ```
   - Morfología: Elimina todo excepto líneas largas en dirección específica

2. **Intersección de Líneas:**
   - Combina líneas H y V: `table_mask = horizontal_lines + vertical_lines`
   - Detecta nodos (intersecciones) donde se cruzan

3. **Construcción de Grid:**
   - Crea matriz de celdas basada en coordenadas de intersecciones
   - Cada celda = rectángulo delimitado por 4 líneas

4. **Extracción de Texto por Celda:**
   - Para cada rectángulo, extrae texto con pdfplumber o PyMuPDF
   - Organiza en DataFrame de pandas según posición (fila, columna)

**Por qué funciona:** Las tablas tradicionales tienen estructura de rejilla visible, fácil de detectar geométricamente.

---

### **Enfoque 2: Stream (Camelot/Tabula)**

**Principio:** Detecta alineación de texto sin bordes visibles.

**Proceso computacional:**
1. **Análisis de Espacios en Blanco:**
   - Recorre la imagen horizontalmente y verticalmente
   - Identifica "gaps" (espacios vacíos) consistentes entre bloques de texto
   - Histograma de proyección:
     ```
     horizontal_projection[y] = Σ pixel_density(x, y) for all x
     ```
   - Valles en el histograma = separadores de filas

2. **Clustering de Texto:**
   - Agrupa palabras por proximidad vertical (misma fila)
   - Agrupa palabras por proximidad horizontal (misma columna)
   - Algoritmo DBSCAN o K-means en coordenadas (x, y)

3. **Alineación de Columnas:**
   - Detecta patrones de alineación (izquierda, derecha, centro)
   - Calcula distribución estadística de posiciones X
   - Picos en la distribución = bordes de columnas

4. **Construcción de Tabla:**
   - Asigna cada bloque de texto a celda (fila, columna)
   - Rellena con vacío si hay celdas faltantes

**Por qué funciona:** Explota la regularidad espacial del texto tabulado, incluso sin bordes.

---

### **Enfoque 3: Deep Learning (VGT - Vision Grid Transformer)**

**Principio:** Modelo transformer que entiende la estructura relacional de celdas.

**Proceso computacional:**
1. **Encoding de Imagen:**
   - CNN extrae features visuales de la región de tabla
   - División en patches (ej: 16×16 píxeles por patch)

2. **Positional Encoding:**
   - Cada patch recibe embeddings de posición (x, y)
   - Permite al modelo entender relaciones espaciales

3. **Self-Attention (Transformer):**
   - Cada patch "atiende" a otros patches relevantes
   - Aprende relaciones como:
     - "Este patch es celda vecina de aquel"
     - "Estos patches forman una columna"
   
4. **Grid Prediction:**
   - Predice matriz de celdas con coordenadas (x₁, y₁, x₂, y₂)
   - Clasificación de contenido: "header", "data", "merged_cell"

5. **OCR por Celda:**
   - TrOCR o PaddleOCR extrae texto de cada celda detectada
   - Preserva estructura en formato estructurado (JSON/CSV)

**Por qué funciona:** Los transformers capturan dependencias de largo alcance, útil para tablas con celdas fusionadas o layouts irregulares.

---

## 5. OCR (Reconocimiento de Texto)

### **Enfoque 1: Tesseract (LSTM-based)**

**Principio:** Red neuronal recurrente que procesa secuencias de píxeles como texto.

**Proceso computacional:**
1. **Segmentación de Líneas:**
   - Proyección horizontal: Suma de píxeles negros por fila
   - Valles en la proyección = espacios entre líneas de texto

2. **Segmentación de Palabras:**
   - Proyección vertical dentro de cada línea
   - Valles = espacios entre palabras

3. **Feature Extraction:**
   - LSTM procesa la línea de izquierda a derecha
   - En cada paso temporal, observa una "ventana" de píxeles
   - Extrae features: orientación de trazos, curvatura, densidad

4. **Reconocimiento de Caracteres (CTC Loss):**
   - LSTM predice secuencia de caracteres más probable
   - CTC (Connectionist Temporal Classification) permite que:
     - Un carácter se extienda por múltiples pasos temporales
     - Se inserten espacios en blanco automáticamente

5. **Language Model (Post-procesamiento):**
   - Corrige errores con diccionario y modelos estadísticos
   - Ej: "c0mputer" → "computer" (confusión 0/o)

**Por qué funciona:** LSTM captura dependencias secuenciales (contexto) para resolver ambigüedades como "l" vs "I".

---

### **Enfoque 2: Transformer-based (TrOCR, Donut)**

**Principio:** Encoder-decoder con atención visual directa sin segmentación explícita.

**Proceso computacional:**
1. **Vision Encoder (ViT - Vision Transformer):**
   - Divide imagen en patches (ej: 16×16)
   - Cada patch → embedding mediante proyección lineal
   - Self-attention entre patches para capturar contexto visual global

2. **Text Decoder (Transformer):**
   - Genera texto carácter por carácter de forma autorregresiva
   - En cada paso:
     - Atiende a TODOS los patches de imagen (cross-attention)
     - Atiende a caracteres ya generados (self-attention)
   - Predice distribución de probabilidad sobre vocabulario

3. **Beam Search:**
   - Mantiene las K secuencias más probables simultáneamente
   - Ej: K=5 → genera 5 hipótesis y selecciona la de mayor probabilidad total

**Por qué funciona:** La atención permite que el modelo "mire" cualquier parte de la imagen cuando genera cada carácter, útil para layouts no lineales o texto manuscrito.

---

## 6. Inpainting de Sellos (LaMa)

### **¿Qué es Inpainting?**
**Inpainting = "Rellenar huecos"** en una imagen de forma inteligente. Es como usar Photoshop para borrar un objeto y que el fondo se complete automáticamente.

**Aplicación aquí:** Cuando detectamos un sello encima de texto, necesitamos:
1. Borrar el sello
2. **Reconstruir** el texto que estaba debajo (que el sello tapaba)

LaMa es un modelo de IA que hace esto de forma muy realista.

---

### **Enfoque Técnico: LaMa (Large Mask Inpainting)**

**Principio:** Generación de contenido plausible en regiones enmascaradas usando convoluciones de Fourier.

**Proceso computacional:**
1. **Entrada:**
   - Imagen original + Máscara binaria (1 = remover, 0 = conservar)

2. **Fast Fourier Transform (FFT) Convolutions:**
   - Problema de inpainting tradicional: Receptive field limitado
   - LaMa usa convoluciones en dominio de frecuencia para:
     - Capturar patrones periódicos (líneas, texturas)
     - Tener receptive field global desde las primeras capas

3. **Encoder-Decoder con Skip Connections:**
   - Encoder comprime la imagen preservando features importantes
   - Decoder reconstruye, "rellenando" la región enmascarada
   - Skip connections preservan detalles finos

4. **Adversarial Training:**
   - Discriminador juzga si el inpainting es "real" o "generado"
   - Generador aprende a crear rellenos indistinguibles del fondo original

5. **Perceptual Loss:**
   - Compara features de alto nivel (no solo píxeles)
   - Asegura que la textura y semántica sean consistentes

**Por qué funciona:** FFT permite capturar estructuras repetitivas (ej: líneas de texto subyacentes al sello) y propagar información de regiones lejanas eficientemente.

---

## Resumen Comparativo

| Elemento | Método Clásico | Deep Learning | Precisión | Velocidad |
|----------|----------------|---------------|-----------|-----------|
| **Sellos** | Color + Contornos | YOLO/Detectron2 | 85% | ⚡⚡⚡ vs ⚡⚡ |
| **Gráficas** | Hough Transform | LayoutParser | 75% | ⚡⚡ vs ⚡ |
| **Tablas** | Grid Detection | VGT | 80% | ⚡⚡⚡ vs ⚡ |
| **Texto** | Tesseract LSTM | TrOCR/Donut | 92% | ⚡⚡ vs ⚡ |
| **Inpainting** | cv2.inpaint | LaMa | 70% | ⚡⚡⚡ vs ⚡ |

**Leyenda Velocidad:** ⚡⚡⚡ Muy rápido | ⚡⚡ Moderado | ⚡ Lento (requiere GPU)

---

## Conceptos Clave

1. **Convolución:** Operación que desliza un kernel (filtro pequeño) sobre la imagen para detectar patrones.
2. **Thresholding:** Convertir imagen en binario (blanco/negro) según un umbral.
3. **Morfología:** Operaciones geométricas (dilatar, erosionar) para limpiar/conectar regiones.
4. **IoU (Intersection over Union):** Métrica para comparar similitud entre 2 bounding boxes.
5. **Self-Attention:** Mecanismo que permite a cada elemento "mirar" todos los demás para capturar relaciones.
6. **CTC Loss:** Permite entrenar modelos de secuencias sin alineación explícita entrada-salida.
