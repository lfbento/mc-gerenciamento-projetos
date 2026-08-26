#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exportador para Microsoft Project XML (MSPDI) com Suporte Completo à EAP e Recursos
==================================================================================
Converte a árvore WBS ponderada, estimativas de 3 pontos, resultados MCMC
e Tabela de Recursos/Atribuições em arquivo .xml perfeitamente compatível com o MS Project 2010+.
"""

import os
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from typing import Dict, Any, List, Optional


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


def add_workdays(d: date, n: float) -> date:
    """Soma n dias úteis (seg-sex), exclusive o dia inicial."""
    dias_inteiros = max(1, int(round(n)))
    while dias_inteiros > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            dias_inteiros -= 1
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
    base_duracao: str = "provavel",
    metricas_recursos: Optional[Dict[str, Any]] = None
) -> str:
    """
    Gera o arquivo Project XML (MSPDI) contendo toda a hierarquia WBS,
    vínculos de precedência, campos customizados, tabela de recursos e atribuições.
    """
    nome_proj = rede_wbs.get("projeto", "Cronograma de Projeto")
    tarefas = rede_wbs["tarefas"]
    pacotes = rede_wbs["pacotes"]

    # 1. Forward pass com suporte a deslocamentos do nivelamento bioinspirado
    starts = {}
    fins = {}
    for t in tarefas:
        tid = t["id"]
        deps = t.get("deps", [])
        dur_dias = t["pessimista"] if base_duracao == "pessimista" else (
            t["otimista"] if base_duracao == "otimista" else t["provavel"]
        )
        shift_niv = t.get("shift_nivelamento", 0.0)

        if deps:
            s_base = max(fins[d] for d in deps) + timedelta(days=1)
            while s_base.weekday() >= 5:
                s_base += timedelta(days=1)
        else:
            s_base = data_inicio

        # Aplica o deslocamento otimizado pelo GA
        s = add_workdays(s_base, shift_niv) if shift_niv > 0 else s_base
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
        f"CRONOGRAMA GERADO POR PIPELINE INTELIGENTE COM EAP PADRONIZADA (MCMC).\n"
        f"Alvo Gerencial P85: {d_mc.get('p85', 0):.1f} dias úteis | P50 Fábrica: {d_mc.get('p50', 0):.1f} dias.\n"
        f"Custo Operacional Estimado (P50): R$ {c_mc.get('p50', 0):,.2f} | Reserva Contingência (P80-P50): R$ {c_mc.get('contingencia_sugerida', 0):,.2f}.\n"
        f"Recursos Dimensionados: {metricas_recursos.get('hh_total_projeto', 0):.1f} HH Totais | Pico: {metricas_recursos.get('pico_efetivo_global', 0):.1f} FTEs." if metricas_recursos else ""
    )
    el(root, "Comments", comentarios)

    # 3. Calendário Padrão (Segunda a Sexta, 8h/dia)
    cals = ET.SubElement(root, f"{{{NS}}}Calendars")
    cal = ET.SubElement(cals, f"{{{NS}}}Calendar")
    el(cal, "UID", "1")
    el(cal, "Name", "Padrao_Caldeiraria")
    el(cal, "IsBaseCalendar", "1")
    wds = ET.SubElement(cal, f"{{{NS}}}WeekDays")
    for day_type in range(1, 8):
        wd = ET.SubElement(wds, f"{{{NS}}}WeekDay")
        el(wd, "DayType", str(day_type))
        if day_type in [2, 3, 4, 5, 6]:
            el(wd, "DayWorking", "1")
            wt = ET.SubElement(wd, f"{{{NS}}}WorkingTimes")
            t1 = ET.SubElement(wt, f"{{{NS}}}WorkingTime")
            el(t1, "FromTime", "08:00:00")
            el(t1, "ToTime", "12:00:00")
            t2 = ET.SubElement(wt, f"{{{NS}}}WorkingTime")
            el(t2, "FromTime", "13:00:00")
            el(t2, "ToTime", "17:00:00")
        else:
            el(wd, "DayWorking", "0")

    # 4. Criação da Estrutura de Tarefas (Tasks)
    tasks_el = ET.SubElement(root, f"{{{NS}}}Tasks")

    # Tarefa Raiz do Projeto (OutlineLevel = 0)
    t_root = ET.SubElement(tasks_el, f"{{{NS}}}Task")
    el(t_root, "UID", "0")
    el(t_root, "ID", "0")
    el(t_root, "Name", nome_proj)
    el(t_root, "Type", "0")
    el(t_root, "IsNull", "0")
    el(t_root, "CreateDate", f"{date.today().isoformat()}T08:00:00")
    el(t_root, "WBS", "0")
    el(t_root, "OutlineNumber", "0")
    el(t_root, "OutlineLevel", "0")
    el(t_root, "Priority", "500")
    el(t_root, "Start", f"{data_inicio.isoformat()}T08:00:00")
    el(t_root, "Finish", f"{fim_projeto.isoformat()}T17:00:00")
    el(t_root, "Summary", "1")

    # Mapeamento de UIDs
    id_counter = 1
    uid_map_tarefas = {}
    uid_map_pacotes = {}
    
    for i, pkg in enumerate(pacotes, start=1):
        uid_map_pacotes[pkg["codigo"]] = id_counter
        id_counter += 1
        for t in pkg["tarefas"]:
            uid_map_tarefas[t["id"]] = id_counter
            id_counter += 1

    id_counter = 1
    for pkg in pacotes:
        pkg_uid = uid_map_pacotes[pkg["codigo"]]
        pkg_tarefas = pkg["tarefas"]
        pkg_start = min(starts[t["id"]] for t in pkg_tarefas)
        pkg_finish = max(fins[t["id"]] for t in pkg_tarefas)
        dur_pkg_dias = max(1, (pkg_finish - pkg_start).days)

        # Tarefa Resumo do Pacote WBS (OutlineLevel = 1)
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

        # Subatividades do pacote WBS (OutlineLevel = 2)
        for t in pkg_tarefas:
            t_uid = uid_map_tarefas[t["id"]]
            s_data = starts[t["id"]]
            f_data = fins[t["id"]]
            dur_dias = t["provavel"]
            crit_val = t.get("indice_criticidade", 0.0)
            hh_t = t.get("hh_total", dur_dias * 8.0)

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
            el(t_elem, "Work", f"PT{int(hh_t)}H0M0S")
            el(t_elem, "Summary", "0")

            # Predecessoras (FS)
            for dep_id in t.get("deps", []):
                if dep_id in uid_map_tarefas:
                    pl = ET.SubElement(t_elem, f"{{{NS}}}PredecessorLink")
                    el(pl, "PredecessorUID", str(uid_map_tarefas[dep_id]))
                    el(pl, "Type", "1")
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

            # Notas da Tarefa com Recursos
            recursos_desc = t.get("nomes_recursos_str", "Conforme equipe padrão")
            notas = (
                f"Estimativas de 3 Pontos: Otimista = {t['otimista']}d | Provável = {t['provavel']}d | Pessimista = {t['pessimista']}d.\n"
                f"Índice de Criticidade MCMC: {crit_val:.1f}% no Caminho Crítico.\n"
                f"Alocação de Recursos: {recursos_desc} | Total: {hh_t:.1f} HH."
            )
            el(t_elem, "Notes", notas)
            id_counter += 1

    # 5. Tabela de Recursos (Resources)
    resources_el = ET.SubElement(root, f"{{{NS}}}Resources")
    if metricas_recursos and "catalogo" in metricas_recursos:
        catalogo = metricas_recursos["catalogo"]
        for cod_rec, info in catalogo.items():
            r_elem = ET.SubElement(resources_el, f"{{{NS}}}Resource")
            el(r_elem, "UID", str(info["uid"]))
            el(r_elem, "ID", str(info["id"]))
            el(r_elem, "Name", info["nome"])
            el(r_elem, "Type", "1") # 1 = Work
            el(r_elem, "IsNull", "0")
            el(r_elem, "MaxUnits", str(info.get("max_units", 1.0)))
            el(r_elem, "StandardRate", f"{info['taxa_hora']:.2f}")
            el(r_elem, "StandardRateFormat", "2")
            el(r_elem, "Cost", "0")

    # 6. Tabela de Atribuições (Assignments)
    assignments_el = ET.SubElement(root, f"{{{NS}}}Assignments")
    if metricas_recursos and "atribuicoes" in metricas_recursos:
        for asgn in metricas_recursos["atribuicoes"]:
            tid = asgn["task_id"]
            if tid in uid_map_tarefas:
                task_uid = uid_map_tarefas[tid]
                a_elem = ET.SubElement(assignments_el, f"{{{NS}}}Assignment")
                el(a_elem, "UID", str(asgn["uid"]))
                el(a_elem, "TaskUID", str(task_uid))
                el(a_elem, "ResourceUID", str(asgn["resource_uid"]))
                el(a_elem, "Units", str(asgn["units"]))
                el(a_elem, "Work", f"PT{int(asgn['work_hours'])}H0M0S")
                el(a_elem, "Cost", f"{asgn['cost']:.2f}")

    # 7. Definição dos Cabeçalhos dos Campos Customizados
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
