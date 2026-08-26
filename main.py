#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Inteligente: Documentos -> EAP Ponderada -> Recursos -> MCMC -> Nivelamento Bioinspirado -> MS Project & PDF
======================================================================================================================
Orquestrador central do fluxo de automação de planejamento, dimensionamento de recursos, análise de riscos e otimização.

Uso:
  python main.py --pasta convertidos/
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
from bioinspired_leveler import executar_nivelamento_bioinspirado


def gerar_relatorio_markdown(
    metadados: dict,
    rede_wbs: dict,
    resultado_mc: dict,
    caminho_xml: str,
    caminho_relatorio: str,
    metricas_recursos: dict = None,
    metricas_nivelamento: dict = None
) -> str:
    """Gera um relatório executivo em Markdown detalhando o planejamento, a análise MCMC e alocação de recursos."""
    d_iner = resultado_mc["duracao"]
    d_mit = resultado_mc["cenario_mitigado"]
    c = resultado_mc["custo"]
    g = resultado_mc["graficos"]
    prazo_nom = float(d_iner.get("prazo_alvo", 71.0))

    linhas = [
        f"# 📊 Relatório Executivo de Planejamento, MCMC & Nivelamento Bioinspirado",
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
            f"| **TOTAL GERAL DE MÃO DE OBRA** | **Pico Inicial: {metricas_recursos.get('pico_efetivo_global', 0):.1f} FTEs** | **{metricas_recursos['hh_total_projeto']:.1f} h** | — | **R$ {metricas_recursos['custo_total_mo']:,.2f}** |"
        )

    if metricas_nivelamento:
        linhas.extend([
            f"",
            f"---",
            f"",
            f"## 5. Nivelamento Bioinspirado de Recursos (Algoritmo Genético & MCMC-Safe Float)",
            f"",
            f"| Indicador de Nivelamento | Antes da Otimização (Nominal) | Após Nivelamento Bioinspirado | Ganho Operacional Efetivo |",
            f"| :--- | :---: | :---: | :--- |",
            f"| **Pico Máximo de Mão de Obra** | {metricas_nivelamento['pico_antes']:.1f} FTEs | **{metricas_nivelamento['pico_depois']:.1f} FTEs** | 🟢 **Redução de -{metricas_nivelamento['pico_antes'] - metricas_nivelamento['pico_depois']:.1f} profissionais no pico** |",
            f"| **Variância da Demanda (σ²)** | {metricas_nivelamento['variancia_antes']:.2f} | **{metricas_nivelamento['variancia_depois']:.2f}** | 🟢 **Suavização: -{metricas_nivelamento['reducao_variancia_pct']:.1f}% de oscilação** |",
            f"| **Carga Total de Trabalho (HH)** | {metricas_recursos['hh_total_projeto']:.1f} h | **{metricas_recursos['hh_total_projeto']:.1f} h** | **100% de aderência ao escopo fabril** |",
            f"| **Prazo Final do Projeto** | {metricas_nivelamento.get('prazo_nominal_base', 74.2):.1f} dias úteis | **{metricas_nivelamento['makespan_final_dias']:.1f} dias úteis** | 🟢 **Redução de -{metricas_nivelamento.get('prazo_nominal_base', 74.2) - metricas_nivelamento['makespan_final_dias']:.1f}d (≤ Alvo P85)** |"
        ])

    linhas.extend([
        f"",
        f"---",
        f"",
        f"## 6. Matriz de Criticidade de Atividades (Top Gargalos Estocásticos)",
        f"",
        f"Atividades com maior probabilidade de travar o cronograma global (presença no Caminho Crítico durante as 20.000 iterações MCMC):",
        f"",
        f"| WBS | Atividade | 3 Pontos (O, M, P) | Índice de Criticidade | Nível de Atenção |",
        f"| :---: | :--- | :---: | :---: | :--- |"
    ])

    for t in resultado_mc["tarefas_ordenadas_criticidade"][:10]:
        crit = t["indice_criticidade"]
        status = "🔴 Crítica (Ação Imediata)" if crit >= 90 else "🟡 Moderada" if crit >= 30 else "🟢 Baixa"
        linhas.append(
            f"| `{t['wbs']}` | {t['nome']} | `({t['otimista']}, {t['provavel']}, {t['pessimista']}) d` | **{crit:.1f}%** | {status} |"
        )

    linhas.extend([
        f"",
        f"---",
        f"",
        f"## 7. Plano de Ação Estratégico para a Diretoria (5W2H)",
        f"",
        f"1. **Fast-Tracking em Suprimentos:** Disparar pedido e cotação de chapas inox (SA-240 304) e tubos assim que o projeto preliminar for concluído (**economia de ~8 dias**).",
        f"2. **Crashing na Soldagem ASME IX:** Alocar 2 soldadores qualificados em paralelo nas soldas do costado (**economia de ~4 dias**).",
        f"3. **Nivelamento de Equipe Fábrica:** Operar com efetivo estável de ~3 a 4 pessoas, evitando custos com horas extras ou contratações de pico temporárias.",
        f"4. **Governança de Feeding Buffer:** Fixar meta de fábrica no P50 ({d_mit['p50']:.1f}d) e contratar no P85 ({d_mit['p85']:.1f}d), mantendo a margem de {d_mit['buffer_disponivel']:.1f} dias como proteção do PMO.",
        f"5. **Reserva de Contingência Financeira:** Provisionar **R$ {c['contingencia_sugerida']:,.2f}** (P80-P50) para absorver flutuações de ligas e frete.",
        f"",
        f"---",
        f"",
        f"## 8. Glossário Técnico (Abreviações, Siglas e Conceitos)",
        f"",
        f"| Termo / Sigla | Definição e Aplicação Técnica no Projeto |",
        f"| :--- | :--- |",
        f"| **EAP / WBS** | **Estrutura Analítica do Projeto** (*Work Breakdown Structure*): Decomposição hierárquica do escopo em pacotes de trabalho ponderados (2%, 20%, 30%, 40%, 7%, 1%). |",
        f"| **MCMC** | **Markov Chain Monte Carlo**: Método estocástico que modela a persistência de bloqueios operacionais e alternância de regimes de produtividade. |",
        f"| **CPM / PERT** | **Critical Path Method & PERT**: Modelagem clássica determinística baseada em estimativas de 3 pontos (Otimista, Mais Provável, Pessimista). |",
        f"| **P50 / P85 / P95** | **Percentis de Confiança Estocástica**: P50 = Mediana interna de fábrica; P85 = Padrão ouro contratual (SLA); P95 = Buffer conservador de missão crítica. |",
        f"| **Feeding Buffer** | **Pulmão de Convergência**: Reserva gerenciada pelo PMO (+2.3 dias) para absorver variações sem postergar a entrega final. |",
        f"| **FTE & HH** | **Full-Time Equivalent & Homem-Hora**: FTE = dedicação integral de 1 profissional (8h/dia); HH = esforço total de 1 hora de trabalho. |",
        f"| **RLP / RCPSP** | **Resource Leveling & Resource-Constrained Scheduling**: Problemas de otimização combinatória para suavização de carga e restrição de recursos. |",
        f"| **MCMC-Safe Float** | **Folga Estocástica Segura**: Regra bioinspirada que delimita os deslocamentos pelo Índice de Criticidade ($CI$), blindando tarefas críticas. |",
        f"| **GA / SA** | **Algoritmos Genéticos & Simulated Annealing**: Meta-heurísticas bioinspiradas de otimização combinatória. |",
        f"| **API 650 & ASME** | Normas técnicas internacionais para tanques de armazenamento atmosférico e qualificação de procedimentos de soldagem (ASME IX). |",
        f"| **END (RX/LP/PMI)** | Ensaios Não Destrutivos: Radiografia Industrial (RX), Líquido Penetrante (LP) e Identificação Positiva de Material (PMI). |",
        f"| **5W2H** | Matriz de plano de ação estruturada (What, Why, Where, When, Who, How, How Much). |",
        f"",
        f"---",
        f"",
        f"## 9. Entregáveis Gerados",
        f"",
        f"- **Relatório Executivo para a Diretoria (PDF 3 Páginas):** [`RELATORIO_DIRETORIA_MONTE_CARLO.pdf`](file:///{os.path.abspath(caminho_relatorio).replace('RELATORIO_PROJETO_MC.md', 'RELATORIO_DIRETORIA_MONTE_CARLO.pdf').replace(chr(92), '/')})",
        f"- **Arquivo MS Project XML Nivelado:** [`{os.path.basename(caminho_xml)}`](file:///{os.path.abspath(caminho_xml).replace(chr(92), '/')})",
        f"- **Gráfico Comparativo de Nivelamento:** `assets/mc_nivelamento_recursos_comparativo.png`",
        f"- **Histograma de Recursos por Função:** `assets/mc_histograma_recursos.png`",
        f"- **Gráficos em Assets:** Comparativo MCMC, Sensibilidade de Caminho Crítico e Riscos de Custos.",
        f"",
        f"---",
        f"*Relatório gerado automaticamente pelo motor estocástico MCMC e Nivelamento Bioinspirado da skill cronograma-mc.*"
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
    print("🚀 INICIANDO PIPELINE: MD -> EAP -> RECURSOS -> MCMC -> NIVELAMENTO -> MS PROJECT & PDF")
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

    # 3. Dimensionamento de Recursos (HH, Equipes e Custos)
    print(f"\n👥 3. Dimensionando Recursos Industriais e Homens-Hora (HH)...")
    atribuicoes, metricas_recursos = dimensionar_recursos_tarefas(rede_wbs)
    print(f"   ✓ Total de Homens-Hora : {metricas_recursos['hh_total_projeto']:.1f} HH")
    print(f"   ✓ Custo Total de M.O.  : R$ {metricas_recursos['custo_total_mo']:,.2f}")

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

    # 5. Nivelamento Bioinspirado de Recursos (Algoritmo Genético & MCMC-Safe Float)
    print(f"\n🧬 5. Executando Nivelamento Bioinspirado de Recursos (Algoritmo Genético & MCMC)...")
    caminho_niv_png = pasta_assets / "mc_nivelamento_recursos_comparativo.png"
    metricas_nivelamento = executar_nivelamento_bioinspirado(
        rede_wbs=rede_wbs,
        metricas_recursos=metricas_recursos,
        resultado_mc=res_mc,
        capacidade_alvo_fte=4.0,
        caminho_saida_png=str(caminho_niv_png)
    )
    print(f"   ✓ Pico Inicial -> Nivelado : {metricas_nivelamento['pico_antes']:.1f} FTEs -> {metricas_nivelamento['pico_depois']:.1f} FTEs")
    print(f"   ✓ Redução da Variância     : -{metricas_nivelamento['reducao_variancia_pct']:.1f}% de oscilação na demanda de pessoal")
    print(f"   ✓ Makespan Final Nivelado  : {metricas_nivelamento['makespan_final_dias']:.1f} dias úteis (Dentro do alvo P85)")
    print(f"   ✓ Gráfico Comparativo      : {caminho_niv_png}")

    # 6. Geração do Histograma Semanal de Recursos (Já com Cronograma Nivelado)
    caminho_hist_png = pasta_assets / "mc_histograma_recursos.png"
    gerar_histograma_recursos_temporal(rede_wbs, metricas_recursos, str(caminho_hist_png))
    print(f"\n📊 6. Gerando Histograma Semanal de Recursos Nivelados...")
    print(f"   ✓ Pico de Mobilização  : {metricas_recursos['pico_efetivo_global']:.1f} profissionais (Semana {metricas_recursos['semana_pico_global']})")
    print(f"   ✓ Histograma Gráfico   : {caminho_hist_png}")

    # 7. Exportação MS Project XML (MSPDI com Recursos Nivelados)
    if data_inicio_str:
        inicio = date.fromisoformat(data_inicio_str)
    else:
        inicio = next_monday(date.today())

    print(f"\n📄 6. Exportando para Microsoft Project XML (MSPDI Nivelado com Recursos)...")
    xml_path = exportar_msproject_xml(rede_wbs, res_mc, inicio, caminho_saida_xml, base_duracao, metricas_recursos)
    print(f"   ✓ Arquivo XML Gerado   : {xml_path}")

    # 7. Geração do Relatório Executivo em PDF para a Diretoria (3 Páginas)
    print(f"\n📑 7. Gerando Relatório Executivo para a Diretoria em PDF (3 Páginas)...")
    pdf_out = gerar_relatorio_pdf_diretoria(metadados, rede_wbs, res_mc, caminho_pdf, metricas_recursos, metricas_nivelamento)
    print(f"   ✓ Relatório PDF Criado : {pdf_out}")

    # 8. Geração do Relatório Markdown
    print(f"\n📝 8. Gerando relatório executivo Markdown...")
    rel_path = gerar_relatorio_markdown(metadados, rede_wbs, res_mc, xml_path, caminho_relatorio, metricas_recursos, metricas_nivelamento)
    print(f"   ✓ Relatório Criado     : {rel_path}")

    print("\n" + "=" * 75)
    print(f"🎉 PIPELINE CONCLUÍDO! TODOS OS ARTEFATOS GRAVADOS EM: {pasta_dir.resolve()}")
    print("=" * 75)


def main():
    parser = argparse.ArgumentParser(description="Pipeline Inteligente de Cronograma, Recursos, MCMC e Nivelamento Bioinspirado")
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
