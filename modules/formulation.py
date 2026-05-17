"""
Módulo de Formulação de Mínimo Custo — LP (HiGHS)

Calcula a dieta mais barata que atende aos requisitos nutricionais.
Retorna composição, custo, perfil nutricional e shadow prices das restrições.
"""

import numpy as np
import pandas as pd
from scipy.optimize import linprog
from pathlib import Path

XLSX_PATH = Path(__file__).resolve().parent.parent / "data" / "Formulation Set.xlsx"

# Custos dos ingredientes ($/kg) — fonte: Ingredient Cost.pdf (÷1000 de $/ton)
CUSTOS_POR_KG = {
    10010: 0.334,   # Wheat - Hard Red Spring
    10100: 0.335,   # Wheat - Soft Red Winter
    10200: 0.320,   # Yellow Corn - STD
    10300: 0.300,   # Sorghum
    20000: 0.550,   # Fullfat Soya - Extruded
    22045: 0.350,   # Soybean Meal - 45%
    22046: 0.367,   # Soybean Meal - 46%
    22048: 0.411,   # Soybean Meal - 48%
    22560: 0.900,   # Corn Gluten 60% CP
    23500: 0.180,   # DDGS Corn - HD
    24000: 0.280,   # Wheat Middlings
    24015: 0.235,   # Wheat Bran < 9% CF
    25000: 1.500,   # Fish Meal Standard
    25115: 0.250,   # Offal Meal - Poultry HD
    25150: 0.350,   # Meat and Bone Meal, Beef
    30000: 1.050,   # Soy Crude Oil
    35020: 1.050,   # Dicalcium Phosphate
    36000: 0.100,   # Limestone 38%
    37000: 0.150,   # Sodium Chloride 39%
    40000: 5.000,   # Generic Premixes
    45000: 2.400,   # L-Lysine.HCl 99
    45050: 5.700,   # DL-Methionine
    45100: 6.000,   # L-Threonine
    45250: 45.000,  # L-Valine
    48010: 2.000,   # Choline Chloride 60%
    66080: 5.000,   # Phytase - Ronozyme NP
    67001: 25.000,  # Etoxiquin
}

# Limites de inclusão (min_frac, max_frac) — base 0–1 (= 0–100%)
LIMITES = {
    10010: (0.00, 0.40),
    10100: (0.00, 0.40),
    10200: (0.00, 0.75),
    10300: (0.00, 0.30),
    20000: (0.00, 0.20),
    22045: (0.00, 0.45),
    22046: (0.00, 0.45),
    22048: (0.00, 0.40),
    22560: (0.00, 0.05),
    23500: (0.00, 0.08),
    24000: (0.00, 0.10),
    24015: (0.00, 0.08),
    25000: (0.00, 0.04),
    25115: (0.00, 0.06),
    25150: (0.00, 0.04),
    30000: (0.01, 0.08),
    35020: (0.005, 0.025),
    36000: (0.005, 0.020),
    37000: (0.002, 0.008),
    40000: (0.001, 0.005),
    45000: (0.000, 0.008),
    45050: (0.000, 0.006),
    45100: (0.000, 0.005),
    45250: (0.000, 0.003),
    48010: (0.000, 0.003),
    66080: (0.000, 0.001),
    67001: (0.000, 0.001),
}

# Mapeamento nutriente → keyword na coluna da matrix
# Adicione ou remova conforme a matrix disponível
_NUTRI_KEYWORDS = {
    "ame_n":    "ST AMEn kg",
    "dig_lys":  "Dig Lysine",
    "dig_met":  "Dig Methionine",
    "dig_cys":  "Dig  Cyst(e)ine",
    "dig_thr":  "Dig Threonine",
    "dig_trp":  "Dig Tryptophan",
    "dig_val":  "Dig Valine",
    "ca_total": "Total Calcium",
    "p_npp":    "Non Phytate Ph",
    "sodium":   "Sodium",
    "chloride": "Chloride",
    # Informativos — calculados mas não usados como restrição (a menos que passados em requisitos)
    "cp":        "Crude Protein",
    "cf":        "Crude Fat",
    "p_total":   "Total Phosphorus",
    "potassium": "Potassium",
    "starch":    "Starch",
    "cf_fiber":  "Crude Fibre",
}

_matrix_cache: pd.DataFrame | None = None
_names_cache:  dict | None = None


def _load_matrix() -> pd.DataFrame:
    global _matrix_cache, _names_cache
    if _matrix_cache is not None:
        return _matrix_cache

    raw = pd.read_excel(XLSX_PATH, sheet_name="Nutritional Matrix", header=0)
    nut_names = raw.iloc[0].tolist()
    new_cols = []
    for i, (orig, nut) in enumerate(zip(raw.columns, nut_names)):
        if i < 2:
            new_cols.append(orig)
        else:
            new_cols.append(str(nut).strip() if pd.notna(nut) else str(orig))
    raw.columns = new_cols

    df = raw.iloc[2:].copy()
    df = df.rename(columns={df.columns[0]: "IngrCode", df.columns[1]: "Ingredient"})
    df["IngrCode"] = pd.to_numeric(df["IngrCode"], errors="coerce")
    df = df.dropna(subset=["IngrCode"])
    df["IngrCode"] = df["IngrCode"].astype(int)

    _names_cache = dict(zip(df["IngrCode"], df["Ingredient"].fillna("").astype(str)))

    df = df.set_index("IngrCode")
    df = df.apply(pd.to_numeric, errors="coerce")
    _matrix_cache = df
    return df


def get_ingredient_names() -> dict:
    """Retorna {código: nome} para todos os ingredientes da matrix."""
    _load_matrix()
    return _names_cache or {}


def _col(df: pd.DataFrame, keyword: str) -> str | None:
    for col in df.columns:
        if keyword.lower() in col.lower():
            return col
    return None


def carregar_ingredientes_ativos(extras: dict | None = None) -> pd.DataFrame:
    matrix = _load_matrix()
    custos = {**CUSTOS_POR_KG, **(extras or {})}
    codigos = [c for c in custos if c in matrix.index]
    df = matrix.loc[codigos].copy()
    df["custo_por_kg"] = [custos[c] for c in df.index]
    return df


def formular_dieta(
    requisitos: dict,
    ingredientes_df: pd.DataFrame | None = None,
    limites_extra: dict | None = None,
) -> dict:
    """
    Formulação LP de mínimo custo.

    requisitos: {nutriente: valor_min} ou {nutriente: (min, max)}
    Retorna: status, custo_por_kg, composicao (%), nutrientes_calculados, shadow_prices
    """
    if ingredientes_df is None:
        ingredientes_df = carregar_ingredientes_ativos()

    matrix = _load_matrix()
    lim = {**LIMITES, **(limites_extra or {})}

    ing_idx = [c for c in ingredientes_df.index if c in matrix.index]
    n = len(ing_idx)
    if n == 0:
        return {"status": "Sem ingredientes", "custo_por_kg": None,
                "composicao": {}, "nutrientes_calculados": {}, "shadow_prices": {}}

    custo_arr = ingredientes_df.loc[ing_idx, "custo_por_kg"].values.astype(float)

    # Restrições nutricionais + mapa para shadow prices
    A_ub, b_ub = [], []
    constraint_map = []  # (nutriente, tipo, meta_valor)

    for nutriente, req in requisitos.items():
        keyword = _NUTRI_KEYWORDS.get(nutriente)
        if keyword is None:
            continue
        col = _col(matrix, keyword)
        if col is None:
            continue
        vals = matrix.loc[ing_idx, col].fillna(0).values.astype(float)

        req_min = req[0] if isinstance(req, (list, tuple)) else req
        req_max = req[1] if isinstance(req, (list, tuple)) else None

        if req_min is not None:
            A_ub.append(-vals)
            b_ub.append(-float(req_min))
            constraint_map.append((nutriente, "min", float(req_min)))

        if req_max is not None:
            A_ub.append(vals)
            b_ub.append(float(req_max))
            constraint_map.append((nutriente, "max", float(req_max)))

    A_eq = np.ones((1, n))
    b_eq = np.array([1.0])
    bounds = [lim.get(c, (0.0, 1.0)) for c in ing_idx]

    A_ub_arr = np.array(A_ub) if A_ub else np.empty((0, n))
    b_ub_arr = np.array(b_ub) if b_ub else np.array([])

    res = linprog(
        c=custo_arr,
        A_ub=A_ub_arr, b_ub=b_ub_arr,
        A_eq=A_eq,     b_eq=b_eq,
        bounds=bounds,
        method="highs",
        options={"disp": False},
    )

    if not res.success:
        return {
            "status": f"INFEASIVEL: {res.message}",
            "custo_por_kg": None,
            "composicao": {},
            "nutrientes_calculados": {},
            "shadow_prices": {},
        }

    x = res.x
    composicao = {ing_idx[i]: round(float(x[i]) * 100, 4)
                  for i in range(n) if x[i] > 5e-5}

    # Perfil nutricional calculado (TODOS os nutrientes, inclusive informativos)
    nutrientes = {}
    for nutriente, keyword in _NUTRI_KEYWORDS.items():
        col = _col(matrix, keyword)
        if col:
            vals = matrix.loc[ing_idx, col].fillna(0).values.astype(float)
            nutrientes[nutriente] = round(float(np.dot(x, vals)), 4)

    # Shadow prices — dual variables das restrições (scipy HiGHS)
    # Para restrição min: −nu@x ≤ −nu_min → d(custo)/d(nu_min) = -marginal
    shadow_prices = {}
    ineq_mg = getattr(getattr(res, "ineqlin", None), "marginals", None)
    if ineq_mg is not None and len(ineq_mg) == len(constraint_map):
        for (nut, tipo, meta), mg in zip(constraint_map, ineq_mg):
            if abs(mg) < 1e-8:
                continue  # não vinculante
            shadow = -float(mg) if tipo == "min" else float(mg)
            # shadow: $/kg por unidade de aumento no requisito (positivo = encarece)
            if nut not in shadow_prices or abs(shadow) > abs(shadow_prices[nut]["shadow_kg"]):
                shadow_prices[nut] = {
                    "meta":       meta,
                    "tipo":       tipo,
                    "shadow_kg":  round(shadow, 7),      # $/kg ração por unidade
                    "shadow_ton": round(shadow * 1000, 4),  # $/ton ração por unidade
                    "binding":    True,
                }

    # Custo marginal dos ingredientes fora da dieta (reduced costs)
    reduced_costs = {}
    low_mg = getattr(getattr(res, "lower", None), "marginals", None)
    if low_mg is not None:
        for i, code in enumerate(ing_idx):
            if x[i] < 1e-5 and i < len(low_mg) and abs(low_mg[i]) > 1e-6:
                reduced_costs[code] = round(float(low_mg[i]), 5)

    return {
        "status":                "OK",
        "custo_por_kg":          round(float(res.fun), 5),
        "composicao":            composicao,
        "nutrientes_calculados": nutrientes,
        "shadow_prices":         shadow_prices,
        "reduced_costs":         reduced_costs,
    }


def formular_programa_completo(programa: dict, limites_extra: dict | None = None) -> dict:
    ing = carregar_ingredientes_ativos()
    return {fase: formular_dieta(req, ing, limites_extra) for fase, req in programa.items()}
