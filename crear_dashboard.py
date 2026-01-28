"""
Dashboard Interactivo - Justificación Recurso Enfermero UTINQX
=============================================================

Este script genera un dashboard HTML interactivo usando Plotly.
El HTML resultante se puede subir a GitHub Pages.

CONCEPTOS DE VISUALIZACIÓN:
--------------------------
1. INDICADORES (Indicators) - Para métricas clave numéricas
   → Muestran un número grande con contexto (ej: "2x más carga")

2. GRÁFICOS DE BARRAS - Para comparar categorías
   → Comparan valores entre grupos (ej: UTINQX vs UTIQX)

3. GRÁFICOS DE LÍNEA - Para tendencias temporales
   → Muestran evolución en el tiempo (ej: carga por mes)

4. GRÁFICOS DE PASTEL/DONA - Para proporciones
   → Muestran partes de un todo (ej: % alto riesgo)

5. TABLAS - Para datos precisos
   → Cuando el número exacto importa

COLORES:
--------
- Rojo (#e74c3c) → UTINQX (alerta, urgencia)
- Azul (#3498db) → UTIQX (comparación, neutro)
- Verde (#27ae60) → Mejora, positivo
- Naranja (#f39c12) → Advertencia

"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ============================================================
# 1. CARGAR Y PREPARAR DATOS
# ============================================================
print("[1/5] Cargando datos...")

# Cargar los 4 archivos Excel (saltando las 2 primeras filas de encabezado)
utiqx_2024 = pd.read_excel("Cat_UTIQX_2024.xlsx", header=2)
utiqx_2025 = pd.read_excel("Cat_UTIQX_2025.xlsx", header=2)
utinqx_2024 = pd.read_excel("Cat_UTINQX_2024.xlsx", header=2)
utinqx_2025 = pd.read_excel("Cat_UTINQx_2025.xlsx", header=2)

# Convertir fechas
for df in [utiqx_2024, utiqx_2025, utinqx_2024, utinqx_2025]:
    df['FECHA_CATEGORIZACION'] = pd.to_datetime(df['FECHA_CATEGORIZACION'], format='%d-%m-%Y')
    df['MES'] = df['FECHA_CATEGORIZACION'].dt.month

# Funciones de análisis
def calcular_complejidad(categoria):
    """Calcula índice de complejidad basado en categoría CUDYR"""
    if pd.isna(categoria):
        return None
    letra = categoria[0]
    numero = categoria[1]
    riesgo = {'A': 4, 'B': 3, 'C': 2, 'D': 1}
    dependencia = {'1': 3, '2': 2, '3': 1}
    return riesgo.get(letra, 0) + dependencia.get(numero, 0)

def es_alto_riesgo(categoria):
    """Determina si es categoría de alto riesgo (A o B)"""
    if pd.isna(categoria):
        return False
    return categoria[0] in ['A', 'B']

# Aplicar funciones
for df in [utiqx_2024, utiqx_2025, utinqx_2024, utinqx_2025]:
    df['COMPLEJIDAD'] = df['CATEGORIA'].apply(calcular_complejidad)
    df['ALTO_RIESGO'] = df['CATEGORIA'].apply(es_alto_riesgo)

print("    OK - Datos cargados y procesados")

# ============================================================
# 2. CALCULAR MÉTRICAS CLAVE
# ============================================================
print("[2/5] Calculando metricas...")

# Constantes de dotación
ENF_UTINQX = 1
ENF_UTIQX = 3

# Filtrar Jun-Dic 2025
utinqx_2025_jun = utinqx_2025[utinqx_2025['MES'] >= 6]
utiqx_2025_jun = utiqx_2025[utiqx_2025['MES'] >= 6]

# Métricas principales
cat_ar_utinqx = utinqx_2025_jun['ALTO_RIESGO'].sum()
cat_ar_utiqx = utiqx_2025_jun['ALTO_RIESGO'].sum()
carga_por_enf_utinqx = cat_ar_utinqx / ENF_UTINQX
carga_por_enf_utiqx = cat_ar_utiqx / ENF_UTIQX
ratio_carga = carga_por_enf_utinqx / carga_por_enf_utiqx

pct_ar_utinqx = utinqx_2025_jun['ALTO_RIESGO'].mean() * 100
pct_ar_utiqx = utiqx_2025_jun['ALTO_RIESGO'].mean() * 100

# Aumento desde abril
carga_2024_abr = utinqx_2024[utinqx_2024['MES'] >= 4]['COMPLEJIDAD'].sum()
carga_2025_abr = utinqx_2025[utinqx_2025['MES'] >= 4]['COMPLEJIDAD'].sum()
aumento_carga = ((carga_2025_abr - carga_2024_abr) / carga_2024_abr) * 100

# Crecimiento anual
crec_utinqx = ((len(utinqx_2025) - len(utinqx_2024)) / len(utinqx_2024)) * 100
crec_utiqx = ((len(utiqx_2025) - len(utiqx_2024)) / len(utiqx_2024)) * 100

# A1 por enfermero
a1_utinqx = (utinqx_2025['CATEGORIA'] == 'A1').sum() / ENF_UTINQX
a1_utiqx = (utiqx_2025['CATEGORIA'] == 'A1').sum() / ENF_UTIQX

print("    OK - Metricas calculadas")

# ============================================================
# 3. CREAR DASHBOARD CON PLOTLY
# ============================================================
print("[3/5] Creando dashboard...")

# Colores del dashboard
COLOR_UTINQX = '#e74c3c'  # Rojo - urgencia
COLOR_UTIQX = '#3498db'   # Azul - comparación
COLOR_FONDO = '#f8f9fa'   # Gris claro

# Crear figura con subplots
# Esto crea una cuadrícula donde colocamos diferentes gráficos
fig = make_subplots(
    rows=4, cols=3,
    specs=[
        # Fila 1: 3 indicadores grandes
        [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
        # Fila 2: Gráfico de barras grande + indicador
        [{"type": "bar", "colspan": 2}, None, {"type": "indicator"}],
        # Fila 3: Gráfico de línea (tendencia) + pastel
        [{"type": "scatter", "colspan": 2}, None, {"type": "pie"}],
        # Fila 4: Comparación barras + tabla resumen
        [{"type": "bar", "colspan": 2}, None, {"type": "indicator"}],
    ],
    subplot_titles=[
        "Ratio Enfermero:Paciente", "Carga por Enfermero", "Aumento desde Abril",
        "Categorizaciones Alto Riesgo por Enfermero (Jun-Dic 2025)", "", "% Pacientes Alto Riesgo",
        "Tendencia Mensual: Carga por Enfermero (2025)", "", "Distribución Categorías UTINQX",
        "Pacientes A1 (Máximo Riesgo) por Enfermero", "", "Crecimiento Anual"
    ],
    vertical_spacing=0.12,
    horizontal_spacing=0.08
)

# ----------------------------------------------------------
# FILA 1: INDICADORES PRINCIPALES (Los números más impactantes)
# ----------------------------------------------------------

# Indicador 1: Ratio enfermero:paciente
# Los INDICADORES son perfectos para mostrar una métrica clave
fig.add_trace(
    go.Indicator(
        mode="number+delta",  # Muestra número + diferencia
        value=6,              # UTINQX tiene ratio 1:6
        title={"text": "UTINQX<br><span style='font-size:0.7em'>pacientes por enfermero</span>"},
        delta={'reference': 3, 'relative': False, 'valueformat': '.0f'},  # Comparado con UTIQX (1:3)
        number={'font': {'size': 60, 'color': COLOR_UTINQX}},
        domain={'row': 0, 'column': 0}
    ),
    row=1, col=1
)

# Indicador 2: Carga de trabajo
fig.add_trace(
    go.Indicator(
        mode="number+delta",
        value=round(ratio_carga, 1),
        title={"text": "Veces más carga<br><span style='font-size:0.7em'>UTINQX vs UTIQX</span>"},
        delta={'reference': 1, 'relative': False},
        number={'font': {'size': 60, 'color': COLOR_UTINQX}, 'suffix': 'x'},
        domain={'row': 0, 'column': 1}
    ),
    row=1, col=2
)

# Indicador 3: Aumento desde abril
fig.add_trace(
    go.Indicator(
        mode="number+delta",
        value=round(aumento_carga, 1),
        title={"text": "Aumento de carga<br><span style='font-size:0.7em'>desde llegada residente</span>"},
        delta={'reference': 0, 'relative': False},
        number={'font': {'size': 60, 'color': COLOR_UTINQX}, 'suffix': '%'},
        domain={'row': 0, 'column': 2}
    ),
    row=1, col=3
)

# ----------------------------------------------------------
# FILA 2: GRÁFICO DE BARRAS - Comparación de carga
# ----------------------------------------------------------

# Gráfico de barras: perfecto para COMPARAR categorías
fig.add_trace(
    go.Bar(
        x=['UTINQX (1 enfermero)', 'UTIQX (3 enfermeros)'],
        y=[carga_por_enf_utinqx, carga_por_enf_utiqx],
        marker_color=[COLOR_UTINQX, COLOR_UTIQX],
        text=[f'{carga_por_enf_utinqx:.0f}', f'{carga_por_enf_utiqx:.0f}'],
        textposition='outside',
        textfont={'size': 16, 'color': 'black'}
    ),
    row=2, col=1
)

# Indicador de % alto riesgo UTINQX
fig.add_trace(
    go.Indicator(
        mode="gauge+number",
        value=pct_ar_utinqx,
        title={"text": "UTINQX"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': COLOR_UTINQX},
            'steps': [
                {'range': [0, 50], 'color': '#d5f5d5'},
                {'range': [50, 80], 'color': '#fff3cd'},
                {'range': [80, 100], 'color': '#f8d7da'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': 99.1
            }
        },
        number={'suffix': '%', 'font': {'size': 30}}
    ),
    row=2, col=3
)

# ----------------------------------------------------------
# FILA 3: GRÁFICO DE LÍNEA + PASTEL
# ----------------------------------------------------------

# Datos de tendencia mensual
alto_riesgo_mes_utinqx = utinqx_2025[utinqx_2025['ALTO_RIESGO']].groupby('MES').size() / ENF_UTINQX
alto_riesgo_mes_utiqx = utiqx_2025[utiqx_2025['ALTO_RIESGO']].groupby('MES').size() / ENF_UTIQX

meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

# Gráfico de línea: perfecto para TENDENCIAS temporales
fig.add_trace(
    go.Scatter(
        x=meses,
        y=[alto_riesgo_mes_utinqx.get(i, 0) for i in range(1, 13)],
        mode='lines+markers',
        name='UTINQX',
        line={'color': COLOR_UTINQX, 'width': 3},
        marker={'size': 10}
    ),
    row=3, col=1
)

fig.add_trace(
    go.Scatter(
        x=meses,
        y=[alto_riesgo_mes_utiqx.get(i, 0) for i in range(1, 13)],
        mode='lines+markers',
        name='UTIQX',
        line={'color': COLOR_UTIQX, 'width': 3},
        marker={'size': 10}
    ),
    row=3, col=1
)

# Gráfico de pastel: distribución de categorías UTINQX
categorias_dist = utinqx_2025['CATEGORIA'].value_counts()
fig.add_trace(
    go.Pie(
        labels=categorias_dist.index.tolist(),
        values=categorias_dist.values.tolist(),
        hole=0.4,  # Hace que sea "dona" en vez de pastel
        marker_colors=px.colors.sequential.Reds_r
    ),
    row=3, col=3
)

# ----------------------------------------------------------
# FILA 4: A1 por enfermero + Crecimiento
# ----------------------------------------------------------

fig.add_trace(
    go.Bar(
        x=['UTINQX', 'UTIQX'],
        y=[a1_utinqx, a1_utiqx],
        marker_color=[COLOR_UTINQX, COLOR_UTIQX],
        text=[f'{a1_utinqx:.0f}', f'{a1_utiqx:.0f}'],
        textposition='outside',
        textfont={'size': 16}
    ),
    row=4, col=1
)

# Indicador de crecimiento
fig.add_trace(
    go.Indicator(
        mode="number+delta",
        value=round(crec_utinqx, 1),
        title={"text": "UTINQX<br><span style='font-size:0.7em'>vs 2024</span>"},
        delta={'reference': crec_utiqx, 'relative': False, 'valueformat': '.1f'},
        number={'font': {'size': 40, 'color': COLOR_UTINQX}, 'suffix': '%'}
    ),
    row=4, col=3
)

# ----------------------------------------------------------
# CONFIGURACIÓN FINAL DEL LAYOUT
# ----------------------------------------------------------

fig.update_layout(
    title={
        'text': '📊 Dashboard: Justificación Recurso Enfermero UTINQX<br><sup>Análisis de Categorización CUDYR 2024-2025</sup>',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 24}
    },
    showlegend=True,
    legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'center', 'x': 0.5},
    height=1200,
    template='plotly_white',
    paper_bgcolor=COLOR_FONDO,
    margin={'t': 100, 'b': 50, 'l': 50, 'r': 50}
)

# Actualizar ejes
fig.update_yaxes(title_text="Categorizaciones", row=2, col=1)
fig.update_yaxes(title_text="Categorizaciones/enfermero", row=3, col=1)
fig.update_yaxes(title_text="Pacientes A1", row=4, col=1)

print("    OK - Dashboard creado")

# ============================================================
# 4. EXPORTAR A HTML
# ============================================================
print("[4/5] Exportando a HTML...")

# Guardar como HTML autónomo (incluye todo el JS necesario)
fig.write_html(
    "dashboard_utinqx.html",
    include_plotlyjs=True,  # Incluye Plotly JS en el archivo
    full_html=True,
    config={
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d']
    }
)

print("    OK - Dashboard guardado como 'dashboard_utinqx.html'")
print("\n    LISTO! Abre el archivo HTML en tu navegador para ver el dashboard.")
print("    Este archivo se puede subir directamente a GitHub Pages.")

# ============================================================
# 5. CREAR PÁGINA INDEX CON RESUMEN EJECUTIVO
# ============================================================
print("\n[5/5] Creando pagina de resumen ejecutivo...")

# HTML con estilos y resumen
html_resumen = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Justificación Recurso Enfermero UTINQX</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            color: white;
            padding: 40px 20px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }}
        .card:hover {{
            transform: translateY(-5px);
        }}
        .card.highlight {{
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
        }}
        .card h3 {{
            font-size: 1.1em;
            margin-bottom: 15px;
            color: #333;
        }}
        .card.highlight h3 {{
            color: white;
        }}
        .metric {{
            font-size: 3em;
            font-weight: bold;
            color: #e74c3c;
        }}
        .card.highlight .metric {{
            color: white;
        }}
        .metric-label {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
        .card.highlight .metric-label {{
            color: rgba(255,255,255,0.8);
        }}
        .conclusion {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-top: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .conclusion h2 {{
            color: #333;
            margin-bottom: 20px;
            border-bottom: 3px solid #e74c3c;
            padding-bottom: 10px;
        }}
        .conclusion ul {{
            list-style: none;
            padding: 0;
        }}
        .conclusion li {{
            padding: 10px 0;
            padding-left: 30px;
            position: relative;
            font-size: 1.1em;
        }}
        .conclusion li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #27ae60;
            font-weight: bold;
        }}
        .btn {{
            display: inline-block;
            background: #e74c3c;
            color: white;
            padding: 15px 30px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 20px;
            transition: background 0.3s;
        }}
        .btn:hover {{
            background: #c0392b;
        }}
        .footer {{
            text-align: center;
            color: white;
            padding: 30px;
            opacity: 0.8;
        }}
        .comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 15px;
        }}
        .comp-item {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        .comp-item.utinqx {{
            background: #fce4e4;
        }}
        .comp-item.utiqx {{
            background: #e4f1fc;
        }}
        .comp-value {{
            font-size: 2em;
            font-weight: bold;
        }}
        .comp-item.utinqx .comp-value {{
            color: #e74c3c;
        }}
        .comp-item.utiqx .comp-value {{
            color: #3498db;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Justificación Recurso Enfermero</h1>
            <p>Unidad de Tratamiento Intensivo Neuroquirúrgico (UTINQX)</p>
            <p style="margin-top: 10px; font-size: 0.9em;">Análisis basado en datos de categorización CUDYR 2024-2025</p>
        </div>

        <div class="cards">
            <div class="card highlight">
                <h3>⚠️ PROBLEMA CENTRAL</h3>
                <div class="metric">1:6</div>
                <div class="metric-label">Ratio enfermero:paciente en UTINQX</div>
                <div style="margin-top: 15px; font-size: 0.95em;">
                    UTIQX tiene ratio 1:3 con pacientes de complejidad similar
                </div>
            </div>

            <div class="card">
                <h3>📊 Carga de Trabajo por Enfermero</h3>
                <div class="metric">{ratio_carga:.1f}x</div>
                <div class="metric-label">más carga en UTINQX vs UTIQX</div>
                <div class="comparison">
                    <div class="comp-item utinqx">
                        <div class="comp-value">{carga_por_enf_utinqx:.0f}</div>
                        <div>UTINQX</div>
                    </div>
                    <div class="comp-item utiqx">
                        <div class="comp-value">{carga_por_enf_utiqx:.0f}</div>
                        <div>UTIQX</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>📈 Aumento desde llegada residente</h3>
                <div class="metric">+{aumento_carga:.1f}%</div>
                <div class="metric-label">Incremento de carga Abr-Dic 2025 vs 2024</div>
            </div>

            <div class="card">
                <h3>🔴 Pacientes Alto Riesgo</h3>
                <div class="metric">{pct_ar_utinqx:.1f}%</div>
                <div class="metric-label">de pacientes son categoría A o B</div>
            </div>

            <div class="card">
                <h3>🚨 Pacientes Máximo Riesgo (A1)</h3>
                <div class="metric">{a1_utinqx:.0f}</div>
                <div class="metric-label">pacientes A1 por enfermero en UTINQX</div>
                <p style="margin-top: 10px; font-size: 0.9em; color: #666;">
                    UTIQX: {a1_utiqx:.0f} por enfermero ({((a1_utinqx/a1_utiqx)-1)*100:.0f}% menos)
                </p>
            </div>

            <div class="card">
                <h3>📅 Crecimiento Anual</h3>
                <div class="metric">+{crec_utinqx:.1f}%</div>
                <div class="metric-label">Aumento de categorizaciones 2024→2025</div>
                <p style="margin-top: 10px; font-size: 0.9em; color: #666;">
                    UTIQX creció +{crec_utiqx:.1f}%
                </p>
            </div>
        </div>

        <div class="conclusion">
            <h2>📋 Conclusión y Solicitud</h2>
            <p style="margin-bottom: 20px; font-size: 1.1em; color: #555;">
                Con la incorporación de <strong>1 ENFERMERO ADICIONAL</strong>, UTINQX lograría:
            </p>
            <ul>
                <li>Ratio 1:3 (equiparado con UTIQX)</li>
                <li>Carga de trabajo equitativa entre unidades</li>
                <li>Mayor seguridad para pacientes de alto riesgo ({pct_ar_utinqx:.1f}% de la unidad)</li>
                <li>Estabilización de dotación (sin depender de refuerzos)</li>
                <li>Preparación para el crecimiento proyectado en 2026</li>
            </ul>
            <a href="dashboard_utinqx.html" class="btn">📊 Ver Dashboard Interactivo Completo</a>
        </div>

        <div class="footer">
            <p>Análisis realizado por Nicolás Morales</p>
            <p>Datos: Sistema de Categorización CUDYR 2024-2025</p>
        </div>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_resumen)

print("    OK - Pagina de resumen guardada como 'index.html'")
print("\n" + "="*60)
print("ARCHIVOS GENERADOS:")
print("   • index.html - Resumen ejecutivo (página principal)")
print("   • dashboard_utinqx.html - Dashboard interactivo completo")
print("="*60)
print("\nPara GitHub Pages:")
print("   1. Crea un repositorio en GitHub")
print("   2. Sube estos archivos + los Excel")
print("   3. Activa GitHub Pages en Settings")
print("   4. ¡Listo! Tu dashboard estará en línea")
