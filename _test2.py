from modules.biological import curva_crescimento, peso_por_idade
from modules.optimizer import calcular_epef, break_even_custo_total, custo_producao_total, calcular_mofc

cc = curva_crescimento(3100, 1.10, 49)
print("Growth curve pesos:", cc["peso_kg"][:8])
print("Escala vs padrao:", cc["escala_vs_padrao"])

for d in [35, 42, 45, 49]:
    pv = peso_por_idade(3100, 1.10, d)
    print(f"  idade={d}d: PV={pv}kg")

niveis = {
    "starter":   {"ame_n": 2975, "dig_lys": 1.32},
    "grower":    {"ame_n": 3050, "dig_lys": 1.20},
    "finisher1": {"ame_n": 3100, "dig_lys": 1.10},
    "finisher2": {"ame_n": 3150, "dig_lys": 1.04},
}
precos = {"frango_vivo": 1.20, "carcaca": 2.20, "peito_desossado": 4.50, "cortes_misc": 1.10}
custos_extras = {"pinto": 0.45, "medicacao": 0.05, "energia": 0.04,
                 "mao_obra": 0.07, "depreciacao": 0.10, "outros": 0.04}

r = calcular_mofc(niveis, precos)
print("MOFC status:", r["status"])

for age in [42, 45, 49]:
    epef = calcular_epef(r, age, 3.0)
    print(f"  EPEF@{age}d: {epef['EPEF']} ({epef['classe']}) PV={epef['peso_estimado_kg']}kg GPD={epef['ganho_diario_g']}g")

be_t = break_even_custo_total(r, custos_extras, "desossado", precos)
print("BE total custo:", be_t["break_even_total"], "margem:", be_t["margem_atual_pct"])

cp = custo_producao_total(r, custos_extras)
print("Custo total:", cp["total"], "feed%:", cp["feed_pct"])
print("ALL OK")
