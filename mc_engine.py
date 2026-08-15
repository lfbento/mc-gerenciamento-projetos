#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Simulação de Monte Carlo para Redes WBS
================================================
Executa simulações estocásticas (20.000 iterações) com amostragem triangular
sobre redes de tarefas com estimativas de 3 pontos (otimista, provável, pessimista).
Calcula percentis (P10, P50, P80, P90), probabilidade de cumprimento do prazo contratual,
índice de criticidade por atividade da EAP e buffers de contingência.
"""

import os
from typing import Dict, Any, Tuple
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RNG = np.random.default_rng(42)
N_SIM_DEFAULT = 20_000


def simular_monte_carlo_rede(
    rede_wbs: Dict[str, Any],
    n_sim: int = N_SIM_DEFAULT,
    plot: bool = True,
    pasta_assets: str = "assets"
) -> Dict[str, Any]:
    """
    Executa a simulação de Monte Carlo na malha WBS fornecida.
    """
    tarefas = rede_wbs["tarefas"]
    prazo_alvo = rede_wbs.get("prazo_total_uteis", 72)
    n_t = len(tarefas)
    idx = {t["id"]: i for i, t in enumerate(tarefas)}

    # 1. Amostragem triangular para cada tarefa
    dur = np.empty((n_sim, n_t))
    for i, t in enumerate(tarefas):
        o, m, p = t["otimista"], t["provavel"], t["pessimista"]
        dur[:, i] = RNG.triangular(o, m, p, size=n_sim)

    # 2. Forward pass: Cálculo do término mais cedo (Early Finish)
    fim = np.zeros((n_sim, n_t))
    for i, t in enumerate(tarefas):
        deps = t.get("deps", [])
        if deps:
            prev = fim[:, idx[deps[0]]]
            for d in deps[1:]:
                prev = np.maximum(prev, fim[:, idx[d]])
            fim[:, i] = dur[:, i] + prev
        else:
            fim[:, i] = dur[:, i]

    duracao_total = fim.max(axis=1)

    # 3. Backward pass: Identificação do caminho crítico por simulação
    crit = np.zeros((n_sim, n_t), dtype=bool)
    lf = np.zeros_like(fim)  # Latest Finish
    for i in range(n_t - 1, -1, -1):
        tid = tarefas[i]["id"]
        # Encontra sucessores diretos
        suc = [j for j, t_suc in enumerate(tarefas) if tid in t_suc.get("deps", [])]
        if suc:
            lf[:, i] = np.min(np.stack([lf[:, j] - dur[:, j] for j in suc]), axis=0)
        else:
            lf[:, i] = duracao_total
        crit[:, i] = (lf[:, i] - fim[:, i] < 0.01)

    crit_idx = crit.mean(axis=0) * 100

    # Atribui o índice de criticidade de volta às tarefas
    for i, t in enumerate(tarefas):
        t["indice_criticidade"] = round(float(crit_idx[i]), 1)

    # 4. Estatísticas de Cronograma
    media = float(duracao_total.mean())
    p10 = float(np.percentile(duracao_total, 10))
    p50 = float(np.percentile(duracao_total, 50))
    p80 = float(np.percentile(duracao_total, 80))
    p90 = float(np.percentile(duracao_total, 90))
    p_cumprir_prazo = float(np.mean(duracao_total <= prazo_alvo) * 100)
    p_estouro_critico = float(np.mean(duracao_total > prazo_alvo * 1.10) * 100)
    buffer_cronograma = p90 - p50

    # 5. Simulação de Custo
    orcamento_base = rede_wbs.get("orcamento_total", 395500.0)
    # Decomposição em pacotes de custo com variabilidade
    custos_sim = (
        RNG.triangular(orcamento_base * 0.25, orcamento_base * 0.30, orcamento_base * 0.40, size=n_sim) + # MP / Tubos / Chapas Inox
        RNG.triangular(orcamento_base * 0.28, orcamento_base * 0.35, orcamento_base * 0.48, size=n_sim) + # Fabricação / Solda / Mão de Obra
        RNG.triangular(orcamento_base * 0.12, orcamento_base * 0.15, orcamento_base * 0.22, size=n_sim) + # Engenharia / Métodos / Testes
        RNG.triangular(orcamento_base * 0.05, orcamento_base * 0.08, orcamento_base * 0.12, size=n_sim) + # Pintura / Tratamento Inox
        RNG.triangular(orcamento_base * 0.08, orcamento_base * 0.12, orcamento_base * 0.18, size=n_sim)   # Frete CIF / Logística Camaçari
    )
    custo_media = float(custos_sim.mean())
    custo_p50 = float(np.percentile(custos_sim, 50))
    custo_p80 = float(np.percentile(custos_sim, 80))
    custo_p90 = float(np.percentile(custos_sim, 90))
    contingencia_custo = custo_p80 - custo_p50
    p_estouro_orcamento = float(np.mean(custos_sim > orcamento_base) * 100)

    # 6. Gráficos
    caminho_cron_png = None
    caminho_custo_png = None

    if plot:
        os.makedirs(pasta_assets, exist_ok=True)
        
        # Histograma Cronograma
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(duracao_total, bins=60, color="#2563EB", alpha=0.85, edgecolor="white")
        ax.axvline(prazo_alvo, color="#DC2626", ls="--", lw=2,
                   label=f"Prazo Alvo ({prazo_alvo:.0f} dias úteis)")
        ax.axvline(p50, color="#10B981", ls=":", lw=2, label=f"P50 ({p50:.1f} d)")
        ax.axvline(p90, color="#F59E0B", ls=":", lw=2, label=f"P90 ({p90:.1f} d)")
        ax.set_xlabel("Duração do Projeto (dias úteis)", fontsize=11)
        ax.set_ylabel("Frequência de Ocorrência", fontsize=11)
        ax.set_title(f"Monte Carlo - Cronograma ({n_sim:,} simulações)\n{rede_wbs.get('projeto', 'Projeto')}", fontsize=12, fontweight="bold")
        ax.legend()
        fig.tight_layout()
        caminho_cron_png = os.path.join(pasta_assets, "mc_cronograma_wbs.png")
        fig.savefig(caminho_cron_png, dpi=140)
        plt.close(fig)

        # Histograma Custo
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(custos_sim / 1000.0, bins=60, color="#059669", alpha=0.85, edgecolor="white")
        ax.axvline(orcamento_base / 1000.0, color="#DC2626", ls="--", lw=2,
                   label=f"Orçamento Alvo (R$ {orcamento_base/1000.0:.1f}k)")
        ax.axvline(custo_p50 / 1000.0, color="#2563EB", ls=":", lw=2, label=f"P50 (R$ {custo_p50/1000.0:.1f}k)")
        ax.axvline(custo_p80 / 1000.0, color="#F59E0B", ls=":", lw=2, label=f"P80 (R$ {custo_p80/1000.0:.1f}k)")
        ax.set_xlabel("Custo Total (R$ mil)", fontsize=11)
        ax.set_ylabel("Frequência", fontsize=11)
        ax.set_title(f"Monte Carlo - Análise de Riscos de Custo ({n_sim:,} simulações)", fontsize=12, fontweight="bold")
        ax.legend()
        fig.tight_layout()
        caminho_custo_png = os.path.join(pasta_assets, "mc_custo_wbs.png")
        fig.savefig(caminho_custo_png, dpi=140)
        plt.close(fig)

    return {
        "duracao": {
            "media": media,
            "p10": p10,
            "p50": p50,
            "p80": p80,
            "p90": p90,
            "min": float(duracao_total.min()),
            "max": float(duracao_total.max()),
            "prazo_alvo": prazo_alvo,
            "prob_sucesso_prazo": p_cumprir_prazo,
            "prob_estouro_critico": p_estouro_critico,
            "buffer_sugerido": buffer_cronograma
        },
        "custo": {
            "media": custo_media,
            "p50": custo_p50,
            "p80": custo_p80,
            "p90": custo_p90,
            "orcamento_base": orcamento_base,
            "contingencia_sugerida": contingencia_custo,
            "prob_estouro_orcamento": p_estouro_orcamento
        },
        "graficos": {
            "cronograma": caminho_cron_png,
            "custo": caminho_custo_png
        },
        "tarefas_ordenadas_criticidade": sorted(tarefas, key=lambda x: x["indice_criticidade"], reverse=True)
    }


if __name__ == "__main__":
    from projeto_extractor import extrair_metadados_projeto
    from wbs_scheduler import gerar_rede_wbs

    meta = extrair_metadados_projeto("convertidos")
    rede = gerar_rede_wbs(meta)
    res = simular_monte_carlo_rede(rede)

    print("=" * 70)
    print(" RESULTADOS DA SIMULAÇÃO DE MONTE CARLO (20.000 ITERAÇÕES)")
    print("=" * 70)
    d = res["duracao"]
    print(f" Duração (dias úteis): Média={d['media']:.1f} | P50={d['p50']:.1f} | P90={d['p90']:.1f}")
    print(f" Probabilidade de cumprir prazo ({d['prazo_alvo']} d): {d['prob_sucesso_prazo']:.1f}%")
    print(f" Buffer de contingência sugerido: {d['buffer_sugerido']:.1f} dias úteis")
    print("\n Top 5 Tarefas Críticas:")
    for t in res["tarefas_ordenadas_criticidade"][:5]:
        print(f"   [{t['wbs']}] {t['nome']:<50} Criticidade: {t['indice_criticidade']}%")
