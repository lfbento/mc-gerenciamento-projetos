#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monte Carlo aplicado a Gerenciamento de Projetos
================================================
Exemplo realista: fabricação de 2 trocadores de calor casco-e-tubo
(caldeiraria, padrão ASME) para cliente Petrobras.

Análises:
  1) CRONOGRAMA -> PERT/CPM + MC com distribuição triangular:
                   distribuicao da duracao, P(term <= prazo), indice de criticidade
  2) CUSTO      -> itens de custo com incerteza -> custo total, contingencia (P80-P50)

Metodologia PMBOK: estimativas de 3 pontos -> triangular -> N iteracoes -> percentis.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RNG = np.random.default_rng(42)
N_SIM = 20_000
PRAZO_ALVO = 45          # dias contratuais (multa acima disso!)
ORCAMENTO = 520          # R$ mil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ======================================================================
# 1) CRONOGRAMA
# ======================================================================
# (id, descricao, dependencias, (otimista, provavel, pessimista) em dias)
TAREFAS = [
    ("A", "Detalhamento / desenhos de fabricacao",      [],              (3, 5, 10)),
    ("B", "Compra de materiais (casco, espelhos, tubos)", ["A"],         (5, 10, 25)),
    ("C", "Corte e chanfro das chapas",                 ["B"],           (2, 4, 8)),
    ("D", "Calandragem do casco",                       ["C"],           (1, 2, 4)),
    ("E", "Montagem do feixe tubular (expansao)",       ["B"],           (3, 6, 12)),
    ("F", "Soldagem das juntas do casco (ASME IX)",     ["D"],           (2, 4, 9)),
    ("G", "Montagem final + cabecotes",                 ["E", "F"],      (2, 4, 7)),
    ("H", "Teste hidrostatico + inspecao (ASME VIII)",  ["G"],           (1, 2, 5)),
    ("I", "Pintura e entrega",                          ["H"],           (1, 2, 4)),
]

def simular_cronograma(plot=True):
    n_t = len(TAREFAS)
    idx = {t[0]: i for i, t in enumerate(TAREFAS)}
    dur = np.empty((N_SIM, n_t))
    for i, (_, _, _, (o, m, p)) in enumerate(TAREFAS):
        dur[:, i] = RNG.triangular(o, m, p, size=N_SIM)

    # forward pass: EF = ES + duracao (ES = max(EF das dependencias))
    fim = np.zeros((N_SIM, n_t))
    for i, (tid, _, deps, _) in enumerate(TAREFAS):
        if deps:
            prev = fim[:, idx[deps[0]]]
            for d in deps[1:]:
                prev = np.maximum(prev, fim[:, idx[d]])
            fim[:, i] = dur[:, i] + prev
        else:
            fim[:, i] = dur[:, i]
    duracao_total = fim.max(axis=1)

    # backward pass: folga -> caminho critico em cada simulacao
    crit = np.zeros((N_SIM, n_t), dtype=bool)
    lf = np.zeros_like(fim)  # latest finish
    for i in range(n_t - 1, -1, -1):
        tid = TAREFAS[i][0]
        suc = [j for j, (_, _, djs, _) in enumerate(TAREFAS) if tid in djs]
        if suc:
            lf[:, i] = np.min(np.stack([lf[:, j] - dur[:, j] for j in suc]), axis=0)
        else:
            lf[:, i] = duracao_total
        crit[:, i] = (lf[:, i] - fim[:, i] < 0.01)
    crit_idx = crit.mean(axis=0) * 100

    # grafico (opcional)
    png = None
    if plot:
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.hist(duracao_total, bins=60, color="#4C8BF5", alpha=0.85, edgecolor="white")
        ax.axvline(PRAZO_ALVO, color="#E63946", ls="--", lw=2,
                   label=f"Prazo contratual ({PRAZO_ALVO} dias)")
        for q in (50, 90):
            ax.axvline(np.percentile(duracao_total, q), color="#2A9D8F", ls=":", lw=1.5)
        ax.set_xlabel("Duracao do projeto (dias)")
        ax.set_ylabel("Frequencia")
        ax.set_title(f"Monte Carlo - Cronograma ({N_SIM:,} simulacoes)")
        ax.legend()
        fig.tight_layout()
        png = os.path.join(SCRIPT_DIR, "mc_cronograma.png")
        fig.savefig(png, dpi=130)
        plt.close(fig)

    return duracao_total, crit_idx, png

# ======================================================================
# 2) CUSTO (valores em R$ mil)
# ======================================================================
ITENS = [
    ("Chapas SA-516 Gr.70 (casco e cabecotes)",  (120, 150, 210)),
    ("Tubos SA-179 (feixe tubular)",             (80, 95, 130)),
    ("Espelhos + usinagem CNC",                  (25, 35, 55)),
    ("Consumiveis de solda",                     (8, 12, 20)),
    ("Mao de obra (caldeiraria + soldadores)",   (90, 120, 180)),
    ("Testes (hidrostatico, gamagrafia, PMI)",   (10, 15, 25)),
    ("Pintura / tratamento de superficie",       (6, 9, 15)),
    ("Transporte e logistica",                   (5, 8, 18)),
]

def simular_custo():
    custos = np.stack([RNG.triangular(o, m, p, size=N_SIM)
                       for _, (o, m, p) in ITENS], axis=1)
    total = custos.sum(axis=1)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.hist(total, bins=60, color="#2A9D8F", alpha=0.85, edgecolor="white")
    ax.axvline(ORCAMENTO, color="#E63946", ls="--", lw=2,
               label=f"Orcamento ({ORCAMENTO} R$ mil)")
    for q in (50, 80):
        ax.axvline(np.percentile(total, q), color="#4C8BF5", ls=":", lw=1.5)
    ax.set_xlabel("Custo total (R$ mil)")
    ax.set_ylabel("Frequencia")
    ax.set_title(f"Monte Carlo - Custo ({N_SIM:,} simulacoes)")
    ax.legend()
    fig.tight_layout()
    png = os.path.join(SCRIPT_DIR, "mc_custo.png")
    fig.savefig(png, dpi=130)
    plt.close(fig)

    return total, png

# ======================================================================
def pct(x, q):
    return np.percentile(x, q)

def main():
    print("=" * 62)
    print(" 1) CRONOGRAMA - fabricacao de 2 trocadores (ASME)")
    print("=" * 62)
    dur, crit, png_cron = simular_cronograma()
    print(f" Duracao do projeto (dias):")
    print(f"   Media: {dur.mean():6.1f} | P10: {pct(dur,10):5.1f} | "
          f"P50: {pct(dur,50):5.1f} | P90: {pct(dur,90):5.1f}")
    print(f"   Minimo plausivel: {dur.min():.1f} | Maximo: {dur.max():.1f}")
    print(f" P(terminar <= {PRAZO_ALVO} dias): {np.mean(dur <= PRAZO_ALVO)*100:5.1f}%")
    print(f" P(estourar > {PRAZO_ALVO+5} dias): {np.mean(dur > PRAZO_ALVO+5)*100:5.1f}%")
    print(f" Indice de criticidade (caminho critico em % das simulacoes):")
    ordem = np.argsort(-crit)
    for i in ordem:
        tid, desc, _, _ = TAREFAS[i]
        barra = "#" * int(crit[i] / 5)
        print(f"   {tid} {desc:<42} {crit[i]:5.1f}%  {barra}")

    print()
    print("=" * 62)
    print(" 2) CUSTO - mesma fabricacao (R$ mil)")
    print("=" * 62)
    tot, png_custo = simular_custo()
    print(f" Custo total (R$ mil):")
    print(f"   Media: {tot.mean():6.1f} | P50: {pct(tot,50):6.1f} | "
          f"P80: {pct(tot,80):6.1f} | P90: {pct(tot,90):6.1f}")
    contingencia = pct(tot, 80) - pct(tot, 50)
    print(f" Contingencia sugerida (P80 - P50): R$ {contingencia:6.1f} mil")
    print(f" P(estourar o orcamento de {ORCAMENTO}): {np.mean(tot > ORCAMENTO)*100:5.1f}%")
    print(f" Itens com maior impacto na incerteza (desvio padrao):")
    for j in np.argsort(-np.std(custos := np.stack(
            [RNG.triangular(o, m, p, size=2000) for _, (o, m, p) in ITENS]), axis=1))[:3]:
        print(f"   - {ITENS[j][0]}")

    print()
    print(f" Graficos: {png_cron}\n           {png_custo}")

if __name__ == "__main__":
    main()
