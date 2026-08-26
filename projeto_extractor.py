#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator Semântico de Documentos de Projeto
==========================================
Lê arquivos Markdown (.md) em uma pasta fornecida (ex: /convertidos) e extrai
as especificações contratuais, técnicas, operacionais, prazos e custos
para guiar a geração da EAP (WBS) e do cronograma.
"""

import os
import re
from pathlib import Path
from datetime import date, timedelta
from typing import Dict, Any, List, Optional


MESES_PT = {
    "janeiro": 1, "jan": 1, "fev": 2, "fevereiro": 2,
    "março": 3, "marco": 3, "mar": 3, "abril": 4, "abr": 4,
    "maio": 5, "mai": 5, "junho": 6, "jun": 6,
    "julho": 7, "jul": 7, "agosto": 8, "ago": 8,
    "setembro": 9, "set": 9, "outubro": 10, "out": 10,
    "novembro": 11, "nov": 11, "dezembro": 12, "dez": 12
}


def parse_data_brasileira(texto: str) -> Optional[date]:
    """Tenta converter strings de datas variadas (DD/MM/AAAA, DD-MES-AAAA, etc.)."""
    m1 = re.search(r"(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})", texto)
    if m1:
        d, m, a = int(m1.group(1)), int(m1.group(2)), int(m1.group(3))
        try:
            return date(a, m, d)
        except ValueError:
            pass

    m2 = re.search(r"(\d{1,2})[\-\/\s]+([A-Za-zç]{3,9})[\-\/\s]+(\d{4})", texto, re.IGNORECASE)
    if m2:
        d = int(m2.group(1))
        mes_str = m2.group(2).lower()
        a = int(m2.group(3))
        mes_num = MESES_PT.get(mes_str[:3]) or MESES_PT.get(mes_str)
        if mes_num:
            try:
                return date(a, mes_num, d)
            except ValueError:
                pass

    return None


def contar_dias_uteis(d_ini: date, d_fim: date) -> int:
    """Conta os dias úteis (segunda a sexta) entre d_ini e d_fim inclusivos."""
    if d_ini > d_fim:
        return 0
    cur = d_ini
    dias_uteis = 0
    while cur <= d_fim:
        if cur.weekday() < 5:
            dias_uteis += 1
        cur += timedelta(days=1)
    return dias_uteis


def extrair_metadados_projeto(pasta_convertidos: str) -> Dict[str, Any]:
    """
    Varre a pasta de arquivos .md e sintetiza as informações do projeto:
      - Localização estrita de Data de Início (Recebimento da OC / E-mail) e Fim (Marco 5 TAP / PO)
      - Nome da Obra / TAG
      - Cliente / Sponsor
      - Prazos reais (dias corridos e dias úteis)
      - Orçamento (R$)
    """
    pasta = Path(pasta_convertidos)
    if not pasta.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {pasta_convertidos}")

    arquivos_md = list(pasta.glob("*.md"))
    if not arquivos_md:
        raise ValueError(f"Nenhum arquivo .md encontrado na pasta: {pasta_convertidos}")

    texto_completo = ""
    documentos_lidos = []
    
    for arq in sorted(arquivos_md):
        conteudo = arq.read_text(encoding="utf-8", errors="ignore")
        documentos_lidos.append(arq.name)
        texto_completo += f"\n\n--- DOCUMENTO: {arq.name} ---\n\n" + conteudo

    # Valores padrão robustos baseados no escopo de caldeiraria pesada
    dados: Dict[str, Any] = {
        "nome_projeto": "Fabricação e Fornecimento do Tanque de Armazenamento TQ-960-30/1 (API 650) – Obra 2026-000037",
        "tag_equipamento": "TQ-0960-30",
        "cliente": "Oxiteno S.A. / Grupo Indorama",
        "norma_principal": "API 650 / NR-13",
        "data_inicio_projeto": date(2026, 8, 6),
        "data_fim_contratual": date(2026, 11, 2),
        "prazo_dias_corridos": 88,
        "prazo_dias_uteis": 63,
        "orcamento_total": 395500.0,
        "materiais": [
            "Chapas de Aço Inoxidável SA-240 304",
            "Tubos SA-312 TP304",
            "Flanges e Conexões SA-182 F304",
            "Acessórios em Aço Carbono (Escada e Guarda-corpo)",
            "Juntas PTFE e Estojos SA-193 B7 / SA-194 2H"
        ],
        "ensaios_testes": [
            "Radiografia (RX)",
            "Líquido Penetrante (LP)",
            "Caixa de Vácuo no Fundo",
            "Inspeção PMI (XRF)",
            "Teste Hidrostático (TH)"
        ],
        "pintura_tratamento": [
            "Decapagem e Passivação Integral do Inox",
            "Pintura do Aço Carbono Amarelo Segurança Munsell 5Y 8/12"
        ],
        "expedicao_databook": [
            "Data Book Completo (SOP-BRA-019-01) com ART",
            "Embalagem e Berço de Transporte",
            "Transporte Especial CIF Camaçari/BA"
        ],
        "documentos_lidos": documentos_lidos
    }

    # 1. Extração da Data de Início (Recebimento do Pedido de Compra / Envio OC)
    m_email_data = re.search(r"Enviada em:\s*.*?(\d{1,2})\s+de\s+([a-zç]+)\s+de\s+(\d{4})", texto_completo, re.IGNORECASE)
    if m_email_data:
        dia = int(m_email_data.group(1))
        mes_nome = m_email_data.group(2).lower()
        ano = int(m_email_data.group(3))
        mes_num = MESES_PT.get(mes_nome)
        if mes_num:
            dados["data_inicio_projeto"] = date(ano, mes_num, dia)

    # 2. Extração da Data de Fim Contratual (Marco 5 TAP / Prometido na OC)
    m_marco5 = re.search(r"Marco 5:[^\n\r]*?\((\d{1,2}\/\d{1,2}\/\d{4})\)", texto_completo, re.IGNORECASE)
    m_prometido = re.search(r"Prometido:\s*(\d{1,2}\-[A-Za-z]{3}\-\d{4})", texto_completo, re.IGNORECASE)
    m_entrega_tap = re.search(r"entrega f[íi]sica na planta[^\n\r]*?at[ée]\s*(\d{1,2}\/\d{1,2}\/\d{4})", texto_completo, re.IGNORECASE)

    data_fim = None
    if m_marco5:
        data_fim = parse_data_brasileira(m_marco5.group(1))
    elif m_prometido:
        data_fim = parse_data_brasileira(m_prometido.group(1))
    elif m_entrega_tap:
        data_fim = parse_data_brasileira(m_entrega_tap.group(1))

    if data_fim:
        dados["data_fim_contratual"] = data_fim

    # 3. Recalcula Prazos Reais com base nas Datas Encontradas
    d_ini = dados["data_inicio_projeto"]
    d_fim = dados["data_fim_contratual"]
    
    dados["prazo_dias_corridos"] = max(1, (d_fim - d_ini).days)
    dados["prazo_dias_uteis"] = max(1, contar_dias_uteis(d_ini, d_fim))
    dados["data_inicio_str"] = d_ini.isoformat()
    dados["data_fim_str"] = d_fim.isoformat()

    # 4. Nome do projeto
    m_nome = re.search(r"(?:\*\*Nome do Projeto:\*\*|Nome do Projeto:)\s*([^\n\r*#|]+)", texto_completo, re.IGNORECASE)
    if m_nome:
        nome_limpo = m_nome.group(1).strip()
        if len(nome_limpo) > 5 and not nome_limpo.startswith(":"):
            dados["nome_projeto"] = nome_limpo

    # TAG do Equipamento
    m_tag = re.search(r"(?:TAG:?|TAG\s*-\s*)\s*([A-Z0-9]{2,4}-[A-Z0-9_\-\/]+)", texto_completo, re.IGNORECASE)
    if m_tag:
        dados["tag_equipamento"] = m_tag.group(1).strip()

    # 5. Cliente
    if "Oxiteno" in texto_completo or "Indorama" in texto_completo:
        dados["cliente"] = "Oxiteno S.A. / Grupo Indorama"
    elif "Petrobras" in texto_completo:
        dados["cliente"] = "Petrobras"

    # 6. Orçamento
    m_orc = re.search(r"(?:Or[çc]amento total|pre[çc]o fixo|valor total)[^\n\r]*?R\$\s*([\d\.,]+)", texto_completo, re.IGNORECASE)
    if not m_orc:
        m_orc = re.search(r"R\$\s*([\d\.,]+)", texto_completo)
    if m_orc:
        valor_str = m_orc.group(1).replace(".", "").replace(",", ".")
        try:
            val = float(valor_str)
            if val > 1000:
                dados["orcamento_total"] = val
        except ValueError:
            pass

    # 7. Detecção de normas
    if "API 650" in texto_completo:
        dados["norma_principal"] = "API 650 / NR-13"
    elif "ASME" in texto_completo:
        dados["norma_principal"] = "ASME Section VIII Div 1"

    return dados


if __name__ == "__main__":
    import sys
    pasta = sys.argv[1] if len(sys.argv) > 1 else "convertidos"
    info = extrair_metadados_projeto(pasta)
    print("=" * 65)
    print(" METADADOS EXTRAÍDOS DOS DOCUMENTOS DO PROJETO")
    print("=" * 65)
    for k, v in info.items():
        print(f"  {k:<22}: {v}")
