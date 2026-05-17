"""
Motor Biológico — Módulo 1
Modelo de Superfície de Resposta (RSM) quadrático — Genesis42d_G

Calibrado com dados experimentais do estudo Genesis MExBP Surface Response.
Entradas: Energia Metabolizável (kcal/kg), Lisina Digestível (%)
Saídas:   Peso Vivo (kg), CAA, Carcaça kg, Peito kg
"""

import numpy as np
from scipy.optimize import minimize

# ---------------------------------------------------------------------------
# Dados de calibração  [ME kcal/kg, Dig_Lys %, PV_kg, CAA, Carcaça_kg, Peito_kg]
# Fonte: Genesis MExBP Surface Response — cenários 45-61d, frango de corte
# ---------------------------------------------------------------------------
CALIBRATION_DATA = np.array([
    # ME      Lys    PV      CAA     Carc    Peito
    [2995,  0.90,  3.650,  1.941,  2.930,  0.895],
    [2995,  1.05,  3.850,  1.870,  3.090,  0.988],
    [2995,  1.20,  3.920,  1.855,  3.145,  1.038],
    [3030,  0.90,  3.850,  1.910,  3.090,  0.960],
    [3030,  1.05,  4.050,  1.850,  3.250,  1.060],
    [3030,  1.20,  4.130,  1.820,  3.315,  1.108],
    [3065,  0.95,  4.283,  1.833,  3.441,  1.333],
    [3065,  1.05,  4.350,  1.810,  3.490,  1.358],
    [3065,  1.20,  4.420,  1.792,  3.551,  1.388],
    [3100,  0.90,  4.100,  1.875,  3.290,  1.040],
    [3100,  1.05,  4.380,  1.800,  3.515,  1.372],
    [3100,  1.20,  4.450,  1.778,  3.572,  1.400],
    [3130,  1.00,  4.420,  1.758,  3.548,  1.382],
    [3130,  1.10,  4.480,  1.738,  3.598,  1.405],
    [3170,  1.10,  4.500,  1.738,  3.617,  1.395],
    [3170,  1.15,  4.523,  1.726,  3.635,  1.406],
    [3170,  1.20,  4.533,  1.717,  3.642,  1.413],
    [3205,  0.90,  4.250,  1.818,  3.414,  1.290],
    [3205,  0.95,  4.327,  1.793,  3.477,  1.320],
    [3205,  1.00,  4.392,  1.771,  3.530,  1.346],
    [3205,  1.05,  4.444,  1.752,  3.572,  1.367],
    [3205,  1.10,  4.498,  1.729,  3.615,  1.391],
    [3205,  1.15,  4.519,  1.717,  3.631,  1.402],
    [3205,  1.20,  4.526,  1.707,  3.637,  1.408],
])

# Pontos ótimos biológicos — Regression Effects Summary
KNOWN_OPTIMA = {
    "peso_vivo": {"ME": 2884, "Lys": 1.271, "value": 3.639, "R2": 0.9349},
    "carcaca":   {"ME": 2921, "Lys": 1.249, "value": 2.647, "R2": 0.9392},
    "peito":     {"ME": 2977, "Lys": 1.227, "value": 1.016, "R2": 0.9328},
    "mofc_vivo": {"ME": 2884, "Lys": 1.184, "value": 1.692, "R2": 0.9985},
    "mofc_deb":  {"ME": 2902, "Lys": 1.184, "value": 2.149, "R2": 0.9970},
}

# ── Curva de crescimento comercial (Ross 308, referência 2022) ────────────────
# Pesos padrão para escalar a previsão RSM às condições de abate reais.
# RSM é calibrado em condições de pesquisa (~49d equiv.); escala para idade real.
_CURVA_DIAS = np.array([0,     7,     14,    21,    28,    35,    42,    49,    56])
_CURVA_PV   = np.array([0.042, 0.182, 0.497, 0.980, 1.654, 2.420, 3.070, 3.630, 4.140])  # kg
_CURVA_FCR  = np.array([0.000, 1.08,  1.25,  1.44,  1.59,  1.69,  1.76,  1.85,  1.94])   # acumulado

_PV_RSM_REF = 3.630   # kg — peso Ross 308 padrão ao qual o RSM é normalizado (49d)


def _design_matrix(ME, Lys):
    ME  = np.asarray(ME,  dtype=float)
    Lys = np.asarray(Lys, dtype=float)
    return np.column_stack([
        np.ones_like(ME),
        ME, Lys,
        ME ** 2, Lys ** 2,
        ME * Lys,
    ])


def _fit_rsm(ME, Lys, Y):
    Phi = _design_matrix(ME, Lys)
    coeffs, _, _, _ = np.linalg.lstsq(Phi, Y, rcond=None)
    return coeffs


def _predict(coeff, ME, Lys):
    phi = np.array([1, ME, Lys, ME**2, Lys**2, ME*Lys])
    return float(np.dot(coeff, phi))


# Ajuste automático ao carregar o módulo
_ME  = CALIBRATION_DATA[:, 0]
_Lys = CALIBRATION_DATA[:, 1]

COEFF_PV  = _fit_rsm(_ME, _Lys, CALIBRATION_DATA[:, 2])
COEFF_CAA = _fit_rsm(_ME, _Lys, CALIBRATION_DATA[:, 3])
COEFF_CAR = _fit_rsm(_ME, _Lys, CALIBRATION_DATA[:, 4])
COEFF_PEI = _fit_rsm(_ME, _Lys, CALIBRATION_DATA[:, 5])


def _r2(coeff, Y_col):
    Y = CALIBRATION_DATA[:, Y_col]
    Y_pred = _design_matrix(_ME, _Lys) @ coeff
    ss_res = np.sum((Y - Y_pred) ** 2)
    ss_tot = np.sum((Y - Y.mean()) ** 2)
    return float(1 - ss_res / ss_tot)


MODEL_STATS = {
    "peso_vivo_kg": {
        "R2":   round(_r2(COEFF_PV,  2), 4),
        "RMSE": round(float(np.sqrt(np.mean((CALIBRATION_DATA[:,2] - _design_matrix(_ME,_Lys)@COEFF_PV)**2))), 4),
        "n":    len(CALIBRATION_DATA),
    },
    "caa": {
        "R2":   round(_r2(COEFF_CAA, 3), 4),
        "RMSE": round(float(np.sqrt(np.mean((CALIBRATION_DATA[:,3] - _design_matrix(_ME,_Lys)@COEFF_CAA)**2))), 4),
        "n":    len(CALIBRATION_DATA),
    },
    "carcaca_kg": {
        "R2":   round(_r2(COEFF_CAR, 4), 4),
        "RMSE": round(float(np.sqrt(np.mean((CALIBRATION_DATA[:,4] - _design_matrix(_ME,_Lys)@COEFF_CAR)**2))), 4),
        "n":    len(CALIBRATION_DATA),
    },
    "peito_kg": {
        "R2":   round(_r2(COEFF_PEI, 5), 4),
        "RMSE": round(float(np.sqrt(np.mean((CALIBRATION_DATA[:,5] - _design_matrix(_ME,_Lys)@COEFF_PEI)**2))), 4),
        "n":    len(CALIBRATION_DATA),
    },
}


def prever_desempenho(ME_kcal: float, dlys_pct: float) -> dict:
    """
    Previsão RSM Genesis42d_G — normalizada ao padrão comercial 49d.
    Retorna pesos em kg, CAA, rendimentos em % e outros cortes em kg.
    """
    pv  = max(_predict(COEFF_PV,  ME_kcal, dlys_pct), 0.5)
    caa = max(_predict(COEFF_CAA, ME_kcal, dlys_pct), 1.0)
    car = max(_predict(COEFF_CAR, ME_kcal, dlys_pct), 0.0)
    pei = max(_predict(COEFF_PEI, ME_kcal, dlys_pct), 0.0)
    return {
        "peso_vivo_kg":     round(pv,  3),
        "caa":              round(caa, 3),
        "carcaca_kg":       round(car, 3),
        "peito_kg":         round(pei, 3),
        "rend_carcaca_pct": round(car / pv * 100, 1) if pv > 0 else 0.0,
        "rend_peito_pct":   round(pei / pv * 100, 1) if pv > 0 else 0.0,
        "outros_car_kg":    round(max(car - pei, 0), 3),
    }


def curva_crescimento(ME_kcal: float, dlys_pct: float,
                      idade_max: int = 49) -> dict:
    """
    Curva de crescimento diária escalada ao RSM Genesis42d_G.

    Usa curva Ross 308 como esqueleto e escala pelo ratio RSM/padrão.
    Adequada para exibição diária/semanal do crescimento estimado da frota.

    Retorna: dias, peso_kg, ganho_diario_g, consumo_acum_kg, caa_acumulado,
             escala_vs_padrao.
    """
    pv_rsm  = max(_predict(COEFF_PV,  ME_kcal, dlys_pct), 0.5)
    caa_rsm = max(_predict(COEFF_CAA, ME_kcal, dlys_pct), 1.0)
    escala  = pv_rsm / _PV_RSM_REF

    dias = list(range(0, min(idade_max + 1, 57)))

    # Pesos escalados
    pesos = [float(np.interp(d, _CURVA_DIAS, _CURVA_PV) * escala) for d in dias]

    # FCR acumulado: escala o CAA mantendo a curva de progressão
    fcr_std = [float(np.interp(d, _CURVA_DIAS, _CURVA_FCR)) for d in dias]
    fcr_ratio = caa_rsm / _CURVA_FCR[-2] if _CURVA_FCR[-2] > 0 else 1.0
    fcr_ac = [round(f * fcr_ratio, 3) for f in fcr_std]
    fcr_ac[0] = 0.0

    # Ganho diário e consumo acumulado
    ganho_g = [0.0] + [round((pesos[i] - pesos[i-1]) * 1000, 1) for i in range(1, len(dias))]
    cons_d  = [0.0] + [round(ganho_g[i] / 1000 * caa_rsm, 4) for i in range(1, len(dias))]
    cons_ac = [0.0]
    for c in cons_d[1:]:
        cons_ac.append(round(cons_ac[-1] + c, 3))

    return {
        "dias":             dias,
        "peso_kg":          [round(p, 3) for p in pesos],
        "ganho_diario_g":   ganho_g,
        "consumo_acum_kg":  cons_ac,
        "caa_acumulado":    fcr_ac,
        "escala_vs_padrao": round(escala, 3),
    }


def peso_por_idade(ME_kcal: float, dlys_pct: float, idade_dias: int) -> float:
    """Peso vivo estimado na idade de abate (kg), escalado ao RSM."""
    pv_rsm = max(_predict(COEFF_PV, ME_kcal, dlys_pct), 0.5)
    escala = pv_rsm / _PV_RSM_REF
    pv_std = float(np.interp(idade_dias, _CURVA_DIAS, _CURVA_PV))
    return round(pv_std * escala, 3)


def superficie_resposta(variavel: str,
                        me_range: tuple = (2900, 3300),
                        lys_range: tuple = (0.85, 1.35),
                        n: int = 30) -> dict:
    _mapa = {
        "peso_vivo_kg": COEFF_PV,
        "caa":          COEFF_CAA,
        "carcaca_kg":   COEFF_CAR,
        "peito_kg":     COEFF_PEI,
    }
    coeff = _mapa[variavel]
    me_arr  = np.linspace(*me_range,  n)
    lys_arr = np.linspace(*lys_range, n)
    ME_grid, Lys_grid = np.meshgrid(me_arr, lys_arr)
    Phi = _design_matrix(ME_grid.ravel(), Lys_grid.ravel())
    Z_grid = (Phi @ coeff).reshape(ME_grid.shape)
    return {"ME": ME_grid, "Lys": Lys_grid, "Z": Z_grid}


def otimo_biologico(variavel: str = "peso_vivo_kg",
                    minimizar: bool = False,
                    me_bounds: tuple = (2850, 3300),
                    lys_bounds: tuple = (0.85, 1.35)) -> dict:
    _mapa = {"peso_vivo_kg": COEFF_PV, "caa": COEFF_CAA,
             "carcaca_kg": COEFF_CAR, "peito_kg": COEFF_PEI}
    coeff = _mapa[variavel]
    sinal = 1 if minimizar else -1
    res = minimize(
        lambda x: sinal * _predict(coeff, x[0], x[1]),
        x0=[3100, 1.10],
        bounds=[me_bounds, lys_bounds],
        method="L-BFGS-B",
    )
    me_opt, lys_opt = res.x
    return {
        "ME_opt":   round(float(me_opt),  0),
        "Lys_opt":  round(float(lys_opt), 3),
        "valor":    round(_predict(coeff, me_opt, lys_opt), 3),
        "R2":       MODEL_STATS[variavel]["R2"],
    }
