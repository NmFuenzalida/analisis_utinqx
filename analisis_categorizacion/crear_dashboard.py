"""
Dashboard - Categorizacion CUDYR 2024-2025
============================================
Solo datos duros: conteos directos de los archivos de categorizacion.
Sin supuestos de dotacion, sin indices inventados, sin proyecciones.
Genera 3 HTML: index.html (resumen UTINQX), dashboard_utinqx.html (interactivo),
ambas_uti.html (exposicion de datos ambas UTIs).
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# 1. CARGAR DATOS
# ============================================================
print("[1/5] Cargando datos...")

utinqx_2024 = pd.read_excel("../data/categorizacion/Cat_UTINQX_2024.xlsx", header=2)
utinqx_2025 = pd.read_excel("../data/categorizacion/Cat_UTINQx_2025.xlsx", header=2)
utiqx_2024 = pd.read_excel("../data/categorizacion/Cat_UTIQX_2024.xlsx", header=2)
utiqx_2025 = pd.read_excel("../data/categorizacion/Cat_UTIQX_2025.xlsx", header=2)

for df in [utinqx_2024, utinqx_2025, utiqx_2024, utiqx_2025]:
    df['FECHA_CATEGORIZACION'] = pd.to_datetime(df['FECHA_CATEGORIZACION'], format='%d-%m-%Y')
    df['MES'] = df['FECHA_CATEGORIZACION'].dt.month

def es_alto_riesgo(cat):
    if pd.isna(cat):
        return False
    return cat[0] in ['A', 'B']

for df in [utinqx_2024, utinqx_2025, utiqx_2024, utiqx_2025]:
    df['ALTO_RIESGO'] = df['CATEGORIA'].apply(es_alto_riesgo)

print("    OK")

# ============================================================
# 2. CALCULAR METRICAS (solo conteos directos)
# ============================================================
print("[2/5] Calculando metricas...")

# Totales
total_2024 = len(utinqx_2024)
total_2025 = len(utinqx_2025)
variacion_anual = ((total_2025 - total_2024) / total_2024) * 100

# Pacientes unicos
pac_2024 = utinqx_2024['RUT'].nunique()
pac_2025 = utinqx_2025['RUT'].nunique()

# Categorizaciones por mes
cat_mes_2024 = utinqx_2024.groupby('MES').size()
cat_mes_2025 = utinqx_2025.groupby('MES').size()

# Diferencia mes a mes
diff_mes = cat_mes_2025 - cat_mes_2024

# % Alto riesgo (A+B) anual
pct_ar_2024 = utinqx_2024['ALTO_RIESGO'].mean() * 100
pct_ar_2025 = utinqx_2025['ALTO_RIESGO'].mean() * 100

# % Alto riesgo por mes
ar_mes_2024 = utinqx_2024.groupby('MES')['ALTO_RIESGO'].mean() * 100
ar_mes_2025 = utinqx_2025.groupby('MES')['ALTO_RIESGO'].mean() * 100

# Distribucion de categorias
dist_2024 = utinqx_2024['CATEGORIA'].value_counts()
dist_2025 = utinqx_2025['CATEGORIA'].value_counts()

# A1 (maximo riesgo + dependencia total)
a1_2024 = (utinqx_2024['CATEGORIA'] == 'A1').sum()
a1_2025 = (utinqx_2025['CATEGORIA'] == 'A1').sum()

# Categorizaciones A+B totales
ab_2024 = utinqx_2024['ALTO_RIESGO'].sum()
ab_2025 = utinqx_2025['ALTO_RIESGO'].sum()

# Pacientes que cambian de categoria durante estadia
cambios_2024 = utinqx_2024.groupby('RUT')['CATEGORIA'].nunique()
cambios_2025 = utinqx_2025.groupby('RUT')['CATEGORIA'].nunique()
pac_cambian_2024 = (cambios_2024 > 1).sum()
pac_cambian_2025 = (cambios_2025 > 1).sum()
pct_cambian_2024 = pac_cambian_2024 / pac_2024 * 100
pct_cambian_2025 = pac_cambian_2025 / pac_2025 * 100

# Pacientes que suben de categoria (empeoran)
empeoran_2025 = 0
total_con_evol_2025 = 0
for rut in utinqx_2025['RUT'].unique():
    pac = utinqx_2025[utinqx_2025['RUT'] == rut].sort_values('FECHA_CATEGORIZACION')
    if len(pac) < 2:
        continue
    total_con_evol_2025 += 1
    primera = pac['CATEGORIA'].iloc[0]
    ultima = pac['CATEGORIA'].iloc[-1]
    # Empeora si sube de riesgo (letra menor) o sube de dependencia (numero menor)
    orden_riesgo = {'A': 4, 'B': 3, 'C': 2, 'D': 1}
    orden_dep = {'1': 3, '2': 2, '3': 1}
    score_primera = orden_riesgo.get(primera[0], 0) + orden_dep.get(primera[1], 0)
    score_ultima = orden_riesgo.get(ultima[0], 0) + orden_dep.get(ultima[1], 0)
    if score_ultima > score_primera:
        empeoran_2025 += 1

# Estadia promedio (categorizaciones por paciente = dias aprox)
estadia_2024 = total_2024 / pac_2024
estadia_2025 = total_2025 / pac_2025

# ----- METRICAS UTIQX -----
qx_total_2024 = len(utiqx_2024)
qx_total_2025 = len(utiqx_2025)
qx_pac_2024 = utiqx_2024['RUT'].nunique()
qx_pac_2025 = utiqx_2025['RUT'].nunique()
qx_cat_mes_2024 = utiqx_2024.groupby('MES').size()
qx_cat_mes_2025 = utiqx_2025.groupby('MES').size()
qx_pct_ar_2024 = utiqx_2024['ALTO_RIESGO'].mean() * 100
qx_pct_ar_2025 = utiqx_2025['ALTO_RIESGO'].mean() * 100
qx_ar_mes_2024 = utiqx_2024.groupby('MES')['ALTO_RIESGO'].mean() * 100
qx_ar_mes_2025 = utiqx_2025.groupby('MES')['ALTO_RIESGO'].mean() * 100
qx_dist_2024 = utiqx_2024['CATEGORIA'].value_counts()
qx_dist_2025 = utiqx_2025['CATEGORIA'].value_counts()
qx_a1_2024 = (utiqx_2024['CATEGORIA'] == 'A1').sum()
qx_a1_2025 = (utiqx_2025['CATEGORIA'] == 'A1').sum()
qx_ab_2024 = utiqx_2024['ALTO_RIESGO'].sum()
qx_ab_2025 = utiqx_2025['ALTO_RIESGO'].sum()
qx_estadia_2024 = qx_total_2024 / qx_pac_2024
qx_estadia_2025 = qx_total_2025 / qx_pac_2025

print("    OK")

# ============================================================
# 3. CREAR DASHBOARD
# ============================================================
print("[3/5] Creando dashboard UTINQX...")

ROJO = '#c0392b'
ROJO_SUAVE = '#e74c3c'
AZUL = '#2c3e50'
GRIS = '#95a5a6'
GRIS_CLARO = '#bdc3c7'
VERDE = '#27ae60'
NARANJA = '#e67e22'
FONDO = '#f8f9fa'

meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
         'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

fig = make_subplots(
    rows=5, cols=3,
    specs=[
        # Fila 1: 3 indicadores de volumen
        [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
        # Fila 2: Tendencia categorizaciones mensual (grande)
        [{"type": "bar", "colspan": 3}, None, None],
        # Fila 3: % alto riesgo por mes + distribucion categorias
        [{"type": "scatter", "colspan": 2}, None, {"type": "pie"}],
        # Fila 4: Diferencia mes a mes 2025 vs 2024
        [{"type": "bar", "colspan": 3}, None, None],
        # Fila 5: 3 indicadores de pacientes
        [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
    ],
    subplot_titles=[
        "", "", "",
        "Categorizaciones Mensuales UTINQX: 2024 vs 2025",
        "", "",
        "Porcentaje de Pacientes Alto Riesgo (A+B) por Mes",
        "", "Distribucion de Categorias CUDYR (2025)",
        "Diferencia Mensual 2025 vs 2024 (categorizaciones)",
        "", "",
        "", "", ""
    ],
    vertical_spacing=0.10,
    horizontal_spacing=0.08,
    row_heights=[0.12, 0.20, 0.20, 0.20, 0.12]
)

# ============================================================
# FILA 1: INDICADORES DE VOLUMEN
# ============================================================

fig.add_trace(
    go.Indicator(
        mode="number+delta",
        value=total_2025,
        title={"text": "Categorizaciones 2025<br><span style='font-size:0.6em;color:#888'>total realizadas</span>"},
        delta={'reference': total_2024, 'relative': True, 'valueformat': '.1%',
               'increasing': {'color': ROJO_SUAVE}},
        number={'font': {'size': 48, 'color': AZUL}},
    ),
    row=1, col=1
)

fig.add_trace(
    go.Indicator(
        mode="number+delta",
        value=pac_2025,
        title={"text": "Pacientes Unicos 2025<br><span style='font-size:0.6em;color:#888'>atendidos en la unidad</span>"},
        delta={'reference': pac_2024, 'relative': True, 'valueformat': '.1%',
               'increasing': {'color': ROJO_SUAVE}},
        number={'font': {'size': 48, 'color': AZUL}},
    ),
    row=1, col=2
)

fig.add_trace(
    go.Indicator(
        mode="number+delta",
        value=round(pct_ar_2025, 1),
        title={"text": "Alto Riesgo (A+B) 2025<br><span style='font-size:0.6em;color:#888'>% del total de categorizaciones</span>"},
        delta={'reference': round(pct_ar_2024, 1), 'relative': False, 'valueformat': '.1f',
               'suffix': ' pp', 'increasing': {'color': ROJO_SUAVE}},
        number={'font': {'size': 48, 'color': ROJO}, 'suffix': '%'},
    ),
    row=1, col=3
)

# ============================================================
# FILA 2: BARRAS COMPARATIVAS POR MES
# ============================================================

fig.add_trace(
    go.Bar(
        x=meses,
        y=[cat_mes_2024.get(i, 0) for i in range(1, 13)],
        name='2024',
        marker_color=GRIS_CLARO,
        text=[str(cat_mes_2024.get(i, 0)) for i in range(1, 13)],
        textposition='outside',
        textfont={'size': 10},
    ),
    row=2, col=1
)

fig.add_trace(
    go.Bar(
        x=meses,
        y=[cat_mes_2025.get(i, 0) for i in range(1, 13)],
        name='2025',
        marker_color=ROJO_SUAVE,
        text=[str(cat_mes_2025.get(i, 0)) for i in range(1, 13)],
        textposition='outside',
        textfont={'size': 10},
    ),
    row=2, col=1
)

# ============================================================
# FILA 3: % ALTO RIESGO POR MES + DONA
# ============================================================

fig.add_trace(
    go.Scatter(
        x=meses,
        y=[ar_mes_2024.get(i, 0) for i in range(1, 13)],
        mode='lines+markers',
        name='% A+B 2024',
        line={'color': GRIS, 'width': 2, 'dash': 'dash'},
        marker={'size': 7},
        showlegend=False,
    ),
    row=3, col=1
)

fig.add_trace(
    go.Scatter(
        x=meses,
        y=[ar_mes_2025.get(i, 0) for i in range(1, 13)],
        mode='lines+markers',
        name='% A+B 2025',
        line={'color': ROJO, 'width': 3},
        marker={'size': 9},
        showlegend=False,
    ),
    row=3, col=1
)

# Anotaciones con valores 2024 y 2025 en el grafico
fig.add_annotation(
    x='Dic', y=ar_mes_2025.get(12, 0),
    text=f"2025: {ar_mes_2025.get(12, 0):.0f}%",
    showarrow=False, font={'size': 10, 'color': ROJO},
    xshift=30, row=3, col=1
)
fig.add_annotation(
    x='Dic', y=ar_mes_2024.get(12, 0),
    text=f"2024: {ar_mes_2024.get(12, 0):.0f}%",
    showarrow=False, font={'size': 10, 'color': GRIS},
    xshift=30, row=3, col=1
)

# Dona de categorias 2025
colores_cat = {
    'A1': '#c0392b', 'A2': '#e74c3c',
    'B1': '#e67e22', 'B2': '#f39c12', 'B3': '#f1c40f',
    'C1': '#27ae60', 'C2': '#2ecc71', 'C3': '#82e0aa',
    'D2': '#3498db'
}
cat_colors = [colores_cat.get(c, '#bdc3c7') for c in dist_2025.index.tolist()]

fig.add_trace(
    go.Pie(
        labels=dist_2025.index.tolist(),
        values=dist_2025.values.tolist(),
        hole=0.45,
        marker_colors=cat_colors,
        textinfo='label+percent',
        textfont={'size': 11},
        showlegend=False
    ),
    row=3, col=3
)

# ============================================================
# FILA 4: DIFERENCIA MES A MES (barras positivas/negativas)
# ============================================================

diff_values = [diff_mes.get(i, 0) for i in range(1, 13)]
diff_colors = [ROJO_SUAVE if v > 0 else VERDE for v in diff_values]

fig.add_trace(
    go.Bar(
        x=meses,
        y=diff_values,
        marker_color=diff_colors,
        text=[f'+{v}' if v > 0 else str(v) for v in diff_values],
        textposition='outside',
        textfont={'size': 11},
        showlegend=False,
    ),
    row=4, col=1
)

# Linea en cero se muestra automaticamente con el eje

# ============================================================
# FILA 5: INDICADORES DE PACIENTES
# ============================================================

fig.add_trace(
    go.Indicator(
        mode="number+delta",
        value=a1_2025,
        title={"text": "Categorizaciones A1<br><span style='font-size:0.6em;color:#888'>maximo riesgo + dependencia total</span>"},
        delta={'reference': a1_2024, 'relative': True, 'valueformat': '.1%',
               'increasing': {'color': ROJO_SUAVE}},
        number={'font': {'size': 44, 'color': ROJO}},
    ),
    row=5, col=1
)

fig.add_trace(
    go.Indicator(
        mode="number+delta",
        value=pac_cambian_2025,
        title={"text": "Cambian de Categoria<br><span style='font-size:0.6em;color:#888'>pacientes con 2+ categorias distintas ({0:.1f}% del total)</span>".format(pct_cambian_2025)},
        delta={'reference': pac_cambian_2024, 'relative': True, 'valueformat': '.1%'},
        number={'font': {'size': 44, 'color': NARANJA}},
    ),
    row=5, col=2
)

fig.add_trace(
    go.Indicator(
        mode="number",
        value=empeoran_2025,
        title={"text": "Pacientes que Empeoran<br><span style='font-size:0.6em;color:#888'>egresan con mayor riesgo que al ingreso</span>"},
        number={'font': {'size': 44, 'color': ROJO}},
    ),
    row=5, col=3
)

# ============================================================
# LAYOUT
# ============================================================

fig.update_layout(
    title={
        'text': (
            'UTINQX - Categorizacion CUDYR 2024-2025'
            '<br><sup style="color:#888">Datos de categorizacion | UTI Neuroquirurgica</sup>'
        ),
        'x': 0.5, 'xanchor': 'center',
        'font': {'size': 22, 'color': AZUL}
    },
    showlegend=True,
    legend={
        'orientation': 'h',
        'yanchor': 'top', 'y': -0.02,
        'xanchor': 'center', 'x': 0.5,
        'font': {'size': 12}
    },
    height=1700,
    template='plotly_white',
    paper_bgcolor=FONDO,
    plot_bgcolor='white',
    margin={'t': 100, 'b': 60, 'l': 60, 'r': 60, 'pad': 10},
    font={'family': 'Segoe UI, sans-serif'},
    barmode='group',
)

fig.update_yaxes(title_text="Categorizaciones", row=2, col=1)
fig.update_yaxes(title_text="% Alto Riesgo", row=3, col=1, range=[82, 102])
fig.update_yaxes(title_text="Diferencia", row=4, col=1, range=[-75, 85])

print("    OK")

# ============================================================
# 4. EXPORTAR
# ============================================================
print("[4/5] Exportando dashboard UTINQX...")

# Barra de navegacion comun
NAV_BAR = """
<nav style="background:#2c3e50;padding:10px 20px;display:flex;gap:15px;align-items:center;font-family:'Segoe UI',sans-serif;flex-wrap:wrap;">
    <a href="index.html" style="color:white;text-decoration:none;padding:6px 14px;border-radius:6px;font-size:0.9em;{nav_active_index}">Resumen UTINQX</a>
    <a href="dashboard_utinqx.html" style="color:white;text-decoration:none;padding:6px 14px;border-radius:6px;font-size:0.9em;{nav_active_dash}">Categorización UTINQX</a>
    <a href="ambas_uti.html" style="color:white;text-decoration:none;padding:6px 14px;border-radius:6px;font-size:0.9em;{nav_active_ambas}">Ambas UTI (Categorización)</a>
    <a href="../analisis_estadistica_uti/dashboard_comparativo_clinico.html" style="color:white;text-decoration:none;padding:6px 14px;border-radius:6px;font-size:0.9em;">Comparativo Clínico</a>
    <a href="../analisis_estadistica_uti/reporte_justificacion_utinqx.html" style="color:white;text-decoration:none;padding:6px 14px;border-radius:6px;font-size:0.9em;">Justificación UTINQX</a>
</nav>
"""

def get_nav(active):
    """Genera la barra de navegacion con el boton activo resaltado."""
    style_active = "background:rgba(255,255,255,0.2);font-weight:bold;"
    style_normal = "opacity:0.8;"
    return NAV_BAR.format(
        nav_active_index=style_active if active == 'index' else style_normal,
        nav_active_dash=style_active if active == 'dashboard' else style_normal,
        nav_active_ambas=style_active if active == 'ambas' else style_normal,
    )

# Inyectar nav en el dashboard Plotly
dashboard_nav = get_nav('dashboard')
fig.write_html(
    "dashboard_utinqx.html",
    include_plotlyjs=True,
    full_html=True,
    config={
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d']
    }
)

# Leer el HTML generado e insertar nav despues de <body>
with open("dashboard_utinqx.html", "r", encoding="utf-8") as f:
    dash_html = f.read()
dash_html = dash_html.replace("<body>", f"<body>\n{dashboard_nav}", 1)
with open("dashboard_utinqx.html", "w", encoding="utf-8") as f:
    f.write(dash_html)

# INDEX.HTML - Solo datos duros
nav_index = get_nav('index')
html_index = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UTINQX - Categorizacion CUDYR 2024-2025</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f0f2f5;
            color: #2c3e50;
            line-height: 1.6;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2em; margin-bottom: 8px; }}
        .header p {{ font-size: 1em; opacity: 0.85; }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 30px 20px; }}

        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-bottom: 30px; }}

        .card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }}
        .card h3 {{
            color: #7f8c8d;
            margin-bottom: 8px;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .card .valor {{
            font-size: 2.8em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .card .valor.rojo {{ color: #c0392b; }}
        .card .cambio {{
            font-size: 0.95em;
            margin-top: 8px;
            padding: 4px 10px;
            border-radius: 4px;
            display: inline-block;
        }}
        .card .cambio.sube {{ background: #fce4e4; color: #c0392b; }}
        .card .cambio.baja {{ background: #d5f5d5; color: #27ae60; }}
        .card .detalle {{ color: #95a5a6; font-size: 0.9em; margin-top: 8px; }}

        .seccion {{ margin-bottom: 30px; }}
        .seccion h2 {{
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e0e0e0;
        }}

        .tabla-container {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            overflow-x: auto;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.95em; }}
        th {{ background: #2c3e50; color: white; padding: 10px 12px; text-align: center; }}
        td {{ padding: 8px 12px; text-align: center; border-bottom: 1px solid #ecf0f1; }}
        tr:hover {{ background: #f8f9fa; }}
        .positivo {{ color: #c0392b; font-weight: bold; }}
        .negativo {{ color: #27ae60; }}

        .nota {{
            background: #fef9e7;
            border-left: 4px solid #f39c12;
            padding: 15px;
            border-radius: 0 8px 8px 0;
            margin-top: 20px;
            font-size: 0.9em;
            color: #7d6608;
        }}

        .btn {{
            display: inline-block;
            background: #2c3e50;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 20px;
        }}
        .btn:hover {{ background: #34495e; }}

        .footer {{
            text-align: center;
            padding: 25px;
            color: #95a5a6;
            font-size: 0.85em;
        }}
    </style>
</head>
<body>
    {nav_index}
    <div class="header">
        <h1>UTINQX - Categorizacion CUDYR</h1>
        <p>Datos de categorizacion 2024-2025 | UTI Neuroquirurgica</p>
    </div>

    <div class="container">

        <div class="seccion">
            <h2>Volumen de Actividad</h2>
            <div class="grid">
                <div class="card">
                    <h3>Total Categorizaciones</h3>
                    <div class="valor">{total_2025:,}</div>
                    <div class="cambio sube">+{variacion_anual:.1f}% vs 2024 ({total_2024:,})</div>
                </div>
                <div class="card">
                    <h3>Pacientes Unicos Atendidos</h3>
                    <div class="valor">{pac_2025}</div>
                    <div class="cambio {"sube" if pac_2025 > pac_2024 else "baja"}">{"+" if pac_2025 > pac_2024 else ""}{((pac_2025-pac_2024)/pac_2024*100):.1f}% vs 2024 ({pac_2024})</div>
                </div>
                <div class="card">
                    <h3>Categorizaciones por Paciente</h3>
                    <div class="valor">{estadia_2025:.1f}</div>
                    <div class="detalle">Promedio de categorizaciones realizadas por cada paciente durante su estadia.
                    Se realiza 1 categorizacion por dia, por lo que equivale a dias de internacion promedio.
                    En 2024 fue {estadia_2024:.1f}.</div>
                </div>
            </div>
        </div>

        <div class="seccion">
            <h2>Perfil de Riesgo</h2>
            <div class="grid">
                <div class="card">
                    <h3>Pacientes Alto Riesgo (A+B)</h3>
                    <div class="valor rojo">{pct_ar_2025:.1f}%</div>
                    <div class="cambio sube">+{pct_ar_2025 - pct_ar_2024:.1f} pp vs 2024 ({pct_ar_2024:.1f}%)</div>
                </div>
                <div class="card">
                    <h3>Categorizaciones A1</h3>
                    <div class="valor rojo">{a1_2025}</div>
                    <div class="cambio {"sube" if a1_2025 > a1_2024 else "baja"}">{"+" if a1_2025 > a1_2024 else ""}{((a1_2025-a1_2024)/a1_2024*100):.1f}% vs 2024 ({a1_2024})</div>
                    <div class="detalle">A1 = Maximo riesgo + Dependencia total. Es la categoria de mayor gravedad en la escala CUDYR.</div>
                </div>
                <div class="card">
                    <h3>Categorizaciones A+B totales</h3>
                    <div class="valor rojo">{int(ab_2025):,}</div>
                    <div class="cambio {"sube" if ab_2025 > ab_2024 else "baja"}">{"+" if ab_2025 > ab_2024 else ""}{((ab_2025-ab_2024)/ab_2024*100):.1f}% vs 2024 ({int(ab_2024):,})</div>
                </div>
            </div>
        </div>

        <div class="seccion">
            <h2>Estabilidad de Pacientes</h2>
            <div class="grid">
                <div class="card">
                    <h3>Pacientes que Cambian de Categoria</h3>
                    <div class="valor">{pac_cambian_2025}</div>
                    <div class="cambio {"sube" if pac_cambian_2025 > pac_cambian_2024 else "baja"}">{pct_cambian_2025:.1f}% del total (2024: {pct_cambian_2024:.1f}%)</div>
                    <div class="detalle">De los {pac_2025} pacientes atendidos en 2025, {pac_cambian_2025} fueron
                    categorizados con al menos 2 categorias CUDYR distintas durante su estadia.
                    Esto indica variabilidad en su condicion clinica.</div>
                </div>
                <div class="card">
                    <h3>Pacientes que Empeoran</h3>
                    <div class="valor rojo">{empeoran_2025}</div>
                    <div class="detalle">{total_con_evol_2025} pacientes estuvieron internados 2 o mas dias
                    (tienen 2+ categorizaciones). De esos, {empeoran_2025} egresaron con una categoria de
                    mayor riesgo que la que tenian al ingresar (ej: de B1 a A1).</div>
                </div>
            </div>
        </div>

        <div class="seccion">
            <h2>Detalle Mensual 2025 vs 2024</h2>
            <div class="tabla-container">
                <table>
                    <thead>
                        <tr>
                            <th>Mes</th>
                            <th>Cat. 2024</th>
                            <th>Cat. 2025</th>
                            <th>Diferencia</th>
                            <th>% A+B 2024</th>
                            <th>% A+B 2025</th>
                        </tr>
                    </thead>
                    <tbody>"""

for i in range(1, 13):
    c24 = cat_mes_2024.get(i, 0)
    c25 = cat_mes_2025.get(i, 0)
    d = c25 - c24
    ar24 = ar_mes_2024.get(i, 0)
    ar25 = ar_mes_2025.get(i, 0)
    clase_diff = 'positivo' if d > 0 else ('negativo' if d < 0 else '')
    signo = '+' if d > 0 else ''
    html_index += f"""
                        <tr>
                            <td><strong>{meses[i-1]}</strong></td>
                            <td>{c24}</td>
                            <td>{c25}</td>
                            <td class="{clase_diff}">{signo}{d}</td>
                            <td>{ar24:.1f}%</td>
                            <td>{ar25:.1f}%</td>
                        </tr>"""

html_index += f"""
                    </tbody>
                    <tfoot>
                        <tr style="background: #f8f9fa; font-weight: bold;">
                            <td>TOTAL</td>
                            <td>{total_2024}</td>
                            <td>{total_2025}</td>
                            <td class="positivo">+{total_2025 - total_2024}</td>
                            <td>{pct_ar_2024:.1f}%</td>
                            <td>{pct_ar_2025:.1f}%</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>

        <div class="seccion">
            <h2>Distribucion de Categorias 2025</h2>
            <div class="tabla-container">
                <table>
                    <thead>
                        <tr>
                            <th>Categoria</th>
                            <th>Cantidad 2024</th>
                            <th>Cantidad 2025</th>
                            <th>% del Total 2025</th>
                            <th>Riesgo</th>
                        </tr>
                    </thead>
                    <tbody>"""

# Todas las categorias que aparecen
todas_cat = sorted(set(dist_2024.index.tolist() + dist_2025.index.tolist()))
riesgo_labels = {'A': 'Maximo', 'B': 'Alto', 'C': 'Mediano', 'D': 'Bajo'}

for cat in todas_cat:
    c24 = dist_2024.get(cat, 0)
    c25 = dist_2025.get(cat, 0)
    pct = c25 / total_2025 * 100
    nivel = riesgo_labels.get(cat[0], '?')
    html_index += f"""
                        <tr>
                            <td><strong>{cat}</strong></td>
                            <td>{c24}</td>
                            <td>{c25}</td>
                            <td>{pct:.1f}%</td>
                            <td>{nivel}</td>
                        </tr>"""

html_index += f"""
                    </tbody>
                </table>
            </div>
        </div>

        <div class="nota">
            <strong>Fuente de datos:</strong> Sistema de categorizacion CUDYR.
            Todos los valores corresponden a conteos directos de las categorizaciones
            registradas en el sistema. No se incluyen estimaciones ni proyecciones.
        </div>

        <div class="footer">
            <p>UTI Neuroquirurgica | Datos CUDYR 2024-2025</p>
        </div>
    </div>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_index)

print("    OK - dashboard_utinqx.html generado")
print("    OK - index.html generado")

# ============================================================
# 5. HTML AMBAS UTIs (exposicion de datos, no comparacion)
# ============================================================
print("[5/5] Creando pagina ambas UTIs...")

nav_ambas = get_nav('ambas')

# Tabla mensual para ambas UTIs
tabla_mensual_ambas = ""
for i in range(1, 13):
    nqx24 = cat_mes_2024.get(i, 0)
    nqx25 = cat_mes_2025.get(i, 0)
    qx24 = qx_cat_mes_2024.get(i, 0)
    qx25 = qx_cat_mes_2025.get(i, 0)
    ar_nqx25 = ar_mes_2025.get(i, 0)
    ar_qx25 = qx_ar_mes_2025.get(i, 0)
    tabla_mensual_ambas += f"""
                        <tr>
                            <td><strong>{meses[i-1]}</strong></td>
                            <td>{nqx24}</td>
                            <td>{nqx25}</td>
                            <td>{qx24}</td>
                            <td>{qx25}</td>
                            <td>{ar_nqx25:.1f}%</td>
                            <td>{ar_qx25:.1f}%</td>
                        </tr>"""

# Tabla distribucion categorias ambas UTIs 2025
todas_cat_ambas = sorted(set(
    dist_2025.index.tolist() + qx_dist_2025.index.tolist()
))
tabla_dist_ambas = ""
for cat in todas_cat_ambas:
    nqx = dist_2025.get(cat, 0)
    qx = qx_dist_2025.get(cat, 0)
    pct_nqx = nqx / total_2025 * 100 if total_2025 > 0 else 0
    pct_qx = qx / qx_total_2025 * 100 if qx_total_2025 > 0 else 0
    nivel = riesgo_labels.get(cat[0], '?')
    tabla_dist_ambas += f"""
                        <tr>
                            <td><strong>{cat}</strong></td>
                            <td>{nqx}</td>
                            <td>{pct_nqx:.1f}%</td>
                            <td>{qx}</td>
                            <td>{pct_qx:.1f}%</td>
                            <td>{nivel}</td>
                        </tr>"""

qx_variacion = ((qx_total_2025 - qx_total_2024) / qx_total_2024) * 100

html_ambas = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ambas UTIs - Categorizacion CUDYR 2024-2025</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f0f2f5;
            color: #2c3e50;
            line-height: 1.6;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2em; margin-bottom: 8px; }}
        .header p {{ font-size: 1em; opacity: 0.85; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px 20px; }}

        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px; }}

        .card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }}
        .card h3 {{
            color: #7f8c8d;
            margin-bottom: 8px;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .card .valor {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .card .valor.rojo {{ color: #c0392b; }}
        .card .cambio {{
            font-size: 0.9em;
            margin-top: 6px;
            padding: 3px 8px;
            border-radius: 4px;
            display: inline-block;
        }}
        .card .cambio.sube {{ background: #fce4e4; color: #c0392b; }}
        .card .cambio.baja {{ background: #d5f5d5; color: #27ae60; }}
        .card .cambio.neutro {{ background: #eee; color: #666; }}
        .card .detalle {{ color: #95a5a6; font-size: 0.88em; margin-top: 8px; }}
        .card .unidad-label {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .label-nqx {{ background: #e8f4fd; color: #2980b9; }}
        .label-qx {{ background: #fdebd0; color: #e67e22; }}

        .seccion {{ margin-bottom: 30px; }}
        .seccion h2 {{
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e0e0e0;
        }}

        .tabla-container {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            overflow-x: auto;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.92em; }}
        th {{ background: #2c3e50; color: white; padding: 10px 12px; text-align: center; }}
        th.nqx {{ background: #2980b9; }}
        th.qx {{ background: #e67e22; }}
        td {{ padding: 8px 12px; text-align: center; border-bottom: 1px solid #ecf0f1; }}
        tr:hover {{ background: #f8f9fa; }}

        .nota {{
            background: #fef9e7;
            border-left: 4px solid #f39c12;
            padding: 15px;
            border-radius: 0 8px 8px 0;
            margin-top: 20px;
            font-size: 0.9em;
            color: #7d6608;
        }}
        .footer {{
            text-align: center;
            padding: 25px;
            color: #95a5a6;
            font-size: 0.85em;
        }}

        @media (max-width: 768px) {{
            .grid-2 {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    {nav_ambas}
    <div class="header">
        <h1>Categorizacion CUDYR - Ambas UTIs</h1>
        <p>Datos de categorizacion 2024-2025 | UTI Neuroquirurgica</p>
    </div>

    <div class="container">

        <!-- VOLUMEN GENERAL -->
        <div class="seccion">
            <h2>Volumen de Actividad por Unidad</h2>
            <div class="grid-2">
                <div class="card">
                    <span class="unidad-label label-nqx">UTINQX</span>
                    <h3>Total Categorizaciones</h3>
                    <div class="valor">{total_2025:,}</div>
                    <div class="cambio sube">+{variacion_anual:.1f}% vs 2024 ({total_2024:,})</div>
                    <div class="detalle">{pac_2025} pacientes unicos atendidos en 2025 (2024: {pac_2024})</div>
                </div>
                <div class="card">
                    <span class="unidad-label label-qx">UTIQX</span>
                    <h3>Total Categorizaciones</h3>
                    <div class="valor">{qx_total_2025:,}</div>
                    <div class="cambio {"sube" if qx_variacion > 0 else "baja"}">{"+" if qx_variacion > 0 else ""}{qx_variacion:.1f}% vs 2024 ({qx_total_2024:,})</div>
                    <div class="detalle">{qx_pac_2025} pacientes unicos atendidos en 2025 (2024: {qx_pac_2024})</div>
                </div>
            </div>
        </div>

        <!-- PERFIL DE RIESGO -->
        <div class="seccion">
            <h2>Perfil de Riesgo por Unidad (2025)</h2>
            <div class="grid">
                <div class="card">
                    <span class="unidad-label label-nqx">UTINQX</span>
                    <h3>% Alto Riesgo (A+B)</h3>
                    <div class="valor rojo">{pct_ar_2025:.1f}%</div>
                    <div class="detalle">{int(ab_2025):,} categorizaciones A+B de {total_2025:,} totales</div>
                </div>
                <div class="card">
                    <span class="unidad-label label-qx">UTIQX</span>
                    <h3>% Alto Riesgo (A+B)</h3>
                    <div class="valor rojo">{qx_pct_ar_2025:.1f}%</div>
                    <div class="detalle">{int(qx_ab_2025):,} categorizaciones A+B de {qx_total_2025:,} totales</div>
                </div>
                <div class="card">
                    <span class="unidad-label label-nqx">UTINQX</span>
                    <h3>Categorizaciones A1</h3>
                    <div class="valor rojo">{a1_2025}</div>
                    <div class="detalle">Maximo riesgo + dependencia total (2024: {a1_2024})</div>
                </div>
                <div class="card">
                    <span class="unidad-label label-qx">UTIQX</span>
                    <h3>Categorizaciones A1</h3>
                    <div class="valor rojo">{qx_a1_2025}</div>
                    <div class="detalle">Maximo riesgo + dependencia total (2024: {qx_a1_2024})</div>
                </div>
            </div>
        </div>

        <!-- ESTADIA -->
        <div class="seccion">
            <h2>Categorizaciones por Paciente</h2>
            <div class="grid-2">
                <div class="card">
                    <span class="unidad-label label-nqx">UTINQX</span>
                    <h3>Promedio cat. por paciente</h3>
                    <div class="valor">{estadia_2025:.1f}</div>
                    <div class="detalle">Equivale aprox. a dias de internacion promedio. En 2024 fue {estadia_2024:.1f}.</div>
                </div>
                <div class="card">
                    <span class="unidad-label label-qx">UTIQX</span>
                    <h3>Promedio cat. por paciente</h3>
                    <div class="valor">{qx_estadia_2025:.1f}</div>
                    <div class="detalle">Equivale aprox. a dias de internacion promedio. En 2024 fue {qx_estadia_2024:.1f}.</div>
                </div>
            </div>
        </div>

        <!-- TABLA MENSUAL AMBAS -->
        <div class="seccion">
            <h2>Detalle Mensual 2024-2025</h2>
            <div class="tabla-container">
                <table>
                    <thead>
                        <tr>
                            <th rowspan="2">Mes</th>
                            <th class="nqx" colspan="2">UTINQX</th>
                            <th class="qx" colspan="2">UTIQX</th>
                            <th class="nqx">% A+B UTINQX</th>
                            <th class="qx">% A+B UTIQX</th>
                        </tr>
                        <tr>
                            <th class="nqx">2024</th>
                            <th class="nqx">2025</th>
                            <th class="qx">2024</th>
                            <th class="qx">2025</th>
                            <th class="nqx">2025</th>
                            <th class="qx">2025</th>
                        </tr>
                    </thead>
                    <tbody>{tabla_mensual_ambas}
                    </tbody>
                    <tfoot>
                        <tr style="background: #f8f9fa; font-weight: bold;">
                            <td>TOTAL</td>
                            <td>{total_2024}</td>
                            <td>{total_2025}</td>
                            <td>{qx_total_2024}</td>
                            <td>{qx_total_2025}</td>
                            <td>{pct_ar_2025:.1f}%</td>
                            <td>{qx_pct_ar_2025:.1f}%</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>

        <!-- DISTRIBUCION CATEGORIAS AMBAS -->
        <div class="seccion">
            <h2>Distribucion de Categorias 2025</h2>
            <div class="tabla-container">
                <table>
                    <thead>
                        <tr>
                            <th rowspan="2">Categoria</th>
                            <th class="nqx" colspan="2">UTINQX</th>
                            <th class="qx" colspan="2">UTIQX</th>
                            <th rowspan="2">Riesgo</th>
                        </tr>
                        <tr>
                            <th class="nqx">Cantidad</th>
                            <th class="nqx">%</th>
                            <th class="qx">Cantidad</th>
                            <th class="qx">%</th>
                        </tr>
                    </thead>
                    <tbody>{tabla_dist_ambas}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="nota">
            <strong>Fuente de datos:</strong> Sistema de categorizacion CUDYR.
            Todos los valores corresponden a conteos directos de las categorizaciones
            registradas en el sistema. No se incluyen estimaciones ni proyecciones.
            Cada unidad se presenta con sus propios datos para su lectura independiente.
        </div>

        <div class="footer">
            <p>UTI Neuroquirurgica | Datos CUDYR 2024-2025</p>
        </div>
    </div>
</body>
</html>"""

with open("ambas_uti.html", "w", encoding="utf-8") as f:
    f.write(html_ambas)

print("    OK - ambas_uti.html generado")
print("\n" + "=" * 50)
print("Archivos generados:")
print("  - index.html (resumen UTINQX)")
print("  - dashboard_utinqx.html (dashboard interactivo UTINQX)")
print("  - ambas_uti.html (datos ambas UTIs)")
print("=" * 50)
