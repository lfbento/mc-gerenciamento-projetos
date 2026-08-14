#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Puxa tarefas de um projeto do OpenProject via API v3 e gera
Project XML (MSPDI) para abrir no MS Project.

Uso:
  python3 openproject_to_xml.py --url http://192.168.100.65:8080 \
          --key SUA_API_KEY --projeto 1
  python3 openproject_to_xml.py --projetos        # lista projetos
  python3 openproject_to_xml.py --mock            # testa sem servidor

Autenticacao: API key do OpenProject (Conta -> Chaves de API).
Alternativa: export OPENPROJECT_URL / OPENPROJECT_KEY.

Limitacoes honestas:
  - Estimativa de 3 pontos nao existe no OpenProject nativo: usa
    estimatedTime como "provavel" e deriva otimista/pessimista
    (0.7x / 1.6x). Se o projeto tiver campos customizados
    Otimista/Provavel/Pessimista, use --campo-o/--campo-m/--campo-p.
  - Vinculos de precedencia nao sao expostos na API v3 sem consultar
    relacoes por pacote; por padrao as tarefas sao encadeadas em FS
    na ordem de exibicao (simplificacao documentada).
"""

import argparse
import base64
import json
import math
import os
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerar_msproject import NS, el, add_workdays  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HORAS_DIA = 8


def api_get(url, key, path):
    req = urllib.request.Request(
        f"{url}/api/v3{path}",
        headers={
            "Authorization": "Basic " + base64.b64encode(
                f"apikey:{key}".encode()).decode(),
            "Accept": "application/json",
        })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def listar_projetos(url, key):
    dados = api_get(url, key, "/projects")
    return [(p["id"], p["name"]) for p in dados.get("_embedded", {}).get("elements", [])]


def buscar_work_packages(url, key, projeto_id):
    """Puxa todos os work packages do projeto (com paginacao)."""
    wps, offset = [], 1
    filtro = json.dumps([{"project": {"operator": "=",
                                      "values": [str(projeto_id)]}}])
    while True:
        path = (f"/work_packages?filters={urllib.parse.quote(filtro)}"
                f"&pageSize=100&offset={offset}")
        dados = api_get(url, key, path)
        wps += dados.get("_embedded", {}).get("elements", [])
        total = dados.get("total", 0)
        if offset * 100 >= total:
            break
        offset += 1
    return wps


def extrair_estimativa(wp, campo_m):
    """Retorna dias (provavel) a partir de estimatedTime ou campo custom."""
    val = wp.get("estimatedTime")
    if not val:
        val = (wp.get("customField#{campo_m}") if campo_m else None)
    if not val:
        return 1
    # estimatedTime e em HORAS DE TRABALHO (PT40H = 40h = 5 dias uteis)
    return max(1, math.ceil(re_duracao_horas(val) / HORAS_DIA))


def re_duracao_horas(val):
    import re
    m = re.match(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?)?", val)
    dias = int(m.group(1) or 0) if m else 0
    horas = int(m.group(2) or 0) if m else 0
    mins = int(m.group(3) or 0) if m else 0
    return dias * HORAS_DIA + horas + mins / 60


def transformar(wps, campo_o=None, campo_m=None, campo_p=None):
    """work packages -> lista de dicts {nome, o, m, p, parent}."""
    tarefas = []
    for wp in wps:
        nome = wp.get("subject", "Sem nome")
        parent = None
        href = wp.get("_links", {}).get("parent", {}).get("href")
        if href:
            parent = href.rstrip("/").rsplit("/", 1)[-1]
        m = extrair_estimativa(wp, campo_m)
        if campo_o:
            o = max(1, int(wp.get(f"customField#{campo_o}", 1) or 1))
        else:
            o = max(1, round(m * 0.7))
        if campo_p:
            p = max(m + 1, int(wp.get(f"customField#{campo_p}", m + 1) or m + 1))
        else:
            p = max(m + 1, math.ceil(m * 1.6))
        tarefas.append({"nome": nome, "o": o, "m": m, "p": p, "parent": parent})
    return tarefas


def gerar_xml(tarefas, nome_projeto, inicio, saida):
    """tarefas -> Project XML (resumo + tarefas encadeadas em FS)."""
    import xml.etree.ElementTree as ET
    ET.register_namespace("", NS)
    root = ET.Element(f"{{{NS}}}Project")
    el(root, "Name", nome_projeto)
    el(root, "Title", nome_projeto)
    el(root, "StartDate", f"{inicio.isoformat()}T08:00:00")
    fim_proj = inicio
    for ta in tarefas:
        fim_proj = add_workdays(fim_proj, ta["m"])
    el(root, "FinishDate", f"{fim_proj.isoformat()}T17:00:00")
    el(root, "ScheduleFromStart", "1")
    el(root, "MinutesPerDay", "480")
    el(root, "MinutesPerWeek", "2400")
    el(root, "DaysPerMonth", "20")
    el(root, "DefaultTaskType", "0")
    el(root, "Comments",
       f"Gerado a partir do OpenProject (API v3). Duracao base = "
       f"estimatedTime (provavel); Otimista/Pessimista derivados "
       f"(0.7x/1.6x). Tarefas encadeadas em FS na ordem de exibicao.")

    tasks_el = ET.SubElement(root, f"{{{NS}}}Tasks")

    # resumo (UID 1)
    t = ET.SubElement(tasks_el, f"{{{NS}}}Task")
    el(t, "UID", "1")
    el(t, "ID", "1")
    el(t, "Name", nome_projeto)
    el(t, "Type", "0")
    el(t, "IsNull", "0")
    el(t, "OutlineLevel", "1")
    el(t, "Priority", "500")
    el(t, "Start", f"{inicio.isoformat()}T08:00:00")
    el(t, "Duration", "PT1H")
    el(t, "DurationFormat", "7")
    el(t, "Summary", "1")

    # tarefas encadeadas em FS
    prev_uid = None
    atual = inicio
    for i, ta in enumerate(tarefas):
        uid = i + 2
        fim = add_workdays(atual, ta["m"])
        t = ET.SubElement(tasks_el, f"{{{NS}}}Task")
        el(t, "UID", str(uid))
        el(t, "ID", str(uid))
        el(t, "Name", ta["nome"])
        el(t, "Type", "0")
        el(t, "IsNull", "0")
        el(t, "OutlineLevel", "3" if ta["parent"] else "2")
        el(t, "Priority", "500")
        el(t, "Start", f"{atual.isoformat()}T08:00:00")
        el(t, "Finish", f"{fim.isoformat()}T17:00:00")
        el(t, "Duration", f"PT{ta['m'] * HORAS_DIA}H")
        el(t, "DurationFormat", "7")
        el(t, "Summary", "0")
        if prev_uid is not None:
            pl = ET.SubElement(t, f"{{{NS}}}PredecessorLink")
            el(pl, "PredecessorUID", str(prev_uid))
            el(pl, "Type", "1")
            el(pl, "LinkLag", "0")
        for fid, v in ((188743731, ta["o"]), (188743732, ta["m"]),
                       (188743733, ta["p"])):
            ea = ET.SubElement(t, f"{{{NS}}}ExtendedAttribute")
            el(ea, "FieldID", str(fid))
            el(ea, "Value", str(v))
        el(t, "Notes", f"3 pontos (dias): otimista {ta['o']} | provavel "
                      f"{ta['m']} | pessimista {ta['p']}")
        prev_uid = uid
        atual = fim

    ET.indent(root, space="  ")
    with open(saida, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n' +
                ET.tostring(root, encoding="unicode"))
    print(f"Arquivo gerado: {saida}")
    print(f"  Projeto : {nome_projeto} | tarefas: {len(tarefas)}")
    print(f"  Inicio  : {inicio} -> fim previsto {atual} "
          f"({(atual - inicio).days} dias uteis)")


def mock_wps():
    return {
        "_embedded": {"elements": [
            {"id": 1, "subject": "Detalhamento / desenhos de fabricacao",
             "estimatedTime": "PT40H", "_links": {}},
            {"id": 2, "subject": "Compra de materiais (casco, espelhos, tubos)",
             "estimatedTime": "PT80H", "_links": {}},
            {"id": 3, "subject": "Corte e chanfro das chapas",
             "estimatedTime": "PT32H", "_links": {}},
            {"id": 4, "subject": "Montagem do feixe tubular (expansao)",
             "estimatedTime": "PT48H",
             "_links": {"parent": {"href": "/api/v3/work_packages/1"}}},
            {"id": 5, "subject": "Soldagem das juntas do casco",
             "estimatedTime": "PT32H", "_links": {}},
            {"id": 6, "subject": "Teste hidrostatico + inspecao",
             "estimatedTime": "PT16H", "_links": {}},
        ]},
        "total": 6,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=os.environ.get("OPENPROJECT_URL"),
                    help="URL do OpenProject (ex: http://192.168.100.65:8080)")
    ap.add_argument("--key", default=os.environ.get("OPENPROJECT_KEY"),
                    help="API key do OpenProject (ou env OPENPROJECT_KEY)")
    ap.add_argument("--projeto", type=int, help="ID do projeto no OpenProject")
    ap.add_argument("--projetos", action="store_true", help="lista projetos")
    ap.add_argument("--mock", action="store_true", help="usa dados de exemplo")
    ap.add_argument("--inicio", help="data de inicio ISO (default: hoje)")
    ap.add_argument("--saida", default=os.path.join(SCRIPT_DIR,
                                                    "openproject_cronograma.xml"))
    ap.add_argument("--campo-o", type=int, help="ID do campo custom 'Otimista'")
    ap.add_argument("--campo-m", type=int, help="ID do campo custom 'Provavel'")
    ap.add_argument("--campo-p", type=int, help="ID do campo custom 'Pessimista'")
    args = ap.parse_args()

    if args.mock:
        wps = mock_wps()["_embedded"]["elements"]
        nome = "Projeto EXEMPLO (mock OpenProject)"
    else:
        if not args.url or not args.key:
            ap.error("informe --url e --key (ou env OPENPROJECT_URL/KEY); "
                     "ou use --mock")
        if args.projetos:
            for pid, nome in listar_projetos(args.url, args.key):
                print(f"  {pid}: {nome}")
            return
        if not args.projeto:
            ap.error("informe --projeto <id> (ou use --projetos para listar)")
        wps = buscar_work_packages(args.url, args.key, args.projeto)
        nome = f"OpenProject projeto {args.projeto}"

    inicio = date.fromisoformat(args.inicio) if args.inicio else date.today()
    tarefas = transformar(wps, args.campo_o, args.campo_m, args.campo_p)
    gerar_xml(tarefas, nome, inicio, args.saida)


if __name__ == "__main__":
    main()
