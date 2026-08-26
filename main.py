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
from resource_allocator import dimensionar_recursos_tarefas, gerar_histograma_recursos_temporal


def gerar_relatorio_markdown(
    metadados: dict,
    rede_wbs: dict,
    resultado_mc: dict,
    caminho_xml: str,
    caminho_relatorio: str,
    metricas_recursos: dict = None
) -> str:
    """Gera um relatório executivo em Markdown detalhando o planejamento, a análise MCMC e alocação de recursos."""
    d_iner = resultado_mc["duracao"]
    d_mit = resultado_mc["cenario_mitigado"]
    c = resultado_mc["custo"]
    g = resultado_mc["graficos"]
    prazo_nom = float(d_iner.get("prazo_alvo", 71.0))

    linhas = [
        f"# 📊 Relatório Executivo de Planejamento & Análise de Riscos (MCMC & Recursos)",
        f"",
        f"**Projeto:** {rede_wbs['projeto']}  ",
        f"**TAG do Equipamento:** `{rede_wbs['tag']}` | **Cliente:** `{rede_wbs['cliente']}`  ",
        f"**Data da Análise:** {date.today().strftime('%d/%m/%Y')} | **Normas:** `{metadados.get('norma_principal', 'API 650 / ASME')}`  ",
        f"",
        f"---",
        f"",
        f"## 1. Cards de Governança de Prazos (Modelagem MCMC)",
        f"",
        f"| PRAZO NOMINAL (CPM) | PREVISÃO MEDIANA (P50) | ALVO GERENCIAL (P85) | NÍVEL CONSERVADOR (P95) |",
        f"| :---: | :---: | :---: | :---: |",
        f"| **{prazo_nom:.0f} dias úteis**<br/>(Soma teórica determinística) | **{d_mit['p50']:.1f} dias úteis**<br/>(Meta de chão de fábrica) | **{d_mit['p85']:.1f} dias úteis**<br/>(Buffer recomendado: +{d_mit['buffer_p85_p50']:.1f}d) | **{d_mit['p95']:.1f} dias úteis**<br/>(Buffer de segurança: +{d_mit['buffer_p95_p50']:.1f}d) |",
        f"",
        f"---",
        f"",
        f"## 2. Quadro de Governança e Perfis de Decisão (Inercial vs. Mitigado)",
        f"",
        f"| Métrica de Cronograma | Prazo Estimado | Buffer Adicional | Prob. Cumprimento | Perfil de Governança Indicado |",
        f"| :--- | :---: | :---: | :---: | :--- |",
        f"| **Baseline CPM (Nominal)** | **{prazo_nom:.1f} dias** | +0.0 d | **< 0.1%** | 🔴 **Risco Inaceitável** (Atraso contratual quase garantido) |",
        f"| **Mediana Estocástica (P50)** | **{d_mit['p50']:.1f} dias** | +0.0 d (base) | **50.0%** | 🟡 **Planejamento Interno** (Meta operacional da fábrica) |",
        f"| **Alvo Recomendado (P85)** | **{d_mit['p85']:.1f} dias** | **+{d_mit['buffer_p85_p50']:.1f} d** | 🟢 **85.0%** | 🏆 **Padrão Ouro** para contratos comerciais e SLAs |",
        f"| **Buffer Conservador (P95)** | **{d_mit['p95']:.1f} dias** | **+{d_mit['buffer_p95_p50']:.1f} d** | 🟢 **95.0%** | 🛡️ **Missão Crítica** / Multas rescisórias severas |",
        f"",
        f"---",
        f"",
        f"## 3. Estrutura Analítica do Projeto (EAP / WBS Ponderada)",
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

    if metricas_recursos and "recursos_detalhados" in metricas_recursos:
        linhas.extend([
            f"",
            f"---",
            f"",
            f"## 4. Dimensionamento de Mão de Obra e Alocação de Recursos (Storm / SENAI)",
            f"",
            f"| Especialidade / Função | Categoria | HH Total | Taxa Horária | Custo Total de M.O. |",
            f"| :--- | :---: | :---: | :---: | :---: |"
        ])
        for r in metricas_recursos["recursos_detalhados"]:
            linhas.append(
                f"| **{r['codigo']}** - {r['nome']} | {r['categoria']} | {r['hh_total']:.1f} h | R$ {r['taxa_hora']:.2f}/h | R$ {r['custo_total']:,.2f} |"
            )
        linhas.append(
            f"| **TOTAL GERAL DE MÃO DE OBRA** | **Pico: {metricas_recursos.get('pico_efetivo_global', 0):.1f} FTEs** | **{metricas_recursos['hh_total_projeto']:.1f} h** | — | **R$ {metricas_recursos['custo_total_mo']:,.2f}** |"
        )

    linhas.extend([
        f"",
        f"---",
        f"",
        f"## 5. Matriz de Criticidade de Atividades (Top Gargalos Estocásticos)",
        f"",
        f"Atividades com maior probabilidade de travar o cronograma global (presença no Caminho Crítico durante as 20.000 iterações MCMC):",
        f"",
        f"| WBS | Atividade | 3 Pontos (O, M, P) | Índice de Criticidade | Nível de Atenção |",
        f"| :---: | :--- | :---: | :---: | :--- |"
    ])

    for t in resultado_mc["tarefas_ordenadas_criticidade"][:10]:
        crit = t["indice_criticidade"]
        status = "🔴 Crítica (>90%)" if crit >= 90 else "🟡 Moderada" if crit >= 30 else "🟢 Baixa"
        linhas.append(
            f"| `{t['wbs']}` | {t['nome']} | `({t['otimista']}, {t['provavel']}, {t['pessimista']}) d` | **{crit:.1f}%** | {status} |"
        )

    linhas.extend([
        f"",
        f"---",
        f"",
        f"## 6. Plano de Ação Estratégico para a Diretoria (5W2H)",
        f"",
        f"1. **Fast-Tracking em Suprimentos:** Disparar pedido e cotação de chapas inox (SA-240 304) e tubos assim que o projeto preliminar for concluído (**economia de ~8 dias**).",
        f"2. **Crashing na Soldagem ASME IX:** Alocar 2 soldadores qualificados em paralelo nas soldas do costado (**economia de ~4 dias**).",
        f"3. **Governança de Feeding Buffer:** Fixar meta de fábrica no P50 ({d_mit['p50']:.1f}d) e contratar no P85 ({d_mit['p85']:.1f}d), mantendo a margem de {d_mit['buffer_disponivel']:.1f} dias como proteção do PMO.",
        f"4. **Reserva de Contingência Financeira:** Provisionar **R$ {c['contingencia_sugerida']:,.2f}** (P80-P50) para absorver flutuações de ligas e frete.",
        f"",
        f"---",
        f"",
        f"## 7. Entregáveis Gerados",
        f"",
        f"- **Relatório Executivo para a Diretoria (PDF 3 Páginas):** [`RELATORIO_DIRETORIA_MONTE_CARLO.pdf`](file:///{os.path.abspath(caminho_relatorio).replace('RELATORIO_PROJETO_MC.md', 'RELATORIO_DIRETORIA_MONTE_CARLO.pdf').replace(chr(92), '/')})",
        f"- **Arquivo MS Project XML (Com Recursos):** [`{os.path.basename(caminho_xml)}`](file:///{os.path.abspath(caminho_xml).replace(chr(92), '/')})",
        f"- **Histograma de Recursos por Função:** `assets/mc_histograma_recursos.png`",
        f"- **Gráficos em Assets:** Comparativo de Cenários MCMC, Sensibilidade do Caminho Crítico e Riscos de Custos.",
        f"",
        f"---",
        f"*Relatório gerado automaticamente pelo motor estocástico MCMC da skill cronograma-mc.*"
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
    print("🚀 INICIANDO PIPELINE: MD -> EAP -> RECURSOS -> MCMC -> MS PROJECT & PDF")
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

    # 3. Dimensionamento e Alocação de Recursos (HH, Equipes e Custos)
    print(f"\n👥 3. Dimensionando Recursos Industriais e Homens-Hora (HH)...")
    atribuicoes, metricas_recursos = dimensionar_recursos_tarefas(rede_wbs)
    caminho_hist_png = pasta_assets / "mc_histograma_recursos.png"
    gerar_histograma_recursos_temporal(rede_wbs, metricas_recursos, str(caminho_hist_png))
    print(f"   ✓ Total de Homens-Hora : {metricas_recursos['hh_total_projeto']:.1f} HH")
    print(f"   ✓ Custo Total de M.O.  : R$ {metricas_recursos['custo_total_mo']:,.2f}")
    print(f"   ✓ Pico de Mobilização  : {metricas_recursos['pico_efetivo_global']:.1f} profissionais (Semana {metricas_recursos['semana_pico_global']})")
    print(f"   ✓ Histograma Gráfico   : {caminho_hist_png}")

    # 4. Simulação de Monte Carlo & Comparativo de Cenários
    print(f"\n🎲 4. Executando Simulação MCMC & Comparativo de Cenários ({n_simulacoes:,} iterações)...")
    res_mc = simular_monte_carlo_rede(rede_wbs, n_sim=n_simulacoes, plot=True, pasta_assets=str(pasta_assets))
    d_inercial = res_mc["duracao"]
    d_mitigado = res_mc["cenario_mitigado"]
    c = res_mc["custo"]

    print(f"\n   ┌── CENÁRIO 1: INERCIAL (SEM MITIGAÇÃO) ──────────────┐")
    print(f"   │ Duração P50 / P90    : {d_inercial['p50']:.1f} dias / {d_inercial['p90']:.1f} dias")
    print(f"   │ P(cumprir prazo)     : {d_inercial['prob_sucesso_prazo']:.1f}% (🔴 Alto Risco de Atraso)")
    print(f"   │ Atraso projetado     : +{d_inercial['p50'] - d_inercial['prazo_alvo']:.1f} dias úteis")
    print(f"   └── CENÁRIO 2: OTIMIZADO COM PLANO DE AÇÃO ────────────┘")
    print(f"   │ Duração P50 / P85    : {d_mitigado['p50']:.1f} dias / {d_mitigado['p85']:.1f} dias")
    print(f"   │ P(cumprir prazo)     : {d_mitigado['prob_sucesso_prazo']:.1f}% (🟢 Baixo Risco / Protegido)")
    print(f"   │ Buffer Disponível    : {d_mitigado['buffer_disponivel']:.1f} dias úteis de margem")
    print(f"   └──────────────────────────────────────────────────────┘")
    print(f"   ✓ Custo P50 / P80      : R$ {c['p50']/1000.0:.1f}k / R$ {c['p80']/1000.0:.1f}k")
    print(f"   ✓ Contingência Custo   : R$ {c['contingencia_sugerida']/1000.0:.1f}k")

    # 5. Exportação MS Project XML (MSPDI com Recursos)
    if data_inicio_str:
        inicio = date.fromisoformat(data_inicio_str)
    else:
        inicio = next_monday(date.today())

    print(f"\n📄 5. Exportando para Microsoft Project XML (MSPDI com Recursos)...")
    xml_path = exportar_msproject_xml(rede_wbs, res_mc, inicio, caminho_saida_xml, base_duracao, metricas_recursos)
    print(f"   ✓ Arquivo XML Gerado   : {xml_path}")

    # 6. Geração do Relatório Executivo em PDF para a Diretoria (3 Páginas)
    print(f"\n📑 6. Gerando Relatório Executivo para a Diretoria em PDF (3 Páginas)...")
    pdf_out = gerar_relatorio_pdf_diretoria(metadados, rede_wbs, res_mc, caminho_pdf, metricas_recursos)
    print(f"   ✓ Relatório PDF Criado : {pdf_out}")

    # 7. Geração do Relatório Markdown
    print(f"\n📝 7. Gerando relatório executivo Markdown...")
    rel_path = gerar_relatorio_markdown(metadados, rede_wbs, res_mc, xml_path, caminho_relatorio, metricas_recursos)
    print(f"   ✓ Relatório Criado     : {rel_path}")

    print("\n" + "=" * 75)
    print(f"🎉 PIPELINE CONCLUÍDO! TODOS OS ARTEFATOS GRAVADOS EM: {pasta_dir.resolve()}")
    print("=" * 75)


def main():
    parser = argparse.ArgumentParser(description="Pipeline Inteligente de Cronograma, Recursos e MCMC para MS Project e PDF da Diretoria")
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
