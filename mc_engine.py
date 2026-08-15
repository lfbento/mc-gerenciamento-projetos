#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Simulação de Monte Carlo para Redes WBS e Análise Comparativa de Riscos
==============================================================================
Executa simulações estocásticas (20.000 iterações) com amostragem triangular
sobre redes de tarefas com estimativas de 3 pontos (otimista, provável, pessimista).
Aplica ordenação topológica formal (Algoritmo de Kahn) e cálculo exato de caminho crítico.
Gera simulação comparativa:
  - Cenário 1: Inercial / Sem Mitigação (Risco de Atraso)
  - Cenário 2: Otimizado com Plano de Ação (Fast-Tracking, Crashing de Solda e Buffer de Proteção)
"""

import os
import copy
from typing import Dict, Any, List, Tuple
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
        return list(range(n))
        
    return topo_order


def _executar_mc_core(tarefas: List[Dict[str, Any]], prazo_alvo: float, n_sim: int) -> Tuple[np.ndarray, np.ndarray]:
    """Executa o forward pass e backward pass vetorizado em n_sim iterações."""
    n_t = len(tarefas)
    idx = {t["id"]: i for i, t in enumerate(tarefas)}
    topo_order = ordenar_topologicamente(tarefas)
    rev_topo_order = list(reversed(topo_order))

    preds = {i: [idx[d] for d in tarefas[i].get("deps", []) if d in idx] for i in range(n_t)}
    succs = {i: [] for i in range(n_t)}
    for i in range(n_t):
        for p in preds[i]:
            succs[p].append(i)

    dur = np.empty((n_sim, n_t))
    for i, t in enumerate(tarefas):
        o, m, p = t["otimista"], t["provavel"], t["pessimista"]
        dur[:, i] = RNG.triangular(o, m, p, size=n_sim)

    # Forward pass (Early Start / Early Finish)
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

    # Backward pass (Latest Finish / Latest Start)
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
        folga = lf[:, u] - ef[:, u]
        crit[:, u] = (folga < 0.05)

    crit_idx = crit.mean(axis=0) * 100.0
    for i, t in enumerate(tarefas):
        t["indice_criticidade"] = round(float(crit_idx[i]), 1)

    return duracao_total, crit_idx


def gerar_rede_mitigada(rede_original: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gera a versão otimizada da rede aplicando o Plano de Ação:
      1. Fast-tracking em Suprimentos (início de cotações em 2.1 após detalhamento inicial).
      2. Crashing na Soldagem e Montagem com reforço de equipe.
      3. Dimensionamento de meta interna de fábrica em 55 dias úteis com buffer de segurança.
    """
    rede = copy.deepcopy(rede_original)
    tarefas = rede["tarefas"]
    
    for t in tarefas:
        tid = t["id"]
        # Ação 1: Fast-Tracking em Suprimentos (antecipação de cotação e encomenda de chapas)
        if tid == "3.1":
            t["deps"] = ["2.1"]  # Inicia logo após o projeto 2D/3D inicial
            t["provavel"] = 2.5
            t["otimista"] = 2.0
            t["pessimista"] = 4.0
        elif tid == "3.2":
            # Usina com entrega priorizada
            t["provavel"] = 10.0
            t["otimista"] = 8.0
            t["pessimista"] = 14.0
        # Ação 2: Crashing de Soldagem (dupla de soldadores qualificados ASME IX)
        elif tid == "4.3":
            t["provavel"] = 4.5
            t["otimista"] = 3.5
            t["pessimista"] = 6.5
        elif tid == "4.4":
            t["provavel"] = 3.5
            t["otimista"] = 2.8
            t["pessimista"] = 5.0
            
    return rede


def simular_monte_carlo_rede(
    rede_wbs: Dict[str, Any],
    n_sim: int = N_SIM_DEFAULT,
    plot: bool = True,
    pasta_assets: str = "assets"
) -> Dict[str, Any]:
    """
    Executa a simulação de Monte Carlo completa com comparação entre
    Cenário Inercial (Sem Mitigação) e Cenário Otimizado (Com Plano de Ação).
    """
    prazo_alvo = float(rede_wbs.get("prazo_total_uteis", 71))
    orcamento_base = float(rede_wbs.get("orcamento_total", 395500.0))

    # 1. Simulação do Cenário Inercial (Base)
    dur_inercial, crit_inercial = _executar_mc_core(rede_wbs["tarefas"], prazo_alvo, n_sim)
    
    # 2. Simulação do Cenário Otimizado com Plano de Ação
    rede_mitigada = gerar_rede_mitigada(rede_wbs)
    dur_mitigado, crit_mitigado = _executar_mc_core(rede_mitigada["tarefas"], prazo_alvo, n_sim)

    # Estatísticas Cenário Inercial
    res_inercial = {
        "media": float(dur_inercial.mean()),
        "p10": float(np.percentile(dur_inercial, 10)),
        "p50": float(np.percentile(dur_inercial, 50)),
        "p80": float(np.percentile(dur_inercial, 80)),
        "p90": float(np.percentile(dur_inercial, 90)),
        "prazo_alvo": prazo_alvo,
        "prob_sucesso_prazo": float(np.mean(dur_inercial <= prazo_alvo) * 100.0),
        "buffer_necessario": float(np.percentile(dur_inercial, 90) - prazo_alvo),
        "buffer_sugerido": float(np.percentile(dur_inercial, 90) - np.percentile(dur_inercial, 50))
    }

    # Estatísticas Cenário Mitigado
    res_mitigado = {
        "media": float(dur_mitigado.mean()),
        "p10": float(np.percentile(dur_mitigado, 10)),
        "p50": float(np.percentile(dur_mitigado, 50)),
        "p80": float(np.percentile(dur_mitigado, 80)),
        "p90": float(np.percentile(dur_mitigado, 90)),
        "prazo_alvo": prazo_alvo,
        "prob_sucesso_prazo": float(np.mean(dur_mitigado <= prazo_alvo) * 100.0),
        "buffer_disponivel": float(prazo_alvo - np.percentile(dur_mitigado, 90)),
        "buffer_sugerido": float(np.percentile(dur_mitigado, 90) - np.percentile(dur_mitigado, 50))
    }

    # 3. Simulação de Custo
    custos_sim = (
        RNG.triangular(orcamento_base * 0.28, orcamento_base * 0.35, orcamento_base * 0.45, size=n_sim) +
        RNG.triangular(orcamento_base * 0.25, orcamento_base * 0.32, orcamento_base * 0.42, size=n_sim) +
        RNG.triangular(orcamento_base * 0.12, orcamento_base * 0.16, orcamento_base * 0.22, size=n_sim) +
        RNG.triangular(orcamento_base * 0.05, orcamento_base * 0.07, orcamento_base * 0.12, size=n_sim) +
        RNG.triangular(orcamento_base * 0.07, orcamento_base * 0.10, orcamento_base * 0.16, size=n_sim)
    )
    custo_media = float(custos_sim.mean())
    custo_p50 = float(np.percentile(custos_sim, 50))
    custo_p80 = float(np.percentile(custos_sim, 80))
    custo_p90 = float(np.percentile(custos_sim, 90))
    contingencia_custo = custo_p80 - custo_p50
    p_estouro_orcamento = float(np.mean(custos_sim > orcamento_base) * 100.0)

    # 4. Gráficos Comparativos Executivos
    caminho_cron_png = None
    caminho_custo_png = None
    caminho_comp_png = None

    if plot:
        os.makedirs(pasta_assets, exist_ok=True)
        
        # Gráfico Comparativo de Cenários (Inercial vs Mitigado)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(dur_inercial, bins=50, color="#DC2626", alpha=0.60, edgecolor="white", label=f"Cenário Inercial (P50 = {res_inercial['p50']:.1f}d | Sucesso: {res_inercial['prob_sucesso_prazo']:.1f}%)")
        ax.hist(dur_mitigado, bins=50, color="#10B981", alpha=0.75, edgecolor="white", label=f"Cenário Mitigado (P50 = {res_mitigado['p50']:.1f}d | Sucesso: {res_mitigado['prob_sucesso_prazo']:.1f}%)")
        ax.axvline(prazo_alvo, color="#1E293B", ls="--", lw=2.5, label=f"Prazo Contratual Alvo ({prazo_alvo:.0f} dias úteis)")
        ax.set_xlabel("Duração Total do Projeto (dias úteis)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Frequência de Ocorrência", fontsize=11, fontweight="bold")
        ax.set_title(f"Monte Carlo: Comparativo de Risco - Antes vs. Depois do Plano de Ação\n{rede_wbs.get('projeto', 'Projeto')}", fontsize=12, fontweight="bold")
        ax.legend(loc="upper right", frameon=True)
        fig.tight_layout()
        caminho_comp_png = os.path.join(pasta_assets, "mc_comparativo_cenarios.png")
        fig.savefig(caminho_comp_png, dpi=140)
        plt.close(fig)

        # Histograma Cronograma Padrão
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(dur_inercial, bins=60, color="#2563EB", alpha=0.85, edgecolor="white")
        ax.axvline(prazo_alvo, color="#DC2626", ls="--", lw=2.5, label=f"Prazo Alvo ({prazo_alvo:.1f} d)")
        ax.axvline(res_inercial["p50"], color="#10B981", ls=":", lw=2, label=f"P50 ({res_inercial['p50']:.1f} d)")
        ax.axvline(res_inercial["p90"], color="#F59E0B", ls=":", lw=2, label=f"P90 ({res_inercial['p90']:.1f} d)")
        ax.set_xlabel("Duração Total do Projeto (dias úteis)", fontsize=11)
        ax.set_ylabel("Frequência", fontsize=11)
        ax.set_title(f"Monte Carlo - Análise de Cronograma ({n_sim:,} simulações)", fontsize=12, fontweight="bold")
        ax.legend(loc="upper right")
        fig.tight_layout()
        caminho_cron_png = os.path.join(pasta_assets, "mc_cronograma_wbs.png")
        fig.savefig(caminho_cron_png, dpi=140)
        plt.close(fig)

        # Histograma Custos
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(custos_sim / 1000.0, bins=60, color="#059669", alpha=0.85, edgecolor="white")
        ax.axvline(orcamento_base / 1000.0, color="#DC2626", ls="--", lw=2.5, label=f"Orçamento Base (R$ {orcamento_base/1000.0:.1f}k)")
        ax.axvline(custo_p50 / 1000.0, color="#2563EB", ls=":", lw=2, label=f"P50 (R$ {custo_p50/1000.0:.1f}k)")
        ax.axvline(custo_p80 / 1000.0, color="#F59E0B", ls=":", lw=2, label=f"P80 (R$ {custo_p80/1000.0:.1f}k) -> Cont. R$ {contingencia_custo/1000.0:.1f}k")
        ax.set_xlabel("Custo Total (R$ mil)", fontsize=11)
        ax.set_ylabel("Frequência", fontsize=11)
        ax.set_title(f"Monte Carlo - Análise de Riscos de Custos ({n_sim:,} simulações)", fontsize=12, fontweight="bold")
        ax.legend(loc="upper right")
        fig.tight_layout()
        caminho_custo_png = os.path.join(pasta_assets, "mc_custo_wbs.png")
        fig.savefig(caminho_custo_png, dpi=140)
        plt.close(fig)

    return {
        "duracao": res_inercial,
        "cenario_mitigado": res_mitigado,
        "rede_mitigada": rede_mitigada,
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
            "custo": caminho_custo_png,
            "comparativo": caminho_comp_png
        },
        "tarefas_ordenadas_criticidade": sorted(rede_wbs["tarefas"], key=lambda x: x["indice_criticidade"], reverse=True)
    }
