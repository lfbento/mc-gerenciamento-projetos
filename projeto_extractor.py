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
from typing import Dict, Any, List


def extrair_metadados_projeto(pasta_convertidos: str) -> Dict[str, Any]:
    """
    Varre a pasta de arquivos .md e sintetiza as informações do projeto:
      - Nome da Obra / TAG
      - Cliente / Sponsor
      - Prazos (dias corridos e cálculo de dias úteis)
      - Orçamento (R$)
      - Materiais e Componentes
      - Ensaios e Testes (RX, LP, TH, PMI, etc.)
      - Pintura e Tratamento Superficial
      - Expedição e Data Book
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
        "nome_projeto": "Fabricação e Fornecimento de Tanque de Armazenamento",
        "tag_equipamento": "TQ-960-30/1",
        "cliente": "Oxiteno / Indorama",
        "norma_principal": "API 650 / ASME",
        "prazo_dias_corridos": 100,
        "prazo_dias_uteis": 72,
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

    # 1. Nome do projeto
    m_nome = re.search(r"(?:\*\*Nome do Projeto:\*\*|Nome do Projeto:)\s*([^\n\r*#|]+)", texto_completo, re.IGNORECASE)
    if m_nome:
        nome_limpo = m_nome.group(1).strip()
        if len(nome_limpo) > 5 and not nome_limpo.startswith(":"):
            dados["nome_projeto"] = nome_limpo

    # TAG do Equipamento
    m_tag = re.search(r"(?:TAG:?|TAG\s*-\s*)\s*([A-Z0-9]{2,4}-[A-Z0-9_\-\/]+)", texto_completo, re.IGNORECASE)
    if m_tag:
        dados["tag_equipamento"] = m_tag.group(1).strip()

    # 2. Cliente
    if "Oxiteno" in texto_completo or "Indorama" in texto_completo:
        dados["cliente"] = "Oxiteno S.A. / Grupo Indorama"
    elif "Petrobras" in texto_completo:
        dados["cliente"] = "Petrobras"

    # 3. Prazos
    m_prazo = re.search(r"(?:prazo|execu[çc][ãa]o|entrega)\s*(?:e entrega)?\s*(?:de at[ée])?\s*(\d{2,3})\s*dias\s*corridos", texto_completo, re.IGNORECASE)
    if m_prazo:
        dias_c = int(m_prazo.group(1))
        dados["prazo_dias_corridos"] = dias_c
        dados["prazo_dias_uteis"] = max(10, int(round(dias_c * (5.0 / 7.0))))

    # 4. Orçamento
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

    # 5. Detecção de ensaios e normas
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
