#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Inteligente: Documentos -> EAP/WBS Ponderada -> Monte Carlo -> MS Project XML
====================================================================================
Orquestrador central do fluxo de automação de planejamento e análise de riscos.

Uso:
  python main.py --pasta convertidos/ --saida exemplos/cronograma_tanque_tq960.xml
"""

import argparse
import os
import sys
from datetime import date
from pathlib import Path

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Garante compatibilidade UTF-8 no console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from projeto_extractor import extrair_metadados_projeto
from wbs_scheduler import gerar_rede_wbs, PESOS_WBS
from mc_engine import simular_monte_carlo_rede
from msproject_exporter import exportar_msproject_xml, next_monday
from relatorio_pdf import gerar_relatorio_pdf_diretoria


def gerar_relatorio_markdown(
    metadados: dict,
    rede_wbs: dict,
    resultado_mc: dict,
    caminho_xml: str,
    caminho_relatorio: str
) -> str:
    """Gera um relatório executivo em Markdown detalhando o planejamento e a análise de riscos."""
    d = resultado_mc["duracao"]
    c = resultado_mc["custo"]
    g = resultado_mc["graficos"]

    linhas = [
        f"# 📊 Relatório Executivo de Planejamento & Análise de Riscos (Monte Carlo)",
        f"",
        f"**Projeto:** {rede_wbs['projeto']}  ",
        f"**TAG do Equipamento:** `{rede_wbs['tag']}` | **Cliente:** `{rede_wbs['cliente']}`  ",
        f"**Data da Análise:** {date.today().strftime('%d/%m/%Y')} | **Normas:** `{metadados.get('norma_principal', 'API 650 / ASME')}`  ",
        f"",
        f"---",
        f"",
        f"## 1. Resumo Executivo e Decisões de Gestão",
        f"",
        f"| Métrica de Cronograma | Valor Calculado | Diretriz de Ação |",
        f"| :--- | :---: | :--- |",
        f"| **Prazo Contratual Alvo** | **{d['prazo_alvo']:.0f} dias úteis** ({rede_wbs['prazo_total_corridos']} dias corridos) | Meta base para medição |",
        f"| **Duração Mais Provável (P50)** | **{d['p50']:.1f} dias úteis** | Duração central da fabricação |",
        f"| **Duração de Segurança (P90)** | **{d['p90']:.1f} dias úteis** | Data segura de entrega operacional |",
        f"| **Probabilidade de Cumprir Prazo** | **{d['prob_sucesso_prazo']:.1f}%** | {'🟢 Baixo Risco' if d['prob_sucesso_prazo'] >= 80 else '🟡 Risco Moderado' if d['prob_sucesso_prazo'] >= 60 else '🔴 Alto Risco de Atraso'} |",
        f"| **Buffer de Cronograma Sugerido (P90 − P50)** | **{d['buffer_sugerido']:.1f} dias úteis** | Inserir antes da expedição CIF |",
        f"",
        f"| Métrica Financeira | Valor Calculado | Diretriz de Ação |",
        f"| :--- | :---: | :--- |",
        f"| **Orçamento Base Aprovado** | **R$ {c['orcamento_base']:,.2f}** | Preço de venda / baseline |",
        f"| **Custo Mais Provável (P50)** | **R$ {c['p50']:,.2f}** | Custo operacional estimado |",
        f"| **Contingência Sugerida (P80 − P50)** | **R$ {c['contingencia_sugerida']:,.2f}** | Reserva gerencial de contingência |",
        f"| **Probabilidade de Estouro Orçamentário** | **{c['prob_estouro_orcamento']:.1f}%** | Nível de exposição a variações de matéria-prima |",
        f"",
        f"---",
        f"",
        f"## 2. Estrutura Analítica do Projeto (EAP / WBS Ponderada)",
        f"",
        f"Distribuição do tempo global do projeto conforme pesos oficiais dos pacotes de serviço:",
        f"",
        f"| Código | Pacote de Serviço | Peso (%) | Duração Alocada | Atividades Chave |",
        f"| :---: | :--- | :---: | :---: | :--- |"
    ]

    for pkg in rede_wbs["pacotes"]:
        nomes_t = ", ".join([t["nome"][:35] + "..." for t in pkg["tarefas"][:2]])
        linhas.append(
            f"| `{pkg['codigo']}` | **{pkg['nome']}** | **{pkg['peso_percentual']:.0f}%** | ~{pkg['duracao_alocada']} dias úteis | {len(pkg['tarefas'])} tarefas ({nomes_t}) |"
        )

    linhas.extend([
        f"",
        f"---",
        f"",
        f"## 3. Matriz de Criticidade de Atividades (Top Gargalos)",
        f"",
        f"Atividades com maior probabilidade de travar o cronograma global (presença no Caminho Crítico durante as 20.000 iterações):",
        f"",
        f"| WBS | Atividade | 3 Pontos (O, M, P) | Índice de Criticidade | Nível de Atenção |",
        f"| :---: | :--- | :---: | :---: | :--- |"
    ])

    for t in resultado_mc["tarefas_ordenadas_criticidade"][:10]:
        crit = t["indice_criticidade"]
        status = "🔴 Crítica (100%)" if crit >= 90 else "🟡 Moderada" if crit >= 30 else "🟢 Baixa"
        linhas.append(
            f"| `{t['wbs']}` | {t['nome']} | `({t['otimista']}, {t['provavel']}, {t['pessimista']}) d` | **{crit:.1f}%** | {status} |"
        )

    linhas.extend([
        f"",
        f"---",
        f"",
        f"## 4. Integração e Entregáveis Gerados",
        f"",
        f"- **Arquivo MS Project XML:** [`{os.path.basename(caminho_xml)}`](file:///{os.path.abspath(caminho_xml).replace(chr(92), '/')}): Compatível com MS Project 2010+ com árvore hierárquica WBS e campos Text1..Text5.",
        f"- **Histograma de Cronograma:** `assets/mc_cronograma_wbs.png`",
        f"- **Histograma de Custos:** `assets/mc_custo_wbs.png`",
        f"",
        f"---",
        f"*Relatório gerado automaticamente pelo pipeline inteligente de cronograma e Monte Carlo.*"
    ])

    relatorio_txt = "\n".join(linhas)
    with open(caminho_relatorio, "w", encoding="utf-8") as f:
        f.write(relatorio_txt)

    return caminho_relatorio


def executar_pipeline(
    pasta_md: str = "convertidos",
    caminho_saida_xml: str = None,
    caminho_relatorio: str = None,
    caminho_pdf: str = None,
    data_inicio_str: str = None,
    n_simulacoes: int = 20000,
    base_duracao: str = "provavel"
):
    print("=" * 75)
    print("🚀 INICIANDO PIPELINE: MD -> EAP PONDERADA -> MONTE CARLO -> MS PROJECT & PDF")
    print("=" * 75)

    pasta_dir = Path(pasta_md)
    if not pasta_dir.exists():
        raise FileNotFoundError(f"Pasta de documentos não encontrada: {pasta_md}")

    # 1. Leitura e Extração Semântica dos MDs
    print(f"\n📂 1. Lendo e analisando documentos da pasta: '{pasta_dir}'...")
    metadados = extrair_metadados_projeto(str(pasta_dir))
    print(f"   ✓ Projeto Identificado : {metadados['nome_projeto']}")
    print(f"   ✓ TAG do Equipamento   : {metadados['tag_equipamento']}")
    print(f"   ✓ Cliente / Norma      : {metadados['cliente']} | {metadados['norma_principal']}")
    print(f"   ✓ Prazo Contratual     : {metadados['prazo_dias_corridos']} dias corridos (~{metadados['prazo_dias_uteis']} dias úteis)")
    print(f"   ✓ Orçamento Base       : R$ {metadados['orcamento_total']:,.2f}")
    print(f"   ✓ Documentos Lidos ({len(metadados['documentos_lidos'])}): {', '.join(metadados['documentos_lidos'][:3])}...")

    # Definição dos caminhos de saída dentro da própria pasta informada
    tag_clean = "".join([c if c.isalnum() or c in "-_" else "_" for c in metadados["tag_equipamento"]]).strip("_").lower()
    pasta_assets = pasta_dir / "assets"
    
    if caminho_saida_xml is None:
        caminho_saida_xml = str(pasta_dir / f"cronograma_{tag_clean}.xml")
    if caminho_pdf is None:
        caminho_pdf = str(pasta_dir / "RELATORIO_DIRETORIA_MONTE_CARLO.pdf")
    if caminho_relatorio is None:
        caminho_relatorio = str(pasta_dir / "RELATORIO_PROJETO_MC.md")

    # 2. Geração da Rede WBS Ponderada
    print(f"\n🏗️  2. Gerando árvore WBS com pesos oficiais (2%, 20%, 30%, 40%, 7%, 1%)...")
    rede_wbs = gerar_rede_wbs(metadados)
    total_tarefas = len(rede_wbs["tarefas"])
    print(f"   ✓ Total de Pacotes EAP : {len(rede_wbs['pacotes'])}")
    print(f"   ✓ Total de Atividades  : {total_tarefas} tarefas com estimativas (O, M, P)")

    # 3. Simulação de Monte Carlo & Comparativo de Cenários
    print(f"\n🎲 3. Executando Simulação de Monte Carlo & Comparativo de Cenários ({n_simulacoes:,} iterações)...")
    res_mc = simular_monte_carlo_rede(rede_wbs, n_sim=n_simulacoes, plot=True, pasta_assets=str(pasta_assets))
    d_inercial = res_mc["duracao"]
    d_mitigado = res_mc["cenario_mitigado"]
    c = res_mc["custo"]

    print(f"\n   ┌── CENÁRIO 1: INERCIAL (SEM MITIGAÇÃO) ──────────────┐")
    print(f"   │ Duração P50 / P90    : {d_inercial['p50']:.1f} dias / {d_inercial['p90']:.1f} dias")
    print(f"   │ P(cumprir prazo)     : {d_inercial['prob_sucesso_prazo']:.1f}% (🔴 Alto Risco de Atraso)")
    print(f"   │ Atraso projetado     : +{d_inercial['p50'] - d_inercial['prazo_alvo']:.1f} dias úteis")
    print(f"   └── CENÁRIO 2: OTIMIZADO COM PLANO DE AÇÃO ────────────┘")
    print(f"   │ Duração P50 / P90    : {d_mitigado['p50']:.1f} dias / {d_mitigado['p90']:.1f} dias")
    print(f"   │ P(cumprir prazo)     : {d_mitigado['prob_sucesso_prazo']:.1f}% (🟢 Baixo Risco / Protegido)")
    print(f"   │ Buffer Disponível    : {d_mitigado['buffer_disponivel']:.1f} dias úteis de margem")
    print(f"   └──────────────────────────────────────────────────────┘")
    print(f"   ✓ Custo P50 / P80      : R$ {c['p50']/1000.0:.1f}k / R$ {c['p80']/1000.0:.1f}k")
    print(f"   ✓ Contingência Custo   : R$ {c['contingencia_sugerida']/1000.0:.1f}k")

    # 4. Exportação MS Project XML (MSPDI)
    if data_inicio_str:
        inicio = date.fromisoformat(data_inicio_str)
    else:
        inicio = next_monday(date.today())

    print(f"\n📄 4. Exportando para Microsoft Project XML (MSPDI)...")
    xml_path = exportar_msproject_xml(rede_wbs, res_mc, inicio, caminho_saida_xml, base_duracao)
    print(f"   ✓ Arquivo XML Gerado   : {xml_path}")

    # 5. Geração do Relatório Executivo em PDF para a Diretoria
    print(f"\n📑 5. Gerando Relatório Executivo para a Diretoria em PDF...")
    pdf_out = gerar_relatorio_pdf_diretoria(metadados, rede_wbs, res_mc, caminho_pdf)
    print(f"   ✓ Relatório PDF Criado : {pdf_out}")

    # 6. Geração do Relatório Markdown
    print(f"\n📝 6. Gerando relatório executivo Markdown...")
    rel_path = gerar_relatorio_markdown(metadados, rede_wbs, res_mc, xml_path, caminho_relatorio)
    print(f"   ✓ Relatório Criado     : {rel_path}")

    print("\n" + "=" * 75)
    print(f"🎉 PIPELINE CONCLUÍDO! TODOS OS ARTEFATOS GRAVADOS EM: {pasta_dir.resolve()}")
    print("=" * 75)


def main():
    parser = argparse.ArgumentParser(description="Pipeline Inteligente de Cronograma e Monte Carlo para MS Project e PDF da Diretoria")
    parser.add_argument("--pasta", "-p", default="convertidos", help="Pasta com os arquivos .md do projeto (onde serão gravados todos os artefatos)")
    parser.add_argument("--saida", "-o", default=None, help="Caminho customizado do arquivo XML de saída (padrão: dentro da pasta do projeto)")
    parser.add_argument("--pdf", default=None, help="Caminho customizado do relatório PDF para a Diretoria (padrão: dentro da pasta do projeto)")
    parser.add_argument("--relatorio", "-r", default=None, help="Caminho customizado do relatório Markdown (padrão: dentro da pasta do projeto)")
    parser.add_argument("--inicio", "-i", default=None, help="Data de início (YYYY-MM-DD)")
    parser.add_argument("--iteracoes", "-n", type=int, default=20000, help="Número de iterações de Monte Carlo")
    parser.add_argument("--base", choices=["provavel", "p50", "otimista", "pessimista"], default="provavel", help="Base de duração das tarefas no MS Project")

    args = parser.parse_args()
    executar_pipeline(
        pasta_md=args.pasta,
        caminho_saida_xml=args.saida,
        caminho_relatorio=args.relatorio,
        caminho_pdf=args.pdf,
        data_inicio_str=args.inicio,
        n_simulacoes=args.iteracoes,
        base_duracao=args.base
    )


if __name__ == "__main__":
    main()
