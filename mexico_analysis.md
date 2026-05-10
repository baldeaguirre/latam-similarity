# Análisis de Similitud Socioeconómica: México en América Latina
> Elaborado a partir del sistema LatAm Quality-of-Life Similarity Score · Puntuación compuesta = media(coseno, euclidiana, Pearson) sobre 30 indicadores, 8 categorías, 20 países.

---

## Resumen ejecutivo

México ocupa una posición profundamente paradójica en el panorama latinoamericano: es, al mismo tiempo, una de las economías más productivas y competitivas de la región y uno de los países con peores indicadores de seguridad pública y gasto en salud. Esta dualidad lo convierte en un caso de estudio singular: ningún otro país de la muestra combina un nivel tan elevado de productividad y logística con una crisis de gobernabilidad tan marcada.

Su mayor par de similitud es **Brasil** (0.736), seguido por **Perú** (0.705) y **Ecuador** (0.676). En el extremo opuesto, las mayores distancias se registran con **Cuba** (0.493), **Nicaragua** (0.500) y **Bolivia** (0.503). Su posición en el espacio vectorial (PCA1: +0.032, PCA2: −0.027) lo sitúa en la zona central del mapa, pero con una ligera inclinación negativa en el segundo componente principal, que captura la dimensión de democracia y gobernanza.

---

## 1. Posicionamiento Regional

### Ranking de similitud (de mayor a menor)

| # | País | Puntuación |
|---|------|-----------|
| 1 | Brasil | **0.736** |
| 2 | Perú | 0.705 |
| 3 | Ecuador | 0.676 |
| 4 | República Dominicana | 0.673 |
| 5 | Panamá | 0.663 |
| 6 | Chile | 0.659 |
| 7 | Paraguay | 0.642 |
| 8 | Venezuela | 0.637 |
| 9 | Colombia | 0.636 |
| 10 | Guatemala | 0.635 |
| 11 | Argentina | 0.601 |
| 12 | Uruguay | 0.588 |
| 13 | Costa Rica | 0.584 |
| 14 | El Salvador | 0.574 |
| 15 | Honduras | 0.517 |
| 16 | Haití | 0.506 |
| 17 | Bolivia | 0.503 |
| 18 | Nicaragua | 0.500 |
| 19 | Cuba | **0.493** |

---

## 2. Análisis Categórico: Fortalezas y Debilidades

### Resumen por categoría

| Categoría | Puntuación z (MX) | Rango regional | Lectura |
|-----------|-----------------|---------------|---------|
| **Productividad & Competitividad** | **+1.082** | **4.º / 20** | Fortaleza crítica |
| **Economía** | **+0.545** | **4.º / 20** | Fortaleza relevante |
| **Infraestructura** | **+0.598** | **5.º / 20** | Fortaleza relevante |
| Desarrollo Social | +0.485 | 7.º / 20 | Por encima del promedio |
| Democracia & Libertad Política | +0.094 | 9.º / 20 | En la mediana |
| Educación | −0.080 | 13.º / 20 | Debilidad moderada |
| **Salud** | **−0.365** | **16.º / 20** | **Debilidad grave** |
| **Gobernanza & Seguridad** | **−0.588** | **17.º / 20** | **Debilidad crítica** |

---

### 2.1 Productividad & Competitividad — La gran fortaleza

México es el 4.º país más productivo de América Latina. Los indicadores individuales son contundentes:

| Indicador | z-score MX |
|-----------|-----------|
| Global Innovation Index (WIPO 2023) | **+1.16** |
| Ease of Doing Business (WB 2020) | **+1.16** |
| Global Competitiveness Index (WEF 2019) | **+1.07** |
| Output per worker (2017 PPP $) | +0.93 |
| Labor productivity (GDP/hora trabajada) | +0.96 |

Esta categoría refleja la madurez del aparato industrial y exportador de México: la manufactura de alto valor agregado (automotriz, aeroespacial, electrónica), la posición en cadenas globales de valor —especialmente tras el T-MEC— y la densa red de clústeres industriales en el norte del país.

**Implicación clave:** Esta fortaleza se concentra geográfica y sectorialmente. No es generalizada al interior del país.

---

### 2.2 Economía — Fortaleza con matices

El PIB nominal de México (+2.29 z-score) es, de lejos, el mayor de la muestra después de Brasil. Sin embargo, el PIB *per cápita* es mucho más moderado (+0.51), evidenciando la profunda desigualdad distributiva: la economía es grande, pero los beneficios no se distribuyen equitativamente.

- **Crecimiento del PIB**: ligeramente por debajo del promedio regional (−0.16), consistente con un ciclo maduro de crecimiento moderado.
- **Inflación**: controlada en términos relativos a la región (+0.28, donde positivo = menor inflación tras el reverse-coding).
- **IED neta (% del PIB)**: por debajo del promedio (−0.26). Pese al nearshoring, como porcentaje del PIB México no lidera la atracción de inversión extranjera directa.

---

### 2.3 Infraestructura — Base sólida, pero distribuida desigualmente

| Indicador | z-score MX |
|-----------|-----------|
| Logistics Performance Index (WB 2023) | **+0.89** |
| Internet users (% pop) | +0.51 |
| Access to electricity (% pop) | +0.36 |

El LPI (+0.89) es el indicador más destacado: México tiene la mejor infraestructura logística de la subregión media-alta de la muestra, un activo crítico para su rol exportador.

---

### 2.4 Desarrollo Social — Posición mediana, tensión interna

Con un HDI de +0.52 z-score (rango 7.º), México se sitúa moderadamente por encima del promedio. El indicador de esperanza de vida es levemente negativo (−0.10), llamativo dado su nivel de ingreso: sugiere que el bajo gasto en salud tiene consecuencias medibles en los resultados de salud poblacional.

El **desempleo** muestra un z-score de +1.00 (positivo por reverse-coding: menor desempleo = mejor). Esto refleja la estructura del mercado laboral: alta informalidad (≈55% de la PEA) que coexiste con bajas tasas de desempleo formal. El indicador no captura la calidad del empleo.

---

### 2.5 Salud — Debilidad grave: el rezago estructural más preocupante

México ocupa el **16.º lugar de 20** en la categoría de salud:

| Indicador | z-score MX | Interpretación |
|-----------|-----------|----------------|
| Gasto público en salud (% PIB) | **−0.99** | Gasto críticamente bajo |
| Camas hospitalarias (por 1,000) | **−0.69** | Infraestructura insuficiente |
| Médicos (por 1,000) | +0.10 | Levemente positivo |
| Mortalidad infantil (por 1,000 NV) | +0.16 | Levemente mejor que el promedio |

El gasto en salud como porcentaje del PIB es casi 1 desviación estándar por debajo del promedio regional. Para un país con la economía más grande de la región después de Brasil, esta cifra es estructuralmente inadecuada.

> **Paradoja central:** México tiene la 4.ª economía más grande de la región y puede costear un gasto en salud significativamente mayor, pero políticamente no lo ha priorizado. Esto es una decisión fiscal, no una restricción de capacidad.

---

### 2.6 Gobernanza & Seguridad — La crisis estructural más profunda

Esta es la dimensión que más penaliza la similitud de México con los países de mejor desempeño:

| Indicador | z-score MX | Posición |
|-----------|-----------|---------|
| Índice de Percepción de Corrupción (CPI) | −0.27 | Bajo promedio |
| **Tasa de homicidios (UNODC 2022)** | **−0.91** | **4.º peor de 20** |
| **Global Peace Index** | **−1.04** | **4.º peor de 20** |
| Rule of Law Index (WJP) | −0.08 | Levemente bajo |

Con más de 25 homicidios por 100,000 habitantes (UNODC 2022), México supera ampliamente el promedio regional. Esta categoría es también la que más reduce la similitud de México con Uruguay (0.588), Costa Rica (0.584) y Chile (0.659) —países con niveles de ingreso o productividad comparables pero gobernanza radicalmente superior.

---

## 3. Análisis de Pares

### México ↔ Brasil (0.736) — El par más similar

La similitud se explica por convergencias estructurales: ambos son economías de gran escala con alta productividad industrial, coexistencia de modernización económica y exclusión masiva.

**Principales divergencias:**
- **Desempleo**: México tiene tasas formales más bajas (reflejando mayor informalidad, no mejor calidad de empleo).
- **Gasto en educación**: México gasta menos en educación como % del PIB que Brasil (−0.0622 ponderado).
- **Gasto en salud**: México invierte significativamente menos que Brasil (−0.0503 ponderado).

Brasil, pese a sus problemas fiscales, ha mantenido compromisos constitucionales con el gasto social que México no ha igualado.

---

### México ↔ Perú (0.705) — Convergencia estructural, divergencia en violencia

**Principales divergencias:**
- **PIB absoluto** (−0.0611): la escala económica de México es muy superior.
- **Tasa de homicidios** (−0.0533): México tiene una tasa de violencia significativamente mayor.
- **Escolaridad media** (−0.0382): México muestra menor escolaridad que Perú.

---

### México ↔ Ecuador (0.676) — Similitud democrática, diferencias de escala

Ecuador y México comparten posiciones similares en democracia e infraestructura. Las divergencias son de escala (PIB) y productividad, donde México supera a Ecuador con amplitud en innovación y competitividad.

> **Nota contextual:** Ecuador ha experimentado un deterioro acelerado de su seguridad pública entre 2022 y 2024. La brecha en gobernanza puede haberse reducido si se usaran datos más recientes.

---

### México ↔ Bolivia (0.503) — Distancia estructural confirmada

| Divergencia | Ponderación |
|------------|------------|
| Gasto en educación | −0.1403 |
| Logistics Performance Index | −0.0770 |
| Global Competitiveness Index | −0.0756 |

Bolivia invierte proporcionalmente mucho más en educación que México. En contrapartida, México lidera en logística y competitividad con amplia ventaja.

---

### México ↔ Cuba (0.493) — La mayor distancia

La distancia es fundamentalmente institucional:
- Cuba invierte masivamente en educación y salud como % del PIB (lo opuesto de México).
- Médicos por habitante (divergencia −0.1124): Cuba tiene una de las densidades médicas más altas del mundo.
- El modelo económico cubano excluye la IED y los mercados, separando radicalmente los perfiles de productividad.

---

## 4. Posición en el Espacio Vectorial

| Proyección | Coordenadas |
|-----------|------------|
| PCA1 / PCA2 | +0.032 / −0.027 |
| t-SNE 1 / t-SNE 2 | −45.41 / +23.59 |
| UMAP 1 / UMAP 2 | +16.74 / +16.90 |

México ocupa la zona central-ligeramente-negativa del segundo eje principal, que captura democracia y gobernanza. En t-SNE y UMAP se posiciona alejado del clúster "Southern Cone" y más próximo al clúster de "reformers de ingreso medio" (Brasil, Ecuador, Perú).

---

## 5. Recomendaciones de Política Pública

### 5.1 🔴 Prioridad máxima: Reducción de la violencia y fortalecimiento institucional

La seguridad pública es la principal falla estructural de México en términos comparativos. Con una tasa de homicidios 4.º peor de la región y un GPI igualmente alarmante, esta dimensión penaliza la similitud con los países de mejor desempeño y representa un costo económico directo (desinversión, migración de talento, costos de seguridad privada, pérdida de capital humano).

**Acciones:**
- Inversión en instituciones de procuración de justicia a nivel estatal y local, no solo federal.
- Reforma al sistema de incentivos de las fuerzas policiales: salarios competitivos, capacitación continua, métricas de desempeño.
- Políticas de prevención del delito con base en evidencia (Hot Spots Policing, intervenciones cognitivo-conductuales en jóvenes).
- Reducción progresiva del rol de las fuerzas armadas en seguridad pública, con transferencia de capacidades a cuerpos civiles profesionales.

### 5.2 🔴 Prioridad alta: Incrementar el gasto en salud

México gasta ≈5.5% del PIB en salud vs. Brasil ≈9.9%, Colombia ≈7.7%, Costa Rica ≈7.8%. Tiene capacidad fiscal para aumentar este gasto; es una decisión política, no económica.

**Acciones:**
- Establecer un piso mínimo de gasto en salud (meta: 7% del PIB en 10 años).
- Consolidar el sistema de salud para la población informal (≈55% de la PEA).
- Invertir en infraestructura hospitalaria (meta: ≥2.5 camas/1,000 habitantes, acorde con la OMS).

### 5.3 🟡 Prioridad alta: Formalización del mercado laboral

La paradoja de bajo desempleo formal con alta informalidad es insostenible. La informalidad deprime la productividad, limita la recaudación fiscal y excluye a los trabajadores de los sistemas de seguridad social.

**Acciones:**
- Simplificación del régimen fiscal para pequeñas empresas.
- Expansión del RESICO con acceso a seguridad social.
- Incentivos a la formalización progresiva (no imposición binaria formal/informal).

### 5.4 🟡 Prioridad media: Incrementar el gasto en educación

México gasta ≈4.3% del PIB en educación (debajo del promedio OCDE ≈5.0%). La eficiencia del gasto en resultados de aprendizaje (PISA) es de las más bajas de la OCDE.

**Acciones:**
- Aumentar inversión en educación media superior y superior.
- Fortalecer la formación docente continua.
- Invertir en infraestructura educativa digital para reducir la brecha urbano-rural.

### 5.5 🟢 Prioridad estratégica: Democratizar los beneficios de la productividad

La productividad está concentrada en el norte industrial. Las regiones del sur muestran indicadores comparables a países de ingreso bajo.

**Acciones:**
- Políticas de desarrollo regional que conecten clústeres industriales del norte con cadenas de valor nacionales.
- Inversión en conectividad (logística, digital, energética) en el sureste para capturar el nearshoring.
- Fortalecer el sistema de educación técnica y vocacional (CONALEP, CECATI) para generar capital humano adecuado a la demanda industrial existente.

---

## 6. Diagnóstico Sintético

> México es un país con las capacidades de una economía avanzada en sectores específicos, pero con las instituciones y el gasto social de un país de ingreso medio-bajo. Su paradoja central no es la falta de recursos, sino la ausencia de voluntad política sostenida para redistribuirlos hacia salud, educación y seguridad pública. Mientras esa brecha persista, México seguirá ocupando una posición ambivalente en el ranking regional: demasiado productivo para ser "pobre", demasiado inseguro y sub-invertido en capital humano para ser "desarrollado".
>
> La similitud con Brasil —su par más cercano— es reveladora: ambos países comparten la misma paradoja de gigantes subdesarrollados en sus propios términos. La pregunta no es si México *puede* alcanzar a Uruguay o Costa Rica en gobernanza y salud; la pregunta es si existe la coalición política doméstica para hacerlo.

---

*Fuentes: Banco Mundial (2022), PNUD HDR 2023, UNODC (2022), Transparencia Internacional CPI 2023, IEP GPI 2023, WJP Rule of Law 2023, EIU Democracy Index 2023, Freedom House 2024, V-Dem 2023, RSF 2024, ILO/Penn World Table (2022), WIPO GII 2023, WEF GCI 2019.*
