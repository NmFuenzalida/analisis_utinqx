"""
Genera dos dashboards HTML estratégicos:
1. reporte_justificacion_utinqx.html — Evidencia clínica para justificar segundo enfermero
2. dashboard_comparativo_clinico.html — Comparación de perfiles UTINQX vs UTIQX
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import mannwhitneyu, chi2_contingency

# ── Cargar datos ─────────────────────────────────────────────────
df = pd.read_csv('eda_outputs/dataset_limpio_anonimizado.csv',
                 parse_dates=['INGRESO', 'EGRESO'])
nqx = df[df.UTI == 'UTINQX'].copy()
qx = df[df.UTI == 'UTIQX'].copy()

# ── Paleta ───────────────────────────────────────────────────────
C_NQX = '#e67e22'
C_QX = '#1f77b4'
C_ACCENT = '#c0392b'
C_OK = '#27ae60'
C_BG = '#f8f9fa'

sev_order = ['Leve (0-10)', 'Moderado (11-20)', 'Severo (21-30)', 'Muy severo (31+)']
edad_order = ['<18', '18-39', '40-59', '60-74', '75+']
estadia_order = ['Corta (<2d)', 'Media (2-4d)', 'Larga (5-9d)', 'Prolongada (10+d)']

# ── Estadísticas UTINQX ─────────────────────────────────────────
n_total = len(nqx)
apache_mean = round(nqx.APACHE_II.mean(), 1)
apache_std = round(nqx.APACHE_II.std(), 1)
apache_median = nqx.APACHE_II.median()
apache_p75 = nqx.APACHE_II.quantile(0.75)
apache_p90 = nqx.APACHE_II.quantile(0.90)
apache_p95 = nqx.APACHE_II.quantile(0.95)
los_mean = round(nqx.DIAS_ESTADIA.mean(), 1)
los_median = nqx.DIAS_ESTADIA.median()
los_p75 = nqx.DIAS_ESTADIA.quantile(0.75)
los_p90 = nqx.DIAS_ESTADIA.quantile(0.90)
los_p95 = nqx.DIAS_ESTADIA.quantile(0.95)
edad_mean = round(nqx.EDAD.mean(), 1)
mort_pct = round(nqx.FALLECIDO.mean() * 100, 2)
n_fallecidos = int(nqx.FALLECIDO.sum())
patient_days = int(nqx.DIAS_ESTADIA.sum())
# Calcular meses reales con datos
n_meses_nqx = nqx.INGRESO.dt.to_period('M').nunique()
avg_monthly = round(n_total / n_meses_nqx, 1)
anio_min = int(nqx.INGRESO.dt.year.min())
anio_max = int(nqx.INGRESO.dt.year.max())
periodo_label = f'{anio_min}-{anio_max}' if anio_min != anio_max else str(anio_min)
pct_masculino = round((nqx.GENERO == 'M').mean() * 100, 1)

# Severity
mod_plus = len(nqx[nqx.SEVERIDAD_APACHE.isin(['Moderado (11-20)', 'Severo (21-30)', 'Muy severo (31+)'])]) / n_total * 100
severo_plus = len(nqx[nqx.SEVERIDAD_APACHE.isin(['Severo (21-30)', 'Muy severo (31+)'])]) / n_total * 100

# Mortality by severity
mort_by_sev = {}
for cat in sev_order:
    sub = nqx[nqx.SEVERIDAD_APACHE == cat]
    if len(sub) > 0:
        mort_by_sev[cat] = {
            'n': len(sub),
            'fallecidos': int(sub.FALLECIDO.sum()),
            'tasa': round(sub.FALLECIDO.mean() * 100, 1)
        }

# Comparative stats
apache_mean_qx = round(qx.APACHE_II.mean(), 1)
mod_plus_qx = len(qx[qx.SEVERIDAD_APACHE.isin(['Moderado (11-20)', 'Severo (21-30)', 'Muy severo (31+)'])]) / len(qx) * 100
mort_qx = round(qx.FALLECIDO.mean() * 100, 2)

# Statistical tests
u_stat_apache, p_apache = mannwhitneyu(qx.APACHE_II.dropna(), nqx.APACHE_II.dropna())
ct_sev = pd.crosstab(df['UTI'], df['SEVERIDAD_APACHE'])
chi2_sev, p_sev, _, _ = chi2_contingency(ct_sev)
ct_dx = pd.crosstab(df['UTI'], df['CATEGORIA_DX'])
chi2_dx, p_dx, _, _ = chi2_contingency(ct_dx)

# ═══════════════════════════════════════════════════════════════════
# HTML 1: REPORTE JUSTIFICACIÓN UTINQX
# ═══════════════════════════════════════════════════════════════════

# Charts for UTINQX report

# 1. Severity distribution UTINQX (pie)
sev_counts = nqx.SEVERIDAD_APACHE.value_counts().reindex(sev_order).fillna(0)
fig_sev_pie = go.Figure(go.Pie(
    labels=sev_order, values=sev_counts.values,
    marker=dict(colors=['#27ae60', '#f39c12', '#e74c3c', '#8e44ad']),
    textinfo='label+percent', textposition='outside',
    hole=0.4, pull=[0, 0.05, 0.1, 0.15]
))
fig_sev_pie.update_layout(
    title=dict(text='Distribución de Severidad APACHE II', x=0.5),
    template='plotly_white', height=400, showlegend=False,
    margin=dict(t=60, b=40, l=40, r=40),
    annotations=[dict(text=f'n={n_total}', x=0.5, y=0.5, font_size=16, showarrow=False)]
)

# 2. APACHE histogram UTINQX
fig_apache_hist = go.Figure()
fig_apache_hist.add_trace(go.Histogram(
    x=nqx.APACHE_II, nbinsx=25, marker_color=C_NQX, opacity=0.85,
    name='UTINQX'
))
fig_apache_hist.add_vline(x=apache_mean, line_dash='dash', line_color=C_ACCENT,
                          annotation_text=f'Media: {apache_mean}')
fig_apache_hist.update_layout(
    title='Distribución de Scores APACHE II en UTINQX',
    xaxis_title='Score APACHE II', yaxis_title='Cantidad de pacientes',
    template='plotly_white', height=350, margin=dict(t=60, b=40)
)

# 3. Mortality by severity (bar)
fig_mort_sev = go.Figure()
cats_with_data = [c for c in sev_order if c in mort_by_sev]
tasas = [mort_by_sev[c]['tasa'] for c in cats_with_data]
ns = [mort_by_sev[c]['n'] for c in cats_with_data]
falls = [mort_by_sev[c]['fallecidos'] for c in cats_with_data]
fig_mort_sev.add_trace(go.Bar(
    x=cats_with_data, y=tasas,
    marker_color=['#27ae60', '#f39c12', '#e74c3c', '#8e44ad'][:len(cats_with_data)],
    text=[f'{t}%<br>(n={n})' for t, n in zip(tasas, ns)],
    textposition='outside'
))
fig_mort_sev.update_layout(
    title='Tasa de Mortalidad según Severidad APACHE II',
    xaxis_title='Categoría de severidad', yaxis_title='Mortalidad (%)',
    template='plotly_white', height=380, margin=dict(t=60, b=40),
    yaxis=dict(range=[0, max(tasas)*1.3 if tasas else 50])
)

# 4. Monthly admissions trend (by ANIO-MES, not summed)
nqx['ANIO_MES'] = nqx['INGRESO'].dt.to_period('M').astype(str)
monthly_nqx = nqx.groupby('ANIO_MES').size()
fig_monthly = go.Figure()
# Colorear barras: rojo desde el mes donde inicia el aumento sostenido (2025-06)
bar_colors = [C_ACCENT if m >= '2025-06' else C_NQX for m in monthly_nqx.index]
fig_monthly.add_trace(go.Bar(
    x=monthly_nqx.index.tolist(),
    y=monthly_nqx.values,
    marker_color=bar_colors,
    text=monthly_nqx.values, textposition='outside'
))
fig_monthly.add_hline(y=avg_monthly, line_dash='dash', line_color=C_ACCENT,
                      annotation_text=f'Promedio: {avg_monthly}/mes')
fig_monthly.update_layout(
    title=f'Ingresos Mensuales a UTINQX ({periodo_label})',
    xaxis_title='Período', yaxis_title='Cantidad de ingresos',
    template='plotly_white', height=380, margin=dict(t=60, b=80),
    xaxis=dict(tickangle=-45)
)

# 5. APACHE trend by month (by ANIO-MES)
apache_monthly = nqx.groupby('ANIO_MES')['APACHE_II'].mean().round(1)
fig_apache_trend = go.Figure()
fig_apache_trend.add_trace(go.Scatter(
    x=apache_monthly.index.tolist(),
    y=apache_monthly.values,
    mode='lines+markers',
    line=dict(color=C_NQX, width=2.5),
    marker=dict(size=7)
))
fig_apache_trend.add_hline(y=apache_mean, line_dash='dot', line_color='#7f8c8d',
                           annotation_text=f'Media global: {apache_mean}')
fig_apache_trend.update_layout(
    title='Tendencia Mensual del Score APACHE II Promedio',
    xaxis_title='Período', yaxis_title='APACHE II promedio',
    template='plotly_white', height=380, margin=dict(t=60, b=80),
    xaxis=dict(tickangle=-45)
)

# 6. Diagnosis categories (horizontal bar)
dx_counts = nqx.CATEGORIA_DX.value_counts()
dx_counts = dx_counts[dx_counts.index != 'NO REGISTRADO'].head(10)
fig_dx = go.Figure()
fig_dx.add_trace(go.Bar(
    y=dx_counts.index[::-1], x=dx_counts.values[::-1],
    orientation='h', marker_color=C_NQX,
    text=[f'{v} ({v/n_total*100:.1f}%)' for v in dx_counts.values[::-1]],
    textposition='outside'
))
fig_dx.update_layout(
    title='Categorías Diagnósticas más Frecuentes',
    xaxis_title='Cantidad de pacientes', template='plotly_white',
    height=400, margin=dict(t=60, b=40, l=180)
)

# 7. Length of stay distribution
fig_los = go.Figure()
nqx_los30 = nqx[nqx.DIAS_ESTADIA <= 30]
fig_los.add_trace(go.Histogram(
    x=nqx_los30.DIAS_ESTADIA, nbinsx=30, marker_color=C_NQX, opacity=0.85
))
fig_los.add_vline(x=los_mean, line_dash='dash', line_color=C_ACCENT,
                  annotation_text=f'Media: {los_mean}d')
fig_los.update_layout(
    title='Distribución de Días de Estadía en UTINQX',
    xaxis_title='Días de estadía', yaxis_title='Cantidad de pacientes',
    template='plotly_white', height=350, margin=dict(t=60, b=40)
)

# 8. Estadia category pie
est_counts = nqx.CAT_ESTADIA.value_counts().reindex(estadia_order).fillna(0)
fig_est_pie = go.Figure(go.Pie(
    labels=estadia_order, values=est_counts.values,
    marker=dict(colors=['#27ae60', '#3498db', '#f39c12', '#e74c3c']),
    textinfo='label+percent', textposition='outside', hole=0.4
))
fig_est_pie.update_layout(
    title=dict(text='Categorías de Estadía', x=0.5),
    template='plotly_white', height=380, showlegend=False,
    margin=dict(t=60, b=40, l=40, r=40)
)

# 9. Patient flow (procedencia/destino)
proc_counts = nqx.PROC_GRUPO.value_counts().head(6)
dest_counts = nqx.DEST_GRUPO.value_counts().head(8)
fig_flow = make_subplots(rows=1, cols=2, subplot_titles=[
    'Procedencia de pacientes', 'Destino al egreso'
])
fig_flow.add_trace(go.Bar(
    y=proc_counts.index[::-1], x=proc_counts.values[::-1],
    orientation='h', marker_color=C_NQX, showlegend=False,
    text=proc_counts.values[::-1], textposition='outside'
), row=1, col=1)
fig_flow.add_trace(go.Bar(
    y=dest_counts.index[::-1], x=dest_counts.values[::-1],
    orientation='h', marker_color='#e67e22', showlegend=False,
    text=dest_counts.values[::-1], textposition='outside'
), row=1, col=2)
fig_flow.update_layout(
    title='Flujo de Pacientes UTINQX', template='plotly_white',
    height=420, margin=dict(t=60, b=40, l=180)
)

# 10. Age groups bar
edad_counts = nqx.GRUPO_ETARIO.value_counts().reindex(edad_order).fillna(0)
fig_edad = go.Figure()
fig_edad.add_trace(go.Bar(
    x=edad_order, y=edad_counts.values,
    marker_color=C_NQX,
    text=[f'{v}<br>({v/n_total*100:.1f}%)' for v in edad_counts.values.astype(int)],
    textposition='outside'
))
fig_edad.update_layout(
    title='Distribución por Grupo Etario',
    xaxis_title='Grupo etario', yaxis_title='Cantidad de pacientes',
    template='plotly_white', height=350, margin=dict(t=60, b=40)
)

# Helper: wrap plotly fig in HTML with narrative
def chart_block(fig, narrative=''):
    plot_html = fig.to_html(full_html=False, include_plotlyjs=False)
    narr = f'<div class="narrative">{narrative}</div>' if narrative else ''
    return f'<div class="chart-block">{plot_html}{narr}</div>'

# CSS compartido
SHARED_CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: 'Segoe UI', system-ui, sans-serif; background: #f8f9fa; color: #212529; }
.nav-bar { display:flex; gap:0; background:#2c3e50; padding:0; position:sticky; top:0; z-index:100; flex-wrap:wrap; }
.nav-bar a { color:#ecf0f1; text-decoration:none; padding:14px 20px; font-size:13px; font-weight:500; transition:background .2s; }
.nav-bar a:hover { background:#34495e; }
.nav-bar a.active { background:#e67e22; color:#fff; }
.container { max-width:1300px; margin:0 auto; padding:20px; }
h1 { text-align:center; margin:20px 0 5px; font-size:1.7rem; color:#2c3e50; }
.subtitle { text-align:center; color:#6c757d; margin-bottom:25px; font-size:0.9rem; }
.section-title { font-size:1.15rem; color:#2c3e50; margin:30px 0 15px; padding-bottom:8px; border-bottom:2px solid #e67e22; }
.kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin-bottom:25px; }
.kpi { background:#fff; border-radius:12px; padding:16px 18px; box-shadow:0 2px 8px rgba(0,0,0,0.08); text-align:center; }
.kpi-label { font-size:0.78rem; color:#6c757d; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px; }
.kpi-value { font-size:1.6rem; font-weight:700; }
.kpi-detail { font-size:0.75rem; color:#95a5a6; margin-top:4px; }
.chart-block { background:#fff; border-radius:12px; padding:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08); margin-bottom:20px; }
.narrative { padding:14px 18px; margin-top:6px; background:#fef9e7; border-left:4px solid #e67e22; border-radius:0 8px 8px 0; font-size:0.88rem; color:#7d6608; line-height:1.5; }
.highlight-box { background:#fdedec; border-left:4px solid #c0392b; padding:18px 22px; border-radius:0 12px 12px 0; margin:20px 0; }
.highlight-box h3 { color:#922b21; margin-bottom:8px; font-size:1rem; }
.highlight-box li { margin:5px 0; color:#641e16; font-size:0.9rem; line-height:1.4; }
.evidence-box { background:#eaf2f8; border-left:4px solid #2980b9; padding:18px 22px; border-radius:0 12px 12px 0; margin:20px 0; }
.evidence-box h3 { color:#1a5276; margin-bottom:8px; font-size:1rem; }
.evidence-box p, .evidence-box li { color:#1b4f72; font-size:0.9rem; line-height:1.5; margin:4px 0; }
.stats-table { width:100%; border-collapse:collapse; margin-bottom:18px; background:#fff; border-radius:12px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.08); }
.stats-table th { background:#2c3e50; color:#fff; padding:10px 14px; text-align:left; font-size:0.82rem; }
.stats-table td { padding:8px 14px; border-bottom:1px solid #eee; font-size:0.87rem; }
.stats-table tr:last-child td { border-bottom:none; }
.stats-table tr:hover { background:#f1f3f5; }
.sig { color:#c0392b; font-weight:bold; }
.ns { color:#6c757d; }
.two-col { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
@media (max-width:900px) { .two-col { grid-template-columns:1fr; } }
footer { text-align:center; color:#adb5bd; padding:30px; font-size:0.78rem; }
@media print { .nav-bar { display:none; } body { background:#fff; } .chart-block, .kpi { box-shadow:none; border:1px solid #ddd; } }
"""

NAV_HTML = """
<nav class="nav-bar">
    <a href="../analisis_categorizacion/index.html">Resumen UTINQX</a>
    <a href="../analisis_categorizacion/dashboard_utinqx.html">Categorización UTINQX</a>
    <a href="../analisis_categorizacion/ambas_uti.html">Ambas UTI (Categorización)</a>
    <a href="dashboard_eda.html">EDA Estadística UTI</a>
    <a href="reporte_justificacion_utinqx.html" {act1}>Justificación UTINQX</a>
    <a href="dashboard_comparativo_clinico.html" {act2}>Comparativo Clínico</a>
</nav>"""

nav1 = NAV_HTML.format(act1='class="active"', act2='')
nav2 = NAV_HTML.format(act1='', act2='class="active"')

# Precalcular valores para narrativas
_mort_mod = mort_by_sev.get('Moderado (11-20)', {'tasa': 0, 'n': 0})
_mort_sev = mort_by_sev.get('Severo (21-30)', {'tasa': 0, 'n': 0})
_mort_msev = mort_by_sev.get('Muy severo (31+)', {'tasa': 0, 'n': 0})
_pct_larga = round(nqx.CAT_ESTADIA.isin(['Larga (5-9d)', 'Prolongada (10+d)']).mean() * 100, 1)
_pct_prolongada = round((nqx.CAT_ESTADIA == 'Prolongada (10+d)').mean() * 100, 1)
_pct_60plus = round((nqx.GRUPO_ETARIO.isin(['60-74', '75+'])).mean() * 100, 1)
_n_onco = int((nqx.CATEGORIA_DX == 'ONCOLÓGICO').sum())
_pct_onco = round((nqx.CATEGORIA_DX == 'ONCOLÓGICO').mean() * 100, 1)
_n_neuro = int((nqx.CATEGORIA_DX == 'NEUROLÓGICO').sum())
_pct_neuro = round((nqx.CATEGORIA_DX == 'NEUROLÓGICO').mean() * 100, 1)
_n_trauma = int((nqx.CATEGORIA_DX == 'TRAUMÁTICO').sum())
_pct_trauma = round((nqx.CATEGORIA_DX == 'TRAUMÁTICO').mean() * 100, 1)
_n_cardio = int((nqx.CATEGORIA_DX == 'CARDIOVASCULAR').sum())
_pct_cardio = round((nqx.CATEGORIA_DX == 'CARDIOVASCULAR').mean() * 100, 1)
_n_6074 = int((nqx.GRUPO_ETARIO == '60-74').sum())
_pct_6074 = round((nqx.GRUPO_ETARIO == '60-74').mean() * 100, 1)

# ══════════════════════════════════════════════════════════════════
# GENERAR HTML 1: JUSTIFICACIÓN UTINQX
# ══════════════════════════════════════════════════════════════════

html1 = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reporte de Justificación — UTI Neuroquirúrgica</title>
<script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
<style>
{SHARED_CSS}
.exec-summary {{ background:linear-gradient(135deg,#2c3e50,#34495e); color:#ecf0f1; padding:30px; border-radius:12px; margin-bottom:30px; }}
.exec-summary h2 {{ color:#e67e22; margin-bottom:12px; font-size:1.2rem; }}
.exec-summary p {{ font-size:0.92rem; line-height:1.6; margin-bottom:8px; }}
.exec-summary .stat-highlight {{ color:#f1c40f; font-weight:700; font-size:1.05rem; }}
</style>
</head>
<body>

{nav1}

<div class="container">
<h1>Reporte Clínico — UTI Neuroquirúrgica (UTINQX)</h1>
<p class="subtitle">Evidencia cuantitativa para la evaluación del recurso enfermero | {periodo_label} ({n_meses_nqx} meses) | n={n_total} pacientes</p>

<!-- RESUMEN EJECUTIVO -->
<div class="exec-summary">
<h2>Resumen Ejecutivo</h2>
<p><span class="stat-highlight">{n_total} pacientes</span> en <span class="stat-highlight">{n_meses_nqx} meses ({periodo_label})</span>. Promedio: <span class="stat-highlight">{avg_monthly} ingresos/mes</span>. Total: <span class="stat-highlight">{patient_days:,} días-paciente</span>.</p>
<p>APACHE II promedio: <span class="stat-highlight">{apache_mean} ± {apache_std}</span>. <span class="stat-highlight">{mod_plus:.1f}%</span> de pacientes en categoría moderada, severa o muy severa (vs {mod_plus_qx:.1f}% en UTIQX, p &lt; 0.001).</p>
<p>Mortalidad global: <span class="stat-highlight">{mort_pct}%</span> ({n_fallecidos} pacientes). En severos: <span class="stat-highlight">{_mort_sev['tasa']}%</span>. En muy severos: <span class="stat-highlight">{_mort_msev['tasa']}%</span>.</p>
</div>

<!-- KPIs -->
<h2 class="section-title">Indicadores Clave de la Unidad</h2>
<div class="kpi-grid">
    <div class="kpi"><div class="kpi-label">Pacientes atendidos</div><div class="kpi-value" style="color:{C_NQX}">{n_total}</div><div class="kpi-detail">{periodo_label} ({n_meses_nqx} meses)</div></div>
    <div class="kpi"><div class="kpi-label">Ingresos mensuales</div><div class="kpi-value" style="color:{C_NQX}">{avg_monthly}</div><div class="kpi-detail">Promedio mes</div></div>
    <div class="kpi"><div class="kpi-label">Días-paciente</div><div class="kpi-value" style="color:{C_NQX}">{patient_days:,}</div><div class="kpi-detail">Carga acumulada</div></div>
    <div class="kpi"><div class="kpi-label">APACHE II promedio</div><div class="kpi-value" style="color:{C_ACCENT}">{apache_mean}</div><div class="kpi-detail">DE ± {apache_std}</div></div>
    <div class="kpi"><div class="kpi-label">Severidad moderada o superior</div><div class="kpi-value" style="color:{C_ACCENT}">{mod_plus:.1f}%</div><div class="kpi-detail">{int(mod_plus*n_total/100)} pacientes</div></div>
    <div class="kpi"><div class="kpi-label">Estadía promedio</div><div class="kpi-value" style="color:{C_NQX}">{los_mean} días</div><div class="kpi-detail">Mediana: {los_median:.0f} días</div></div>
    <div class="kpi"><div class="kpi-label">Mortalidad global</div><div class="kpi-value" style="color:{C_ACCENT}">{mort_pct}%</div><div class="kpi-detail">{n_fallecidos} fallecidos</div></div>
    <div class="kpi"><div class="kpi-label">Edad promedio</div><div class="kpi-value" style="color:{C_NQX}">{edad_mean} años</div><div class="kpi-detail">{pct_masculino}% masculino</div></div>
</div>

<!-- SEVERIDAD -->
<h2 class="section-title">1. Severidad Clínica</h2>

<div class="highlight-box">
<h3>Datos de severidad APACHE II</h3>
<ul>
<li><strong>{mod_plus:.1f}%</strong> de pacientes UTINQX en categoría moderada, severa o muy severa vs <strong>{mod_plus_qx:.1f}%</strong> en UTIQX (p &lt; 0.001).</li>
<li><strong>{severo_plus:.1f}%</strong> en categoría severa o muy severa (APACHE &ge; 21).</li>
</ul>
</div>

<div class="two-col">
{chart_block(fig_sev_pie,
    f'<strong>{mod_plus:.1f}%</strong> en categoría moderada o superior. '
    f'<strong>{100-mod_plus:.1f}%</strong> en categoría leve (APACHE 0-10).'
)}
{chart_block(fig_apache_hist,
    f'Media: <strong>{apache_mean}</strong>. Mediana: <strong>{apache_median:.0f}</strong>. '
    f'P75: <strong>{apache_p75:.0f}</strong>. P90: <strong>{apache_p90:.0f}</strong>. P95: <strong>{apache_p95:.0f}</strong>.'
)}
</div>

<!-- MORTALIDAD POR SEVERIDAD -->
<h2 class="section-title">2. Mortalidad según Severidad</h2>

{chart_block(fig_mort_sev,
    f'Leve: 0%. Moderada: <strong>{_mort_mod["tasa"]}%</strong> (n={_mort_mod["n"]}). '
    f'Severa: <strong>{_mort_sev["tasa"]}%</strong> (n={_mort_sev["n"]}). '
    f'Muy severa: <strong>{_mort_msev["tasa"]}%</strong> (n={_mort_msev["n"]}).'
)}

<!-- ESTADÍA -->
<h2 class="section-title">3. Estadía Hospitalaria</h2>

<div class="two-col">
{chart_block(fig_los,
    f'Promedio: <strong>{los_mean} días</strong>. Mediana: <strong>{los_median:.0f}</strong>. '
    f'P90: <strong>{los_p90:.0f} días</strong>. P95: <strong>{los_p95:.0f} días</strong>. '
    f'Total acumulado: <strong>{patient_days:,} días-paciente</strong>.'
)}
{chart_block(fig_est_pie,
    f'<strong>{_pct_larga}%</strong> con estadías de 5 o más días. '
    f'<strong>{_pct_prolongada}%</strong> con estadías de 10 o más días.'
)}
</div>

<!-- TENDENCIA TEMPORAL -->
<h2 class="section-title">4. Tendencia Temporal</h2>

<div class="two-col">
{chart_block(fig_monthly,
    f'{n_meses_nqx} meses de registro ({periodo_label}). Promedio: <strong>{avg_monthly} ingresos/mes</strong>. '
    f'Máximo: <strong>{int(monthly_nqx.max())}</strong>. Mínimo: <strong>{int(monthly_nqx.min())}</strong>. '
    f'En rojo: desde junio 2025, aumento sostenido del volumen.'
)}
{chart_block(fig_apache_trend,
    f'APACHE II promedio mensual: rango <strong>{apache_monthly.min()}</strong> a <strong>{apache_monthly.max()}</strong>. '
    f'Media global: <strong>{apache_mean}</strong>.'
)}
</div>

<!-- PERFIL DIAGNÓSTICO -->
<h2 class="section-title">5. Perfil Diagnóstico</h2>

{chart_block(fig_dx,
    f'Oncológico: {_n_onco} ({_pct_onco}%). Neurológico: {_n_neuro} ({_pct_neuro}%). '
    f'Traumático: {_n_trauma} ({_pct_trauma}%). Cardiovascular: {_n_cardio} ({_pct_cardio}%).'
)}

<!-- DEMOGRAFÍA -->
<h2 class="section-title">6. Perfil Demográfico y Flujo de Pacientes</h2>

<div class="two-col">
{chart_block(fig_edad,
    f'Mayores de 60 años: <strong>{_pct_60plus}%</strong>. '
    f'Grupo más frecuente: 60-74 años ({_n_6074} pacientes, {_pct_6074}%).'
)}
{chart_block(fig_flow,
    f'Principal procedencia: otra UCI/UTI ({proc_counts.iloc[0]}). '
    f'Segundo origen: pabellón/postoperatorio ({proc_counts.iloc[1] if len(proc_counts)>1 else 0}).'
)}
</div>

<!-- SÍNTESIS -->
<div class="highlight-box" style="background:#d5f5e3; border-left-color:#27ae60;">
<h3 style="color:#1e8449;">Síntesis de datos</h3>
<ul style="color:#186a3b;">
<li><strong>{n_total} pacientes</strong> en {n_meses_nqx} meses ({periodo_label}). Promedio: <strong>{avg_monthly} ingresos/mes</strong>. Total: <strong>{patient_days:,} días-paciente</strong>.</li>
<li>APACHE II: <strong>{apache_mean} ± {apache_std}</strong>. Severidad moderada+: <strong>{mod_plus:.1f}%</strong> vs {mod_plus_qx:.1f}% en UTIQX (p &lt; 0.001).</li>
<li>Mortalidad: severos <strong>{_mort_sev['tasa']}%</strong>, muy severos <strong>{_mort_msev['tasa']}%</strong>.</li>
<li>Diagnósticos: oncológico {_pct_onco}%, neurológico {_pct_neuro}%, traumático {_pct_trauma}%.</li>
<li>Mayores de 60 años: <strong>{_pct_60plus}%</strong>.</li>
</ul>
</div>

</div>

<footer>
    Reporte generado a partir de datos anonimizados — {periodo_label} ({n_meses_nqx} meses) — n={n_total} pacientes — UTINQX
</footer>
</body>
</html>"""

with open('reporte_justificacion_utinqx.html', 'w', encoding='utf-8') as f:
    f.write(html1)
print(f'[OK] reporte_justificacion_utinqx.html generado ({n_total} pacientes UTINQX)')


# ══════════════════════════════════════════════════════════════════
# GENERAR HTML 2: DASHBOARD COMPARATIVO CLÍNICO
# ══════════════════════════════════════════════════════════════════

# Charts comparativos

# 1. APACHE comparison (overlaid histograms)
fig2_apache = go.Figure()
for uti, color, name in [('UTIQX', C_QX, 'UTI Quirúrgica'), ('UTINQX', C_NQX, 'UTI Neuroquirúrgica')]:
    s = df[df.UTI == uti]['APACHE_II']
    fig2_apache.add_trace(go.Histogram(x=s, name=name, opacity=0.6, marker_color=color, nbinsx=30))
fig2_apache.update_layout(
    title='Distribución Comparativa del Score APACHE II',
    barmode='overlay', xaxis_title='Score APACHE II', yaxis_title='Cantidad de pacientes',
    template='plotly_white', height=380, margin=dict(t=60, b=40)
)

# 2. Severity comparison (grouped bars %)
fig2_sev = go.Figure()
for uti, color, name in [('UTIQX', C_QX, 'UTI Quirúrgica'), ('UTINQX', C_NQX, 'UTI Neuroquirúrgica')]:
    s = df[df.UTI == uti]
    counts = s.SEVERIDAD_APACHE.value_counts()
    pcts = [(counts.get(cat, 0) / len(s) * 100) for cat in sev_order]
    fig2_sev.add_trace(go.Bar(x=sev_order, y=pcts, name=name, marker_color=color,
                               text=[f'{p:.1f}%' for p in pcts], textposition='auto'))
fig2_sev.update_layout(
    title='Distribución de Severidad APACHE II por Unidad (%)',
    barmode='group', yaxis_title='Porcentaje (%)', template='plotly_white',
    height=380, margin=dict(t=60, b=40)
)

# 3. LOS comparison
fig2_los = go.Figure()
for uti, color, name in [('UTIQX', C_QX, 'UTI Quirúrgica'), ('UTINQX', C_NQX, 'UTI Neuroquirúrgica')]:
    s = df[(df.UTI == uti) & (df.DIAS_ESTADIA <= 30)]['DIAS_ESTADIA']
    fig2_los.add_trace(go.Histogram(x=s, name=name, opacity=0.6, marker_color=color, nbinsx=30))
fig2_los.update_layout(
    title='Distribución Comparativa de Días de Estadía (≤30 días)',
    barmode='overlay', xaxis_title='Días de estadía', yaxis_title='Cantidad de pacientes',
    template='plotly_white', height=380, margin=dict(t=60, b=40)
)

# 4. Diagnosis comparison
fig2_dx = make_subplots(rows=1, cols=2, subplot_titles=['UTI Quirúrgica (UTIQX)', 'UTI Neuroquirúrgica (UTINQX)'])
for i, (uti, color) in enumerate([('UTIQX', C_QX), ('UTINQX', C_NQX)], 1):
    s = df[df.UTI == uti]
    vc = s.CATEGORIA_DX.value_counts()
    vc = vc[vc.index != 'NO REGISTRADO'].head(10)
    pcts = [f'{v} ({v/len(s)*100:.1f}%)' for v in vc.values[::-1]]
    fig2_dx.add_trace(go.Bar(
        y=vc.index[::-1], x=vc.values[::-1], orientation='h',
        marker_color=color, showlegend=False, text=pcts, textposition='outside'
    ), row=1, col=i)
fig2_dx.update_layout(
    title='Categorías Diagnósticas por Unidad', template='plotly_white',
    height=450, margin=dict(t=60, b=40, l=180)
)

# 5. Monthly admissions comparison
df['ANIO_MES'] = df['INGRESO'].dt.to_period('M').astype(str)
monthly_comp = df.groupby(['ANIO_MES', 'UTI']).size().unstack(fill_value=0)
fig2_monthly = go.Figure()
for uti, color, name in [('UTIQX', C_QX, 'UTI Quirúrgica'), ('UTINQX', C_NQX, 'UTI Neuroquirúrgica')]:
    if uti in monthly_comp.columns:
        fig2_monthly.add_trace(go.Bar(
            x=monthly_comp.index.tolist(), y=monthly_comp[uti].values,
            name=name, marker_color=color
        ))
fig2_monthly.update_layout(
    title='Ingresos Mensuales Comparativos', barmode='group',
    xaxis_title='Período', yaxis_title='Cantidad de ingresos',
    template='plotly_white', height=380, margin=dict(t=60, b=60)
)

# 6. APACHE trend comparison
monthly_apache = df.groupby(['ANIO_MES', 'UTI'])['APACHE_II'].mean().unstack()
fig2_apache_trend = go.Figure()
for uti, color, name in [('UTIQX', C_QX, 'UTI Quirúrgica'), ('UTINQX', C_NQX, 'UTI Neuroquirúrgica')]:
    if uti in monthly_apache.columns:
        fig2_apache_trend.add_trace(go.Scatter(
            x=monthly_apache.index.tolist(), y=monthly_apache[uti].values,
            mode='lines+markers', name=name, line=dict(color=color, width=2.5)
        ))
fig2_apache_trend.update_layout(
    title='Tendencia Mensual del Score APACHE II Promedio',
    xaxis_title='Período', yaxis_title='APACHE II promedio',
    template='plotly_white', height=380, margin=dict(t=60, b=60)
)

# 7. Age groups comparison
fig2_edad = go.Figure()
for uti, color, name in [('UTIQX', C_QX, 'UTI Quirúrgica'), ('UTINQX', C_NQX, 'UTI Neuroquirúrgica')]:
    s = df[df.UTI == uti]
    counts = s.GRUPO_ETARIO.value_counts()
    pcts = [(counts.get(cat, 0) / len(s) * 100) for cat in edad_order]
    fig2_edad.add_trace(go.Bar(x=edad_order, y=pcts, name=name, marker_color=color,
                                text=[f'{p:.1f}%' for p in pcts], textposition='auto'))
fig2_edad.update_layout(
    title='Distribución por Grupo Etario (%)', barmode='group',
    yaxis_title='Porcentaje (%)', template='plotly_white', height=380, margin=dict(t=60, b=40)
)

# 8. Mortality comparison by severity
fig2_mort = make_subplots(rows=1, cols=2, subplot_titles=['UTI Quirúrgica (UTIQX)', 'UTI Neuroquirúrgica (UTINQX)'])
for i, (uti, color) in enumerate([('UTIQX', C_QX), ('UTINQX', C_NQX)], 1):
    s = df[df.UTI == uti]
    mort = s.groupby('SEVERIDAD_APACHE')['FALLECIDO'].agg(['sum', 'count'])
    mort['tasa'] = (mort['sum'] / mort['count'] * 100).round(1)
    mort = mort.reindex(sev_order)
    fig2_mort.add_trace(go.Bar(
        x=sev_order, y=mort['tasa'].values, marker_color=color,
        text=[f"{t:.1f}%" if not np.isnan(t) else "0%" for t in mort['tasa'].values],
        textposition='auto', showlegend=False
    ), row=1, col=i)
fig2_mort.update_layout(
    title='Mortalidad por Categoría de Severidad', template='plotly_white',
    height=380, margin=dict(t=60, b=40)
)
fig2_mort.update_yaxes(title_text='Mortalidad (%)')

# 9. Scatter APACHE vs LOS
fig2_scatter = make_subplots(rows=1, cols=2, subplot_titles=['UTI Quirúrgica (UTIQX)', 'UTI Neuroquirúrgica (UTINQX)'])
for i, (uti, color) in enumerate([('UTIQX', C_QX), ('UTINQX', C_NQX)], 1):
    s = df[(df.UTI == uti) & (df.DIAS_ESTADIA <= 40)]
    fig2_scatter.add_trace(go.Scatter(
        x=s.APACHE_II, y=s.DIAS_ESTADIA, mode='markers',
        marker=dict(color=color, opacity=0.35, size=5), showlegend=False
    ), row=1, col=i)
fig2_scatter.update_layout(
    title='Relación APACHE II vs Días de Estadía', template='plotly_white',
    height=380, margin=dict(t=60, b=40)
)
fig2_scatter.update_xaxes(title_text='Score APACHE II')
fig2_scatter.update_yaxes(title_text='Días de estadía')

# 10. Patient flow comparison
fig2_flow = make_subplots(rows=2, cols=2, subplot_titles=[
    'Procedencia — UTIQX', 'Procedencia — UTINQX', 'Destino — UTIQX', 'Destino — UTINQX'
])
for i, (uti, color) in enumerate([('UTIQX', C_QX), ('UTINQX', C_NQX)], 1):
    s = df[df.UTI == uti]
    vc_p = s.PROC_GRUPO.value_counts().head(6)
    fig2_flow.add_trace(go.Bar(y=vc_p.index[::-1], x=vc_p.values[::-1], orientation='h',
                                marker_color=color, showlegend=False,
                                text=vc_p.values[::-1], textposition='auto'), row=1, col=i)
    vc_d = s.DEST_GRUPO.value_counts().head(6)
    fig2_flow.add_trace(go.Bar(y=vc_d.index[::-1], x=vc_d.values[::-1], orientation='h',
                                marker_color=color, showlegend=False,
                                text=vc_d.values[::-1], textposition='auto'), row=2, col=i)
fig2_flow.update_layout(
    title='Flujo de Pacientes: Procedencia y Destino', template='plotly_white',
    height=650, margin=dict(t=60, b=40, l=160)
)

# Métricas comparativas
m_qx = {
    'n': len(qx), 'apache_mean': apache_mean_qx,
    'apache_std': round(qx.APACHE_II.std(), 1),
    'los_mean': round(qx.DIAS_ESTADIA.mean(), 1),
    'los_median': qx.DIAS_ESTADIA.median(),
    'edad_mean': round(qx.EDAD.mean(), 1),
    'mort': mort_qx,
    'pct_m': round((qx.GENERO == 'M').mean() * 100, 1),
    'patient_days': int(qx.DIAS_ESTADIA.sum()),
    'avg_monthly': round(len(qx) / qx['INGRESO'].dt.to_period('M').nunique(), 1),
}
n_meses_total = df['INGRESO'].dt.to_period('M').nunique()

def kpi_comp(label, val_qx, val_nqx, unit='', warn_higher=True):
    diff = val_nqx - val_qx
    arrow = '▲' if diff > 0 else '▼' if diff < 0 else '═'
    clr = C_ACCENT if (diff > 0 and warn_higher) else C_OK if (diff < 0 and warn_higher) else '#7f8c8d'
    return f"""<div class="kpi" style="border-top:3px solid {clr}">
    <div class="kpi-label">{label}</div>
    <div style="display:flex;justify-content:space-around;align-items:center;">
        <div><div style="font-size:0.75rem;color:{C_QX}">UTIQX</div><div style="font-size:1.3rem;font-weight:700;color:{C_QX}">{val_qx}{unit}</div></div>
        <div style="font-size:1.2rem;font-weight:700;color:{clr}">{arrow} {abs(diff):.1f}{unit}</div>
        <div><div style="font-size:0.75rem;color:{C_NQX}">UTINQX</div><div style="font-size:1.3rem;font-weight:700;color:{C_NQX}">{val_nqx}{unit}</div></div>
    </div></div>"""

# Statistical tests table
tests_rows = ''
for col, label, test_name in [('EDAD', 'Edad', 'Mann-Whitney U'), ('APACHE_II', 'APACHE II', 'Mann-Whitney U'),
                                ('DIAS_ESTADIA', 'Días de estadía', 'Mann-Whitney U')]:
    stat, p = mannwhitneyu(qx[col].dropna(), nqx[col].dropna(), alternative='two-sided')
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
    cls = 'sig' if p < 0.05 else 'ns'
    interp = 'Diferencia significativa' if p < 0.05 else 'Sin diferencia significativa'
    tests_rows += f'<tr><td>{label}</td><td>{test_name}</td><td>{stat:,.0f}</td><td>{p:.2e}</td><td class="{cls}">{sig}</td><td>{interp}</td></tr>\n'

for col, label in [('GENERO', 'Género'), ('CONDICION_EGRESO', 'Condición al egreso'),
                    ('SEVERIDAD_APACHE', 'Severidad APACHE'), ('GRUPO_ETARIO', 'Grupo etario'),
                    ('CATEGORIA_DX', 'Categoría diagnóstica')]:
    ct = pd.crosstab(df['UTI'], df[col])
    chi2, p, dof, _ = chi2_contingency(ct)
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
    cls = 'sig' if p < 0.05 else 'ns'
    interp = 'Diferencia significativa' if p < 0.05 else 'Sin diferencia significativa'
    tests_rows += f'<tr><td>{label}</td><td>Chi² (gl={dof})</td><td>{chi2:.1f}</td><td>{p:.2e}</td><td class="{cls}">{sig}</td><td>{interp}</td></tr>\n'

html2 = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard Comparativo Clínico — UTIQX vs UTINQX</title>
<script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
<style>
{SHARED_CSS}
</style>
</head>
<body>

{nav2}

<div class="container">
<h1>Dashboard Comparativo Clínico</h1>
<p class="subtitle">UTI Quirúrgica vs UTI Neuroquirúrgica | {periodo_label} ({n_meses_total} meses) | n={len(df)} pacientes ({len(qx)} UTIQX + {n_total} UTINQX)</p>

<!-- KPIs COMPARATIVOS -->
<h2 class="section-title">Indicadores Comparativos</h2>
<div class="kpi-grid">
    {kpi_comp('Pacientes', m_qx['n'], n_total, '', False)}
    {kpi_comp('APACHE II promedio', m_qx['apache_mean'], apache_mean, '', True)}
    {kpi_comp('Estadía promedio', m_qx['los_mean'], los_mean, ' d', True)}
    {kpi_comp('Mortalidad', m_qx['mort'], mort_pct, '%', True)}
    {kpi_comp('Edad promedio', m_qx['edad_mean'], edad_mean, ' años', False)}
    {kpi_comp('Severidad moderada+', round(mod_plus_qx,1), round(mod_plus,1), '%', True)}
    {kpi_comp('Ingresos/mes', m_qx['avg_monthly'], avg_monthly, '', False)}
    {kpi_comp('Días-paciente', m_qx['patient_days'], patient_days, '', False)}
</div>

<!-- TESTS ESTADÍSTICOS -->
<h2 class="section-title">Pruebas Estadísticas</h2>
<p style="font-size:0.88rem;color:#6c757d;margin-bottom:12px;">Pruebas no paramétricas: Mann-Whitney U (numéricas) y Chi-cuadrado (categóricas).</p>
<table class="stats-table">
<tr><th>Variable</th><th>Prueba</th><th>Estadístico</th><th>Valor p</th><th>Significancia</th><th>Interpretación</th></tr>
{tests_rows}
</table>
<p style="font-size:0.78rem;color:#95a5a6;">* p&lt;0.05 &nbsp; ** p&lt;0.01 &nbsp; *** p&lt;0.001 &nbsp; ns: no significativo.</p>

<!-- HALLAZGOS -->
<div class="highlight-box">
<h3>Diferencias estadísticamente significativas</h3>
<ul>
<li><strong>APACHE II</strong>: UTINQX {apache_mean} vs UTIQX {apache_mean_qx} (p &lt; 0.001).</li>
<li><strong>Severidad</strong>: {mod_plus:.1f}% moderada+ en UTINQX vs {mod_plus_qx:.1f}% en UTIQX (p &lt; 0.001).</li>
<li><strong>Diagnóstico</strong>: perfiles diferentes (p &lt; 0.001).</li>
<li><strong>Mortalidad</strong>: UTINQX {mort_pct}% vs UTIQX {mort_qx}%.</li>
<li><strong>Edad, género, estadía</strong>: sin diferencias significativas.</li>
</ul>
</div>

<!-- GRÁFICOS -->
<h2 class="section-title">Severidad Clínica</h2>
<div class="two-col">
{chart_block(fig2_apache,
    f'APACHE II — UTINQX: media {apache_mean} ± {apache_std}. UTIQX: media {apache_mean_qx} ± {m_qx["apache_std"]}. '
    f'Diferencia significativa (p &lt; 0.001).'
)}
{chart_block(fig2_sev,
    f'Moderada+: UTINQX {mod_plus:.1f}% vs UTIQX {mod_plus_qx:.1f}%. '
    f'Leve: UTINQX {100-mod_plus:.1f}% vs UTIQX {100-mod_plus_qx:.1f}%.'
)}
</div>

<h2 class="section-title">Estadía Hospitalaria</h2>
{chart_block(fig2_los,
    f'UTINQX: media {los_mean}d, mediana {los_median:.0f}d. '
    f'UTIQX: media {m_qx["los_mean"]}d, mediana {m_qx["los_median"]:.0f}d. '
    f'Sin diferencia significativa.'
)}

<h2 class="section-title">Mortalidad por Severidad</h2>
{chart_block(fig2_mort,
    f'UTINQX — Severos: {_mort_sev["tasa"]}% (n={_mort_sev["n"]}). Muy severos: {_mort_msev["tasa"]}% (n={_mort_msev["n"]}).'
)}

<h2 class="section-title">Perfil Diagnóstico</h2>
{chart_block(fig2_dx,
    f'Perfiles diagnósticos estadísticamente diferentes (p &lt; 0.001).'
)}

<h2 class="section-title">Demografía</h2>
{chart_block(fig2_edad,
    f'Distribución etaria sin diferencia significativa entre ambas unidades.'
)}

<h2 class="section-title">Tendencias Temporales</h2>
<div class="two-col">
{chart_block(fig2_monthly,
    f'UTIQX: {m_qx["avg_monthly"]} ingresos/mes. UTINQX: {avg_monthly} ingresos/mes.'
)}
{chart_block(fig2_apache_trend,
    f'APACHE II promedio mensual consistentemente mayor en UTINQX durante todo el período.'
)}
</div>

<h2 class="section-title">Flujo de Pacientes</h2>
{chart_block(fig2_flow,
    f'Principal procedencia en ambas unidades: otra UCI/UTI y pabellón/postoperatorio.'
)}

</div>

<footer>
    Dashboard comparativo clínico — Datos anonimizados — {periodo_label} ({n_meses_total} meses) — n={len(df)} pacientes
</footer>
</body>
</html>"""

with open('dashboard_comparativo_clinico.html', 'w', encoding='utf-8') as f:
    f.write(html2)
print(f'[OK] dashboard_comparativo_clinico.html generado ({len(df)} pacientes total)')
