"""
Analisador Paramétrico - Parte 4
Análise de Sensibilidade e Curvas de Resposta Econômica

Varia um nutriente de cada vez enquanto mantém os demais fixos,
revelando o impacto marginal e o ponto de máximo retorno.
"""

import numpy as np
from modules.biological import prever_desempenho, superficie_resposta


def curva_resposta_nutriente(
    nutriente: str,
    fase: str,
    precos: dict,
    programa_base: dict,
    n_pontos: int = 30,
    cenario_venda: str = "desossado",
) -> dict:
    """
    Calcula a curva de MOFC em função de um nutriente em uma fase.

    nutriente: 'ame_n' | 'dig_lys'
    fase: 'starter' | 'grower' | 'finisher1' | 'finisher2'
    programa_base: programa nutricional completo (todas as fases)
    """
    from modules.optimizer import calcular_mofc, PROP_CONSUMO

    base = {f: dict(v) for f, v in programa_base.items()}

    if nutriente == "ame_n":
        valores = np.linspace(2800, 3350, n_pontos)
    elif nutriente == "dig_lys":
        valores = np.linspace(0.80, 1.45, n_pontos)
    else:
        raise ValueError(f"Nutriente '{nutriente}' não suportado.")

    mofc_list, desemp_list = [], []
    chave = f"mofc_{cenario_venda}"

    for v in valores:
        niveis = {f: dict(r) for f, r in base.items()}
        niveis[fase][nutriente] = round(float(v), 4)
        try:
            res = calcular_mofc(niveis, precos)
            mofc_list.append(res.get(chave, np.nan) if res["status"] == "OK" else np.nan)
            desemp_list.append(res.get("desempenho", {}) if res["status"] == "OK" else {})
        except Exception:
            mofc_list.append(np.nan)
            desemp_list.append({})

    mofc_arr = np.array(mofc_list, dtype=float)
    idx_max = int(np.nanargmax(mofc_arr)) if not np.all(np.isnan(mofc_arr)) else 0

    return {
        "valores_x": valores.tolist(),
        "mofc_y": mofc_arr.tolist(),
        "otimo_x": float(valores[idx_max]),
        "otimo_y": float(mofc_arr[idx_max]),
        "nutriente": nutriente,
        "fase": fase,
        "cenario": cenario_venda,
        "desempenhos": desemp_list,
    }


def analise_preco_venda(
    variavel_preco: str,
    programa_base: dict,
    precos_base: dict,
    cenario_venda: str = "desossado",
    n_pontos: int = 25,
    delta: float = 0.30,
) -> dict:
    """
    Analisa como a MOFC varia com o preço de venda do produto.

    variavel_preco: 'frango_vivo' | 'carcaca' | 'peito_desossado' | 'cortes_misc'
    delta: variação (±) em torno do preço base
    """
    from modules.optimizer import calcular_mofc

    preco_base_val = precos_base.get(variavel_preco, 1.00)
    precos_range = np.linspace(
        max(preco_base_val - delta, 0.01),
        preco_base_val + delta,
        n_pontos
    )

    mofc_list = []
    for p in precos_range:
        precos_var = {**precos_base, variavel_preco: float(p)}
        try:
            res = calcular_mofc(programa_base, precos_var)
            chave = f"mofc_{cenario_venda}"
            mofc_list.append(res.get(chave, np.nan) if res["status"] == "OK" else np.nan)
        except Exception:
            mofc_list.append(np.nan)

    return {
        "precos_x": precos_range.tolist(),
        "mofc_y": mofc_list,
        "variavel_preco": variavel_preco,
        "preco_base": preco_base_val,
        "cenario": cenario_venda,
    }


def analise_preco_ingrediente(
    ingrediente_nome: str,
    ingrediente_code: int,
    programa_base: dict,
    precos_produto: dict,
    cenario_venda: str = "desossado",
    n_pontos: int = 25,
    variacao_pct: float = 0.40,
) -> dict:
    """
    Analisa o impacto do preço de um ingrediente-chave na MOFC.
    """
    from modules.formulation import CUSTOS_POR_KG
    from modules.optimizer import calcular_mofc

    custo_base = CUSTOS_POR_KG.get(ingrediente_code, 0.35)
    custos_range = np.linspace(
        custo_base * (1 - variacao_pct),
        custo_base * (1 + variacao_pct),
        n_pontos
    )

    mofc_list = []
    chave = f"mofc_{cenario_venda}"

    for custo in custos_range:
        extras = {ingrediente_code: float(custo)}
        from modules.formulation import carregar_ingredientes_ativos
        ing_df = carregar_ingredientes_ativos(extras=extras)
        try:
            from modules.formulation import formular_programa_completo
            from modules.optimizer import _montar_programa, REQUISITOS_FASE_BASE
            prog = _montar_programa(programa_base, REQUISITOS_FASE_BASE)
            form = formular_programa_completo(prog)
            res = calcular_mofc(programa_base, precos_produto, cache_formulacao=form)
            mofc_list.append(res.get(chave, np.nan) if res["status"] == "OK" else np.nan)
        except Exception:
            mofc_list.append(np.nan)

    return {
        "custos_x": custos_range.tolist(),
        "mofc_y": mofc_list,
        "ingrediente": ingrediente_nome,
        "custo_base": custo_base,
        "cenario": cenario_venda,
    }


def resumo_sensibilidade(
    programa_base: dict,
    precos: dict,
    cenario_venda: str = "desossado",
    n_pontos: int = 20,
) -> dict:
    """
    Gera curvas de sensibilidade para ME e Lys em todas as fases.
    Retorna dict pronto para plotagem.
    """
    resultados = {}
    for fase in ["starter", "grower", "finisher1", "finisher2"]:
        for nutriente in ["ame_n", "dig_lys"]:
            chave = f"{fase}_{nutriente}"
            resultados[chave] = curva_resposta_nutriente(
                nutriente=nutriente,
                fase=fase,
                precos=precos,
                programa_base=programa_base,
                n_pontos=n_pontos,
                cenario_venda=cenario_venda,
            )
    return resultados
