# Categorizacion CUDYR - UTI Neuroquirurgica (2024-2025)

Analisis de datos de categorizacion CUDYR para las unidades UTI Neuroquirurgica (UTINQX) y UTI Quirurgica (UTIQX), periodos 2024 y 2025.

## Estructura del Proyecto

```
├── Cat_UTINQX_2024.xlsx          # Datos categorizacion UTINQX 2024
├── Cat_UTINQx_2025.xlsx          # Datos categorizacion UTINQX 2025
├── Cat_UTIQX_2024.xlsx           # Datos categorizacion UTIQX 2024
├── Cat_UTIQX_2025.xlsx           # Datos categorizacion UTIQX 2025
├── analisis_categorizacion.ipynb  # Notebook con analisis exploratorio completo
├── crear_dashboard.py             # Script que genera los 3 HTML
├── index.html                     # Resumen UTINQX (pagina principal)
├── dashboard_utinqx.html          # Dashboard interactivo Plotly (UTINQX)
├── ambas_uti.html                 # Exposicion de datos ambas UTIs
└── README.md                      # Este archivo
```

## Fuente de Datos

Los archivos Excel provienen del sistema de categorizacion CUDYR deL HIS (SIRYC). Cada fila representa una categorizacion diaria de un paciente. Los archivos tienen un encabezado de 2 filas que se salta al cargar (`header=2`).

**Columnas disponibles:** ARE_ID, CPA_ID, N ARCHIVO, RUT, NOMBRE, APELLIDO_PATERNO, APELLIDO_MATERNO, EDAD, UNIDAD, CAMA, CATEGORIA, FECHA_CATEGORIZACION.

**Volumenes de datos (con header=2):**
- UTINQX 2024: 1,651 registros
- UTINQX 2025: 1,791 registros
- UTIQX 2024: 2,610 registros
- UTIQX 2025: 2,780 registros (no incluye columna CAMA)

## Escala de Categorizacion CUDYR

Cada paciente es categorizado diariamente con una combinacion de **letra + numero**:

| Letra | Nivel de Riesgo | Numero | Nivel de Dependencia |
|-------|----------------|--------|---------------------|
| A     | Maximo         | 1      | Total               |
| B     | Alto           | 2      | Parcial             |
| C     | Mediano        | 3      | Leve                |
| D     | Bajo           |        |                     |

Ejemplos: **A1** = Maximo riesgo + Dependencia total (el mas grave), **B2** = Alto riesgo + Dependencia parcial, **C3** = Mediano riesgo + Dependencia leve.

Se considera **Alto Riesgo** a las categorias A y B (letras A o B en la primera posicion).

---

## Paginas HTML creadas.

Las 3 paginas estan conectadas por una barra de navegacion.

### 1. index.html - Resumen UTINQX

Pagina estatica con tarjetas y tablas enfocada exclusivamente en UTINQX.

#### Seccion: Volumen de Actividad

| Indicador | Que muestra | Como se calcula |
|-----------|------------|----------------|
| **Total Categorizaciones** | Cantidad total de registros en el archivo 2025 | `len(utinqx_2025)` = 1,791. Son todas las categorizaciones realizadas en el anio, no pacientes. Un paciente internado 5 dias genera 5 categorizaciones. |
| **Pacientes Unicos Atendidos** | Cantidad de pacientes distintos atendidos | `utinqx_2025['RUT'].nunique()` = 365. Se cuentan RUTs unicos, sin repetir. |
| **Categorizaciones por Paciente** | Promedio de categorizaciones por cada paciente | `total_categorizaciones / pacientes_unicos` = 1791 / 365 = 4.9. Como se realiza 1 categorizacion por dia, equivale aproximadamente a dias de internacion promedio. |

Las variaciones porcentuales (ej: "+8.5% vs 2024") se calculan como: `((valor_2025 - valor_2024) / valor_2024) * 100`.

#### Seccion: Perfil de Riesgo

| Indicador | Que muestra | Como se calcula |
|-----------|------------|----------------|
| **% Alto Riesgo (A+B)** | Porcentaje de categorizaciones donde el paciente fue clasificado como A o B | Se marca como alto riesgo si la primera letra de la categoria es 'A' o 'B'. Luego: `(cantidad_alto_riesgo / total) * 100` = 97.6%. |
| **Categorizaciones A1** | Cantidad de veces que un paciente fue categorizado como A1 | Conteo directo: `(utinqx_2025['CATEGORIA'] == 'A1').sum()` = 286. A1 es la categoria de mayor gravedad (maximo riesgo + dependencia total). |
| **Categorizaciones A+B totales** | Cantidad absoluta de categorizaciones de alto riesgo | Suma de todas las categorizaciones donde la categoria empieza con A o B = 1,748. |

La variacion en puntos porcentuales (pp) indica la diferencia absoluta entre dos porcentajes: si 2024 fue 94.1% y 2025 fue 97.6%, la diferencia es +3.5 pp.

#### Seccion: Estabilidad de Pacientes

| Indicador | Que muestra | Como se calcula |
|-----------|------------|----------------|
| **Pacientes que Cambian de Categoria** | Pacientes que tuvieron 2 o mas categorias distintas durante su estadia | Se agrupan las categorizaciones por RUT y se cuentan categorias unicas por paciente. Si un paciente tuvo B1 y luego A1, tiene 2 categorias distintas. En 2025: 128 de 365 pacientes (35.1%). |
| **Pacientes que Empeoran** | Pacientes que egresan con mayor riesgo que al ingresar | De los pacientes con 2+ categorizaciones (270 en 2025), se compara la primera y ultima categoria. Se asigna un puntaje: riesgo (A=4, B=3, C=2, D=1) + dependencia (1=3, 2=2, 3=1). Si el puntaje final es mayor que el inicial, el paciente empeoro. Resultado: 19 pacientes. |

#### Seccion: Detalle Mensual

Tabla con 12 filas (una por mes) que muestra:
- **Cat. 2024 / Cat. 2025**: Categorizaciones realizadas cada mes en cada anio.
- **Diferencia**: `cat_2025 - cat_2024` para cada mes. Positivo (rojo) = mas carga en 2025. Negativo (verde) = menos carga.
- **% A+B**: Porcentaje de alto riesgo por mes = `(alto_riesgo_del_mes / total_del_mes) * 100`.

#### Seccion: Distribucion de Categorias

Tabla con todas las categorias que aparecen en los datos (A1, A2, B1, B2, B3, C1, C2, C3, D2), mostrando cantidad en 2024, cantidad en 2025, porcentaje del total 2025, y nivel de riesgo.

---

### 2. dashboard_utinqx.html - Dashboard Interactivo

Dashboard generado con Plotly, con 5 filas de graficos interactivos. Se puede hacer zoom, hover para ver valores, y descargar como imagen.

#### Fila 1: Indicadores de Volumen (3 tarjetas)

| Indicador | Valor | Delta |
|-----------|-------|-------|
| Categorizaciones 2025 | 1,791 | vs 2024 (1,651), variacion relativa |
| Pacientes Unicos 2025 | 365 | vs 2024 (277), variacion relativa |
| Alto Riesgo (A+B) 2025 | 97.6% | vs 2024, diferencia en puntos porcentuales |

Los deltas rojos indican aumento (mas carga/riesgo respecto a 2024).

#### Fila 2: Barras Comparativas Mensuales

Grafico de barras agrupadas con 12 meses en el eje X. Cada mes tiene 2 barras:
- **Gris claro**: Categorizaciones del mes en 2024
- **Rojo**: Categorizaciones del mes en 2025

Permite ver visualmente en que meses 2025 supero a 2024 y viceversa.

#### Fila 3: Linea de Alto Riesgo + Dona de Categorias

**Grafico izquierdo (linea):** Porcentaje de alto riesgo (A+B) por mes.
- Linea gris punteada: 2024
- Linea roja solida: 2025
- Eje Y fijado entre 82% y 102% para ver las diferencias con claridad.
- Muestra como el porcentaje de alto riesgo subio consistentemente en 2025.

**Grafico derecho (dona):** Distribucion de categorias CUDYR en 2025.
- Cada porcion representa una categoria (A1, B1, B2, etc.)
- Colores: rojos para A, naranjas para B, verdes para C, azul para D.
- El hueco central (45%) es decorativo (dona vs pie).

#### Fila 4: Diferencia Mensual 2025 vs 2024

Grafico de barras positivas/negativas:
- **Barra roja hacia arriba**: Meses donde 2025 tuvo MAS categorizaciones que 2024 (aumento de carga).
- **Barra verde hacia abajo**: Meses donde 2025 tuvo MENOS que 2024 (disminucion de carga).
- Eje Y fijado entre -75 y +85 para que todos los valores y etiquetas sean visibles.
- Los valores estan anotados sobre/bajo cada barra.

#### Fila 5: Indicadores de Pacientes (3 tarjetas)

| Indicador | Valor | Descripcion |
|-----------|-------|------------|
| Categorizaciones A1 | 286 | Maximo riesgo + dependencia total. Delta vs 2024 (273). |
| Cambian de Categoria | 128 | Pacientes con 2+ categorias distintas (35.1% del total). |
| Pacientes que Empeoran | 19 | Egresan con mayor riesgo que al ingreso. |

---

### 3. ambas_uti.html - Datos Ambas UTIs

Pagina estatica que presenta datos de UTINQX y UTIQX lado a lado. No es una comparacion directa sino una exposicion de los datos de cada unidad para lectura independiente.

#### Seccion: Volumen de Actividad por Unidad

Dos tarjetas lado a lado:
- **UTINQX** (etiqueta azul): 1,791 categorizaciones (+8.5% vs 2024), 365 pacientes unicos.
- **UTIQX** (etiqueta naranja): 2,780 categorizaciones (+6.5% vs 2024), 604 pacientes unicos.

#### Seccion: Perfil de Riesgo por Unidad (2025)

4 tarjetas en grilla:
- % Alto Riesgo UTINQX: 97.6% (1,748 de 1,791)
- % Alto Riesgo UTIQX: 99.5% (2,767 de 2,780)
- A1 UTINQX: 286 (2024: 273)
- A1 UTIQX: 668 (2024: 389)

#### Seccion: Categorizaciones por Paciente

- UTINQX: 4.9 promedio (2024: 6.0)
- UTIQX: 4.6 promedio (2024: 4.4)

#### Seccion: Detalle Mensual 2024-2025

Tabla con columnas diferenciadas por color:
- **Azul (UTINQX)**: Categorizaciones 2024, 2025, % A+B 2025
- **Naranja (UTIQX)**: Categorizaciones 2024, 2025, % A+B 2025

#### Seccion: Distribucion de Categorias 2025

Tabla con todas las categorias, mostrando cantidad y porcentaje para cada unidad.

---

## Notebook: analisis_categorizacion.ipynb

El notebook contiene el analisis exploratorio completo paso a paso:

1. **Carga y limpieza**: Lectura de archivos con `header=2`, identificacion de columna CAMA faltante en UTIQX 2025, conversion de fechas.
2. **EDA**: Categorias unicas por dataset, distribucion de frecuencias.
3. **Flujo mensual**: Categorizaciones por mes, comparacion 2024 vs 2025.
4. **Indice de complejidad**: Puntaje calculado como riesgo (A=4,B=3,C=2,D=1) + dependencia (1=3,2=2,3=1). Promedio 2024: 5.97, Promedio 2025: 6.06.
5. **Alto riesgo**: Porcentaje de categorizaciones A+B por periodo y unidad.
6. **Rotacion de pacientes**: Pacientes unicos por mes, estadia promedio.
7. **Evolucion de pacientes**: Analisis de pacientes que empeoran, mejoran o se mantienen.
8. **Resumen ejecutivo**: Consolidacion de metricas clave.

**Nota:** El notebook incluye analisis adicionales (indice de complejidad, carga por enfermero, proyecciones) que fueron deliberadamente excluidos de los HTML para mantener solo datos duros y objetivos.

---

## Como Ejecutar

```bash
pip install pandas plotly openpyxl
python crear_dashboard.py
```

Genera los 3 archivos HTML en el directorio actual. Abrir cualquiera con un navegador o Live Server.

## Tecnologias

- Python 3.14
- Pandas (manipulacion de datos)
- Plotly (dashboard interactivo)
- HTML/CSS estatico (index.html, ambas_uti.html)
