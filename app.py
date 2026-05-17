"""GENESIS OPTIMIZER v6.0 — Sistema Integrado de Otimização Econômica para Frangos de Corte"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import hashlib, json

st.set_page_config(page_title="Genesis Optimizer", page_icon="🌾",
                   layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════════
# CSS  —  Design System v6.0
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter',-apple-system,'Segoe UI',sans-serif !important; }
.stApp { background: #F0F4F9 !important; }
.main .block-container { padding: 0 2rem 4rem; max-width: 1920px; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] { background: #0F172A !important; border-right: 1px solid #1E293B !important; }
[data-testid="stSidebar"] * { color: #94A3B8 !important; }
[data-testid="stSidebar"] label { color: #64748B !important; font-size: 0.63rem !important; font-weight: 700 !important; letter-spacing: 0.5px !important; text-transform: uppercase !important; }
[data-testid="stSidebar"] hr { border-color: #1E293B !important; }
[data-testid="stSidebar"] .stSlider [data-testid="stSliderTrackFill"] { background: #3B82F6 !important; }
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] [role="slider"] { background: #3B82F6 !important; box-shadow: 0 0 0 4px rgba(59,130,246,0.20) !important; }
[data-testid="stSidebar"] .stNumberInput > div > div > input { background: #1E293B !important; border: 1px solid #334155 !important; border-radius: 6px !important; color: #E2E8F0 !important; font-size: 0.80rem !important; }
[data-testid="stSidebar"] .stSelectbox > div > div { background: #1E293B !important; border: 1px solid #334155 !important; }
[data-testid="stSidebar"] .stRadio label { color: #94A3B8 !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] { background: #E2E8F0 !important; border: none !important; padding: 4px !important; gap: 2px !important; border-radius: 14px !important; box-shadow: none !important; margin-bottom: 0 !important; }
.stTabs [data-baseweb="tab"] { color: #64748B !important; font-size: 0.68rem !important; font-weight: 600 !important; letter-spacing: 0.4px !important; text-transform: uppercase !important; padding: 8px 16px !important; background: transparent !important; border: none !important; border-radius: 10px !important; transition: all 0.18s !important; }
.stTabs [data-baseweb="tab"]:hover { color: #1E293B !important; background: rgba(255,255,255,0.65) !important; }
.stTabs [aria-selected="true"] { color: #1E40AF !important; background: #FFFFFF !important; font-weight: 700 !important; box-shadow: 0 1px 8px rgba(0,0,0,0.12) !important; }
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; border: none !important; padding: 20px 0 0 !important; box-shadow: none !important; }

/* ── BUTTONS ── */
.stButton > button { background: #FFFFFF !important; color: #2563EB !important; border: 1px solid #BFDBFE !important; border-radius: 8px !important; font-size: 0.72rem !important; font-weight: 600 !important; letter-spacing: 0.3px !important; text-transform: uppercase !important; padding: 9px 20px !important; transition: all 0.15s !important; }
.stButton > button:hover { background: #EFF6FF !important; border-color: #93C5FD !important; box-shadow: 0 2px 8px rgba(37,99,235,0.12) !important; }
.stButton > button[kind="primary"] { background: #2563EB !important; color: #FFFFFF !important; border-color: #2563EB !important; box-shadow: 0 3px 10px rgba(37,99,235,0.30) !important; }
.stButton > button[kind="primary"]:hover { background: #1D4ED8 !important; box-shadow: 0 4px 14px rgba(37,99,235,0.40) !important; }
.stDownloadButton > button { background: #ECFDF5 !important; color: #047857 !important; border: 1px solid #6EE7B7 !important; border-radius: 8px !important; font-size: 0.72rem !important; font-weight: 600 !important; }

/* ── INPUTS ── */
.stNumberInput > div > div > input, .stTextInput > div > div > input { background: #FFFFFF !important; border: 1px solid #D1D9E0 !important; border-radius: 8px !important; color: #0F172A !important; font-size: 0.82rem !important; }
.stNumberInput > div > div > input:focus, .stTextInput > div > div > input:focus { border-color: #3B82F6 !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.10) !important; }
.stSelectbox > div > div { background: #FFFFFF !important; border: 1px solid #D1D9E0 !important; border-radius: 8px !important; }
.stSlider [data-baseweb="slider"] [role="slider"] { background: #2563EB !important; box-shadow: 0 0 0 4px rgba(37,99,235,0.14) !important; }
.stSlider [data-testid="stSliderTrackFill"] { background: #2563EB !important; }

/* ── DATAFRAMES ── */
.dataframe thead tr th { background: #F8FAFC !important; color: #0F172A !important; font-size: 0.67rem !important; font-weight: 700 !important; letter-spacing: 0.5px !important; text-transform: uppercase !important; border-color: #E2E8F0 !important; padding: 10px 14px !important; }
.dataframe tbody tr td { color: #374151 !important; font-size: 0.82rem !important; border-color: #F1F5F9 !important; padding: 8px 14px !important; }
.dataframe tbody tr:hover td { background: #EFF6FF !important; }

/* ── CHART CONTAINERS ── */
[data-testid="stPlotlyChart"] { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 4px; box-shadow: 0 1px 6px rgba(15,23,42,0.07); margin-bottom: 8px; }

/* ── MISC ── */
.stAlert { border-radius: 10px !important; font-size: 0.82rem !important; }
.stCaption { color: #64748B !important; font-size: 0.75rem !important; }
p { color: #374151; font-size: 0.88rem; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F1F5F9; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94A3B8; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# PALETA & HELPERS
# ══════════════════════════════════════════════════════════════════

_C = {
    "blue":   "#2563EB",
    "green":  "#16A34A",
    "amber":  "#D97706",
    "red":    "#DC2626",
    "purple": "#7C3AED",
    "teal":   "#0891B2",
    "gray":   "#64748B",
    "navy":   "#0F172A",
    "indigo": "#4F46E5",
    "cyan":   "#0284C7",
}

CHART_COLORS = ["#2563EB","#16A34A","#D97706","#DC2626","#7C3AED",
                "#0891B2","#F59E0B","#8B5CF6","#10B981","#EF4444","#6366F1","#14B8A6"]
PALETA_14 = CHART_COLORS[:14]

_FONT   = "'Inter',-apple-system,'Segoe UI',sans-serif"
_CFG    = {"displayModeBar": False, "responsive": True}
SYM_LIST = ["diamond", "square", "circle", "triangle-up"]


def card(col, valor, label, cor="blue", sub="", pct=None):
    clr = _C.get(cor, _C["blue"])
    pct_bar = ""
    if pct is not None:
        fill = max(0, min(100, pct))
        pct_bar = (f'<div style="height:3px;background:#F1F5F9;margin-top:10px;border-radius:2px;">'
                   f'<div style="height:3px;width:{fill}%;background:{clr};border-radius:2px;'
                   f'transition:width 0.4s;"></div></div>')
    sub_html = (f'<div style="font-size:0.67rem;color:#94A3B8;margin-top:4px;font-family:{_FONT};'
                f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{sub}</div>') if sub else ""
    col.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:14px;
                overflow:hidden;box-shadow:0 1px 6px rgba(15,23,42,0.07);margin-bottom:8px;">
      <div style="height:3px;background:linear-gradient(90deg,{clr},{clr}99);"></div>
      <div style="padding:14px 16px 14px;font-family:{_FONT};">
        <div style="font-size:0.56rem;font-weight:700;color:#94A3B8;letter-spacing:0.6px;
                    text-transform:uppercase;margin-bottom:5px;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{label}</div>
        <div style="font-size:1.32rem;font-weight:800;color:{clr};line-height:1.1;
                    letter-spacing:-0.8px;white-space:nowrap;overflow:hidden;
                    text-overflow:ellipsis;">{valor}</div>
        {sub_html}{pct_bar}
      </div>
    </div>""", unsafe_allow_html=True)


def section(title, detail=""):
    det = (f'<span style="background:#EFF6FF;color:#2563EB;font-size:0.60rem;'
           f'font-weight:600;padding:2px 9px;border-radius:20px;letter-spacing:0.2px;'
           f'font-family:{_FONT};white-space:nowrap;">{detail}</span>') if detail else ""
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin:24px 0 14px;font-family:{_FONT};">
      <div style="width:3px;height:22px;background:#2563EB;
                  border-radius:2px;flex-shrink:0;"></div>
      <span style="font-size:0.87rem;font-weight:700;color:#0F172A;
                   letter-spacing:-0.3px;">{title}</span>
      {det}
    </div>""", unsafe_allow_html=True)


def divider():
    st.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,'
        'transparent,#E2E8F0 20%,#E2E8F0 80%,transparent);margin:20px 0;"></div>',
        unsafe_allow_html=True)


# keep old alias for internal usage
divline = divider


def box(content_md):
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:14px;'
        f'padding:18px 20px;box-shadow:0 1px 4px rgba(15,23,42,0.06);margin-bottom:12px;'
        f'font-family:{_FONT};">{content_md}</div>',
        unsafe_allow_html=True)


def _hash(obj):
    return hashlib.md5(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:10]


def _jlay(h=340, title="", extra=None):
    """Standard Plotly layout — clean professional style v6."""
    d = dict(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FAFBFC",
        font=dict(color="#374151", family="Inter,-apple-system,sans-serif", size=11),
        xaxis=dict(gridcolor="#F1F5F9", linecolor="#E2E8F0", zeroline=False,
                   tickfont=dict(color="#94A3B8", size=9),
                   title_font=dict(color="#64748B", size=11)),
        yaxis=dict(gridcolor="#F1F5F9", linecolor="#E2E8F0", zeroline=False,
                   tickfont=dict(color="#94A3B8", size=9),
                   title_font=dict(color="#64748B", size=11)),
        legend=dict(bgcolor="rgba(255,255,255,0.97)",
                    font=dict(color="#374151", size=10),
                    bordercolor="#E2E8F0", borderwidth=1),
        hoverlabel=dict(bgcolor="#0F172A", bordercolor="#334155",
                        font_family="Inter,-apple-system,sans-serif",
                        font_size=12, font_color="#F1F5F9"),
        margin=dict(t=44, b=30, l=52, r=20), height=h,
        colorway=CHART_COLORS,
        title=dict(text=title,
                   font=dict(color="#0F172A", family="Inter,-apple-system,sans-serif",
                             size=12), x=0.5),
    )
    if extra:
        d.update(extra)
    return d


# ══════════════════════════════════════════════════════════════════
# CACHE
# ══════════════════════════════════════════════════════════════════

@st.cache_resource
def _get_ing():
    from modules.formulation import carregar_ingredientes_ativos, get_ingredient_names
    return carregar_ingredientes_ativos(), get_ingredient_names()


@st.cache_data(ttl=90, show_spinner="Formulando dietas · LP HiGHS…")
def _mofc(h_n, h_p, niveis, precos):
    from modules.optimizer import calcular_mofc
    return calcular_mofc(niveis, precos)


@st.cache_data(ttl=300)
def _surf(var, a, b, c, d, n):
    from modules.biological import superficie_resposta
    return superficie_resposta(var, (a, b), (c, d), n)


@st.cache_data(ttl=300)
def _heat(h_p, cen, precos, a, b, c, d, n):
    from modules.optimizer import grid_mofc
    return grid_mofc(precos, cen, (a, b), (c, d), n)


@st.cache_data(ttl=300)
def _crescimento(me, lys, age):
    from modules.biological import curva_crescimento
    return curva_crescimento(float(me), float(lys), int(age))


# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(f"""
    <div style="border-bottom:1px solid #1E293B;padding-bottom:16px;margin-bottom:16px;font-family:{_FONT};">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <div style="width:34px;height:34px;background:#2563EB;border-radius:9px;
                    display:flex;align-items:center;justify-content:center;font-size:1rem;
                    box-shadow:0 3px 8px rgba(37,99,235,0.40);">🌾</div>
        <div>
          <div style="font-size:1.02rem;font-weight:800;color:#F1F5F9;letter-spacing:-0.3px;">Genesis</div>
          <div style="font-size:0.58rem;color:#475569;letter-spacing:0.3px;">Optimizer v6.0</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f'<p style="font-size:0.60rem;font-weight:700;color:#64748B;letter-spacing:0.5px;'
                f'text-transform:uppercase;margin-bottom:2px;font-family:{_FONT};">'
                f'Preços de Venda ($/kg)</p>', unsafe_allow_html=True)
    p_vivo   = st.slider("Frango Vivo",     0.50, 2.50, 1.00, 0.01, format="$%.2f")
    p_car    = st.slider("Carcaça WOG",     0.50, 3.00, 2.20, 0.01, format="$%.2f")
    p_peito  = st.slider("Peito Desossado", 1.50, 6.00, 4.50, 0.05, format="$%.2f")
    p_cortes = st.slider("Cortes Diversos", 0.50, 2.50, 1.10, 0.05, format="$%.2f")
    precos   = {"frango_vivo": p_vivo, "carcaca": p_car,
                "peito_desossado": p_peito, "cortes_misc": p_cortes}

    st.markdown("---")
    st.markdown(f'<p style="font-size:0.60rem;font-weight:700;color:#64748B;letter-spacing:0.5px;'
                f'text-transform:uppercase;margin-bottom:2px;font-family:{_FONT};">Cenário Primário</p>',
                unsafe_allow_html=True)
    cenario = st.radio("", ["vivo", "carcaca", "desossado"],
        format_func=lambda x: {"vivo": "Frango Vivo",
                                "carcaca": "Carcaça WOG",
                                "desossado": "Peito Desossado"}[x], index=2)

    st.markdown("---")
    st.markdown(f'<p style="font-size:0.60rem;font-weight:700;color:#64748B;letter-spacing:0.5px;'
                f'text-transform:uppercase;margin-bottom:2px;font-family:{_FONT};">Frota & Produção</p>',
                unsafe_allow_html=True)
    n_aves   = st.number_input("Aves alojadas",   10_000, 2_000_000, 100_000, 10_000)
    mort_pct = st.slider("Mortalidade (%)", 0.5, 10.0, 3.0, 0.5)
    idade_d  = st.slider("Idade de abate (dias)", 35, 56, 45)

    st.markdown("---")
    st.markdown(f'<p style="font-size:0.60rem;font-weight:700;color:#64748B;letter-spacing:0.5px;'
                f'text-transform:uppercase;margin-bottom:2px;font-family:{_FONT};">Custos Extras ($/ave)</p>',
                unsafe_allow_html=True)
    c_pinto = st.number_input("Pinto 1d",     0.10, 2.00, 0.45, 0.05, format="%.2f")
    c_med   = st.number_input("Medicação",    0.01, 0.30, 0.05, 0.01, format="%.2f")
    c_ener  = st.number_input("Energia",      0.01, 0.20, 0.04, 0.01, format="%.2f")
    c_mo    = st.number_input("Mão de obra",  0.02, 0.30, 0.07, 0.01, format="%.2f")
    c_depr  = st.number_input("Depreciação",  0.02, 0.30, 0.10, 0.01, format="%.2f")
    c_out   = st.number_input("Outros",       0.01, 0.20, 0.04, 0.01, format="%.2f")
    custos_extras = {"pinto": c_pinto, "medicacao": c_med, "energia": c_ener,
                     "mao_obra": c_mo, "depreciacao": c_depr, "outros": c_out}

    st.markdown("---")
    st.markdown(f'<p style="font-size:0.60rem;font-weight:700;color:#64748B;letter-spacing:0.5px;'
                f'text-transform:uppercase;margin-bottom:2px;font-family:{_FONT};">Programa Nutricional</p>',
                unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        me_s  = st.number_input("ME Strt",  2800, 3400, 2975, 25, key="me_s")
        me_g  = st.number_input("ME Grow",  2800, 3400, 3050, 25, key="me_g")
        me_f1 = st.number_input("ME Fin1",  2800, 3400, 3100, 25, key="me_f1")
        me_f2 = st.number_input("ME Fin2",  2800, 3400, 3150, 25, key="me_f2")
    with cb:
        ly_s  = st.number_input("Lys Strt", 0.80, 1.60, 1.320, 0.005, key="ly_s",  format="%.3f")
        ly_g  = st.number_input("Lys Grow", 0.80, 1.60, 1.204, 0.005, key="ly_g",  format="%.3f")
        ly_f1 = st.number_input("Lys Fin1", 0.80, 1.60, 1.135, 0.005, key="ly_f1", format="%.3f")
        ly_f2 = st.number_input("Lys Fin2", 0.80, 1.60, 1.063, 0.005, key="ly_f2", format="%.3f")

    programa = {
        "starter":   {"ame_n": float(me_s),  "dig_lys": float(ly_s)},
        "grower":    {"ame_n": float(me_g),  "dig_lys": float(ly_g)},
        "finisher1": {"ame_n": float(me_f1), "dig_lys": float(ly_f1)},
        "finisher2": {"ame_n": float(me_f2), "dig_lys": float(ly_f2)},
    }
    std_sel = st.selectbox("Padrão de referência", ["Nenhum", "Cobb 500", "Ross 308"])


# ══════════════════════════════════════════════════════════════════
# HEADER  — dark navy bar
# ══════════════════════════════════════════════════════════════════

st.markdown(f"""
<div style="background:linear-gradient(135deg,#0F172A 0%,#1E293B 100%);
            padding:0;margin:0 -2rem 24px;border-bottom:1px solid #334155;
            font-family:{_FONT};">
  <div style="max-width:1920px;margin:0 auto;padding:15px 2rem;
              display:flex;align-items:center;justify-content:space-between;">
    <div style="display:flex;align-items:center;gap:16px;">
      <div style="width:44px;height:44px;
                  background:linear-gradient(135deg,#3B82F6 0%,#2563EB 100%);
                  border-radius:12px;display:flex;align-items:center;
                  justify-content:center;font-size:1.25rem;flex-shrink:0;
                  box-shadow:0 4px 14px rgba(37,99,235,0.45);">🌾</div>
      <div>
        <div style="font-size:1.18rem;font-weight:800;color:#F1F5F9;letter-spacing:-0.5px;
                    line-height:1.2;">Genesis Optimizer</div>
        <div style="font-size:0.62rem;color:#64748B;margin-top:2px;letter-spacing:0.3px;">
          RSM Genesis42d_G &nbsp;·&nbsp; LP HiGHS &nbsp;·&nbsp;
          MOFC Multi-Cenário &nbsp;·&nbsp; v6.0</div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:12px;">
      <div style="font-size:0.67rem;font-weight:600;color:#4ADE80;
                  background:rgba(74,222,128,0.10);padding:5px 14px;
                  border-radius:20px;border:1px solid rgba(74,222,128,0.22);">
        ● Sistema Online</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# CÁLCULO PRINCIPAL
# ══════════════════════════════════════════════════════════════════

resultado = _mofc(_hash(programa), _hash(precos), programa, precos)
ok        = resultado["status"] == "OK"
FASES     = ["starter", "grower", "finisher1", "finisher2"]
F_LABEL   = ["Starter (0-12d)", "Grower (12-24d)", "Finisher 1 (24-36d)", "Finisher 2 (36-45d)"]
F_SHORT   = ["Starter", "Grower", "Fin.1", "Fin.2"]


# ══════════════════════════════════════════════════════════════════
# ABAS
# ══════════════════════════════════════════════════════════════════

tabs = st.tabs(["Overview", "Formulação LP", "Produção", "Otimizador",
                "RSM · Crescimento", "Sensibilidade"])
T_OVR, T_FORM, T_PROD, T_OPT, T_RSM, T_SENS = tabs


# ┌──────────────────────────────────────────────────────────────┐
# │  ABA 1 · OVERVIEW                                            │
# └──────────────────────────────────────────────────────────────┘
with T_OVR:
    if not ok:
        st.error(f"Formulação impossível: {resultado['status']}")
    else:
        from modules.optimizer import calcular_epef, custo_producao_total, escalas_frota

        d         = resultado["desempenho"]
        custo_ave = resultado["custo_alimentacao_por_ave"]
        epef_d    = calcular_epef(resultado, int(idade_d), float(mort_pct))
        cprod     = custo_producao_total(resultado, custos_extras)
        frota     = escalas_frota(resultado, int(n_aves), float(mort_pct))
        mofc_v    = resultado["mofc_vivo"]
        mofc_c    = resultado["mofc_carcaca"]
        mofc_d    = resultado["mofc_desossado"]
        mofc_sel  = resultado.get(f"mofc_{cenario}", 0) or 0
        custo_ext = sum(custos_extras.values())
        ioac      = mofc_sel - custo_ext
        rec_key   = f"receita_{cenario}" if cenario != "desossado" else "receita_desossado"
        receita   = resultado.get(rec_key, 0) or 0
        marg_bruta_pct = (mofc_sel / receita * 100) if receita > 0 else 0
        custo_kg_carc  = (cprod["total"] / d["carcaca_kg"]) if d.get("carcaca_kg", 0) > 0 else 0

        # ── Smart Insights Banner
        _ins = []
        if epef_d["EPEF"] >= 480:
            _ins.append(("#ECFDF5","#16A34A","🏆", f"<b>EPEF Excelente {epef_d['EPEF']:.0f}</b> — performance de referência (meta &gt; 480)"))
        elif epef_d["EPEF"] >= 420:
            _ins.append(("#EFF6FF","#2563EB","✓", f"<b>EPEF Muito Bom {epef_d['EPEF']:.0f}</b> — acima da média de mercado (meta &gt; 420)"))
        elif epef_d["EPEF"] >= 340:
            _ins.append(("#FFFBEB","#D97706","⚠", f"<b>EPEF Bom {epef_d['EPEF']:.0f}</b> — potencial de melhoria no programa nutricional"))
        else:
            _ins.append(("#FEF2F2","#DC2626","✕", f"<b>EPEF Baixo {epef_d['EPEF']:.0f}</b> — revise o programa. Meta mínima: 340"))

        if ioac < 0:
            _ins.append(("#FEF2F2","#DC2626","✕", f"<b>IOAC negativo ${ioac:.3f}</b> — custo total supera receita no cenário <b>{cenario.upper()}</b>"))
        elif ioac < 0.05:
            _ins.append(("#FFFBEB","#D97706","⚠", f"<b>Margem apertada</b> — IOAC ${ioac:.3f} · aumentar preço de venda ou reduzir custo extra"))
        else:
            _ins.append(("#ECFDF5","#16A34A","✓", f"<b>Operação lucrativa</b> — IOAC ${ioac:.3f}/ave no cenário {cenario.upper()}"))

        if d.get("caa", 0) > 2.0:
            _ins.append(("#FFFBEB","#D97706","⚠", f"<b>CAA elevado {d['caa']:.3f}</b> — revise ambiência, saúde do lote e densidade de alojamento"))

        _ins_html = "".join(
            f'<div style="display:flex;align-items:flex-start;gap:10px;padding:10px 14px;'
            f'background:{bg};border:1px solid {cl}33;border-radius:10px;flex:1;min-width:220px;'
            f'font-family:{_FONT};">'
            f'<span style="font-size:0.9rem;flex-shrink:0;margin-top:1px;">{ic}</span>'
            f'<span style="font-size:0.75rem;color:#1E293B;line-height:1.5;">{msg}</span>'
            f'</div>'
            for bg, cl, ic, msg in _ins)
        st.markdown(
            f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px;">'
            f'{_ins_html}</div>',
            unsafe_allow_html=True)

        # ── Row 1 — 4 Large KPI cards
        section("Indicadores Principais", "RSM Genesis42d_G · LP HiGHS")
        r1 = st.columns(4)
        ec = "green" if epef_d["EPEF"] >= 420 else ("amber" if epef_d["EPEF"] >= 340 else "red")
        card(r1[0], f"{epef_d['EPEF']:.0f}",
             f"EPEF · {epef_d['classe']}", ec,
             sub=f"Viab. {epef_d['viabilidade_pct']:.1f}%",
             pct=min(epef_d["EPEF"] / 550 * 100, 100))
        card(r1[1], f"{epef_d['peso_estimado_kg']:.3f} kg",
             f"Peso Vivo d{int(idade_d)}", "blue",
             sub=f"RSM: {d['peso_vivo_kg']:.3f} kg")
        mofc_cor = "green" if mofc_sel > 0 else "red"
        card(r1[2], f"${mofc_sel:.3f}",
             f"MOFC {cenario.upper()}", mofc_cor,
             sub=f"Receita: ${receita:.3f}/ave")
        card(r1[3], f"${cprod['total']:.4f}",
             "Custo Total/ave", "amber",
             sub=f"Feed: {cprod['feed_pct']:.0f}%")

        # ── Row 2 — 4 secondary KPI cards
        r2 = st.columns(4)
        card(r2[0], f"{d['caa']:.3f}", "CAA", "amber",
             sub=f"Aj. {epef_d['caa_ajustado']:.3f}")
        card(r2[1], f"{d['carcaca_kg']:.3f} kg", "Carcaça WOG", "teal")
        card(r2[2], f"{d['peito_kg']:.3f} kg", "Peito Desossado", "green")
        card(r2[3], f"${ioac:.3f}", f"IOAC {cenario[:4].upper()}",
             "green" if ioac > 0 else "red",
             sub="Margem s/ custo total")

        # ── Row 3 — 4 supporting KPI cards
        r3 = st.columns(4)
        card(r3[0], f"{d['rend_carcaca_pct']:.1f}%",  "Rend. Carcaça %",  "gray")
        card(r3[1], f"{d['rend_peito_pct']:.1f}%",    "Rend. Peito %",    "gray")
        card(r3[2], f"${custo_kg_carc:.4f}",           "Custo/kg Carcaça", "amber",
             sub=f"Feed: ${resultado.get('custo_por_kg_pv',0):.4f}/kg PV")
        card(r3[3], f"{marg_bruta_pct:.1f}%",
             "Margem Bruta MOFC", "green" if marg_bruta_pct > 15 else "amber",
             sub=f"Receita: ${receita:.3f}/ave")

        divider()

        # ── Charts row — EPEF gauge left, cost donut right
        cl, cr = st.columns(2)
        with cl:
            section("EPEF · Performance Index", "escala 0-600 · classificação de mercado")
            _ev = epef_d["EPEF"]
            _ec = (CHART_COLORS[1] if _ev >= 480 else
                   CHART_COLORS[0] if _ev >= 420 else
                   CHART_COLORS[2] if _ev >= 340 else
                   CHART_COLORS[3])
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=_ev,
                delta={"reference": 420, "relative": False,
                       "increasing": {"color": CHART_COLORS[1]},
                       "decreasing": {"color": CHART_COLORS[3]},
                       "font": {"color": "#374151", "size": 13, "family": "Inter"}},
                number={"font": {"color": _ec, "size": 40, "family": "Inter"},
                        "suffix": ""},
                title={"text": f"EPEF · {epef_d['classe']}<br>"
                               f"<span style='font-size:0.8em;color:#94A3B8'>"
                               f"Viab. {epef_d['viabilidade_pct']:.1f}%  ·  "
                               f"GPD {epef_d['ganho_diario_g']:.0f} g/d</span>",
                       "font": {"color": "#0F172A", "size": 13, "family": "Inter"}},
                gauge={
                    "axis": {"range": [0, 600], "tickwidth": 1,
                             "tickcolor": "#94A3B8", "nticks": 7,
                             "tickfont": {"color": "#94A3B8", "size": 9, "family": "Inter"}},
                    "bar": {"color": _ec, "thickness": 0.22},
                    "bgcolor": "#F8FAFC",
                    "borderwidth": 1, "bordercolor": "#E2E8F0",
                    "steps": [
                        {"range": [0,   280], "color": "#FEE2E2"},
                        {"range": [280, 340], "color": "#FEF3C7"},
                        {"range": [340, 420], "color": "#DBEAFE"},
                        {"range": [420, 480], "color": "#D1FAE5"},
                        {"range": [480, 600], "color": "#ECFDF5"},
                    ],
                    "threshold": {
                        "line": {"color": "#0F172A", "width": 2.5},
                        "thickness": 0.80, "value": _ev
                    }
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor="#FFFFFF", height=320,
                font=dict(family="Inter,-apple-system,sans-serif"),
                hoverlabel=dict(bgcolor="#0F172A", bordercolor="#334155",
                                font_family="Inter", font_size=12, font_color="#F1F5F9"),
                margin=dict(t=30, b=10, l=30, r=30),
                annotations=[
                    dict(x=0.12, y=0.13, text="Ruim",    showarrow=False,
                         font=dict(color="#EF4444", size=8, family="Inter")),
                    dict(x=0.28, y=0.05, text="Regular", showarrow=False,
                         font=dict(color="#D97706", size=8, family="Inter")),
                    dict(x=0.50, y=0.01, text="Bom",     showarrow=False,
                         font=dict(color="#3B82F6", size=8, family="Inter")),
                    dict(x=0.72, y=0.05, text="Muito Bom", showarrow=False,
                         font=dict(color="#16A34A", size=8, family="Inter")),
                    dict(x=0.88, y=0.13, text="Excelente", showarrow=False,
                         font=dict(color="#059669", size=8, family="Inter")),
                ])
            st.plotly_chart(fig_gauge, use_container_width=True, config=_CFG)

        with cr:
            section("Custo de Produção — Breakdown", "distribuição por item · $/ave")
            itens  = cprod["itens"]
            fig_bp = go.Figure(go.Pie(
                labels=list(itens.keys()), values=list(itens.values()),
                hole=0.55,
                marker=dict(colors=CHART_COLORS[:len(itens)],
                            line=dict(color="#FFFFFF", width=2)),
                textfont=dict(color="#FFFFFF", size=9, family="Inter"),
                texttemplate="%{label}<br>$%{value:.3f}",
                hovertemplate="<b>%{label}</b><br>$%{value:.4f}/ave<br>%{percent}<extra></extra>",
            ))
            fig_bp.update_layout(
                paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
                legend=dict(bgcolor="#FFFFFF", font=dict(color="#374151", size=9,
                            family="Inter"), bordercolor="#E2E8F0", borderwidth=1),
                hoverlabel=dict(bgcolor="#0F172A", bordercolor="#334155",
                                font_family="Inter", font_size=12, font_color="#F1F5F9"),
                margin=dict(t=12, b=12, l=12, r=12), height=320,
                annotations=[dict(text=f"${cprod['total']:.3f}<br><sub>/ave</sub>",
                                  x=0.5, y=0.5,
                                  font=dict(color="#1E293B", size=14, family="Inter"),
                                  showarrow=False)],
            )
            st.plotly_chart(fig_bp, use_container_width=True, config=_CFG)

        # ── Frota
        section("Escala de Frota", f"{int(n_aves):,} aves · {mort_pct:.1f}% mortalidade")
        fr_cols = st.columns(5)
        card(fr_cols[0], f"{int(frota['n_aves_vendidas']):,}", "Aves Vendidas",    "gray")
        card(fr_cols[1], f"${frota['custo_total_alim']:,.0f}", "Custo Feed Total", "amber")
        card(fr_cols[2], f"${frota[f'mofc_{cenario}']:,.0f}",
             f"MOFC {cenario[:4].title()} Total",
             "green" if frota[f"mofc_{cenario}"] > 0 else "red")
        card(fr_cols[3], f"{frota['peso_total_kg']/1000:,.1f} t", "Biomassa Total","teal")
        card(fr_cols[4], f"${frota[rec_key]:,.0f}",
             f"Receita {cenario[:4].title()}", "blue")

        divider()

        # ── MOFC & IOAC bar + Receita vs Custo
        _m1, _m2 = st.columns(2)
        with _m1:
            section("MOFC & IOAC por Cenário", "$/ave · margem feed vs custo total")
            nomes_c   = ["Frango Vivo", "Carcaça WOG", "Peito Desossado"]
            vals_m    = [mofc_v, mofc_c, mofc_d]
            cen_list  = [("vivo", "Vivo"), ("carcaca", "Carcaça"), ("desossado", "Peito")]
            iofc_vals = [resultado.get(f"mofc_{c}", 0) for c, _ in cen_list]
            ioac_vals = [v - custo_ext for v in iofc_vals]
            fig_m = go.Figure()
            fig_m.add_trace(go.Bar(
                name="MOFC (feed)", x=nomes_c, y=vals_m,
                marker_color=CHART_COLORS[0],
                marker_line=dict(color="rgba(255,255,255,0)", width=0),
                text=[f"${v:.3f}" for v in vals_m], textposition="outside",
                textfont=dict(color="#374151", size=10, family="Inter"),
                hovertemplate="<b>%{x}</b><br>MOFC Feed: $%{y:.4f}/ave<extra></extra>"))
            fig_m.add_trace(go.Bar(
                name="IOAC (total)", x=nomes_c, y=ioac_vals,
                marker_color=CHART_COLORS[1],
                marker_line=dict(color="rgba(255,255,255,0)", width=0),
                text=[f"${v:.3f}" for v in ioac_vals], textposition="outside",
                textfont=dict(color="#374151", size=10, family="Inter"),
                hovertemplate="<b>%{x}</b><br>IOAC Total: $%{y:.4f}/ave<extra></extra>"))
            fig_m.add_hline(y=0, line_color="#DC2626", line_width=1.5,
                            line_dash="dot", opacity=0.6,
                            annotation_text="Break-even",
                            annotation_font=dict(color="#DC2626", size=9, family="Inter"))
            fig_m.update_layout(**_jlay(300, "MOFC & IOAC por Cenário ($/ave)",
                                        extra=dict(barmode="group",
                                                   bargap=0.25, bargroupgap=0.06)))
            st.plotly_chart(fig_m, use_container_width=True, config=_CFG)

        with _m2:
            section("Receita vs Custo por Cenário", "$/ave · estrutura econômica completa")
            cen_list2 = [("vivo","Vivo"),("carcaca","Carcaça"),("desossado","Peito")]
            rec_vals  = [resultado.get(f"receita_{c}", 0) or 0 for c,_ in cen_list2]
            custo_vals = [cprod["total"]] * 3
            fig_rv2 = go.Figure()
            fig_rv2.add_trace(go.Bar(
                name="Receita", x=[l for _,l in cen_list2], y=rec_vals,
                marker_color=CHART_COLORS[1],
                marker_line=dict(color="rgba(255,255,255,0)", width=0),
                text=[f"${v:.3f}" for v in rec_vals], textposition="outside",
                textfont=dict(color="#374151", size=10, family="Inter"),
                hovertemplate="<b>%{x}</b><br>Receita: $%{y:.4f}/ave<extra></extra>"))
            fig_rv2.add_trace(go.Bar(
                name="Custo Total", x=[l for _,l in cen_list2], y=custo_vals,
                marker_color=CHART_COLORS[3],
                marker_line=dict(color="rgba(255,255,255,0)", width=0),
                text=[f"${v:.3f}" for v in custo_vals], textposition="outside",
                textfont=dict(color="#374151", size=10, family="Inter"),
                hovertemplate="<b>%{x}</b><br>Custo Total: $%{y:.4f}/ave<extra></extra>"))
            fig_rv2.update_layout(**_jlay(300, "Receita vs Custo Total ($/ave)",
                                          extra=dict(barmode="group",
                                                     bargap=0.25, bargroupgap=0.06)))
            st.plotly_chart(fig_rv2, use_container_width=True, config=_CFG)

        divider()

        # ── Programa nutricional atual
        section("Programa Nutricional Atual", "ME × Lisina por fase")
        fig_prog = make_subplots(specs=[[{"secondary_y": True}]])
        me_prog  = [programa[f]["ame_n"]   for f in FASES]
        lys_prog = [programa[f]["dig_lys"] for f in FASES]
        fig_prog.add_trace(go.Bar(
            x=F_SHORT, y=me_prog, name="ME (kcal/kg)",
            marker_color="rgba(37,99,235,0.18)",
            marker_line=dict(color=CHART_COLORS[0], width=1.5),
            text=[str(int(v)) for v in me_prog], textposition="inside",
            textfont=dict(color=CHART_COLORS[0], size=10, family="Inter"),
            hovertemplate="<b>%{x}</b><br>ME: %{y:.0f} kcal/kg<extra></extra>"),
            secondary_y=False)
        fig_prog.add_trace(go.Scatter(
            x=F_SHORT, y=lys_prog, name="Dig. Lisina (%)",
            mode="lines+markers+text",
            text=[f"{v:.3f}%" for v in lys_prog], textposition="top center",
            textfont=dict(color=CHART_COLORS[2], size=10, family="Inter"),
            line=dict(color=CHART_COLORS[2], width=2.5),
            marker=dict(size=9, color=CHART_COLORS[2],
                        line=dict(color="white", width=1.5)),
            hovertemplate="<b>%{x}</b><br>Dig. Lisina: %{y:.3f}%<extra></extra>"),
            secondary_y=True)
        fig_prog.update_layout(**_jlay(280))
        fig_prog.update_yaxes(title_text="ME (kcal/kg)", secondary_y=False,
                              title_font=dict(color="#64748B"))
        fig_prog.update_yaxes(title_text="Dig. Lisina (%)", secondary_y=True,
                              title_font=dict(color="#64748B"))
        st.plotly_chart(fig_prog, use_container_width=True, config=_CFG)

        fa, fb = st.columns(2)
        with fa:
            section("Custo de Ração por Fase", "$/kg de ração formulada")
            form_res  = resultado.get("formulacao", {})
            fase_cust = [(f, F_SHORT[i], form_res.get(f, {}).get("custo_por_kg", 0))
                         for i, f in enumerate(FASES)]
            fig_fc = go.Figure(go.Bar(
                x=[x[1] for x in fase_cust], y=[x[2] for x in fase_cust],
                marker_color=CHART_COLORS[:4],
                marker_line=dict(color="rgba(255,255,255,0)", width=0),
                text=[f"${v:.4f}" for _, _, v in fase_cust], textposition="outside",
                textfont=dict(color="#374151", size=10, family="Inter"),
                hovertemplate="<b>%{x}</b><br>Custo: $%{y:.4f}/kg<extra></extra>"))
            fig_fc.update_layout(**_jlay(260, "Custo Ração por Fase ($/kg)"))
            fig_fc.update_yaxes(title_text="$/kg")
            st.plotly_chart(fig_fc, use_container_width=True, config=_CFG)

        with fb:
            if std_sel != "Nenhum":
                from modules.optimizer import STANDARDS
                std = STANDARDS[std_sel]
                section(f"vs {std_sel}", "diferença do programa atual")
                comp_rows = []
                for fase, lbl in zip(FASES, F_SHORT):
                    ref    = std.get(fase, {})
                    prog_f = programa.get(fase, {})
                    for nut, nut_lbl in [("ame_n", "ME"), ("dig_lys", "Dig.Lys")]:
                        pv2 = prog_f.get(nut); rv = ref.get(nut)
                        if pv2 and rv:
                            diff = pv2 - rv
                            comp_rows.append({
                                "Fase": lbl, "Nutriente": nut_lbl,
                                "Programa": f"{pv2:.3f}", std_sel: f"{rv:.3f}",
                                "Δ": f"{diff:+.3f}",
                                "Status": "✓" if abs(diff / rv) < 0.03 else ("↑" if diff > 0 else "↓"),
                            })
                if comp_rows:
                    st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)
            else:
                section("Receita vs MOFC por Cenário", "$/ave · comparativo feed vs receita")
                cen_list2 = [("vivo", "Vivo"), ("carcaca", "Carcaça"), ("desossado", "Peito")]
                rec_vals  = [resultado.get(f"receita_{c}", 0) or 0 for c, _ in cen_list2]
                mofc_v2   = [resultado.get(f"mofc_{c}", 0) or 0 for c, _ in cen_list2]
                fig_rv = go.Figure()
                fig_rv.add_trace(go.Bar(
                    name="Receita", x=[l for _, l in cen_list2], y=rec_vals,
                    marker_color=CHART_COLORS[4],
                    marker_line=dict(color="rgba(255,255,255,0)", width=0),
                    text=[f"${v:.3f}" for v in rec_vals], textposition="outside",
                    textfont=dict(color="#374151", size=9, family="Inter"),
                    hovertemplate="<b>%{x}</b><br>Receita: $%{y:.4f}<extra></extra>"))
                fig_rv.add_trace(go.Bar(
                    name="MOFC (feed)", x=[l for _, l in cen_list2], y=mofc_v2,
                    marker_color=CHART_COLORS[0],
                    marker_line=dict(color="rgba(255,255,255,0)", width=0),
                    text=[f"${v:.3f}" for v in mofc_v2], textposition="outside",
                    textfont=dict(color="#374151", size=9, family="Inter"),
                    hovertemplate="<b>%{x}</b><br>MOFC: $%{y:.4f}<extra></extra>"))
                fig_rv.add_hline(y=0, line_color="#DC2626", line_width=1.5,
                                 line_dash="dot", opacity=0.5)
                fig_rv.update_layout(**_jlay(260, "Receita vs MOFC ($/ave)",
                                             extra=dict(barmode="group",
                                                        bargap=0.25, bargroupgap=0.06)))
                st.plotly_chart(fig_rv, use_container_width=True, config=_CFG)

        st.markdown("---")
        from utils.report import gerar_relatorio_excel
        xlsx = gerar_relatorio_excel(resultado, programa, precos,
                                     custos_extras=custos_extras,
                                     n_aves=int(n_aves),
                                     mortalidade_pct=float(mort_pct),
                                     idade_d=int(idade_d))
        if xlsx:
            st.download_button("⬇  Exportar Relatório Excel (8 abas)", data=xlsx,
                file_name="genesis_optimizer_v60.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ┌──────────────────────────────────────────────────────────────┐
# │  ABA 2 · FORMULAÇÃO LP                                       │
# └──────────────────────────────────────────────────────────────┘
with T_FORM:
    if not ok:
        st.error(resultado["status"])
    else:
        _, nomes_ing = _get_ing()
        form = resultado.get("formulacao", {})

        section("Composição das Rações", "% inclusão por ingrediente e fase")
        all_codes = sorted(set(c for f in FASES for c in form.get(f, {}).get("composicao", {}).keys()))
        totais    = {c: sum(form.get(f, {}).get("composicao", {}).get(c, 0) for f in FASES) for c in all_codes}
        codes_ord = sorted(all_codes, key=lambda c: -totais[c])

        fig_stk = go.Figure()
        for idx, code in enumerate(codes_ord[:14]):
            nome = nomes_ing.get(code, str(code))[:24]
            vals = [form.get(f, {}).get("composicao", {}).get(code, 0.0) for f in FASES]
            fig_stk.add_trace(go.Bar(
                name=nome, x=F_SHORT, y=vals,
                marker_color=PALETA_14[idx % len(PALETA_14)],
                marker_line=dict(color="rgba(255,255,255,0.5)", width=0.4),
                text=[f"{v:.1f}" if v > 1.5 else "" for v in vals],
                textposition="inside", textfont=dict(size=8, color="white", family="Inter"),
                hovertemplate=f"<b>{nome}</b><br>%{{x}}: %{{y:.2f}}%<extra></extra>"))
        fig_stk.update_layout(**_jlay(420, "Composição por Fase (%)",
            extra=dict(barmode="stack",
                       legend=dict(orientation="h", y=-0.28,
                                   font=dict(size=8, color="#374151", family="Inter")))))
        fig_stk.update_yaxes(title_text="%", range=[0, 103])
        st.plotly_chart(fig_stk, use_container_width=True, config=_CFG)

        section("Perfil Nutricional Completo", "calculado vs meta · ✓ ok · ⚠ abaixo da meta")
        from modules.optimizer import REQUISITOS_FASE_BASE
        NUT_LBL = {
            "ame_n":      "ME (kcal/kg)",
            "dig_lys":    "Dig. Lisina (%)",
            "dig_met":    "Dig. Metionina (%)",
            "dig_cys":    "Dig. Cistina (%)",
            "dig_thr":    "Dig. Treonina (%)",
            "dig_trp":    "Dig. Triptofano (%)",
            "dig_val":    "Dig. Valina (%)",
            "ca_total":   "Cálcio Total (%)",
            "p_npp":      "P Não-Fítico (%)",
            "sodium":     "Sódio (%)",
            "chloride":   "Cloreto (%)",
            "potassium":  "Potássio (%)",
            "cp":         "Proteína Bruta (%)",
            "cf":         "Extrato Etéreo (%)",
        }
        nut_rows = []
        for nut, label in NUT_LBL.items():
            row = {"Nutriente": label}
            for fase, lbl in zip(FASES, F_SHORT):
                calc = form.get(fase, {}).get("nutrientes_calculados", {}).get(nut)
                meta = programa.get(fase, {}).get(nut) or REQUISITOS_FASE_BASE.get(fase, {}).get(nut)
                if calc is not None:
                    ok_f = "✓" if (meta is None or calc >= meta * 0.995) else "⚠"
                    row[lbl] = f"{ok_f} {calc:.4f}" + (f" (≥{meta:.3f})" if meta else "")
                else:
                    row[lbl] = "—"
            nut_rows.append(row)
        st.dataframe(pd.DataFrame(nut_rows).set_index("Nutriente"), use_container_width=True)

        divider()
        cl, cr = st.columns(2)

        with cl:
            section("Proteína Ideal · Radar AA", "Grower · formulado vs Ross 308")
            from modules.optimizer import IDEAL_PROTEIN
            ratios = resultado.get("ratios_aa", {}).get("grower", {})
            cats   = ["Met/Lys", "Met+Cys/Lys", "Thr/Lys", "Trp/Lys", "Val/Lys"]
            ideal_v = [IDEAL_PROTEIN[k] for k in
                ["met_pct_lys","metcys_pct_lys","thr_pct_lys","trp_pct_lys","val_pct_lys"]]
            form_v  = [ratios.get(k, 0) for k in
                ["met_pct_lys","metcys_pct_lys","thr_pct_lys","trp_pct_lys","val_pct_lys"]]

            fig_rad = go.Figure()
            fig_rad.add_trace(go.Scatterpolar(
                r=ideal_v + [ideal_v[0]], theta=cats + [cats[0]], name="Ideal (Ross 308)",
                fill="toself", fillcolor="rgba(37,99,235,0.06)",
                line=dict(color=CHART_COLORS[0], width=1.5, dash="dash"),
                marker=dict(size=5, color=CHART_COLORS[0])))
            fig_rad.add_trace(go.Scatterpolar(
                r=form_v + [form_v[0]], theta=cats + [cats[0]], name="Formulado",
                fill="toself", fillcolor="rgba(22,163,74,0.10)",
                line=dict(color=CHART_COLORS[1], width=2.5),
                marker=dict(size=7, color=CHART_COLORS[1],
                            line=dict(color="white", width=1.5))))
            fig_rad.update_layout(
                polar=dict(
                    bgcolor="#FAFBFD",
                    radialaxis=dict(visible=True, range=[0, 120],
                                   gridcolor="#E2E8F0",
                                   tickfont=dict(color="#64748B", size=8, family="Inter")),
                    angularaxis=dict(gridcolor="#E2E8F0",
                                     tickfont=dict(color="#374151", size=9, family="Inter"))),
                paper_bgcolor="#FFFFFF",
                hoverlabel=dict(bgcolor="#0F172A", bordercolor="#334155",
                                font_family="Inter", font_size=12, font_color="#F1F5F9"),
                legend=dict(bgcolor="#FFFFFF", font=dict(color="#374151", size=9, family="Inter")),
                margin=dict(t=30, b=20, l=50, r=50), height=340)
            st.plotly_chart(fig_rad, use_container_width=True, config=_CFG)

        with cr:
            section("Balanço Eletrolítico", "Na+K-Cl (mEq/kg) · ideal 200-280")
            eb_data = resultado.get("eb_fases", {})
            eb_vals = [eb_data.get(f, 0) for f in FASES]
            eb_cors = [CHART_COLORS[1] if 200 <= v <= 280 else
                       (CHART_COLORS[2] if 160 <= v <= 320 else CHART_COLORS[3])
                       for v in eb_vals]
            fig_eb = go.Figure()
            fig_eb.add_trace(go.Bar(
                x=F_SHORT, y=eb_vals, name="EB mEq/kg",
                marker_color=eb_cors,
                marker_line=dict(color="rgba(255,255,255,0)", width=0),
                text=[f"{v:.0f}" for v in eb_vals], textposition="outside",
                textfont=dict(color="#374151", size=10, family="Inter"),
                hovertemplate="<b>%{x}</b><br>EB: %{y:.1f} mEq/kg<extra></extra>"))
            fig_eb.add_hrect(y0=200, y1=280,
                             fillcolor="rgba(22,163,74,0.06)",
                             line=dict(color=CHART_COLORS[1], dash="dash", width=1),
                             annotation_text="Ideal 200-280",
                             annotation_font=dict(color=CHART_COLORS[1], size=9,
                                                  family="Inter"))
            fig_eb.update_layout(**_jlay(340, "Balanço Eletrolítico (mEq/kg)"))
            fig_eb.update_yaxes(title_text="mEq/kg", range=[0, max(max(eb_vals)*1.3, 360)])
            st.plotly_chart(fig_eb, use_container_width=True, config=_CFG)

        divider()

        section("Razões de Aminoácidos por Fase", "% relativa à Lisina · meta Ross 308")
        ratios_all = resultado.get("ratios_aa", {})
        AA_META = {"met_pct_lys": 36, "metcys_pct_lys": 75, "thr_pct_lys": 67,
                   "trp_pct_lys": 18, "val_pct_lys": 77}
        AA_LBL  = {"met_pct_lys": "Met/Lys", "metcys_pct_lys": "Met+Cys/Lys",
                   "thr_pct_lys": "Thr/Lys", "trp_pct_lys": "Trp/Lys",
                   "val_pct_lys": "Val/Lys"}
        aa_rows = []
        for aa_k, aa_lbl in AA_LBL.items():
            row = {"Aminoácido": aa_lbl, "Meta Ross308": f"{AA_META[aa_k]}%"}
            for fase, fs in zip(FASES, F_SHORT):
                v      = ratios_all.get(fase, {}).get(aa_k, 0)
                meta_v = AA_META[aa_k]
                status = "✓" if v >= meta_v * 0.98 else "⚠"
                row[fs] = f"{status} {v:.1f}%"
            aa_rows.append(row)
        st.dataframe(pd.DataFrame(aa_rows).set_index("Aminoácido"), use_container_width=True)

        divider()
        col_sp, col_grp = st.columns(2)

        with col_sp:
            section("Shadow Prices (Grower)", "custo marginal das restrições ativas")
            sp = form.get("grower", {}).get("shadow_prices", {})
            if sp:
                sp_rows = []
                for nut, sv in sorted(sp.items(), key=lambda x: -abs(x[1]["shadow_ton"])):
                    sp_rows.append({
                        "Nutriente":     NUT_LBL.get(nut, nut),
                        "Meta":          f"{sv['meta']:.4f}",
                        "Tipo":          sv["tipo"].upper(),
                        "$/ton (+1 un)": f"{sv['shadow_ton']:+.3f}",
                        "$/kg (+1 un)":  f"{sv['shadow_kg']:+.7f}",
                        "Status":        "BINDING",
                    })
                st.dataframe(pd.DataFrame(sp_rows).set_index("Nutriente"),
                             use_container_width=True)
                st.caption("Shadow price positivo = restrição ativa. "
                           "Quanto o custo da ração aumenta ao elevar o requisito em 1 unidade.")
            else:
                st.info("Nenhum shadow price calculado para esta fase.")

        with col_grp:
            section("Custo por Grupo de Ingredientes", "Grower · $/kg de ração")
            grupos = resultado.get("custo_grupos_grower", {})
            if grupos:
                fig_grp = go.Figure(go.Bar(
                    x=list(grupos.keys()), y=list(grupos.values()),
                    marker_color=CHART_COLORS[:len(grupos)],
                    marker_line=dict(color="rgba(255,255,255,0)", width=0),
                    text=[f"${v:.4f}" for v in grupos.values()],
                    textposition="outside",
                    textfont=dict(color="#374151", size=9, family="Inter"),
                    hovertemplate="<b>%{x}</b><br>Custo: $%{y:.5f}/kg<extra></extra>"))
                fig_grp.update_layout(**_jlay(300, "Custo por Grupo ($/kg · Grower)"))
                fig_grp.update_yaxes(title_text="$/kg ração")
                st.plotly_chart(fig_grp, use_container_width=True, config=_CFG)


# ┌──────────────────────────────────────────────────────────────┐
# │  ABA 3 · PRODUÇÃO                                            │
# └──────────────────────────────────────────────────────────────┘
with T_PROD:
    if not ok:
        st.error(resultado["status"])
    else:
        from modules.optimizer import (calcular_epef, custo_producao_total,
                                       escalas_frota, break_even_preco,
                                       break_even_custo_total)

        d     = resultado["desempenho"]
        epef  = calcular_epef(resultado, int(idade_d), float(mort_pct))
        cprod = custo_producao_total(resultado, custos_extras)
        frota = escalas_frota(resultado, int(n_aves), float(mort_pct))
        custo_ext = sum(custos_extras.values())

        # ── 7 KPI cards full row
        section("Índices Zootécnicos de Produção")
        z1, z2, z3, z4, z5, z6, z7 = st.columns(7)
        ec = "green" if epef["EPEF"] >= 420 else ("amber" if epef["EPEF"] >= 340 else "red")
        card(z1, f"{epef['EPEF']:.0f}",                "EPEF",            ec, sub=epef["classe"])
        card(z2, f"{epef['viabilidade_pct']:.1f}%",    "Viabilidade",     "gray")
        card(z3, f"{epef['ganho_diario_g']:.1f} g",    "Ganho Diário",    "blue")
        card(z4, f"{epef['consumo_diario_g']:.1f} g",  "Consumo Diário",  "amber")
        card(z5, f"{epef['peso_estimado_kg']:.3f} kg", f"PV {int(idade_d)}d", "blue")
        card(z6, f"${resultado['custo_por_kg_pv']:.4f}", "Custo/kg PV",   "amber")
        card(z7, f"${cprod['custo_por_kg_ganho']:.4f}", "Custo/kg Ganho", "red")

        divider()

        # ── Waterfall custo total
        section("Custo Total de Produção", "breakdown por item · $/ave · waterfall")
        itens  = cprod["itens"]
        fig_wf = go.Figure(go.Waterfall(
            x=list(itens.keys()) + ["TOTAL"],
            y=list(itens.values()) + [cprod["total"]],
            measure=["relative"] * len(itens) + ["total"],
            text=[f"${v:.3f}" for v in list(itens.values()) + [cprod["total"]]],
            textfont=dict(color="#374151", size=9, family="Inter"),
            textposition="outside",
            increasing=dict(marker=dict(color="rgba(37,99,235,0.65)",
                                        line=dict(color=CHART_COLORS[0], width=1))),
            totals=dict(marker=dict(color="rgba(217,119,6,0.80)",
                                    line=dict(color=CHART_COLORS[2], width=1.5))),
            connector=dict(line=dict(color="#D1D9E0", dash="dot", width=1)),
            hovertemplate="<b>%{x}</b><br>$%{y:.4f}<extra></extra>"))
        fig_wf.update_layout(**_jlay(340, "Custo Total ($/ave)"))
        fig_wf.update_yaxes(title_text="$/ave")
        st.plotly_chart(fig_wf, use_container_width=True, config=_CFG)

        divider()

        # ── Break-Even
        section("Análise Break-Even", "preço mínimo de venda ($/kg) para cobrir custos")

        def _be_str(bev):
            if bev is None:
                return "N/A"
            return "< $0.00" if bev <= 0 else f"${bev:.3f}"

        be_cols = st.columns(3)
        for i, (cen_be, lbl_be, key_p) in enumerate([
            ("vivo",      "Frango Vivo",    "frango_vivo"),
            ("carcaca",   "Carcaça WOG",    "carcaca"),
            ("desossado", "Peito Desossado","peito_desossado"),
        ]):
            be_feed  = break_even_preco(programa, precos, cen_be)
            be_total = break_even_custo_total(resultado, custos_extras, cen_be, precos)
            bev_f    = be_feed.get("break_even")
            bev_t    = be_total.get("break_even_total")
            marg_f   = be_feed.get("margem_atual_pct")
            marg_t   = be_total.get("margem_atual_pct")
            pa       = precos.get(key_p, 0)
            cor_f    = "green" if (marg_f and marg_f > 10) else ("amber" if marg_f else "red")
            cor_t    = "green" if (marg_t and marg_t > 5) else ("amber" if marg_t else "red")
            clr_f = _C[cor_f]; clr_t = _C[cor_t]

            with be_cols[i]:
                st.markdown(f"""
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:14px;
                            overflow:hidden;box-shadow:0 1px 6px rgba(15,23,42,0.07);
                            font-family:{_FONT};margin-bottom:8px;">
                  <div style="height:3px;background:linear-gradient(90deg,#2563EB,#3B82F6);"></div>
                  <div style="padding:16px;">
                    <div style="font-size:0.56rem;font-weight:700;color:#94A3B8;
                                letter-spacing:0.5px;text-transform:uppercase;margin-bottom:12px;">
                      Break-Even &middot; {lbl_be}</div>
                    <div style="display:flex;justify-content:space-between;gap:10px;">
                      <div style="flex:1;background:#F8FAFC;border-radius:10px;padding:12px;
                                  border:1px solid #F1F5F9;">
                        <div style="font-size:0.52rem;font-weight:700;color:#94A3B8;
                                    text-transform:uppercase;margin-bottom:6px;">Feed Apenas</div>
                        <div style="font-size:1.15rem;font-weight:800;color:{clr_f};
                                    white-space:nowrap;letter-spacing:-0.5px;">{_be_str(bev_f)}</div>
                        <div style="font-size:0.67rem;color:#64748B;margin-top:5px;">
                          Margem: {f'{marg_f:+.1f}%' if marg_f is not None else 'N/A'}</div>
                      </div>
                      <div style="flex:1;background:#F8FAFC;border-radius:10px;padding:12px;
                                  border:1px solid #F1F5F9;">
                        <div style="font-size:0.52rem;font-weight:700;color:#94A3B8;
                                    text-transform:uppercase;margin-bottom:6px;">Custo Total</div>
                        <div style="font-size:1.15rem;font-weight:800;color:{clr_t};
                                    white-space:nowrap;letter-spacing:-0.5px;">{_be_str(bev_t)}</div>
                        <div style="font-size:0.67rem;color:#64748B;margin-top:5px;">
                          Margem: {f'{marg_t:+.1f}%' if marg_t is not None else 'N/A'}</div>
                      </div>
                    </div>
                    <div style="font-size:0.65rem;color:#94A3B8;border-top:1px solid #F1F5F9;
                                margin-top:12px;padding-top:8px;">
                      Preço atual: ${pa:.3f}/kg
                      &nbsp;&middot;&nbsp; Custo total/ave: ${be_total['custo_total_ave']:.4f}
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

        divider()

        # ── IOFC vs IOAC
        section("IOFC vs IOAC por Cenário", "margem sobre custo feed vs custo total · $/ave")
        cen_list = [("vivo","Vivo"),("carcaca","Carcaça"),("desossado","Peito")]
        iofc_v   = [resultado.get(f"mofc_{c}", 0) for c, _ in cen_list]
        ioac_v   = [v - custo_ext for v in iofc_v]
        fig_io   = go.Figure()
        fig_io.add_trace(go.Bar(name="IOFC (feed)", x=[l for _, l in cen_list],
            y=iofc_v, marker_color=CHART_COLORS[0],
            marker_line=dict(color="rgba(255,255,255,0)", width=0),
            text=[f"${v:.3f}" for v in iofc_v], textposition="outside",
            textfont=dict(color="#374151", size=9, family="Inter"),
            hovertemplate="<b>%{x}</b><br>IOFC: $%{y:.4f}<extra></extra>"))
        fig_io.add_trace(go.Bar(name="IOAC (total)", x=[l for _, l in cen_list],
            y=ioac_v, marker_color=CHART_COLORS[1],
            marker_line=dict(color="rgba(255,255,255,0)", width=0),
            text=[f"${v:.3f}" for v in ioac_v], textposition="outside",
            textfont=dict(color="#374151", size=9, family="Inter"),
            hovertemplate="<b>%{x}</b><br>IOAC: $%{y:.4f}<extra></extra>"))
        fig_io.add_hline(y=0, line_color="#DC2626", line_width=1.5,
                         line_dash="dot", opacity=0.5,
                         annotation_text="Break-even",
                         annotation_font=dict(color="#DC2626", size=9, family="Inter"))
        fig_io.update_layout(**_jlay(300, "IOFC vs IOAC ($/ave)",
                                     extra=dict(barmode="group",
                                                bargap=0.25, bargroupgap=0.06)))
        fig_io.update_yaxes(title_text="$/ave")
        st.plotly_chart(fig_io, use_container_width=True, config=_CFG)

        section("Resultado de Frota Detalhado", f"{int(n_aves):,} aves · {mort_pct:.1f}% mortalidade")
        n_vend = frota["n_aves_vendidas"]
        fr_data = {
            "Item": ["Aves alojadas", "Aves vendidas", "Mortalidade (aves)",
                     "Custo feed total", "Custo total produção",
                     "Receita Vivo", "Receita Carcaça", "Receita Desossado",
                     "MOFC Vivo", "MOFC Carcaça", "MOFC Desossado",
                     "IOAC Vivo", "IOAC Carcaça", "IOAC Peito",
                     "Biomassa total"],
            "Valor": [
                f"{int(frota['n_aves_alojadas']):,}",
                f"{int(n_vend):,}",
                f"{int(frota['n_aves_alojadas'] - n_vend):,}",
                f"${frota['custo_total_alim']:,.2f}",
                f"${cprod['total'] * int(n_aves):,.2f}",
                f"${frota['receita_vivo']:,.2f}",
                f"${frota['receita_carcaca']:,.2f}",
                f"${frota['receita_desossado']:,.2f}",
                f"${frota['mofc_vivo']:,.2f}",
                f"${frota['mofc_carcaca']:,.2f}",
                f"${frota['mofc_desossado']:,.2f}",
                f"${frota['mofc_vivo'] - custo_ext * n_vend:,.2f}",
                f"${frota['mofc_carcaca'] - custo_ext * n_vend:,.2f}",
                f"${frota['mofc_desossado'] - custo_ext * n_vend:,.2f}",
                f"{frota['peso_total_kg']/1000:,.2f} t",
            ]
        }
        st.dataframe(pd.DataFrame(fr_data).set_index("Item"), use_container_width=True)


# ┌──────────────────────────────────────────────────────────────┐
# │  ABA 4 · OTIMIZADOR                                          │
# └──────────────────────────────────────────────────────────────┘
with T_OPT:
    section("Otimizador de Programa Nutricional",
            "busca grid ME × Lisina · maximiza MOFC por LP")
    oa, ob, oc = st.columns(3)
    with oa:
        me_min_o = st.number_input("ME mín.",  2700, 3200, 2900, 25)
        me_max_o = st.number_input("ME máx.",  3000, 3500, 3300, 25)
    with ob:
        lys_min_o = st.number_input("Lys mín.", 0.70, 1.20, 0.85, 0.01, format="%.2f")
        lys_max_o = st.number_input("Lys máx.", 0.90, 1.60, 1.40, 0.01, format="%.2f")
    with oc:
        n_grid_o = st.slider("Resolução grid", 5, 20, 10)
        st.markdown("")
        rodar = st.button("▶  Otimizar Agora", type="primary", use_container_width=True)

    section("Mapa de MOFC", f"ME × Lisina · cenário {cenario.upper()} · resolução analítica")
    n_heat = st.slider("Resolução do heatmap", 14, 30, 20, 2)
    heat   = _heat(_hash(precos), cenario, precos,
                   float(me_min_o), float(me_max_o),
                   float(lys_min_o), float(lys_max_o), n_heat)

    fig_heat = go.Figure()
    fig_heat.add_trace(go.Heatmap(
        x=heat["ME"].round(0), y=heat["Lys"].round(3), z=heat["Z"],
        colorscale=[[0, "#EFF6FF"], [0.3, "#93C5FD"], [0.7, "#2563EB"], [1.0, "#1D4ED8"]],
        colorbar=dict(title=dict(text=f"MOFC {cenario}",
                                 font=dict(color="#374151", size=10, family="Inter")),
                      tickfont=dict(color="#94A3B8", size=9, family="Inter")),
        hovertemplate="ME=%{x:.0f} kcal/kg<br>Lys=%{y:.3f}%<br>MOFC=$%{z:.4f}<extra></extra>"))
    for fase, clr_f, sym_f in zip(FASES, CHART_COLORS[:4], SYM_LIST):
        fig_heat.add_trace(go.Scatter(
            x=[programa[fase]["ame_n"]], y=[programa[fase]["dig_lys"]],
            mode="markers+text", text=[fase[:3].upper()],
            marker=dict(symbol=sym_f, size=12, color=clr_f,
                        line=dict(color="white", width=1.5)),
            textfont=dict(color=clr_f, size=9, family="Inter"),
            textposition="top right", name=fase.title(),
            hovertemplate=f"<b>{fase.title()}</b><br>ME=%{{x:.0f}}<br>Lys=%{{y:.3f}}<extra></extra>"))
    fig_heat.update_layout(**_jlay(440, f"Mapa MOFC — {cenario.upper()}"))
    fig_heat.update_xaxes(title_text="ME (kcal/kg)")
    fig_heat.update_yaxes(title_text="Dig. Lisina (%)")
    st.plotly_chart(fig_heat, use_container_width=True, config=_CFG)

    if rodar and ok:
        with st.spinner(f"Calculando {n_grid_o**2} combinações LP + RSM…"):
            from modules.optimizer import otimizar_programa
            opt = otimizar_programa(precos, cenario, (me_min_o, me_max_o),
                                    (lys_min_o, lys_max_o), n_grid=n_grid_o)
        if opt["status"] == "OK":
            ro    = opt["resultado_completo"]
            ganho = opt["mofc_otima"] - (resultado.get(f"mofc_{cenario}") or 0)
            ganho_frota = ganho * int(n_aves) * (1 - mort_pct / 100)
            st.success(
                f"✓ Ótimo encontrado  |  MOFC {cenario}: ${opt['mofc_otima']:.4f}/ave  "
                f"|  Ganho vs atual: ${ganho:+.4f}/ave  "
                f"|  Ganho frota: ${ganho_frota:+,.0f}")
            o1, o2 = st.columns(2)
            with o1:
                section("Programa Ótimo Encontrado")
                rows_ot = [{"Fase": f.title(),
                             "ME (kcal/kg)": int(opt["niveis_otimos"][f]["ame_n"]),
                             "Dig. Lys (%)": f"{opt['niveis_otimos'][f]['dig_lys']:.3f}"}
                           for f in FASES]
                st.dataframe(pd.DataFrame(rows_ot), use_container_width=True, hide_index=True)
            with o2:
                section("Comparativo Atual vs Ótimo")
                metr = ["MOFC Vivo", "MOFC Carcaça", "MOFC Desossado",
                        "Peso Vivo (RSM)", "CAA", "Peito (RSM)", "Custo Feed/ave"]
                av = [f"${resultado['mofc_vivo']:.4f}", f"${resultado['mofc_carcaca']:.4f}",
                      f"${resultado['mofc_desossado']:.4f}",
                      f"{resultado['desempenho']['peso_vivo_kg']:.3f} kg",
                      f"{resultado['desempenho']['caa']:.3f}",
                      f"{resultado['desempenho']['peito_kg']:.3f} kg",
                      f"${resultado['custo_alimentacao_por_ave']:.4f}"]
                ov = [f"${ro['mofc_vivo']:.4f}", f"${ro['mofc_carcaca']:.4f}",
                      f"${ro['mofc_desossado']:.4f}",
                      f"{ro['desempenho']['peso_vivo_kg']:.3f} kg",
                      f"{ro['desempenho']['caa']:.3f}",
                      f"{ro['desempenho']['peito_kg']:.3f} kg",
                      f"${ro['custo_alimentacao_por_ave']:.4f}"]
                st.dataframe(
                    pd.DataFrame({"Métrica": metr, "Atual": av, "Ótimo": ov}).set_index("Métrica"),
                    use_container_width=True)
        else:
            st.warning("Nenhuma solução factível encontrada. Tente expandir o espaço de busca.")


# ┌──────────────────────────────────────────────────────────────┐
# │  ABA 5 · RSM + CRESCIMENTO                                   │
# └──────────────────────────────────────────────────────────────┘
with T_RSM:
    from modules.biological import MODEL_STATS, otimo_biologico

    # ── 4 model stat cards
    section("Modelos RSM", "Genesis42d_G · regressão quadrática OLS · n=24 pontos")
    ms_cols = st.columns(4)
    for idx, (var, lbl, cor_ms) in enumerate([
        ("peso_vivo_kg", "Peso Vivo", "blue"),
        ("caa",          "CAA",       "amber"),
        ("carcaca_kg",   "Carcaça",   "teal"),
        ("peito_kg",     "Peito",     "green"),
    ]):
        s = MODEL_STATS[var]
        card(ms_cols[idx], f"R² = {s['R2']:.4f}", f"RSM {lbl}", cor_ms,
             sub=f"RMSE = {s['RMSE']:.4f}  ·  n = {s['n']}", pct=s["R2"] * 100)

    divider()

    # Controls left (1 col), 3D surface right (2 cols)
    c_cfg, c_3d = st.columns([1, 2])
    with c_cfg:
        var_rsm = st.selectbox("Variável",
            ["peso_vivo_kg", "caa", "carcaca_kg", "peito_kg"],
            format_func=lambda x: {"peso_vivo_kg": "Peso Vivo (kg)", "caa": "CAA",
                                    "carcaca_kg": "Carcaça (kg)", "peito_kg": "Peito (kg)"}[x])
        me_rng  = st.slider("ME (kcal/kg)", 2800, 3400, (2880, 3320), 25)
        lys_rng = st.slider("Lisina (%)",   0.75, 1.55, (0.85, 1.40), 0.01)
        n_rsm   = st.slider("Resolução 3D", 15, 50, 28, 5)

        ot     = otimo_biologico(var_rsm, minimizar=(var_rsm == "caa"),
                                  me_bounds=me_rng, lys_bounds=lys_rng)
        cor_ot = "amber" if var_rsm == "caa" else "blue"
        clr_ot = _C[cor_ot]
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E2E8F0;
                    border-radius:14px;overflow:hidden;
                    box-shadow:0 1px 6px rgba(15,23,42,0.07);margin-top:12px;">
          <div style="height:3px;background:linear-gradient(90deg,{clr_ot},{clr_ot}99);"></div>
          <div style="padding:16px;font-family:{_FONT};">
            <div style="font-size:0.53rem;font-weight:700;color:#94A3B8;letter-spacing:0.5px;
                        text-transform:uppercase;margin-bottom:6px;">
              Ótimo Biológico &middot;
              {var_rsm.replace('_kg','').replace('_',' ').title()}</div>
            <div style="font-size:1.45rem;font-weight:900;color:{clr_ot};line-height:1;
                        letter-spacing:-1px;">{ot['valor']:.3f}</div>
            <div style="font-size:0.78rem;color:#374151;margin-top:8px;line-height:1.6;">
              ME = {ot['ME_opt']:.0f} kcal/kg &nbsp;&middot;&nbsp;
              Lys = {ot['Lys_opt']:.3f}%</div>
            <div style="font-size:0.68rem;color:#94A3B8;margin-top:4px;">
              R² = {MODEL_STATS[var_rsm]['R2']:.4f} &nbsp;&middot;&nbsp;
              RMSE = {MODEL_STATS[var_rsm]['RMSE']:.4f}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    with c_3d:
        dados    = _surf(var_rsm, float(me_rng[0]), float(me_rng[1]),
                         float(lys_rng[0]), float(lys_rng[1]), n_rsm)
        nome_var = {"peso_vivo_kg": "Peso Vivo (kg)", "caa": "CAA",
                    "carcaca_kg": "Carcaça (kg)", "peito_kg": "Peito (kg)"}[var_rsm]
        cscale   = "RdYlGn_r" if var_rsm == "caa" else "Blues"

        fig3d = go.Figure(data=[go.Surface(
            x=dados["ME"][0, :], y=dados["Lys"][:, 0], z=dados["Z"],
            colorscale=cscale,
            colorbar=dict(title=dict(text=nome_var,
                                     font=dict(color="#374151", size=10, family="Inter")),
                          tickfont=dict(color="#94A3B8", size=9, family="Inter")),
            lighting=dict(ambient=0.75, diffuse=0.85, roughness=0.4),
            lightposition=dict(x=1, y=1, z=2),
            hovertemplate="ME=%{x:.0f}<br>Lys=%{y:.3f}<br>%{z:.3f}<extra></extra>")])
        fig3d.update_layout(
            scene=dict(
                xaxis=dict(title="ME (kcal/kg)", gridcolor="#E2E8F0",
                           backgroundcolor="#F8FAFD",
                           tickfont=dict(color="#374151", size=8, family="Inter")),
                yaxis=dict(title="Dig. Lisina (%)", gridcolor="#E2E8F0",
                           backgroundcolor="#F8FAFD",
                           tickfont=dict(color="#374151", size=8, family="Inter")),
                zaxis=dict(title=nome_var, gridcolor="#E2E8F0",
                           backgroundcolor="#F8FAFD",
                           tickfont=dict(color="#374151", size=8, family="Inter")),
                bgcolor="#F8FAFD",
                camera=dict(eye=dict(x=1.4, y=-1.4, z=0.85))),
            paper_bgcolor="#FFFFFF",
            margin=dict(l=0, r=0, t=42, b=0), height=480,
            font=dict(family="Inter,-apple-system,sans-serif", color="#374151"),
            hoverlabel=dict(bgcolor="#0F172A", bordercolor="#334155",
                            font_family="Inter", font_size=12, font_color="#F1F5F9"),
            title=dict(text=f"Superfície RSM · {nome_var}",
                       font=dict(color="#0F172A", size=12, family="Inter"), x=0.5))
        st.plotly_chart(fig3d, use_container_width=True, config=_CFG)

    # Contour below
    section("Mapa de Contorno", "visão superior · cada fase do programa marcada")
    fig_ct = go.Figure()
    fig_ct.add_trace(go.Contour(
        x=dados["ME"][0, :], y=dados["Lys"][:, 0], z=dados["Z"],
        colorscale=cscale, ncontours=22,
        colorbar=dict(title=dict(text=nome_var,
                                 font=dict(color="#374151", size=10, family="Inter")),
                      tickfont=dict(color="#94A3B8", size=9, family="Inter")),
        contours=dict(coloring="heatmap", showlabels=True,
                      labelfont=dict(color="#1E293B", size=8, family="Inter")),
        hovertemplate="ME=%{x:.0f}<br>Lys=%{y:.3f}<br>%{z:.3f}<extra></extra>"))
    for fase, clr_f, sym_f in zip(FASES, CHART_COLORS[:4], SYM_LIST):
        fig_ct.add_trace(go.Scatter(
            x=[programa[fase]["ame_n"]], y=[programa[fase]["dig_lys"]],
            mode="markers+text", text=[F_SHORT[FASES.index(fase)]],
            marker=dict(symbol=sym_f, size=13, color=clr_f,
                        line=dict(color="white", width=1.5)),
            textfont=dict(color=clr_f, size=9, family="Inter"),
            textposition="top right", name=fase.title(),
            hovertemplate=f"<b>{fase.title()}</b><br>ME=%{{x:.0f}}<br>Lys=%{{y:.3f}}<extra></extra>"))
    fig_ct.update_layout(**_jlay(400, f"Contorno RSM · {nome_var}"))
    fig_ct.update_xaxes(title_text="ME (kcal/kg)")
    fig_ct.update_yaxes(title_text="Dig. Lisina (%)")
    st.plotly_chart(fig_ct, use_container_width=True, config=_CFG)

    divider()

    # Growth curve section
    section("Curva de Crescimento Estimada",
            "escalada ao RSM Genesis42d_G · referência Ross 308")

    me_med_pond  = float(resultado.get("me_ponderado",  3050))
    lys_med_pond = float(resultado.get("lys_ponderada", 1.10))
    cc = _crescimento(me_med_pond, lys_med_pond, int(idade_d))

    escala = cc["escala_vs_padrao"]
    st.markdown(
        f'<p style="font-size:0.78rem;color:#64748B;margin-bottom:10px;font-family:{_FONT};">'
        f'Escala vs Ross 308: <strong style="color:{_C["blue"]};">'
        f'{escala:.3f}&times;</strong>'
        f' &nbsp;&middot;&nbsp; ME ponderada: <strong style="color:{_C["amber"]};">'
        f'{me_med_pond:.0f} kcal/kg</strong>'
        f' &nbsp;&middot;&nbsp; Lys ponderada: <strong style="color:{_C["green"]};">'
        f'{lys_med_pond:.3f}%</strong></p>', unsafe_allow_html=True)

    fig_cc = make_subplots(specs=[[{"secondary_y": True}]])

    # Ross 308 reference line (scaled back to standard)
    ross_pesos  = [v / escala for v in cc["peso_kg"]]
    fig_cc.add_trace(go.Scatter(
        x=cc["dias"], y=ross_pesos, name="Ross 308 (ref.)",
        mode="lines", line=dict(color="#94A3B8", width=1.5, dash="dot"),
        opacity=0.7,
        hovertemplate="<b>Ross 308</b><br>Dia %{x}: %{y:.3f} kg<extra></extra>"),
        secondary_y=False)

    # Estimated growth (our program)
    fig_cc.add_trace(go.Scatter(
        x=cc["dias"], y=cc["peso_kg"], name="Peso Vivo (kg)",
        mode="lines", line=dict(color=CHART_COLORS[0], width=3),
        fill="tonexty", fillcolor="rgba(37,99,235,0.06)",
        hovertemplate="<b>Prog. Atual</b><br>Dia %{x}: %{y:.3f} kg<extra></extra>"),
        secondary_y=False)

    fig_cc.add_trace(go.Scatter(
        x=cc["dias"], y=cc["caa_acumulado"], name="CAA Acumulado",
        mode="lines", line=dict(color=CHART_COLORS[2], width=2, dash="dot"),
        hovertemplate="<b>CAA Ac.</b><br>Dia %{x}: %{y:.3f}<extra></extra>"),
        secondary_y=True)

    fig_cc.add_trace(go.Bar(
        x=cc["dias"], y=[g / 1000 for g in cc["ganho_diario_g"]],
        name="Ganho Diário (kg)", opacity=0.25,
        marker_color=CHART_COLORS[1],
        hovertemplate="<b>GPD</b><br>Dia %{x}: %{y:.3f} kg/d<extra></extra>"),
        secondary_y=False)

    FASE_DIAS = {"Starter": 12, "Grower": 24, "Fin.1": 36, "Fin.2": int(idade_d)}
    for fs_lbl, fs_dia in FASE_DIAS.items():
        pv_at = float(np.interp(fs_dia, cc["dias"], cc["peso_kg"]))
        fig_cc.add_vline(x=fs_dia, line_dash="dash",
                         line_color="#CBD5E1", line_width=1)
        fig_cc.add_annotation(x=fs_dia, y=pv_at, text=fs_lbl,
                              font=dict(color="#64748B", size=8, family="Inter"),
                              showarrow=False, yshift=12)

    pv_abate = float(np.interp(idade_d, cc["dias"], cc["peso_kg"]))
    fig_cc.add_trace(go.Scatter(
        x=[idade_d], y=[pv_abate], mode="markers+text",
        marker=dict(symbol="star", size=16, color=CHART_COLORS[2],
                    line=dict(color="white", width=1.5)),
        text=[f"Abate: {pv_abate:.3f} kg"],
        textfont=dict(color=CHART_COLORS[2], size=10, family="Inter"),
        textposition="top right", name=f"Abate d{idade_d}",
        hovertemplate=f"<b>Abate d{idade_d}</b><br>{pv_abate:.3f} kg<extra></extra>"),
        secondary_y=False)

    fig_cc.update_layout(**_jlay(420, "Curva de Crescimento Estimada"))
    fig_cc.update_yaxes(title_text="Peso Vivo (kg) / Ganho (kg/d)",
                        secondary_y=False, title_font=dict(color="#64748B"))
    fig_cc.update_yaxes(title_text="CAA Acumulado", secondary_y=True,
                        title_font=dict(color="#64748B"))
    fig_cc.update_xaxes(title_text="Dias de vida", dtick=7)
    st.plotly_chart(fig_cc, use_container_width=True, config=_CFG)

    section("Projeção Semanal", f"semana a semana até d{int(idade_d)}")
    semanas = list(range(0, int(idade_d) + 1, 7))
    if idade_d not in semanas:
        semanas.append(int(idade_d))
    tab_cc = []
    for dia in semanas:
        idx  = min(dia, len(cc["dias"]) - 1)
        pv   = cc["peso_kg"][idx]
        gd   = cc["ganho_diario_g"][idx] if dia > 0 else 0
        ca   = cc["consumo_acum_kg"][idx]
        caa_ = cc["caa_acumulado"][idx]
        tab_cc.append({
            "Dia":           dia,
            "Semana":        f"S{dia//7}" if dia % 7 == 0 else f"d{dia}",
            "Peso (kg)":     f"{pv:.3f}",
            "GPD (g/d)":     f"{gd:.1f}",
            "Cons. Ac. (kg)":f"{ca:.3f}",
            "CAA Ac.":       f"{caa_:.3f}",
        })
    st.dataframe(pd.DataFrame(tab_cc).set_index("Dia"), use_container_width=True)


# ┌──────────────────────────────────────────────────────────────┐
# │  ABA 6 · SENSIBILIDADE                                       │
# └──────────────────────────────────────────────────────────────┘
with T_SENS:
    section("Sensibilidade Nutricional",
            "variação de ME ou Lisina em uma fase · impacto na MOFC")
    s1, s2, s3 = st.columns(3)
    with s1:
        nut_sel = st.selectbox("Nutriente", ["ame_n", "dig_lys"],
            format_func=lambda x: "Energia ME (kcal/kg)" if x == "ame_n" else "Dig. Lisina (%)")
    with s2:
        fase_sel = st.selectbox("Fase", FASES, index=1,
            format_func=lambda x: {"starter": "Starter (0-12d)", "grower": "Grower (12-24d)",
                                    "finisher1": "Finisher 1 (24-36d)",
                                    "finisher2": "Finisher 2 (36-45d)"}[x])
    with s3:
        n_pts = st.slider("Pontos na curva", 14, 40, 22, 2)

    gerar_curva = st.button("▶  Gerar Curva de Sensibilidade", type="primary")

    if gerar_curva and ok:
        with st.spinner("Formulando LP para cada nível…"):
            from modules.sensitivity import curva_resposta_nutriente
            curva = curva_resposta_nutriente(nut_sel, fase_sel, precos, programa, n_pts, cenario)

        vals_x = curva["valores_x"]
        mofc_y = [v if v is not None and not (isinstance(v, float) and np.isnan(v)) else None
                  for v in curva["mofc_y"]]
        opt_x  = curva["otimo_x"]
        opt_y  = curva["otimo_y"]
        val_at = programa[fase_sel][nut_sel]

        fig_sens = go.Figure()
        fig_sens.add_trace(go.Scatter(
            x=vals_x, y=mofc_y, mode="lines", name="MOFC",
            line=dict(color=CHART_COLORS[0], width=3),
            fill="tozeroy", fillcolor="rgba(37,99,235,0.06)",
            hovertemplate="<b>Nível %{x:.3f}</b><br>MOFC: $%{y:.4f}<extra></extra>"))
        fig_sens.add_trace(go.Scatter(
            x=[opt_x], y=[opt_y], mode="markers+text", name="Ótimo",
            marker=dict(symbol="star", size=18, color=CHART_COLORS[2],
                        line=dict(color="white", width=1.5)),
            text=[f"Ótimo: ${opt_y:.3f}"],
            textfont=dict(color=CHART_COLORS[2], size=10, family="Inter"),
            textposition="top right",
            hovertemplate=f"<b>Ótimo</b><br>Nível: {opt_x:.3f}<br>MOFC: ${opt_y:.4f}<extra></extra>"))
        fig_sens.add_vline(x=val_at, line_dash="dash", line_color="#DC2626", line_width=1.5,
                           annotation_text=f"Atual: {val_at:.3f}",
                           annotation_font=dict(color="#DC2626", size=9, family="Inter"))
        fig_sens.add_vline(x=opt_x, line_dash="dot", line_color=CHART_COLORS[2], line_width=1,
                           annotation_text=f"Ótimo: {opt_x:.3f}",
                           annotation_font=dict(color=CHART_COLORS[2], size=9, family="Inter"))
        fig_sens.add_hline(y=0, line_color="#DC2626", line_width=1, line_dash="dot",
                           opacity=0.40)

        label_x = "ME (kcal/kg)" if nut_sel == "ame_n" else "Dig. Lisina (%)"
        fig_sens.update_layout(**_jlay(380, f"MOFC {cenario} vs {label_x} · {fase_sel.title()}"))
        fig_sens.update_xaxes(title_text=label_x)
        fig_sens.update_yaxes(title_text=f"MOFC {cenario} ($/ave)")
        st.plotly_chart(fig_sens, use_container_width=True, config=_CFG)

        mofc_nnan = [v for v in curva["mofc_y"] if v is not None and not np.isnan(v)]
        delta = opt_y - min(mofc_nnan) if mofc_nnan else 0
        r1, r2, r3, r4 = st.columns(4)
        card(r1, f"{opt_x:.3f}",    f"Nível Ótimo ({label_x})", "amber")
        card(r2, f"${opt_y:.4f}",   "MOFC Máxima",              "green")
        card(r3, f"${delta:+.4f}",  "Ganho Mín→Ótimo",          "blue")
        card(r4, f"${delta*int(n_aves)*(1-mort_pct/100):+,.0f}",
             f"Ganho Frota {int(n_aves/1000):.0f}k aves",
             "green" if delta > 0 else "red")
    else:
        st.markdown(f"""
        <div style="text-align:center;padding:60px 20px;border:1px solid #E2E8F0;
                    border-radius:14px;background:#FFFFFF;font-family:{_FONT};
                    box-shadow:0 1px 6px rgba(15,23,42,0.05);">
          <div style="font-size:2.5rem;opacity:0.20;">📈</div>
          <div style="font-size:0.82rem;color:#94A3B8;font-weight:500;margin-top:12px;">
            Selecione o nutriente e a fase &middot; Clique em Gerar Curva
          </div>
        </div>""", unsafe_allow_html=True)

    divider()

    section("Sensibilidade ao Preço de Ingredientes",
            "impacto na MOFC por variação de custo")
    from modules.formulation import CUSTOS_POR_KG
    ING_OPTS = {
        10200: "Milho Amarelo (10200)",
        22045: "Farelo Soja 45% (22045)",
        22048: "Farelo Soja 48% (22048)",
        45050: "DL-Metionina (45050)",
        45000: "L-Lisina HCl (45000)",
        30000: "Óleo de Soja (30000)",
        25000: "Farinha de Peixe (25000)",
    }
    ia, ib = st.columns([1, 3])
    with ia:
        ing_c = st.selectbox("Ingrediente", list(ING_OPTS.keys()),
                             format_func=lambda x: ING_OPTS[x])
        var_p = st.slider("Variação ± (%)", 10, 60, 35, 5)
        n_ip  = st.slider("Pontos", 8, 20, 12)
        c_ing = st.button("Calcular", type="primary",
                          use_container_width=True, key="btn_ing")
    with ib:
        if c_ing and ok:
            with st.spinner("Rodando LP para cada preço…"):
                from modules.optimizer import sensibilidade_ingrediente
                ci = sensibilidade_ingrediente(ing_c, programa, precos, cenario, var_p/100, n_ip)
            fig_ig = go.Figure()
            fig_ig.add_trace(go.Scatter(
                x=ci["custos_x"], y=ci["mofc_y"],
                mode="lines+markers", line=dict(color=CHART_COLORS[0], width=2.5),
                marker=dict(size=6, color=CHART_COLORS[0],
                            line=dict(color="white", width=1)),
                fill="tozeroy", fillcolor="rgba(37,99,235,0.05)",
                hovertemplate="$%{x:.4f}/kg → MOFC $%{y:.4f}<extra></extra>"))
            fig_ig.add_vline(x=ci["custo_base"], line_dash="dash",
                             line_color=CHART_COLORS[2], line_width=1.5,
                             annotation_text="Preço atual",
                             annotation_font=dict(color=CHART_COLORS[2], size=9,
                                                  family="Inter"))
            fig_ig.update_layout(**_jlay(340, f"MOFC vs Preço · {ING_OPTS[ing_c]}"))
            fig_ig.update_xaxes(title_text="Preço ($/kg)")
            fig_ig.update_yaxes(title_text=f"MOFC {cenario} ($/ave)")
            st.plotly_chart(fig_ig, use_container_width=True, config=_CFG)
        else:
            st.info("Selecione o ingrediente e clique em Calcular.")

    divider()

    section("Sensibilidade ao Preço de Venda",
            "impacto na MOFC por variação de preço de mercado")
    pa, pb = st.columns([1, 3])
    with pa:
        pv_var   = st.selectbox("Variável de preço", list(precos.keys()),
            format_func=lambda x: {"frango_vivo":      "Frango Vivo ($/kg)",
                                    "carcaca":           "Carcaça WOG ($/kg)",
                                    "peito_desossado":   "Peito Desossado ($/kg)",
                                    "cortes_misc":       "Cortes Diversos ($/kg)"}[x])
        delta_pv = st.slider("Variação ± ($)", 0.10, 1.00, 0.40, 0.05)
        n_pv     = st.slider("Pontos ", 10, 40, 20)
        c_pv     = st.button("Calcular", use_container_width=True, key="btn_pv")
    with pb:
        if c_pv and ok:
            from modules.sensitivity import analise_preco_venda
            with st.spinner("Calculando…"):
                cpv = analise_preco_venda(pv_var, programa, precos, cenario, n_pv, delta_pv)
            fig_pv = go.Figure()
            fig_pv.add_trace(go.Scatter(
                x=cpv["precos_x"], y=cpv["mofc_y"],
                mode="lines+markers", line=dict(color=CHART_COLORS[1], width=2.5),
                marker=dict(size=6, color=CHART_COLORS[1],
                            line=dict(color="white", width=1)),
                fill="tozeroy", fillcolor="rgba(22,163,74,0.06)",
                hovertemplate="$%{x:.3f}/kg → MOFC $%{y:.4f}<extra></extra>"))
            fig_pv.add_vline(x=cpv["preco_base"], line_dash="dash",
                             line_color=CHART_COLORS[2], line_width=1.5,
                             annotation_text="Preço atual",
                             annotation_font=dict(color=CHART_COLORS[2], size=9,
                                                  family="Inter"))
            fig_pv.add_hline(y=0, line_color="#DC2626", line_width=1.5,
                             line_dash="dot", opacity=0.45,
                             annotation_text="Break-even",
                             annotation_font=dict(color="#DC2626", size=9, family="Inter"))
            fig_pv.update_layout(**_jlay(340, "MOFC vs Preço de Venda"))
            fig_pv.update_xaxes(title_text="Preço ($/kg)")
            fig_pv.update_yaxes(title_text=f"MOFC {cenario} ($/ave)")
            st.plotly_chart(fig_pv, use_container_width=True, config=_CFG)
        else:
            st.info("Selecione a variável e clique em Calcular.")
