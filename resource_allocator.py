#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Dimensionamento e Alocação de Recursos Industriais
===========================================================
Implementado em conformidade estrita com o Guia / System Prompt:
`@estimativa-recursos-fabricacao-industrial`

Base Normativa e Bibliográfica:
  - Kenneth Storm (Industrial Piping and Equipment Estimating Manual - 2ª ed.)
  - Richardson Engineering (Process Plant Construction Estimating Standards)
  - Dennis R. Moss (Pressure Vessel Design Manual - 4ª ed.)
  - Normas: API 650, ASME BPVC Sec. VIII Div.1 / Sec. IX, NR-13, AWS D1.1 e NBR 8800.
  - Tabelas de Homem-Hora (HH) e Fatores de Produtividade SENAI/SESI Caldeiraria Pesada.

Parâmetros de Engenharia:
  - Fator Material Inox SA-240 304: 1.40x (vs. Aço Carbono)
  - Fator de Complexidade API 650 (Costado, Bocais A1-W1 e BV M1): 1.30x
  - Fator de Conformidade Regulatória NR-13: +15% (1.15x)
  - Eficiência Operacional Padrão de Fábrica: 75%
  - Jornada de Trabalho: 8h/dia (40h úteis/semana, 08:00-12:00 e 13:00-17:00)
"""

import os
from typing import Dict, Any, List, Tuple
from datetime import date, timedelta
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Constantes de Engenharia extraídas de @estimativa-recursos-fabricacao-industrial
FATOR_MATERIAL_INOX_304 = 1.40
FATOR_COMPLEXIDADE_API650 = 1.30
FATOR_REGULATORIO_NR13 = 1.15
EFICIENCIA_OFICINA = 0.75
JORNADA_HORAS_DIA = 8.0

# Catálogo Padrão de Recursos e Especialidades Industriais
CATALOGO_RECURSOS = {
    "ENG-PROJ": {
        "uid": 1, "id": 1,
        "nome": "Engenheiro Mecânico de Projetos / Cálculos",
        "tipo": 1, # 1 = Work
        "taxa_hora": 110.00,
        "max_units": 1.0,
        "cor": "#1E3A8A", # Azul Marinho
        "categoria": "Engenharia"
    },
    "PROJ-CAD": {
        "uid": 2, "id": 2,
        "nome": "Projetista Mecânico / Modelador 3D",
        "tipo": 1,
        "taxa_hora": 65.00,
        "max_units": 1.0,
        "cor": "#3B82F6", # Azul Royal
        "categoria": "Engenharia"
    },
    "COMP-TEC": {
        "uid": 3, "id": 3,
        "nome": "Comprador Técnico Industrial / Diligenciamento",
        "tipo": 1,
        "taxa_hora": 55.00,
        "max_units": 1.0,
        "cor": "#F59E0B", # Âmbar
        "categoria": "Suprimentos"
    },
    "CALD-PREP": {
        "uid": 4, "id": 4,
        "nome": "Caldeireiro de Traçado e Corte Plasma",
        "tipo": 1,
        "taxa_hora": 50.00,
        "max_units": 2.0,
        "cor": "#F97316", # Laranja
        "categoria": "Caldeiraria"
    },
    "OPER-CAL": {
        "uid": 5, "id": 5,
        "nome": "Operador de Calandra e Conformação",
        "tipo": 1,
        "taxa_hora": 50.00,
        "max_units": 1.0,
        "cor": "#EA580C", # Laranja Escuro
        "categoria": "Caldeiraria"
    },
    "SOLD-ASME": {
        "uid": 6, "id": 6,
        "nome": "Soldador Qualificado ASME IX (TIG/MIG/SAW)",
        "tipo": 1,
        "taxa_hora": 65.00,
        "max_units": 3.0,
        "cor": "#DC2626", # Vermelho
        "categoria": "Soldagem"
    },
    "CALD-MONT": {
        "uid": 7, "id": 7,
        "nome": "Caldeireiro Montador / Ajustador de Equipamentos",
        "tipo": 1,
        "taxa_hora": 55.00,
        "max_units": 2.0,
        "cor": "#D97706", # Dourado/Âmbar Escuro
        "categoria": "Montagem"
    },
    "INSP-END": {
        "uid": 8, "id": 8,
        "nome": "Inspetor de Soldagem / END Nível II (SNQC)",
        "tipo": 1,
        "taxa_hora": 90.00,
        "max_units": 1.0,
        "cor": "#8B5CF6", # Roxo
        "categoria": "Qualidade"
    },
    "PINT-IND": {
        "uid": 9, "id": 9,
        "nome": "Pintor Industrial / Tratador de Superfície Inox",
        "tipo": 1,
        "taxa_hora": 45.00,
        "max_units": 2.0,
        "cor": "#10B981", # Verde Esmeralda
        "categoria": "Tratamento"
    },
    "AJUD-OP": {
        "uid": 10, "id": 10,
        "nome": "Ajudante Operacional de Caldeiraria e Fábrica",
        "tipo": 1,
        "taxa_hora": 30.00,
        "max_units": 4.0,
        "cor": "#64748B", # Cinza Ardósia
        "categoria": "Apoio"
    },
    "RIG-LOG": {
        "uid": 11, "id": 11,
        "nome": "Rigger / Operador de Carga, Berço e Expedição",
        "tipo": 1,
        "taxa_hora": 45.00,
        "max_units": 2.0,
        "cor": "#78350F", # Marrom
        "categoria": "Logística"
    }
}

# Regras de Alocação de Recursos por Atividade da WBS
# Estrutura: {wbs_id: [(cod_recurso, unidades)]}
REGRAS_ALOCACAO_WBS = {
    "1.1": [("ENG-PROJ", 1.0), ("PROJ-CAD", 1.0)],
    "1.2": [("ENG-PROJ", 1.0)],
    "2.1": [("PROJ-CAD", 1.0), ("ENG-PROJ", 0.5)],
    "2.2": [("ENG-PROJ", 1.0)],
    "2.3": [("ENG-PROJ", 0.5), ("INSP-END", 1.0)],
    "2.4": [("ENG-PROJ", 0.5)],
    "3.1": [("COMP-TEC", 1.0)],
    "3.2": [("COMP-TEC", 0.25)], # Acompanhamento / Diligenciamento com usina
    "3.3": [("COMP-TEC", 0.50)],
    "3.4": [("INSP-END", 1.0), ("AJUD-OP", 1.0)],
    "4.1": [("CALD-PREP", 1.0), ("AJUD-OP", 1.0)],
    "4.2": [("OPER-CAL", 1.0), ("AJUD-OP", 1.0)],
    "4.3": [("SOLD-ASME", 2.0), ("AJUD-OP", 2.0)], # Dupla de soldadores qualificados ASME IX
    "4.4": [("CALD-MONT", 2.0), ("SOLD-ASME", 1.0), ("AJUD-OP", 2.0)],
    "4.5": [("CALD-MONT", 1.0), ("SOLD-ASME", 1.0), ("AJUD-OP", 1.0)],
    "4.6": [("INSP-END", 1.0), ("AJUD-OP", 1.0)],
    "4.7": [("ENG-PROJ", 0.5), ("INSP-END", 1.0), ("CALD-MONT", 1.0), ("AJUD-OP", 1.0)],
    "5.1": [("PINT-IND", 1.0), ("AJUD-OP", 1.0)],
    "5.2": [("PINT-IND", 1.0), ("AJUD-OP", 1.0)],
    "6.1": [("ENG-PROJ", 1.0), ("INSP-END", 0.5)],
    "6.2": [("CALD-MONT", 1.0), ("RIG-LOG", 1.0), ("AJUD-OP", 1.0)],
    "6.3": [("RIG-LOG", 1.0), ("COMP-TEC", 0.25)],
}


def dimensionar_recursos_tarefas(rede_wbs: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Calcula Homens-Hora (HH), custos de mão de obra e estrutura de atribuições para cada tarefa.
    """
    tarefas = rede_wbs["tarefas"]
    atribuicoes = []
    totais_por_recurso = {cod: {"hh": 0.0, "custo": 0.0, "pico_fte": 0.0} for cod in CATALOGO_RECURSOS}

    asgn_uid = 1
    for t in tarefas:
        tid = t["id"]
        duracao_dias = float(t.get("provavel", t.get("duracao_base", 1.0)))
        duracao_horas = duracao_dias * 8.0 # 8 horas por dia útil
        
        recursos_tarefa = REGRAS_ALOCACAO_WBS.get(tid, [("AJUD-OP", 1.0)])
        t["recursos_alocados"] = []
        hh_tarefa_total = 0.0
        custo_mo_tarefa = 0.0

        for cod_rec, units in recursos_tarefa:
            info_rec = CATALOGO_RECURSOS[cod_rec]
            hh_item = duracao_horas * units
            custo_item = hh_item * info_rec["taxa_hora"]

            hh_tarefa_total += hh_item
            custo_mo_tarefa += custo_item

            totais_por_recurso[cod_rec]["hh"] += hh_item
            totais_por_recurso[cod_rec]["custo"] += custo_item

            atribuicao = {
                "uid": asgn_uid,
                "task_id": tid,
                "resource_code": cod_rec,
                "resource_uid": info_rec["uid"],
                "resource_name": info_rec["nome"],
                "units": units,
                "work_hours": hh_item,
                "cost": custo_item
            }
            atribuicoes.append(atribuicao)
            t["recursos_alocados"].append(atribuicao)
            asgn_uid += 1

        t["hh_total"] = round(hh_tarefa_total, 1)
        t["custo_mao_de_obra"] = round(custo_mo_tarefa, 2)
        t["nomes_recursos_str"] = ", ".join([f"{CATALOGO_RECURSOS[r[0]]['nome'].split('/')[0].strip()} [{int(r[1]*100)}%]" for r in recursos_tarefa])

    resumo_recursos = []
    hh_geral = 0.0
    custo_mo_geral = 0.0

    for cod, dados in totais_por_recurso.items():
        if dados["hh"] > 0:
            info = CATALOGO_RECURSOS[cod]
            hh_geral += dados["hh"]
            custo_mo_geral += dados["custo"]
            resumo_recursos.append({
                "codigo": cod,
                "nome": info["nome"],
                "categoria": info["categoria"],
                "taxa_hora": info["taxa_hora"],
                "hh_total": round(dados["hh"], 1),
                "custo_total": round(dados["custo"], 2),
                "cor": info["cor"]
            })

    metricas_consolidadas = {
        "hh_total_projeto": round(hh_geral, 1),
        "custo_total_mo": round(custo_mo_geral, 2),
        "recursos_detalhados": sorted(resumo_recursos, key=lambda x: x["hh_total"], reverse=True),
        "atribuicoes": atribuicoes,
        "catalogo": CATALOGO_RECURSOS
    }

    return atribuicoes, metricas_consolidadas


def gerar_histograma_recursos_temporal(
    rede_wbs: Dict[str, Any],
    metricas_recursos: Dict[str, Any],
    caminho_saida_png: str = "assets/mc_histograma_recursos.png"
) -> str:
    """
    Gera o gráfico de Histograma de Alocação de Recursos por Função ao Longo do Tempo (Semanas de Projeto).
    Plota barras empilhadas por especialidade e linha da Curva S de Homem-Hora acumulado.
    """
    os.makedirs(os.path.dirname(os.path.abspath(caminho_saida_png)) or ".", exist_ok=True)
    tarefas = rede_wbs["tarefas"]
    
    # 1. Simulação temporal do cronograma (Usa datas niveladas pelo GA se disponíveis)
    idx_map = {t["id"]: i for i, t in enumerate(tarefas)}
    
    n_t = len(tarefas)
    start_days = [0.0] * n_t
    finish_days = [0.0] * n_t
    
    # Se o nivelamento já foi executado, utiliza as datas niveladas
    tem_nivelamento = any("start_nivelado" in t for t in tarefas)
    
    for i, t in enumerate(tarefas):
        dur = float(t.get("provavel", 1.0))
        if t["id"] == "4.3" and tem_nivelamento:
            dur = max(1.0, round(float(t.get("provavel", 1.0)) * 0.65, 1)) # Crashing mitigado com equipe reforçada
            
        if tem_nivelamento and "start_nivelado" in t and "finish_nivelado" in t:
            start_days[i] = float(t["start_nivelado"])
            finish_days[i] = float(t["finish_nivelado"])
        else:
            deps = t.get("deps", [])
            if deps:
                max_prev = max([finish_days[idx_map[d]] for d in deps if d in idx_map] or [0.0])
                start_days[i] = max_prev
            else:
                start_days[i] = 0.0
            finish_days[i] = start_days[i] + dur

    total_dias_projeto = max(finish_days) if finish_days else 61.6
    num_semanas = int(np.ceil(total_dias_projeto / 5.0)) # 5 dias úteis por semana
    
    # 2. Matriz de Alocação: [semanas x especialidades]
    codigos_ativos = [r["codigo"] for r in metricas_recursos["recursos_detalhados"]]
    alocacao_semanal = {cod: np.zeros(num_semanas) for cod in codigos_ativos}
    
    for i, t in enumerate(tarefas):
        s_day = start_days[i]
        f_day = finish_days[i]
        dur = f_day - s_day
        if dur <= 0: continue
        
        for asgn in t.get("recursos_alocados", []):
            cod_rec = asgn["resource_code"]
            units = asgn["units"]
            
            # Distribui as unidades pelas semanas correspondentes
            for sem in range(num_semanas):
                sem_inicio = sem * 5.0
                sem_fim = (sem + 1) * 5.0
                
                # Sobreposição entre a tarefa e a semana
                inter_inicio = max(s_day, sem_inicio)
                inter_fim = min(f_day, sem_fim)
                
                if inter_fim > inter_inicio:
                    dias_na_semana = inter_fim - inter_inicio
                    # FTE médio na semana
                    fte_semanal = units * (dias_na_semana / 5.0)
                    alocacao_semanal[cod_rec][sem] += fte_semanal

    # 3. Plotagem com Proporção Otimizada para PDF (12.0 x 3.8 inches, 300 DPI)
    fig, ax1 = plt.subplots(figsize=(12.0, 3.8), dpi=300)
    x_indices = np.arange(num_semanas)
    
    if num_semanas > 16:
        semanas_labels = [f"S{s+1:02d}" for s in range(num_semanas)]
        rot_x = 45
        ha_x = "right"
    else:
        semanas_labels = [f"Sem {s+1}" for s in range(num_semanas)]
        rot_x = 0
        ha_x = "center"

    bottom_y = np.zeros(num_semanas)
    for cod in codigos_ativos:
        valores = alocacao_semanal[cod]
        info = CATALOGO_RECURSOS[cod]
        nome_label = f"{info['categoria']} ({info['nome'].split('/')[0].strip()})"
        ax1.bar(
            x_indices, valores, bottom=bottom_y, label=nome_label,
            color=info["cor"], edgecolor="#FFFFFF", linewidth=0.4, alpha=0.92, width=0.74
        )
        bottom_y += valores

    pico_efetivo = float(np.max(bottom_y))
    semana_pico = int(np.argmax(bottom_y)) + 1
    hh_total_proj = metricas_recursos.get("hh_total_projeto", float(np.sum(bottom_y) * 40.0))

    # Eixo 2: Curva S de Homem-Hora Acumulado (HH)
    ax2 = ax1.twinx()
    hh_por_semana = bottom_y * 40.0
    hh_acumulado = np.cumsum(hh_por_semana)
    ax2.plot(x_indices, hh_acumulado, color="#0F172A", lw=1.9, linestyle="-", marker="o", markersize=3.2, label="Curva S (HH Acumulado)")
    ax2.set_ylabel("Homem-Hora Acumulado (HH)", fontsize=7.8, fontweight="bold", color="#0F172A", labelpad=6)
    ax2.tick_params(axis='y', labelsize=7.0, labelcolor="#0F172A")
    ax2.set_ylim(0, max(hh_total_proj * 1.15, 100))
    ax2.grid(False)

    # Rótulos limpos e despoluídos no topo das barras
    for i, val in enumerate(bottom_y):
        if val >= 0.2:
            if abs(val - pico_efetivo) < 1e-4:
                ax1.text(
                    x_indices[i], val + 0.10, f"★ {val:.1f}\nPICO",
                    ha="center", va="bottom", fontsize=6.2, fontweight="bold", color="#DC2626",
                    bbox=dict(boxstyle="round,pad=0.12", facecolor="#FEE2E2", edgecolor="#DC2626", lw=0.5)
                )
            elif val >= 0.9:
                ax1.text(
                    x_indices[i], val + 0.06, f"{val:.1f}",
                    ha="center", va="bottom", fontsize=6.2, fontweight="bold", color="#1E293B"
                )

    # Linha guia horizontal do Pico Máximo
    ax1.axhline(pico_efetivo, color="#DC2626", linestyle="--", linewidth=0.9, alpha=0.7)
    ax1.text(
        0.0, pico_efetivo + 0.10, f"Pico Máximo: {pico_efetivo:.1f} FTEs ({int(round(pico_efetivo*40))}h/sem na Semana {semana_pico})",
        color="#DC2626", fontweight="bold", fontsize=7.2, ha="left"
    )

    # Configuração dos eixos principais
    ax1.set_xlabel("Semanas de Execução Fabril", fontsize=7.8, fontweight="bold", color="#1E293B", labelpad=4)
    ax1.set_ylabel("Efetivo (FTEs)", fontsize=7.8, fontweight="bold", color="#1E293B", labelpad=4)
    ax1.set_xticks(x_indices)
    ax1.set_xticklabels(semanas_labels, rotation=rot_x, ha=ha_x, fontsize=6.8)
    ax1.set_ylim(0, max(5.8, pico_efetivo * 1.34))
    ax1.tick_params(axis='both', labelsize=7.0)
    ax1.grid(axis='y', linestyle=':', alpha=0.4, color='#94A3B8')

    # Título executivo padronizado
    fig.suptitle(
        f"Histograma Semanal de Recursos por Função Nivelada (Pico: {pico_efetivo:.1f} FTEs na Sem {semana_pico} | Total: {hh_total_proj:.1f} HH)",
        fontsize=8.8, fontweight="bold", color="#0B2545", y=0.98
    )

    # Legenda externa inferior em 4 colunas limpas
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    fig.legend(
        handles1 + handles2, labels1 + labels2,
        loc="lower center", bbox_to_anchor=(0.5, -0.06),
        fontsize=6.0, frameon=True, edgecolor="#CBD5E1", facecolor="#F8FAFC",
        ncol=4
    )

    plt.tight_layout(rect=[0, 0.10, 1, 0.94])
    fig.savefig(caminho_saida_png, dpi=300, bbox_inches="tight")
    plt.close(fig)

    metricas_recursos["pico_efetivo_global"] = round(pico_efetivo, 1)
    metricas_recursos["semana_pico_global"] = semana_pico
    metricas_recursos["caminho_histograma_png"] = caminho_saida_png

    return caminho_saida_png
