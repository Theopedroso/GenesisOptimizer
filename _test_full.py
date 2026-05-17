"""Full integration test — run with: python _test_full.py"""
import traceback, sys

niveis = {
    "starter":   {"ame_n": 2975, "dig_lys": 1.32},
    "grower":    {"ame_n": 3050, "dig_lys": 1.20},
    "finisher1": {"ame_n": 3100, "dig_lys": 1.10},
    "finisher2": {"ame_n": 3150, "dig_lys": 1.04},
}
precos = {"frango_vivo": 1.20, "carcaca": 2.20, "peito_desossado": 4.50, "cortes_misc": 2.00}
custos_extras = {"pinto": 0.45, "medicacao": 0.05, "energia": 0.04, "mao_obra": 0.07, "depreciacao": 0.10, "outros": 0.04}

errors = []

def chk(label, fn, *a, **kw):
    try:
        result = fn(*a, **kw)
        print(f"  OK  {label}")
        return result
    except Exception:
        tb = traceback.format_exc()
        print(f"  ERR {label}\n{tb}")
        errors.append(label)
        return None

from modules.optimizer import (
    calcular_mofc, escalas_frota, calcular_epef, custo_producao_total,
    break_even_preco, sensibilidade_ingrediente, grid_mofc, otimizar_programa,
    STANDARDS, IDEAL_PROTEIN, PROP_CONSUMO, calcular_eb
)
from modules.biological import prever_desempenho, superficie_resposta, MODEL_STATS, otimo_biologico
from modules.formulation import get_ingredient_names, carregar_ingredientes_ativos, CUSTOS_POR_KG
from utils.report import gerar_relatorio_excel

print("\n=== BIOLOGICAL ===")
bio = chk("prever_desempenho", prever_desempenho, 3100, 1.10)
chk("superficie_resposta", superficie_resposta, "peso_vivo_kg")
chk("otimo_biologico", otimo_biologico, "peso_vivo_kg")
print("  MODEL_STATS:", MODEL_STATS)

print("\n=== FORMULATION ===")
nomes = chk("get_ingredient_names", get_ingredient_names)
ing   = chk("carregar_ingredientes_ativos", carregar_ingredientes_ativos)
print(f"  Ingredientes: {len(ing) if ing is not None else 'NONE'} itens")

print("\n=== OPTIMIZER ===")
r = chk("calcular_mofc", calcular_mofc, niveis, precos)
if r:
    print(f"  status={r['status']}, mofc_vivo={r['mofc_vivo']}, mofc_desossado={r['mofc_desossado']}")
    print(f"  desempenho keys: {list(r['desempenho'].keys())}")
    print(f"  eb_fases: {r['eb_fases']}")
    print(f"  ratios_aa keys: {list(r['ratios_aa'].keys())}")
    for fase in r["formulacao"]:
        f = r["formulacao"][fase]
        sp = f.get("shadow_prices", {})
        nuts = f.get("nutrientes_calculados", {})
        eb = calcular_eb(nuts)
        print(f"  {fase}: custo={f['custo_por_kg']}, shadow_n={len(sp)}, EB={eb}, potassium={nuts.get('potassium')}")

    epef = chk("calcular_epef", calcular_epef, r, 45, 3.0)
    cp   = chk("custo_producao_total", custo_producao_total, r, custos_extras)
    fr   = chk("escalas_frota", escalas_frota, r, 100000, 3.0)
    be   = chk("break_even_preco", break_even_preco, niveis, precos, "desossado")

    if epef: print(f"  EPEF={epef['EPEF']}, classe={epef['classe']}")
    if cp:   print(f"  custo_total={cp['total']}, feed_pct={cp['feed_pct']}%")
    if fr:   print(f"  n_vendidas={fr['n_aves_vendidas']}, mofc_desossado={fr['mofc_desossado']}")
    if be:   print(f"  break_even={be.get('break_even')}, margem={be.get('margem_atual_pct')}%")

print("\n=== HEATMAP ===")
hm = chk("grid_mofc", grid_mofc, precos, "desossado", (2900,3200), (0.90,1.30), 8)
if hm: print(f"  Z shape={hm['Z'].shape}, nan_count={sum(1 for v in hm['Z'].ravel() if v != v)}")

print("\n=== REPORT ===")
if r:
    xlsx = chk("gerar_relatorio_excel", gerar_relatorio_excel, r, niveis, precos)
    print(f"  xlsx bytes={len(xlsx) if xlsx else 'NONE'}")

print(f"\n{'='*40}")
if errors:
    print(f"ERRORS ({len(errors)}): {errors}")
    sys.exit(1)
else:
    print("ALL TESTS PASSED")
