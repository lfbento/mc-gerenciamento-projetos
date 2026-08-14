#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera cronograma para MS Project (Project XML / MSPDI)
=====================================================
Converte a rede de tarefas definida em mc_projetos.py (estimativas de 3
pontos) em um arquivo .xml que o MS Project 2010+ abre nativamente
(Arquivo > Abrir > selecionar .xml).

Por que XML e nao .mpp?
  .mpp e formato binario proprietario da Microsoft - nao ha gerador
  confiavel fora do Windows (COM). O Project XML e o formato oficial de
  intercambio e o Project abre direto. No Windows, da para converter
  .xml -> .mpp abrindo e salvando, ou via COM (pywin32).

O que o arquivo carrega:
  - Tarefas com duracao base (provavel ou P50 do MC), datas e vinculos FS
  - Campos customizados Text1/2/3 = Otimista/Provavel/Pessimista (dias)
    (alimenta Primavera Risk / @RISK depois)
  - Nota em cada tarefa com as 3 estimativas
  - Comentarios do projeto com o resumo do Monte Carlo

Uso:
  python3 gerar_msproject.py [--inicio 2026-08-17] [--base provavel|p50]
                             [--prazo 45] [--saida cronograma.xml]
"""

import argparse
import math
import os
import sys
import xml.etree.ElementTree as ET
from datetime import date, timedelta

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mc_projetos import TAREFAS, simular_cronograma, RNG  # noqa: E402

NS = "http://schemas.microsoft.com/project/2007"
FIELD_TEXT1, FIELD_TEXT2, FIELD_TEXT3 = 188743731, 188743732, 188743733

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def el(parent, tag, text=None):
    e = ET.SubElement(parent, f"{{{NS}}}{tag}")
    if text is not None:
        e.text = text
    return e


def add_workdays(d, n):
    """Soma n dias uteis (seg-sex), exclusive o dia inicial."""
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def next_monday(d):
    d += timedelta(days=1)
    while d.weekday() != 0:
        d += timedelta(days=1)
    return d


def build_schedule(inicio, dur_base):
    """Forward pass deterministico: start = max(fim das dependencias)."""
    starts, fins = {}, {}
    for tid, _, deps, _ in TAREFAS:
        if deps:
            s = max(fins[d] for d in deps) + timedelta(days=1)
            while s.weekday() >= 5:
                s += timedelta(days=1)
        else:
            s = inicio
        starts[tid] = s
        fins[tid] = add_workdays(s, dur_base[tid])
    return starts, fins


def add_task(tasks_el, uid, id_, name, start, finish, dur_dias,
             deps_uids, pontos, summary=False, wbs="1", notes=""):
    t = ET.SubElement(tasks_el, f"{{{NS}}}Task")
    el(t, "UID", str(uid))
    el(t, "ID", str(id_))
    el(t, "Name", name)
    el(t, "Type", "0")
    el(t, "IsNull", "0")
    el(t, "CreateDate", f"{date.today().isoformat()}T08:00:00")
    el(t, "WBS", wbs)
    el(t, "OutlineNumber", wbs)
    el(t, "OutlineLevel", "1" if summary else "2")
    el(t, "Priority", "500")
    el(t, "Start", f"{start.isoformat()}T08:00:00")
    el(t, "Finish", f"{finish.isoformat()}T17:00:00")
    el(t, "Duration", f"PT{int(dur_dias * 8)}H")
    el(t, "DurationFormat", "7")  # 7 = dias
    el(t, "Summary", "1" if summary else "0")
    for d in deps_uids:
        pl = ET.SubElement(t, f"{{{NS}}}PredecessorLink")
        el(pl, "PredecessorUID", str(d))
        el(pl, "Type", "1")  # 1 = termino-a-inicio (FS)
        el(pl, "LinkLag", "0")
    if not summary and pontos:
        for fid, v in zip((FIELD_TEXT1, FIELD_TEXT2, FIELD_TEXT3), pontos):
            ea = ET.SubElement(t, f"{{{NS}}}ExtendedAttribute")
            el(ea, "FieldID", str(fid))
            el(ea, "Value", str(v))
    if notes:
        el(t, "Notes", notes)
    return t


def gerar_xml(inicio, dur_base, nome, prazo, saida):
    # --- Monte Carlo (so para o relatorio) ---
    dur_sims, crit, _ = simular_cronograma(plot=False)
    p50, p90 = np.percentile(dur_sims, [50, 90])
    prob = np.mean(dur_sims <= prazo) * 100

    # --- rede deterministica ---
    starts, fins = build_schedule(inicio, dur_base)
    fim_proj = max(fins.values())

    # --- XML ---
    ET.register_namespace("", NS)
    root = ET.Element(f"{{{NS}}}Project")
    el(root, "Name", nome)
    el(root, "Title", nome)
    el(root, "StartDate", f"{inicio.isoformat()}T08:00:00")
    el(root, "FinishDate", f"{fim_proj.isoformat()}T17:00:00")
    el(root, "ScheduleFromStart", "1")
    el(root, "MinutesPerDay", "480")
    el(root, "MinutesPerWeek", "2400")
    el(root, "DaysPerMonth", "20")
    el(root, "DefaultTaskType", "0")
    el(root, "Comments",
       f"Gerado por script. Monte Carlo ({dur_sims.size:,} sims): "
       f"P50 = {p50:.1f} d | P90 = {p90:.1f} d | "
       f"P(terminar <= {prazo} d) = {prob:.1f}%. "
       f"Duracao base = estimativa {'P50' if dur_base is not None else 'provavel'}. "
       f"Text1/2/3 = Otimista/Provavel/Pessimista (dias).")

    tasks_el = ET.SubElement(root, f"{{{NS}}}Tasks")

    # tarefa resumo (UID 1)
    add_task(tasks_el, uid=1, id_=1, name=nome, start=inicio, finish=fim_proj,
             dur_dias=(fim_proj - inicio).days, deps_uids=[], pontos=None,
             summary=True, wbs="1",
             notes="Tarefa resumo gerada automaticamente.")

    # tarefas (UID 2..N+1)
    idx = {t[0]: i for i, t in enumerate(TAREFAS)}
    uid = {t[0]: i + 2 for i, t in enumerate(TAREFAS)}
    for i, (tid, desc, deps, (o, m, p)) in enumerate(TAREFAS):
        add_task(tasks_el, uid=uid[tid], id_=i + 2, name=desc,
                 start=starts[tid], finish=fins[tid],
                 dur_dias=dur_base[tid],
                 deps_uids=[uid[d] for d in deps],
                 pontos=(o, m, p), summary=False, wbs=f"1.{i + 1}",
                 notes=f"Estimativas (dias): otimista {o} | provavel {m} | "
                       f"pessimista {p}. Criticidade no MC: {crit[i]:.0f}%")

    # campos customizados Text1/2/3 (alias)
    ea_proj = ET.SubElement(root, f"{{{NS}}}ExtendedAttributes")
    for fid, campo, alias in ((FIELD_TEXT1, "Text1", "Otimista (dias)"),
                              (FIELD_TEXT2, "Text2", "Provavel (dias)"),
                              (FIELD_TEXT3, "Text3", "Pessimista (dias)")):
        e = ET.SubElement(ea_proj, f"{{{NS}}}ExtendedAttribute")
        el(e, "FieldID", str(fid))
        el(e, "FieldName", campo)
        el(e, "Alias", alias)

    ET.indent(root, space="  ")
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + \
              ET.tostring(root, encoding="unicode")
    with open(saida, "w", encoding="utf-8") as f:
        f.write(xml_str)

    # --- relatorio ---
    print(f"Arquivo gerado: {saida}")
    print(f"  Projeto      : {nome}")
    print(f"  Inicio/Fim   : {inicio} -> {fim_proj} "
          f"({(fim_proj - inicio).days} dias uteis)")
    print(f"  Tarefas      : {len(TAREFAS)} + resumo, vinculos FS")
    print(f"  Duracao base : estimativa {dur_base[TAREFAS[0][0]]}d "
          f"(valores: {sorted(set(dur_base.values()))} dias por tarefa)")
    print(f"  MC embutido  : P50={p50:.1f}d | P90={p90:.1f}d | "
          f"P(<= {prazo}d) = {prob:.1f}%")
    print(f"  Campos       : Text1/2/3 = Otimista/Provavel/Pessimista")
    print()
    print("Para abrir no MS Project: Arquivo > Abrir > selecionar o .xml")
    print("(o Project converte para .mpp ao salvar)")


def main():
    ap = argparse.ArgumentParser(
        description="Gera cronograma MS Project (Project XML) a partir "
                    "da rede de tarefas do mc_projetos.py")
    ap.add_argument("--inicio", help="data de inicio ISO (YYYY-MM-DD); "
                                     "default: proxima segunda-feira")
    ap.add_argument("--saida", default=os.path.join(
        SCRIPT_DIR, "cronograma_trocadores.xml"))
    ap.add_argument("--nome", default="Fabricacao 2 trocadores de calor - REPLAN (ASME)")
    ap.add_argument("--prazo", type=int, default=45,
                    help="prazo contratual em dias (so para o relatorio MC)")
    ap.add_argument("--base", choices=["provavel", "p50"], default="provavel",
                    help="duracao base: estimativa provavel ou P50 do MC")
    args = ap.parse_args()

    inicio = date.fromisoformat(args.inicio) if args.inicio else next_monday(date.today())

    if args.base == "p50":
        dur_base = {tid: math.ceil(np.percentile(
            RNG.triangular(o, m, p, size=20000), 50))
            for tid, _, _, (o, m, p) in TAREFAS}
    else:
        dur_base = {tid: m for tid, _, _, (_, m, _) in TAREFAS}

    gerar_xml(inicio, dur_base, args.nome, args.prazo, args.saida)


if __name__ == "__main__":
    main()
