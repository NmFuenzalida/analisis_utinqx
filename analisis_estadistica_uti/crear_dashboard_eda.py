"""
Genera dashboard HTML interactivo con los resultados del EDA
de Estadística UTI Quirúrgica y Neuroquirúrgica 2024-2025.
Lee el dataset limpio exportado por el notebook.
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ── Cargar datos limpios ──────────────────────────────────────────
df = pd.read_csv('eda_outputs/dataset_limpio_anonimizado.csv',
                 parse_dates=['INGRESO', 'EGRESO'])

# ── Métricas globales ─────────────────────────────────────────────
metrics = {}
for uti in ['UTIQX', 'UTINQX']:
    s = df[df.UTI == uti]
    metrics[uti] = {
        'n': len(s),
        'edad_mean': round(s.EDAD.mean(), 1),
        'edad_median': s.EDAD.median(),
        'pct_m': round((s.GENERO == 'M').mean() * 100, 1),
        'apache_mean': round(s.APACHE_II.mean(), 1),
        'apache_median': s.APACHE_II.median(),
        'apache_p95': round(s.APACHE_II.quantile(0.95), 1),
        'los_mean': round(s.DIAS_ESTADIA.mean(), 1),
        'los_median': s.DIAS_ESTADIA.median(),
        'los_p95': round(s.DIAS_ESTADIA.quantile(0.95), 1),
        'mort': round(s.FALLECIDO.mean() * 100, 2),
        'patient_days': int(s.DIAS_ESTADIA.sum()),
    }

m_qx = metrics['UTIQX']
m_nqx = metrics['UTINQX']

# ── Colores ───────────────────────────────────────────────────────
C_QX = '#1f77b4'
C_NQX = '#ff7f0e'
C_BG = '#f8f9fa'

# ── Funciones helper ──────────────────────────────────────────────
def card_html(title, val_qx, val_nqx, unit='', highlight_higher=True):
    """Genera HTML de una tarjeta comparativa."""
    diff = val_nqx - val_qx if isinstance(val_qx, (int, float)) else 0
    arrow = '▲' if diff > 0 else '▼' if diff < 0 else '─'
    color_diff = '#dc3545' if (diff > 0 and highlight_higher) else '#28a745' if (diff < 0 and highlight_higher) else '#6c757d'
    return f"""
    <div class="card">
        <div class="card-title">{title}</div>
        <div class="card-row">
            <div class="card-val" style="color:{C_QX}">UTIQX<br><strong>{val_qx}{unit}</strong></div>
            <div class="card-diff" style="color:{color_diff}">{arrow} {abs(diff):.1f}{unit}</div>
            <div class="card-val" style="color:{C_NQX}">UTINQX<br><strong>{val_nqx}{unit}</strong></div>
        </div>
    </div>"""

# ── Gráficos Plotly ───────────────────────────────────────────────

# 1. Distribución APACHE II
fig_apache = go.Figure()
for uti, color in [('UTIQX', C_QX), ('UTINQX', C_NQX)]:
    s = df[df.UTI == uti]['APACHE_II']
    fig_apache.add_trace(go.Histogram(x=s, name=uti, opacity=0.6,
                                       marker_color=color, nbinsx=30))
fig_apache.update_layout(title='Distribución APACHE II', barmode='overlay',
                          xaxis_title='APACHE II', yaxis_title='Frecuencia',
                          template='plotly_white', height=350, margin=dict(t=40, b=40))

# 2. Distribución LOS
fig_los = go.Figure()
for uti, color in [('UTIQX', C_QX), ('UTINQX', C_NQX)]:
    s = df[(df.UTI == uti) & (df.DIAS_ESTADIA <= 30)]['DIAS_ESTADIA']
    fig_los.add_trace(go.Histogram(x=s, name=uti, opacity=0.6,
                                    marker_color=color, nbinsx=30))
fig_los.update_layout(title='Distribución Días Estadía (≤30d)', barmode='overlay',
                       xaxis_title='Días', yaxis_title='Frecuencia',
                       template='plotly_white', height=350, margin=dict(t=40, b=40))

# 3. Severidad APACHE por UTI (barras agrupadas %)
sev_order = ['Leve (0-10)', 'Moderado (11-20)', 'Severo (21-30)', 'Muy severo (31+)']
fig_sev = go.Figure()
for uti, color in [('UTIQX', C_QX), ('UTINQX', C_NQX)]:
    s = df[df.UTI == uti]
    counts = s.SEVERIDAD_APACHE.value_counts()
    pcts = [(counts.get(cat, 0) / len(s) * 100) for cat in sev_order]
    fig_sev.add_trace(go.Bar(x=sev_order, y=pcts, name=uti, marker_color=color,
                              text=[f'{p:.1f}%' for p in pcts], textposition='auto'))
fig_sev.update_layout(title='Distribución de Severidad APACHE II (%)', barmode='group',
                       yaxis_title='%', template='plotly_white', height=350,
                       margin=dict(t=40, b=40))

# 4. Mortalidad por severidad
fig_mort_sev = make_subplots(rows=1, cols=2, subplot_titles=['UTIQX', 'UTINQX'])
for i, (uti, color) in enumerate([('UTIQX', C_QX), ('UTINQX', C_NQX)], 1):
    s = df[df.UTI == uti]
    mort = s.groupby('SEVERIDAD_APACHE')['FALLECIDO'].agg(['sum', 'count'])
    mort['tasa'] = (mort['sum'] / mort['count'] * 100).round(1)
    mort = mort.reindex(sev_order)
    fig_mort_sev.add_trace(go.Bar(
        x=sev_order, y=mort['tasa'].values, marker_color=color,
        text=[f"{t:.1f}% (n={int(n)})" for t, n in zip(mort['tasa'].values, mort['count'].values)],
        textposition='auto', showlegend=False
    ), row=1, col=i)
fig_mort_sev.update_layout(title='Mortalidad % por Severidad APACHE',
                            template='plotly_white', height=350, margin=dict(t=60, b=40))
fig_mort_sev.update_yaxes(title_text='Mortalidad %')

# 5. Diagnósticos agrupados
fig_dx = make_subplots(rows=1, cols=2, subplot_titles=['UTIQX', 'UTINQX'])
for i, (uti, color) in enumerate([('UTIQX', C_QX), ('UTINQX', C_NQX)], 1):
    s = df[df.UTI == uti]
    vc = s.CATEGORIA_DX.value_counts().head(10)
    fig_dx.add_trace(go.Bar(
        y=vc.index[::-1], x=vc.values[::-1], orientation='h',
        marker_color=color, showlegend=False,
        text=vc.values[::-1], textposition='auto'
    ), row=1, col=i)
fig_dx.update_layout(title='Top 10 Categorías Diagnósticas', template='plotly_white',
                      height=400, margin=dict(t=60, b=40, l=180))

# 6. Ingresos mensuales
df['ANIO_MES'] = df['INGRESO'].dt.to_period('M').astype(str)
monthly = df.groupby(['ANIO_MES', 'UTI']).size().unstack(fill_value=0)
fig_monthly = go.Figure()
for uti, color in [('UTIQX', C_QX), ('UTINQX', C_NQX)]:
    fig_monthly.add_trace(go.Bar(x=monthly.index.tolist(), y=monthly[uti].values,
                                  name=uti, marker_color=color))
fig_monthly.update_layout(title='Ingresos Mensuales por UTI', barmode='group',
                           xaxis_title='Período', yaxis_title='N° Ingresos',
                           template='plotly_white', height=350, margin=dict(t=40, b=60))

# 7. APACHE II mensual trend
monthly_apache = df.groupby(['ANIO_MES', 'UTI'])['APACHE_II'].mean().unstack()
fig_apache_trend = go.Figure()
for uti, color in [('UTIQX', C_QX), ('UTINQX', C_NQX)]:
    fig_apache_trend.add_trace(go.Scatter(
        x=monthly_apache.index.tolist(), y=monthly_apache[uti].values,
        mode='lines+markers', name=uti, line=dict(color=color)))
fig_apache_trend.update_layout(title='Tendencia APACHE II Promedio Mensual',
                                xaxis_title='Período', yaxis_title='APACHE II medio',
                                template='plotly_white', height=350, margin=dict(t=40, b=60))

# 8. Flujo: Procedencia y Destino (Sankey-like barras)
fig_flujo = make_subplots(rows=2, cols=2,
                           subplot_titles=['Procedencia - UTIQX', 'Procedencia - UTINQX',
                                          'Destino - UTIQX', 'Destino - UTINQX'])
for i, (uti, color) in enumerate([('UTIQX', C_QX), ('UTINQX', C_NQX)], 1):
    s = df[df.UTI == uti]
    # Procedencia
    vc_p = s.PROC_GRUPO.value_counts().head(8)
    fig_flujo.add_trace(go.Bar(y=vc_p.index[::-1], x=vc_p.values[::-1], orientation='h',
                                marker_color=color, showlegend=False,
                                text=vc_p.values[::-1], textposition='auto'), row=1, col=i)
    # Destino
    vc_d = s.DEST_GRUPO.value_counts().head(8)
    fig_flujo.add_trace(go.Bar(y=vc_d.index[::-1], x=vc_d.values[::-1], orientation='h',
                                marker_color=color, showlegend=False,
                                text=vc_d.values[::-1], textposition='auto'), row=2, col=i)
fig_flujo.update_layout(title='Flujo de Pacientes: Procedencia y Destino',
                         template='plotly_white', height=700, margin=dict(t=60, b=40, l=160))

# 9. Grupo etario
edad_order = ['<18', '18-39', '40-59', '60-74', '75+']
fig_edad = go.Figure()
for uti, color in [('UTIQX', C_QX), ('UTINQX', C_NQX)]:
    s = df[df.UTI == uti]
    counts = s.GRUPO_ETARIO.value_counts()
    pcts = [(counts.get(cat, 0) / len(s) * 100) for cat in edad_order]
    fig_edad.add_trace(go.Bar(x=edad_order, y=pcts, name=uti, marker_color=color,
                               text=[f'{p:.1f}%' for p in pcts], textposition='auto'))
fig_edad.update_layout(title='Distribución por Grupo Etario (%)', barmode='group',
                        yaxis_title='%', template='plotly_white', height=350,
                        margin=dict(t=40, b=40))

# 10. Scatter APACHE vs LOS
fig_scatter = make_subplots(rows=1, cols=2, subplot_titles=['UTIQX', 'UTINQX'])
for i, (uti, color) in enumerate([('UTIQX', C_QX), ('UTINQX', C_NQX)], 1):
    s = df[(df.UTI == uti) & (df.DIAS_ESTADIA <= 40)]
    fig_scatter.add_trace(go.Scatter(
        x=s.APACHE_II, y=s.DIAS_ESTADIA, mode='markers',
        marker=dict(color=color, opacity=0.3, size=5),
        showlegend=False
    ), row=1, col=i)
fig_scatter.update_layout(title='APACHE II vs Días Estadía',
                           template='plotly_white', height=350, margin=dict(t=60, b=40))
fig_scatter.update_xaxes(title_text='APACHE II')
fig_scatter.update_yaxes(title_text='Días Estadía')

# ── Generar HTML ──────────────────────────────────────────────────
plots_html = ''.join([
    f'<div class="plot-container">{fig.to_html(full_html=False, include_plotlyjs=False)}</div>'
    for fig in [fig_apache, fig_los, fig_sev, fig_mort_sev, fig_edad, fig_dx,
                fig_monthly, fig_apache_trend, fig_scatter, fig_flujo]
])

# Navegación
nav_html = """
<nav class="nav-bar">
    <a href="../analisis_categorizacion/index.html">Resumen UTINQX</a>
    <a href="../analisis_categorizacion/dashboard_utinqx.html">Dashboard UTINQX</a>
    <a href="../analisis_categorizacion/ambas_uti.html">Ambas UTI (Categorización)</a>
    <a href="dashboard_eda.html" class="active">EDA Estadística UTI</a>
</nav>"""

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EDA — Estadística UTI 2024-2025</title>
<script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: {C_BG}; color: #212529; }}

.nav-bar {{
    display: flex; gap: 0; background: #2c3e50; padding: 0;
    position: sticky; top: 0; z-index: 100;
}}
.nav-bar a {{
    color: #ecf0f1; text-decoration: none; padding: 14px 24px;
    font-size: 14px; font-weight: 500; transition: background .2s;
}}
.nav-bar a:hover {{ background: #34495e; }}
.nav-bar a.active {{ background: #e67e22; color: #fff; }}

.container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}

h1 {{ text-align: center; margin: 20px 0 5px; font-size: 1.8rem; color: #2c3e50; }}
.subtitle {{ text-align: center; color: #6c757d; margin-bottom: 25px; font-size: 0.95rem; }}

.cards-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px; margin-bottom: 30px;
}}
.card {{
    background: #fff; border-radius: 12px; padding: 18px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
}}
.card-title {{ font-size: 0.85rem; color: #6c757d; text-transform: uppercase;
               letter-spacing: 0.5px; margin-bottom: 10px; }}
.card-row {{ display: flex; align-items: center; justify-content: center; gap: 15px; }}
.card-val {{ font-size: 0.9rem; }}
.card-val strong {{ font-size: 1.4rem; display: block; }}
.card-diff {{ font-size: 1.1rem; font-weight: bold; }}

.section-title {{
    font-size: 1.2rem; color: #2c3e50; margin: 30px 0 15px;
    padding-bottom: 8px; border-bottom: 2px solid #e67e22;
}}

.plot-container {{ background: #fff; border-radius: 12px; padding: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px; }}

.stats-table {{
    width: 100%; border-collapse: collapse; margin-bottom: 20px;
    background: #fff; border-radius: 12px; overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}}
.stats-table th {{ background: #2c3e50; color: #fff; padding: 10px 15px;
                    text-align: left; font-size: 0.85rem; }}
.stats-table td {{ padding: 8px 15px; border-bottom: 1px solid #eee; font-size: 0.9rem; }}
.stats-table tr:last-child td {{ border-bottom: none; }}
.stats-table tr:hover {{ background: #f1f3f5; }}

.sig {{ color: #dc3545; font-weight: bold; }}
.ns {{ color: #6c757d; }}

.findings {{
    background: #fff3cd; border-left: 4px solid #e67e22; padding: 20px;
    border-radius: 0 12px 12px 0; margin: 20px 0;
}}
.findings h3 {{ color: #856404; margin-bottom: 10px; }}
.findings li {{ margin: 5px 0; color: #856404; }}

footer {{ text-align: center; color: #adb5bd; padding: 30px; font-size: 0.8rem; }}
</style>
</head>
<body>

{nav_html}

<div class="container">
<h1>EDA — Estadística UTI 2024-2025</h1>
<p class="subtitle">Análisis exploratorio comparativo: UTI Quirúrgica vs UTI Neuroquirúrgica | Datos anonimizados | n={len(df)}</p>

<!-- ═══ INDICADORES ═══ -->
<h2 class="section-title">Indicadores Clave</h2>
<div class="cards-grid">
    {card_html('Registros', m_qx['n'], m_nqx['n'], '', False)}
    {card_html('Edad Media', m_qx['edad_mean'], m_nqx['edad_mean'], ' años', False)}
    {card_html('% Masculino', m_qx['pct_m'], m_nqx['pct_m'], '%', False)}
    {card_html('APACHE II Media', m_qx['apache_mean'], m_nqx['apache_mean'], '', True)}
    {card_html('APACHE II p95', m_qx['apache_p95'], m_nqx['apache_p95'], '', True)}
    {card_html('LOS Media', m_qx['los_mean'], m_nqx['los_mean'], ' d', True)}
    {card_html('LOS p95', m_qx['los_p95'], m_nqx['los_p95'], ' d', True)}
    {card_html('Mortalidad', m_qx['mort'], m_nqx['mort'], '%', True)}
    {card_html('Patient-Days', m_qx['patient_days'], m_nqx['patient_days'], '', False)}
</div>

<!-- ═══ TESTS ESTADÍSTICOS ═══ -->
<h2 class="section-title">Tests Estadísticos (UTIQX vs UTINQX)</h2>
<table class="stats-table">
<tr><th>Variable</th><th>Test</th><th>Estadístico</th><th>p-valor</th><th>Significancia</th></tr>
"""

# Agregar tests estadísticos
from scipy.stats import mannwhitneyu, chi2_contingency

qx = df[df.UTI == 'UTIQX']
nqx = df[df.UTI == 'UTINQX']

for col, label in [('EDAD', 'Edad'), ('APACHE_II', 'APACHE II'), ('DIAS_ESTADIA', 'Días Estadía')]:
    stat, p = mannwhitneyu(qx[col].dropna(), nqx[col].dropna(), alternative='two-sided')
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
    cls = 'sig' if p < 0.05 else 'ns'
    html += f'<tr><td>{label}</td><td>Mann-Whitney U</td><td>{stat:.0f}</td><td>{p:.6f}</td><td class="{cls}">{sig}</td></tr>\n'

for col, label in [('GENERO', 'Género'), ('CONDICION_EGRESO', 'Cond. Egreso'),
                    ('SEVERIDAD_APACHE', 'Severidad APACHE'), ('GRUPO_ETARIO', 'Grupo Etario'),
                    ('CATEGORIA_DX', 'Categoría Dx')]:
    ct = pd.crosstab(df['UTI'], df[col])
    chi2, p, dof, _ = chi2_contingency(ct)
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
    cls = 'sig' if p < 0.05 else 'ns'
    html += f'<tr><td>{label}</td><td>Chi² (dof={dof})</td><td>{chi2:.2f}</td><td>{p:.6f}</td><td class="{cls}">{sig}</td></tr>\n'

html += """</table>
<p style="font-size:0.8rem;color:#6c757d">* p&lt;0.05 &nbsp; ** p&lt;0.01 &nbsp; *** p&lt;0.001 &nbsp; ns: no significativo</p>

<!-- ═══ HALLAZGOS ═══ -->
<div class="findings">
<h3>Hallazgos Principales</h3>
<ul>
<li><strong>APACHE II significativamente mayor en UTINQX</strong> (p&lt;0.001): mayor severidad clínica en la unidad neuroquirúrgica.</li>
<li><strong>Perfil diagnóstico diferenciado</strong> (p&lt;0.001): UTINQX concentra patología neurológica y oncológica; UTIQX es más diversa.</li>
<li><strong>Distribución de severidad distinta</strong> (p&lt;0.001): UTINQX tiene mayor proporción de pacientes moderados y severos.</li>
<li><strong>Edad y género sin diferencias significativas</strong>: ambas poblaciones son demográficamente similares.</li>
<li><strong>LOS sin diferencia significativa</strong>, pero con mayor complejidad por paciente en UTINQX.</li>
<li><strong>Mortalidad mayor en UTINQX</strong>, concentrada en los estratos de severidad más altos.</li>
</ul>
</div>

<!-- ═══ GRÁFICOS ═══ -->
<h2 class="section-title">Distribuciones</h2>
"""

html += plots_html

html += """
</div>

<footer>
    EDA Estadística UTI 2024-2025 — Datos anonimizados — Generado automáticamente
</footer>
</body>
</html>"""

with open('dashboard_eda.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Dashboard generado: dashboard_eda.html')
print(f'Datos: {len(df)} registros ({len(qx)} UTIQX + {len(nqx)} UTINQX)')
