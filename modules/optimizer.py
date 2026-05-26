"""
Orquestrador Econômico — Módulo 3
Integra Biológico (RSM) + Formulação (LP) → MOFC + KPIs completos.

Funções: calcular_mofc, break_even_preco, escalas_frota,
         calcular_epef, calcular_eb, custo_producao_total,
         otimizar_programa, grid_mofc, sensibilidade_ingrediente
"""

import numpy as np
from modules.biological import prever_desempenho
from modules.formulation import formular_programa_completo, carregar_ingredientes_ativos

# ── Requisitos base por fase (Formulation Set.xlsx — Nutrient Specs) ───────
REQUISITOS_FASE_BASE = {
    "starter": {
        "dig_met": 0.697, "dig_cys": 0.306, "dig_thr": 0.884,
        "dig_trp": 0.239, "dig_val": 1.003,
        "ca_total": 0.96, "p_npp": 0.49,
        "sodium": 0.22, "chloride": 0.28,
    },
    "grower": {
        "dig_met": 0.650, "dig_cys": 0.289, "dig_thr": 0.819,
        "dig_trp": 0.222, "dig_val": 0.927,
        "ca_total": 0.75, "p_npp": 0.43,
        "sodium": 0.20, "chloride": 0.28,
    },
    "finisher1": {
        "dig_met": 0.632, "dig_cys": 0.276, "dig_thr": 0.772,
        "dig_trp": 0.205, "dig_val": 0.885,
        "ca_total": 0.65, "p_npp": 0.37,
        "sodium": 0.18, "chloride": 0.26,
    },
    "finisher2": {
        "dig_met": 0.589, "dig_cys": 0.262, "dig_thr": 0.734,
        "dig_trp": 0.189, "dig_val": 0.840,
        "ca_total": 0.60, "p_npp": 0.33,
        "sodium": 0.18, "chloride": 0.26,
    },
}

PROP_CONSUMO = {"starter": 0.12, "grower": 0.28, "finisher1": 0.30, "finisher2": 0.30}

DIAS_FASE = {"starter": (0, 12), "grower": (12, 24), "finisher1": (24, 36), "finisher2": (36, 45)}

NIVEIS_PADRAO = {
    "starter":   {"ame_n": 2975, "dig_lys": 1.32},
    "grower":    {"ame_n": 3050, "dig_lys": 1.204},
    "finisher1": {"ame_n": 3100, "dig_lys": 1.135},
    "finisher2": {"ame_n": 3150, "dig_lys": 1.063},
}

# Proteína ideal — Ross 308 (% relativa à Lys digestível)
IDEAL_PROTEIN = {
    "met_pct_lys":    36,
    "metcys_pct_lys": 75,
    "thr_pct_lys":    67,
    "trp_pct_lys":    18,
    "val_pct_lys":    77,
}

# Padrões de mercado: Cobb 500 e Ross 308 (referência para comparação)
STANDARDS = {
    "Cobb 500": {
        "starter":   {"ame_n": 2950, "dig_lys": 1.32, "dig_met": 0.72, "dig_thr": 0.88, "ca_total": 0.96, "p_npp": 0.45},
        "grower":    {"ame_n": 3050, "dig_lys": 1.20, "dig_met": 0.65, "dig_thr": 0.80, "ca_total": 0.84, "p_npp": 0.42},
        "finisher1": {"ame_n": 3100, "dig_lys": 1.09, "dig_met": 0.59, "dig_thr": 0.73, "ca_total": 0.72, "p_npp": 0.38},
        "finisher2": {"ame_n": 3150, "dig_lys": 1.01, "dig_met": 0.55, "dig_thr": 0.68, "ca_total": 0.65, "p_npp": 0.35},
    },
    "Ross 308": {
        "starter":   {"ame_n": 2975, "dig_lys": 1.35, "dig_met": 0.72, "dig_thr": 0.87, "ca_total": 0.98, "p_npp": 0.48},
        "grower":    {"ame_n": 3050, "dig_lys": 1.21, "dig_met": 0.66, "dig_thr": 0.81, "ca_total": 0.85, "p_npp": 0.43},
        "finisher1": {"ame_n": 3100, "dig_lys": 1.11, "dig_met": 0.61, "dig_thr": 0.74, "ca_total": 0.75, "p_npp": 0.40},
        "finisher2": {"ame_n": 3150, "dig_lys": 1.04, "dig_met": 0.57, "dig_thr": 0.70, "ca_total": 0.68, "p_npp": 0.37},
    },
}


def _montar_programa(niveis: dict, base: dict | None = None) -> dict:
    b = base or REQUISITOS_FASE_BASE
    return {fase: {**b.get(fase, {}), **niv} for fase, niv in niveis.items()}


# ── Balanço eletrolítico ─────────────────────────────────────────────────────

def calcular_eb(nuts: dict) -> float:
    """
    Electrolyte Balance = Na + K - Cl (mEq/kg de ração).
    Faixa ideal broiler: 200–280 mEq/kg.
    Cada mineral em %, convertido para mEq via peso molecular.
    """
    na = nuts.get("sodium",    0) * 10 / 22.990 * 1000   # % → g/kg → mEq
    k  = nuts.get("potassium", 0) * 10 / 39.098 * 1000
    cl = nuts.get("chloride",  0) * 10 / 35.453 * 1000
    return round(na + k - cl, 1)


# ── EPEF ────────────────────────────────────────────────────────────────────

# Curva de referência Ross 308 para correção de idade no EPEF
_EPEF_DIAS_REF = np.array([35,    42,    45,    49,    56])
_EPEF_PV_REF   = np.array([2.420, 3.070, 3.290, 3.630, 4.140])  # kg padrão comercial
_EPEF_PV_RSM_REF = 3.630   # RSM calibrado ao equivalente de 49d


def calcular_epef(resultado: dict, idade_dias: int = 45,
                  mortalidade_pct: float = 3.0) -> dict:
    """
    European Production Efficiency Factor com correção de idade.

    O RSM é calibrado para ~49d (média dos dados experimentais).
    Corrigimos o PV estimado para a idade real de abate usando a curva Ross 308,
    garantindo EPEF realista para qualquer idade entre 35-56 dias.

    EPEF = (Viabilidade% × PV_kg) / (CAA × Idade_dias) × 100
    Benchmark (calibrado para RSM Genesis42d_G):
        >420 = EXCELENTE · 340-420 = BOM · 270-340 = REGULAR · <270 = RUIM
    """
    d      = resultado["desempenho"]
    pv_rsm = d["peso_vivo_kg"]   # peso previsto pelo RSM (ref ~49d)
    caa    = d["caa"]

    # Escala do programa vs padrão Ross 308 a 49d
    escala = pv_rsm / _EPEF_PV_RSM_REF

    # Peso estimado na idade real de abate
    pv_std_target = float(np.interp(float(idade_dias), _EPEF_DIAS_REF, _EPEF_PV_REF))
    pv  = round(pv_std_target * escala, 3)

    # CAA ajustado: piora 0.8% por dia acima de 49d (deposição de gordura)
    if idade_dias > 49:
        caa = round(caa * (1 + 0.008 * (idade_dias - 49)), 3)

    viab = round((1 - mortalidade_pct / 100) * 100, 1)
    epef = round(viab * pv / (caa * idade_dias) * 100, 1)

    gpd = round(pv / idade_dias * 1000, 1)   # ganho/dia g
    cpd = round(pv * caa / idade_dias * 1000, 1)  # consumo/dia g

    # Custo de ganho relativo (eficiência biológica normalizada)
    eff_bio = round(pv / (caa * idade_dias / 100), 3)

    classe = ("EXCELENTE" if epef >= 420 else
              "BOM"       if epef >= 340 else
              "REGULAR"   if epef >= 270 else "RUIM")

    return {
        "EPEF":              epef,
        "viabilidade_pct":   viab,
        "ganho_diario_g":    gpd,
        "consumo_diario_g":  cpd,
        "peso_estimado_kg":  pv,
        "caa_ajustado":      caa,
        "dias_mercado":      idade_dias,
        "eficiencia_bio":    eff_bio,
        "classe":            classe,
    }


# ── Custo total de produção ──────────────────────────────────────────────────

def custo_producao_total(resultado: dict, custos_extras: dict) -> dict:
    """
    Custo total de produção incluindo feed + outros.

    custos_extras: {
        'pinto':       $/ave  (custo do pinto 1 dia)
        'medicacao':   $/ave  (vacinas + medicamentos)
        'energia':     $/ave  (aquecimento + iluminação)
        'mao_obra':    $/ave  (mão de obra + gestão)
        'depreciacao': $/ave  (depreciação do galpão)
        'outros':      $/ave  (mortalidade + overhead)
    }
    """
    d    = resultado["desempenho"]
    pv   = d["peso_vivo_kg"]
    feed = resultado["custo_alimentacao_por_ave"]

    itens = {
        "Feed":        feed,
        "Pinto":       custos_extras.get("pinto",       0.45),
        "Medicação":   custos_extras.get("medicacao",   0.05),
        "Energia":     custos_extras.get("energia",     0.04),
        "Mão de Obra": custos_extras.get("mao_obra",    0.07),
        "Depreciação": custos_extras.get("depreciacao", 0.10),
        "Outros":      custos_extras.get("outros",      0.04),
    }
    total = sum(itens.values())

    extras_total = total - feed
    return {
        "itens":              itens,
        "total":              round(total, 4),
        "total_por_kg":       round(total / pv if pv > 0 else 0, 4),
        "feed_pct":           round(feed / total * 100, 1) if total > 0 else 0,
        "extras_total":       round(extras_total, 4),
        "custo_feed":         round(feed, 4),
        "custo_por_kg_ganho": round(total / pv if pv > 0 else 0, 4),
    }


# ── MOFC principal ───────────────────────────────────────────────────────────

def calcular_mofc(niveis_nutri: dict, precos: dict,
                  cache_formulacao: dict | None = None,
                  custos_ingredientes: dict | None = None,
                  requisitos_base: dict | None = None) -> dict:
    """
    MOFC completa: biológico RSM + formulação LP + economics.
    Inclui shadow prices, ratios AA, balanço eletrolítico por fase.
    custos_ingredientes: overrides de preço {código: $/kg} p/ ingredientes específicos.
    requisitos_base: substitui REQUISITOS_FASE_BASE quando fornecido (p/ outros animais).
    """
    programa = _montar_programa(niveis_nutri, base=requisitos_base)
    form     = cache_formulacao or formular_programa_completo(
        programa, custos_ingredientes=custos_ingredientes)

    erros = [f"{f}: {form[f]['status']}" for f in form if form[f]["status"] != "OK"]
    if erros:
        return {"status": " | ".join(erros),
                "mofc_vivo": None, "mofc_carcaca": None, "mofc_desossado": None}

    custo_kg = {f: form[f]["custo_por_kg"] for f in form}

    # Predição RSM — médias ponderadas pelo consumo
    me_med  = np.average([niveis_nutri[f]["ame_n"]   for f in niveis_nutri],
                         weights=[PROP_CONSUMO[f] for f in niveis_nutri])
    lys_med = np.average([niveis_nutri[f]["dig_lys"] for f in niveis_nutri],
                         weights=[PROP_CONSUMO[f] for f in niveis_nutri])
    desemp  = prever_desempenho(me_med, lys_med)

    pv  = desemp["peso_vivo_kg"]
    caa = desemp["caa"]
    car = desemp["carcaca_kg"]
    pei = desemp["peito_kg"]

    consumo_total = pv * caa
    custo_alim    = sum(consumo_total * PROP_CONSUMO[f] * custo_kg[f] for f in form)

    p_vivo   = precos.get("frango_vivo",     1.00)
    p_car    = precos.get("carcaca",         0.90)
    p_peito  = precos.get("peito_desossado", 1.87)
    p_cortes = precos.get("cortes_misc",     1.10)

    outros_car        = max(car - pei, 0)
    receita_vivo      = pv  * p_vivo
    receita_carcaca   = car * p_car
    receita_desossado = pei * p_peito + outros_car * p_cortes

    # Razões de proteína ideal + balanço eletrolítico por fase
    ratios_aa = {}
    eb_fases  = {}
    for fase in form:
        nuts  = form[fase].get("nutrientes_calculados", {})
        lys_f = nuts.get("dig_lys", 0)
        if lys_f > 0:
            met = nuts.get("dig_met", 0)
            cys = nuts.get("dig_cys", 0)
            thr = nuts.get("dig_thr", 0)
            trp = nuts.get("dig_trp", 0)
            val = nuts.get("dig_val", 0)
            ratios_aa[fase] = {
                "met_pct_lys":    round(met / lys_f * 100, 1),
                "metcys_pct_lys": round((met + cys) / lys_f * 100, 1),
                "thr_pct_lys":    round(thr / lys_f * 100, 1),
                "trp_pct_lys":    round(trp / lys_f * 100, 1),
                "val_pct_lys":    round(val / lys_f * 100, 1),
            }
        eb_fases[fase] = calcular_eb(nuts)

    # Custo por grupo de ingredientes (Energia, Proteína, Minerais, AA sintéticos, Outros)
    from modules.formulation import CUSTOS_POR_KG, get_ingredient_names
    _custos_ef = {**CUSTOS_POR_KG, **(custos_ingredientes or {})}
    GRUPOS = {
        "Energia":       [10010, 10100, 10200, 10300, 20000, 23500, 24000, 24015, 30000],
        "Proteína":      [22045, 22046, 22048, 22560, 25000, 25115, 25150],
        "Minerais":      [35020, 36000, 37000, 48010],
        "AA Sint.":      [45000, 45050, 45100, 45250],
        "Premix/Outros": [40000, 66080, 67001],
    }
    custo_grupos_grower = {}
    comp_grower = form.get("grower", {}).get("composicao", {})
    for grupo, codigos in GRUPOS.items():
        custo_ing_grupo = sum(
            (comp_grower.get(c, 0) / 100) * _custos_ef.get(c, 0) for c in codigos
        )
        custo_grupos_grower[grupo] = round(custo_ing_grupo, 5)

    return {
        "status":                    "OK",
        "desempenho":                desemp,
        "custo_alimentacao_por_ave": round(custo_alim,    4),
        "custo_por_kg_pv":           round(custo_alim / pv if pv > 0 else 0, 4),
        "custos_racao_por_kg":       custo_kg,
        "receita_vivo":              round(receita_vivo,      4),
        "receita_carcaca":           round(receita_carcaca,   4),
        "receita_desossado":         round(receita_desossado, 4),
        "mofc_vivo":                 round(receita_vivo     - custo_alim, 4),
        "mofc_carcaca":              round(receita_carcaca  - custo_alim, 4),
        "mofc_desossado":            round(receita_desossado - custo_alim, 4),
        "formulacao":                form,
        "ratios_aa":                 ratios_aa,
        "eb_fases":                  eb_fases,
        "custo_grupos_grower":       custo_grupos_grower,
        "me_ponderado":              round(me_med,  0),
        "lys_ponderada":             round(lys_med, 3),
    }


# ── Formulação LP apenas (sem RSM) — espécies não-broiler ────────────────────

def calcular_form_apenas(niveis_nutri: dict,
                          custos_ingredientes: dict | None = None,
                          requisitos_base: dict | None = None) -> dict:
    """
    Formulação LP sem predição RSM. Uso para espécies não-broiler (peru, poedeira, etc.).
    Retorna: status, formulacao, custos_racao_por_kg, ratios_aa, eb_fases, custo_grupos_ref.
    """
    from modules.formulation import CUSTOS_POR_KG, get_ingredient_names
    programa = _montar_programa(niveis_nutri, base=requisitos_base)
    form     = formular_programa_completo(programa, custos_ingredientes=custos_ingredientes)

    erros = [f"{f}: {form[f]['status']}" for f in form if form[f]["status"] != "OK"]
    if erros:
        return {"status": " | ".join(erros), "formulacao": {},
                "ratios_aa": {}, "eb_fases": {}, "custos_racao_por_kg": {},
                "custo_grupos_ref": {}}

    _custos_ef = {**CUSTOS_POR_KG, **(custos_ingredientes or {})}
    GRUPOS = {
        "Energia":       [10010, 10100, 10200, 10300, 20000, 23500, 24000, 24015, 30000],
        "Proteína":      [22045, 22046, 22048, 22560, 25000, 25115, 25150],
        "Minerais":      [35020, 36000, 37000, 48010],
        "AA Sint.":      [45000, 45050, 45100, 45250],
        "Premix/Outros": [40000, 66080, 67001],
    }

    ratios_aa = {}
    eb_fases  = {}
    custo_grupos_ref = {}

    first_fase  = next(iter(form))
    comp_ref    = form.get(first_fase, {}).get("composicao", {})
    for grupo, codigos in GRUPOS.items():
        custo_grupos_ref[grupo] = round(
            sum((comp_ref.get(c, 0) / 100) * _custos_ef.get(c, 0) for c in codigos), 5)

    for fase in form:
        nuts  = form[fase].get("nutrientes_calculados", {})
        eb_fases[fase] = calcular_eb(nuts)
        lys_f = nuts.get("dig_lys", 0)
        if lys_f > 0:
            met = nuts.get("dig_met", 0); cys = nuts.get("dig_cys", 0)
            thr = nuts.get("dig_thr", 0); trp = nuts.get("dig_trp", 0)
            val = nuts.get("dig_val", 0)
            ratios_aa[fase] = {
                "met_pct_lys":    round(met / lys_f * 100, 1),
                "metcys_pct_lys": round((met + cys) / lys_f * 100, 1),
                "thr_pct_lys":    round(thr / lys_f * 100, 1),
                "trp_pct_lys":    round(trp / lys_f * 100, 1),
                "val_pct_lys":    round(val / lys_f * 100, 1),
            }

    return {
        "status":               "OK",
        "formulacao":           form,
        "custos_racao_por_kg":  {f: form[f]["custo_por_kg"] for f in form},
        "ratios_aa":            ratios_aa,
        "eb_fases":             eb_fases,
        "custo_grupos_ref":     custo_grupos_ref,
    }


# ── Break-even ───────────────────────────────────────────────────────────────

def break_even_preco(niveis_nutri: dict, precos: dict, cenario: str) -> dict:
    res = calcular_mofc(niveis_nutri, precos)
    if res["status"] != "OK":
        return {}
    custo    = res["custo_alimentacao_por_ave"]
    d        = res["desempenho"]
    p_cortes = precos.get("cortes_misc", 1.10)

    if cenario == "vivo":
        kg = d["peso_vivo_kg"]
        be = custo / kg if kg > 0 else None
    elif cenario == "carcaca":
        kg = d["carcaca_kg"]
        be = custo / kg if kg > 0 else None
    else:
        kg_pei = d["peito_kg"]
        kg_out = d["outros_car_kg"]
        be = (custo - kg_out * p_cortes) / kg_pei if kg_pei > 0 else None

    key = {"vivo": "frango_vivo", "carcaca": "carcaca", "desossado": "peito_desossado"}.get(cenario)
    preco_atual = precos.get(key, 1.00)

    be_val  = round(be, 4) if be is not None else None
    be_pos  = be_val is not None and be_val > 0
    marg    = round((preco_atual / be - 1) * 100, 1) if be_pos else None

    return {
        "break_even":        be_val,
        "break_even_valido": be_pos,
        "preco_atual":       preco_atual,
        "margem_atual_pct":  marg,
        "margem_5pct":       round(be * 1.05, 4) if be_pos else None,
        "margem_10pct":      round(be * 1.10, 4) if be_pos else None,
        "margem_15pct":      round(be * 1.15, 4) if be_pos else None,
        "custo_alimentacao": round(custo, 4),
    }


def break_even_custo_total(resultado: dict, custos_extras: dict,
                           cenario: str, precos: dict) -> dict:
    """
    Break-even considerando TODOS os custos (feed + produção).
    Retorna o preço de venda mínimo para cobrir custo total por ave.
    """
    d        = resultado["desempenho"]
    feed     = resultado["custo_alimentacao_por_ave"]
    extras   = sum(custos_extras.values())
    custo_t  = feed + extras
    p_cortes = precos.get("cortes_misc", 1.10)

    if cenario == "vivo":
        kg = d["peso_vivo_kg"]
        be = custo_t / kg if kg > 0 else None
    elif cenario == "carcaca":
        kg = d["carcaca_kg"]
        be = custo_t / kg if kg > 0 else None
    else:
        kg_pei = d["peito_kg"]
        kg_out = d["outros_car_kg"]
        receita_outros = kg_out * p_cortes
        be = (custo_t - receita_outros) / kg_pei if kg_pei > 0 else None

    key         = {"vivo": "frango_vivo", "carcaca": "carcaca",
                   "desossado": "peito_desossado"}.get(cenario)
    preco_atual = precos.get(key, 1.00)
    be_pos      = be is not None and be > 0
    marg        = round((preco_atual / be - 1) * 100, 1) if be_pos else None

    return {
        "custo_total_ave":   round(custo_t, 4),
        "custo_feed_ave":    round(feed, 4),
        "custo_extras_ave":  round(extras, 4),
        "break_even_total":  round(be, 4) if be_pos else be,
        "break_even_valido": be_pos,
        "preco_atual":       preco_atual,
        "margem_atual_pct":  marg,
    }


# ── Escala de frota ──────────────────────────────────────────────────────────

def escalas_frota(resultado: dict, n_aves: int = 100_000,
                  mortalidade_pct: float = 3.0) -> dict:
    sobrev = n_aves * (1 - mortalidade_pct / 100)
    return {
        "n_aves_alojadas":   n_aves,
        "n_aves_vendidas":   round(sobrev),
        "mortalidade_pct":   mortalidade_pct,
        "custo_total_alim":  round(resultado["custo_alimentacao_por_ave"] * n_aves, 0),
        "receita_vivo":      round(resultado["receita_vivo"]               * sobrev, 0),
        "receita_carcaca":   round(resultado["receita_carcaca"]            * sobrev, 0),
        "receita_desossado": round(resultado["receita_desossado"]          * sobrev, 0),
        "mofc_vivo":         round(resultado["mofc_vivo"]                  * sobrev, 0),
        "mofc_carcaca":      round(resultado["mofc_carcaca"]               * sobrev, 0),
        "mofc_desossado":    round(resultado["mofc_desossado"]             * sobrev, 0),
        "peso_total_kg":     round(resultado["desempenho"]["peso_vivo_kg"] * sobrev, 0),
    }


# ── Sensibilidade a ingredientes ─────────────────────────────────────────────

def sensibilidade_ingrediente(codigo: int, niveis_nutri: dict, precos: dict,
                              cenario: str = "desossado",
                              variacao_pct: float = 0.40, n: int = 15) -> dict:
    from modules.formulation import CUSTOS_POR_KG, formular_dieta
    custo_base  = CUSTOS_POR_KG.get(codigo, 0.35)
    custos_range = np.linspace(custo_base * (1 - variacao_pct),
                               custo_base * (1 + variacao_pct), n)
    chave = f"mofc_{cenario}"
    prog  = _montar_programa(niveis_nutri)
    mofc_list = []
    for c in custos_range:
        ing = carregar_ingredientes_ativos({codigo: float(c)})
        form2 = {fase: formular_dieta(req, ing) for fase, req in prog.items()}
        try:
            res = calcular_mofc(niveis_nutri, precos, cache_formulacao=form2)
            mofc_list.append(res.get(chave) if res["status"] == "OK" else np.nan)
        except Exception:
            mofc_list.append(np.nan)
    return {"custos_x": custos_range.tolist(), "mofc_y": mofc_list,
            "custo_base": custo_base, "codigo": codigo}


# ── Otimizador grid ──────────────────────────────────────────────────────────

def otimizar_programa(precos: dict, cenario_venda: str = "desossado",
                      me_range: tuple = (2900, 3300), lys_range: tuple = (0.85, 1.35),
                      relacao_lys: dict | None = None, n_grid: int = 12,
                      verbose: bool = False) -> dict:
    rel = relacao_lys or {"starter": 1.000, "grower": 0.913,
                          "finisher1": 0.860, "finisher2": 0.806}
    me_vals  = np.linspace(*me_range,  n_grid).round(0)
    lys_vals = np.linspace(*lys_range, n_grid).round(3)
    chave    = f"mofc_{cenario_venda}"
    melhor   = {"valor": -np.inf, "niveis": None, "resultado": None}

    for me_s in me_vals:
        for lys_s in lys_vals:
            niveis = {}
            offs = {"starter": 0, "grower": 75, "finisher1": 125, "finisher2": 175}
            for fase in ["starter", "grower", "finisher1", "finisher2"]:
                niveis[fase] = {"ame_n":   min(me_s + offs[fase], me_range[1]),
                                "dig_lys": round(lys_s * rel[fase], 4)}
            try:
                res = calcular_mofc(niveis, precos)
                if res["status"] != "OK": continue
                v = res.get(chave, -np.inf)
                if v > melhor["valor"]:
                    melhor.update({"valor": v, "niveis": niveis, "resultado": res})
            except Exception:
                continue

    return {
        "status":             "OK" if melhor["resultado"] else "Sem solução factível",
        "cenario":            cenario_venda,
        "mofc_otima":         round(melhor["valor"], 4) if melhor["resultado"] else None,
        "niveis_otimos":      melhor["niveis"],
        "resultado_completo": melhor["resultado"],
    }


# ── Heatmap MOFC (aproximado) ────────────────────────────────────────────────

def grid_mofc(precos: dict, cenario_venda: str = "desossado",
              me_range: tuple = (2900, 3300), lys_range: tuple = (0.85, 1.35),
              n: int = 20) -> dict:
    me_arr  = np.linspace(*me_range,  n)
    lys_arr = np.linspace(*lys_range, n)
    Z = np.full((n, n), np.nan)

    for i, me in enumerate(me_arr):
        for j, lys in enumerate(lys_arr):
            d   = prever_desempenho(me, lys)
            pv  = d["peso_vivo_kg"]; caa = d["caa"]
            car = d["carcaca_kg"];   pei = d["peito_kg"]
            out = d["outros_car_kg"]

            cost_approx = 0.30 + (me - 3000) * 0.000165 + (lys - 1.05) * 0.28
            custo_alim  = pv * caa * cost_approx

            p_vivo   = precos.get("frango_vivo",     1.00)
            p_car    = precos.get("carcaca",         0.90)
            p_peito  = precos.get("peito_desossado", 1.87)
            p_cortes = precos.get("cortes_misc",     1.10)

            if cenario_venda == "vivo":
                mofc = pv  * p_vivo - custo_alim
            elif cenario_venda == "carcaca":
                mofc = car * p_car  - custo_alim
            else:
                mofc = pei * p_peito + out * p_cortes - custo_alim
            Z[j, i] = mofc

    return {"ME": me_arr, "Lys": lys_arr, "Z": Z, "cenario": cenario_venda}
