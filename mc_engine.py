#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Simulação de Monte Carlo para Redes WBS
================================================
Executa simulações estocásticas (20.000 iterações) com amostragem triangular
sobre redes de tarefas com estimativas de 3 pontos (otimista, provável, pessimista).
Aplica ordenação topológica formal (Algoritmo de Kahn) e cálculo exato de caminho crítico
(Forward/Backward Pass com folga zero) para cada simulação.
Calcula percentis (P10, P50, P80, P90), probabilidade real de cumprimento do prazo contratual,
índice de criticidade por atividade e buffers de contingência.
"""

import os
from typing import Dict, Any, List
from collections import deque
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RNG = np.random.default_rng(42)
N_SIM_DEFAULT = 20_000


def ordenar_topologicamente(tarefas: List[Dict[str, Any]]) -> List[int]:
    """
    Ordena as tarefas topologicamente usando o algoritmo de Kahn.
    Retorna a lista de índices das tarefas na ordem correta de execução.
    """
    n = len(tarefas)
    idx_map = {t["id"]: i for i, t in enumerate(tarefas)}
    
    in_degree = [0] * n
    adj = [[] for _ in range(n)]
    
    for i, t in enumerate(tarefas):
        for dep in t.get("deps", []):
            if dep in idx_map:
                u = idx_map[dep]
                adj[u].append(i)
                in_degree[i] += 1

    queue = deque([i for i in range(n) if in_degree[i] == 0])
    topo_order = []
    
    while queue:
        u = queue.popleft()
        topo_order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
                
    if len(topo_order) != n:
        # Se houver ciclo ou desconexão, mantém a ordem original
        return list(range(n))
        
    return topo_order


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
    prazo_alvo = float(rede_wbs.get("prazo_total_uteis", 71))
    n_t = len(tarefas)
    idx = {t["id"]: i for i, t in enumerate(tarefas)}

    # 1. Ordenação topológica da malha
    topo_order = ordenar_topologicamente(tarefas)
    rev_topo_order = list(reversed(topo_order))

    # Predecessores e Sucessores mapeados
    preds = {i: [idx[d] for d in tarefas[i].get("deps", []) if d in idx] for i in range(n_t)}
    succs = {i: [] for i in range(n_t)}
    for i in range(n_t):
        for p in preds[i]:
            succs[p].append(i)

    # 2. Amostragem triangular para cada tarefa (20.000 iterações)
    dur = np.empty((n_sim, n_t))
    for i, t in enumerate(tarefas):
        o, m, p = t["otimista"], t["provavel"], t["pessimista"]
        dur[:, i] = RNG.triangular(o, m, p, size=n_sim)

    # 3. Forward pass (Early Start / Early Finish) na ordem topológica
    es = np.zeros((n_sim, n_t))
    ef = np.zeros((n_sim, n_t))

    for u in topo_order:
        if preds[u]:
            max_prev = ef[:, preds[u][0]]
            for p in preds[u][1:]:
                max_prev = np.maximum(max_prev, ef[:, p])
            es[:, u] = max_prev
        else:
            es[:, u] = 0.0
        ef[:, u] = es[:, u] + dur[:, u]

    duracao_total = ef.max(axis=1)

    # 4. Backward pass (Latest Finish / Latest Start) na ordem reversa
    lf = np.zeros((n_sim, n_t))
    ls = np.zeros((n_sim, n_t))
    crit = np.zeros((n_sim, n_t), dtype=bool)

    for u in rev_topo_order:
        if succs[u]:
            min_succ = ls[:, succs[u][0]]
            for s in succs[u][1:]:
                min_succ = np.minimum(min_succ, ls[:, s])
            lf[:, u] = min_succ
        else:
            lf[:, u] = duracao_total
        ls[:, u] = lf[:, u] - dur[:, u]
        
        # Folga total (Float) = LF - EF (ou LS - ES)
        folga = lf[:, u] - ef[:, u]
        crit[:, u] = (folga < 0.05)

    # Índice de Criticidade: % de iterações em que a atividade esteve no caminho crítico
    crit_idx = crit.mean(axis=0) * 100.0

    # Atribui o índice de criticidade de volta às tarefas
    for i, t in enumerate(tarefas):
        t["indice_criticidade"] = round(float(crit_idx[i]), 1)

    # 5. Estatísticas de Cronograma
    media = float(duracao_total.mean())
    p10 = float(np.percentile(duracao_total, 10))
    p50 = float(np.percentile(duracao_total, 50))
    p80 = float(np.percentile(duracao_total, 80))
    p90 = float(np.percentile(duracao_total, 90))
    p_cumprir_prazo = float(np.mean(duracao_total <= prazo_alvo) * 100.0)
    p_estouro_critico = float(np.mean(duracao_total > prazo_alvo * 1.10) * 100.0)
    buffer_cronograma = p90 - p50

    # 6. Simulação de Custo
    orcamento_base = float(rede_wbs.get("orcamento_total", 395500.0))
    custos_sim = (
        RNG.triangular(orcamento_base * 0.28, orcamento_base * 0.35, orcamento_base * 0.45, size=n_sim) + # MP Inox / Tubos / Chapas
        RNG.triangular(orcamento_base * 0.25, orcamento_base * 0.32, orcamento_base * 0.42, size=n_sim) + # Fabricação / Soldagem
        RNG.triangular(orcamento_base * 0.12, orcamento_base * 0.16, orcamento_base * 0.22, size=n_sim) + # Engenharia / Cálculos / PIT / ENDs
        RNG.triangular(orcamento_base * 0.05, orcamento_base * 0.07, orcamento_base * 0.12, size=n_sim) + # Decapagem / Passivação / Pintura
        RNG.triangular(orcamento_base * 0.07, orcamento_base * 0.10, orcamento_base * 0.16, size=n_sim)   # Logística / Transporte CIF Camaçari
    )
    custo_media = float(custos_sim.mean())
    custo_p50 = float(np.percentile(custos_sim, 50))
    custo_p80 = float(np.percentile(custos_sim, 80))
    custo_p90 = float(np.percentile(custos_sim, 90))
    contingencia_custo = custo_p80 - custo_p50
    p_estouro_orcamento = float(np.mean(custos_sim > orcamento_base) * 100.0)

    # 7. Gráficos
    caminho_cron_png = None
    caminho_custo_png = None

    if plot:
        os.makedirs(pasta_assets, exist_ok=True)
        
        # Histograma Cronograma
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(duracao_total, bins=60, color="#2563EB", alpha=0.85, edgecolor="white")
        ax.axvline(prazo_alvo, color="#DC2626", ls="--", lw=2.5,
                   label=f"Prazo Contratual Alvo ({prazo_alvo:.1f} d) - P(cumprir) = {p_cumprir_prazo:.1f}%")
        ax.axvline(p50, color="#10B981", ls=":", lw=2, label=f"P50 ({p50:.1f} d)")
        ax.axvline(p90, color="#F59E0B", ls=":", lw=2, label=f"P90 ({p90:.1f} d) -> Buffer = {buffer_cronograma:.1f} d")
        ax.set_xlabel("Duração Total do Projeto (dias úteis)", fontsize=11)
        ax.set_ylabel("Frequência de Ocorrência", fontsize=11)
        ax.set_title(f"Monte Carlo - Análise de Cronograma & Caminho Crítico ({n_sim:,} simulações)\n{rede_wbs.get('projeto', 'Projeto')}", fontsize=12, fontweight="bold")
        ax.legend(loc="upper right")
        fig.tight_layout()
        caminho_cron_png = os.path.join(pasta_assets, "mc_cronograma_wbs.png")
        fig.savefig(caminho_cron_png, dpi=140)
        plt.close(fig)

        # Histograma Custo
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(custos_sim / 1000.0, bins=60, color="#059669", alpha=0.85, edgecolor="white")
        ax.axvline(orcamento_base / 1000.0, color="#DC2626", ls="--", lw=2.5,
                   label=f"Orçamento Base (R$ {orcamento_base/1000.0:.1f}k)")
        ax.axvline(custo_p50 / 1000.0, color="#2563EB", ls=":", lw=2, label=f"P50 (R$ {custo_p50/1000.0:.1f}k)")
        ax.axvline(custo_p80 / 1000.0, color="#F59E0B", ls=":", lw=2, label=f"P80 (R$ {custo_p80/1000.0:.1f}k) -> Contingência = R$ {contingencia_custo/1000.0:.1f}k")
        ax.set_xlabel("Custo Total (R$ mil)", fontsize=11)
        ax.set_ylabel("Frequência", fontsize=11)
        ax.set_title(f"Monte Carlo - Análise de Riscos Orçamentários ({n_sim:,} simulações)", fontsize=12, fontweight="bold")
        ax.legend(loc="upper right")
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
