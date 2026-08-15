#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exportador para Microsoft Project XML (MSPDI) com Suporte Completo à EAP (WBS)
=============================================================================
Converte a árvore WBS ponderada e as estimativas de 3 pontos com resultados
do Monte Carlo em arquivo .xml perfeitamente compatível com o MS Project 2010+.
"""

import os
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from typing import Dict, Any


NS = "http://schemas.microsoft.com/project/2007"
FIELD_TEXT1 = 188743731  # Otimista (dias)
FIELD_TEXT2 = 188743732  # Provável (dias)
FIELD_TEXT3 = 188743733  # Pessimista (dias)
FIELD_TEXT4 = 188743734  # Índice de Criticidade (%)
FIELD_TEXT5 = 188743735  # Pacote EAP


def el(parent, tag, text=None):
    e = ET.SubElement(parent, f"{{{NS}}}{tag}")
    if text is not None:
        e.text = str(text)
    return e


def add_workdays(d: date, n: int) -> date:
    """Soma n dias úteis (seg-sex), exclusive o dia inicial."""
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def next_monday(d: date) -> date:
    """Retorna a próxima segunda-feira."""
    d += timedelta(days=1)
    while d.weekday() != 0:
        d += timedelta(days=1)
    return d


def exportar_msproject_xml(
    rede_wbs: Dict[str, Any],
    resultado_mc: Dict[str, Any],
    data_inicio: date,
    caminho_saida: str,
    base_duracao: str = "provavel"
) -> str:
    """
    Gera o arquivo Project XML (MSPDI) contendo toda a hierarquia WBS,
    vínculos de precedência, campos customizados e resultados do Monte Carlo.
    """
    nome_proj = rede_wbs.get("projeto", "Cronograma de Projeto")
    tarefas = rede_wbs["tarefas"]
    pacotes = rede_wbs["pacotes"]

    # 1. Forward pass determinístico para datas
    starts = {}
    fins = {}
    for t in tarefas:
        tid = t["id"]
        deps = t.get("deps", [])
        dur_dias = t["pessimista"] if base_duracao == "pessimista" else (
            t["otimista"] if base_duracao == "otimista" else t["provavel"]
        )
        if deps:
            s = max(fins[d] for d in deps) + timedelta(days=1)
            while s.weekday() >= 5:
                s += timedelta(days=1)
        else:
            s = data_inicio
        starts[tid] = s
        fins[tid] = add_workdays(s, dur_dias)

    fim_projeto = max(fins.values()) if fins else add_workdays(data_inicio, 10)

    # 2. Construção do documento XML (MSPDI)
    ET.register_namespace("", NS)
    root = ET.Element(f"{{{NS}}}Project")
    el(root, "Name", nome_proj)
    el(root, "Title", nome_proj)
    el(root, "StartDate", f"{data_inicio.isoformat()}T08:00:00")
    el(root, "FinishDate", f"{fim_projeto.isoformat()}T17:00:00")
    el(root, "ScheduleFromStart", "1")
    el(root, "MinutesPerDay", "480")
    el(root, "MinutesPerWeek", "2400")
    el(root, "DaysPerMonth", "20")
    el(root, "DefaultTaskType", "0")

    # Resumo executivo do Monte Carlo nos comentários do projeto
    d_mc = resultado_mc.get("duracao", {})
    c_mc = resultado_mc.get("custo", {})
    comentarios = (
        f"CRONOGRAMA GERADO POR PIPELINE INTELIGENTE COM EAP PADRONIZADA.\n"
        f"Análise de Monte Carlo (20.000 simulações):\n"
        f" • Prazo P50: {d_mc.get('p50', 0):.1f} dias úteis | P90: {d_mc.get('p90', 0):.1f} dias úteis\n"
        f" • Probabilidade de cumprimento do prazo contratual: {d_mc.get('prob_sucesso_prazo', 0):.1f}%\n"
        f" • Buffer de contingência sugerido: {d_mc.get('buffer_sugerido', 0):.1f} dias úteis\n"
        f" • Custo Médio Estimado: R$ {c_mc.get('media', 0)/1000.0:.1f}k (Contingência P80-P50: R$ {c_mc.get('contingencia_sugerida', 0)/1000.0:.1f}k)\n"
        f"Text1/2/3 = Estimativas Otimista/Provável/Pessimista | Text4 = Índice de Criticidade (%) | Text5 = Pacote WBS."
    )
    el(root, "Comments", comentarios)

    tasks_el = ET.SubElement(root, f"{{{NS}}}Tasks")

    # Tarefa Resumo do Projeto Geral (UID 1)
    t_raiz = ET.SubElement(tasks_el, f"{{{NS}}}Task")
    el(t_raiz, "UID", "1")
    el(t_raiz, "ID", "1")
    el(t_raiz, "Name", nome_proj)
    el(t_raiz, "Type", "0")
    el(t_raiz, "IsNull", "0")
    el(t_raiz, "CreateDate", f"{date.today().isoformat()}T08:00:00")
    el(t_raiz, "WBS", "0")
    el(t_raiz, "OutlineNumber", "0")
    el(t_raiz, "OutlineLevel", "1")
    el(t_raiz, "Priority", "500")
    el(t_raiz, "Start", f"{data_inicio.isoformat()}T08:00:00")
    el(t_raiz, "Finish", f"{fim_projeto.isoformat()}T17:00:00")
    el(t_raiz, "Duration", f"PT{int((fim_projeto - data_inicio).days * 8)}H")
    el(t_raiz, "DurationFormat", "7")
    el(t_raiz, "Summary", "1")
    el(t_raiz, "Notes", comentarios)

    # Mapeamento de UIDs
    # Pacotes WBS recebem UIDs (ex: 2..7), tarefas detalhadas recebem UIDs subsequentes
    uid_counter = 2
    uid_map_tarefas = {}
    uid_map_pacotes = {}

    for pkg in pacotes:
        uid_map_pacotes[pkg["codigo"]] = uid_counter
        uid_counter += 1
        for t in pkg["tarefas"]:
            uid_map_tarefas[t["id"]] = uid_counter
            uid_counter += 1

    id_counter = 2
    for pkg in pacotes:
        pkg_uid = uid_map_pacotes[pkg["codigo"]]
        pkg_tarefas = pkg["tarefas"]
        
        # Datas do pacote WBS
        pkg_start = min(starts[t["id"]] for t in pkg_tarefas)
        pkg_finish = max(fins[t["id"]] for t in pkg_tarefas)
        dur_pkg_dias = max(1, (pkg_finish - pkg_start).days)

        # 1. Cria o nó de Tarefa Resumo do Pacote WBS (OutlineLevel = 1)
        t_pkg = ET.SubElement(tasks_el, f"{{{NS}}}Task")
        el(t_pkg, "UID", str(pkg_uid))
        el(t_pkg, "ID", str(id_counter))
        el(t_pkg, "Name", f"{pkg['codigo']} {pkg['nome']} (Peso: {pkg['peso_percentual']:.0f}%)")
        el(t_pkg, "Type", "0")
        el(t_pkg, "IsNull", "0")
        el(t_pkg, "CreateDate", f"{date.today().isoformat()}T08:00:00")
        el(t_pkg, "WBS", pkg["codigo"])
        el(t_pkg, "OutlineNumber", pkg["codigo"])
        el(t_pkg, "OutlineLevel", "1")
        el(t_pkg, "Priority", "500")
        el(t_pkg, "Start", f"{pkg_start.isoformat()}T08:00:00")
        el(t_pkg, "Finish", f"{pkg_finish.isoformat()}T17:00:00")
        el(t_pkg, "Duration", f"PT{int(dur_pkg_dias * 8)}H")
        el(t_pkg, "DurationFormat", "7")
        el(t_pkg, "Summary", "1")
        id_counter += 1

        # 2. Cria as subatividades do pacote WBS (OutlineLevel = 2)
        for t in pkg_tarefas:
            t_uid = uid_map_tarefas[t["id"]]
            s_data = starts[t["id"]]
            f_data = fins[t["id"]]
            dur_dias = t["provavel"]
            crit_val = t.get("indice_criticidade", 0.0)

            t_elem = ET.SubElement(tasks_el, f"{{{NS}}}Task")
            el(t_elem, "UID", str(t_uid))
            el(t_elem, "ID", str(id_counter))
            el(t_elem, "Name", t["nome"])
            el(t_elem, "Type", "0")
            el(t_elem, "IsNull", "0")
            el(t_elem, "CreateDate", f"{date.today().isoformat()}T08:00:00")
            el(t_elem, "WBS", t["wbs"])
            el(t_elem, "OutlineNumber", t["wbs"])
            el(t_elem, "OutlineLevel", "2")
            el(t_elem, "Priority", "500")
            el(t_elem, "Start", f"{s_data.isoformat()}T08:00:00")
            el(t_elem, "Finish", f"{f_data.isoformat()}T17:00:00")
            el(t_elem, "Duration", f"PT{int(dur_dias * 8)}H")
            el(t_elem, "DurationFormat", "7")
            el(t_elem, "Summary", "0")

            # Predecessoras (Vínculos Finish-to-Start)
            for dep_id in t.get("deps", []):
                if dep_id in uid_map_tarefas:
                    pl = ET.SubElement(t_elem, f"{{{NS}}}PredecessorLink")
                    el(pl, "PredecessorUID", str(uid_map_tarefas[dep_id]))
                    el(pl, "Type", "1")  # 1 = Termino-a-Inicio (FS)
                    el(pl, "LinkLag", "0")

            # Campos Customizados
            valores_campos = [
                (FIELD_TEXT1, f"{t['otimista']} d"),
                (FIELD_TEXT2, f"{t['provavel']} d"),
                (FIELD_TEXT3, f"{t['pessimista']} d"),
                (FIELD_TEXT4, f"{crit_val:.1f}%"),
                (FIELD_TEXT5, f"{pkg['codigo']} - {pkg['nome']}")
            ]
            for fid, val in valores_campos:
                ea = ET.SubElement(t_elem, f"{{{NS}}}ExtendedAttribute")
                el(ea, "FieldID", str(fid))
                el(ea, "Value", str(val))

            # Notas da Tarefa
            notas = (
                f"Estimativas de 3 Pontos: Otimista = {t['otimista']}d | Provável = {t['provavel']}d | Pessimista = {t['pessimista']}d.\n"
                f"Índice de Criticidade (Monte Carlo): {crit_val:.1f}% das 20.000 iterações no Caminho Crítico."
            )
            el(t_elem, "Notes", notas)
            id_counter += 1

    # Definição dos Cabeçalhos dos Campos Customizados
    ea_proj = ET.SubElement(root, f"{{{NS}}}ExtendedAttributes")
    campos_def = [
        (FIELD_TEXT1, "Text1", "Estimativa Otimista"),
        (FIELD_TEXT2, "Text2", "Estimativa Provavel"),
        (FIELD_TEXT3, "Text3", "Estimativa Pessimista"),
        (FIELD_TEXT4, "Text4", "Indice Criticidade (%)"),
        (FIELD_TEXT5, "Text5", "Pacote WBS / EAP")
    ]
    for fid, campo, alias in campos_def:
        e = ET.SubElement(ea_proj, f"{{{NS}}}ExtendedAttribute")
        el(e, "FieldID", str(fid))
        el(e, "FieldName", campo)
        el(e, "Alias", alias)

    # Serialização do XML
    os.makedirs(os.path.dirname(os.path.abspath(caminho_saida)), exist_ok=True)
    ET.indent(root, space="  ")
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(xml_str)

    return caminho_saida
