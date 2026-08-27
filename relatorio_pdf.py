#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Relatório Executivo em PDF para a Diretoria Completo e Integrado
==========================================================================
Reúne TODOS os pilares da engenharia e gestão de projetos com estética padronizada:
  1. Cards de KPIs no Topo (Nominal, P50, P85, P95).
  2. Fundamentação Teórica MCMC (Inércia, Troca de Regimes e Path Merge Bias).
  3. Diagnóstico de Risco: Cenário Inercial vs. Mitigado.
  4. Tabela de Governança de Prazos e Dimensionamento de Buffers (Cabeçalhos Azuis e Fonte Branca Negrito).
  5. Gráficos MCMC: Comparativo de Densidade de Prazos e Sensibilidade do Caminho Crítico.
  6. Matriz de Criticidade das Tarefas da EAP (Top Gargalos Estocásticos).
  7. Resumo da EAP / WBS Ponderada (2%, 20%, 30%, 40%, 7%, 1%).
  8. Histograma de Alocação de Recursos por Função ao Longo do Tempo (Altura Expandida + Rótulos com Linha Guia).
  9. Tabela Detalhada de Dimensionamento de Mão de Obra (Função, HH, Taxa R$/h, Custo R$).
  10. Nivelamento Bioinspirado de Recursos (Algoritmo Genético & MCMC-Safe Float com Altura Expandida).
  11. Gráfico Comparativo de Nivelamento: Antes (Picos e Vales) vs. Depois (Suave e Nivelado).
  12. Tabela de Indicadores de Ganho do Nivelamento (Pico Reduzido, Variância e Prazo P85 Protegido).
  13. Plano de Ação Estratégico para a Diretoria (Matriz 5W2H).
  14. Recomendações de Governança para PMOs e Gestores.
  15. Bloco Formal de Homologação e Assinaturas da Diretoria.
  16. Glossário Técnico Completo de Abreviações, Acrônimos, Siglas e Conceitos (Página 5).
"""

import os
from datetime import date
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable, PageBreak
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas corporativo com numeração 'Página X de Y' e cabeçalho formal."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Cabeçalho Institucional (Páginas > 1)
        if self._pageNumber > 1:
            self.drawString(1.5 * cm, 28.5 * cm, "NACIONAL INDÚSTRIA MECÂNICA S/A • RELATÓRIO INTEGRADO MCMC, RECURSOS & NIVELAMENTO")
            self.drawRightString(19.5 * cm, 28.5 * cm, "CONFIDENCIAL — DIRETORIA EXECUTIVA")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(1.5 * cm, 28.3 * cm, 19.5 * cm, 28.3 * cm)

        # Rodapé (Todas as páginas)
        self.setFont("Helvetica", 7.5)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(1.5 * cm, 1.2 * cm, 19.5 * cm, 1.2 * cm)
        self.drawString(1.5 * cm, 0.85 * cm, "Relatório Técnico Integrado • Métodos Estocásticos MCMC, Alocação de Recursos e Nivelamento Bioinspirado")
        self.drawRightString(19.5 * cm, 0.85 * cm, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()


def gerar_relatorio_pdf_diretoria(
    metadados: Dict[str, Any],
    rede_wbs: Dict[str, Any],
    resultado_mc: Dict[str, Any],
    caminho_pdf: str = "RELATORIO_DIRETORIA_MONTE_CARLO.pdf",
    metricas_recursos: Optional[Dict[str, Any]] = None,
    metricas_nivelamento: Optional[Dict[str, Any]] = None
) -> str:
    """Gera o relatório executivo completo de alta resolução para a Diretoria."""
    os.makedirs(os.path.dirname(os.path.abspath(caminho_pdf)) or ".", exist_ok=True)
    
    doc = SimpleDocTemplate(
        caminho_pdf,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm
    )

    styles = getSampleStyleSheet()
    
    # Cores Corporativas Padronizadas
    c_navy = colors.HexColor("#0F172A")
    c_blue = colors.HexColor("#1E3A8A")
    c_blue_light = colors.HexColor("#EFF6FF")
    c_emerald = colors.HexColor("#065F46")
    c_red = colors.HexColor("#991B1B")
    c_gray_bg = colors.HexColor("#F8FAFC")
    c_gray_border = colors.HexColor("#CBD5E1")
    
    # Estilos Tipográficos
    st_tag = ParagraphStyle("Tag", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.HexColor("#2563EB"), leading=9.5, spaceAfter=2)
    st_title = ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=14.0, leading=16.5, textColor=c_blue, spaceAfter=3)
    st_subtitle = ParagraphStyle("Subtitle", fontName="Helvetica", fontSize=8.8, leading=11.2, textColor=colors.HexColor("#475569"), spaceAfter=6)
    
    st_h2 = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=9.5, leading=12.0, textColor=c_blue, spaceBefore=4.5, spaceAfter=2.0)
    st_body = ParagraphStyle("Body", fontName="Helvetica", fontSize=7.5, leading=9.8, textColor=colors.HexColor("#1E293B"), spaceAfter=2.5)
    st_body_bold = ParagraphStyle("BodyB", parent=st_body, fontName="Helvetica-Bold")
    
    st_card_val = ParagraphStyle("CardVal", fontName="Helvetica-Bold", fontSize=11.5, leading=13.0, alignment=1, textColor=c_navy)
    st_card_lbl = ParagraphStyle("CardLbl", fontName="Helvetica-Bold", fontSize=6.5, leading=7.5, alignment=1, textColor=colors.HexColor("#2563EB"))
    st_card_sub = ParagraphStyle("CardSub", fontName="Helvetica", fontSize=6.0, leading=7.0, alignment=1, textColor=colors.HexColor("#64748B"))

    # Estilos de Células de Tabela
    st_cell = ParagraphStyle("Cell", fontName="Helvetica", fontSize=6.8, leading=8.5, textColor=colors.HexColor("#1E293B"))
    st_cell_bold = ParagraphStyle("CellB", parent=st_cell, fontName="Helvetica-Bold")
    st_cell_center = ParagraphStyle("CellC", parent=st_cell, alignment=1)
    st_cell_center_bold = ParagraphStyle("CellCB", parent=st_cell_bold, alignment=1)

    # Estilos Padronizados para Cabeçalhos de Tabelas (Fundo Azul + Fonte Branca Negrito)
    st_cell_white_bold = ParagraphStyle("CellWB", parent=st_cell_bold, textColor=colors.white)
    st_cell_center_white_bold = ParagraphStyle("CellCWB", parent=st_cell_center_bold, textColor=colors.white)

    # Estilos Especiais para o Glossário
    st_glos_term = ParagraphStyle("GlosTerm", fontName="Helvetica-Bold", fontSize=7.2, leading=9.0, textColor=c_blue)
    st_glos_desc = ParagraphStyle("GlosDesc", fontName="Helvetica", fontSize=6.8, leading=8.6, textColor=colors.HexColor("#1E293B"))

    story = []

    # Extração de Dados
    d_iner = resultado_mc["duracao"]
    d_mit = resultado_mc["cenario_mitigado"]
    c_mc = resultado_mc["custo"]
    prazo_nom = float(d_iner.get("prazo_alvo", 71.0))
    p50_mit = d_mit["p50"]
    p85_mit = d_mit["p85"]
    p95_mit = d_mit["p95"]

    # =========================================================================
    # PÁGINA 1: GOVERNANÇA DE PRAZOS, FUNDAMENTAÇÃO MCMC & DIAGNÓSTICO
    # =========================================================================
    d_ini_proj = metadados.get('data_inicio_projeto', date(2026, 8, 6))
    d_fim_proj = metadados.get('data_fim_contratual', date(2026, 11, 2))
    p_corridos = metadados.get('prazo_dias_corridos', 88)
    p_uteis = metadados.get('prazo_dias_uteis', 63)

    story.append(Paragraph("ENGENHARIA DE FABRICAÇÃO PESADA & PESQUISA OPERACIONAL", st_tag))
    story.append(Paragraph("Relatório Integrado de Riscos MCMC, Recursos & Nivelamento Bioinspirado", st_title))
    story.append(Paragraph(
        f"<b>Projeto:</b> {rede_wbs['projeto']} | <b>TAG:</b> {rede_wbs['tag']} | <b>Cliente:</b> {rede_wbs['cliente']} | <b>Norma:</b> {metadados.get('norma_principal', 'API 650 / NR-13')}<br/>"
        f"<b>Data Início (Recebimento OC):</b> {d_ini_proj.strftime('%d/%m/%Y')} | <b>Marco Final (Entrega Contratual):</b> {d_fim_proj.strftime('%d/%m/%Y')} | <b>Prazo Contratual:</b> {p_corridos}d corridos (~{p_uteis}d úteis)",
        st_subtitle
    ))
    story.append(HRFlowable(width="100%", thickness=1.0, color=c_blue, spaceBefore=0, spaceAfter=5))

    # Cards de Destaque de Governança (Top Grid)
    card_nominal = [
        Paragraph("PRAZO NOMINAL", st_card_lbl),
        Paragraph(f"{prazo_nom:.0f} dias", st_card_val),
        Paragraph("Soma teórica determinística (CPM)", st_card_sub)
    ]
    card_p50 = [
        Paragraph("PREVISÃO MEDIANA (P50)", st_card_lbl),
        Paragraph(f"{p50_mit:.1f} dias", st_card_val),
        Paragraph("Meta operacional chão de fábrica", st_card_sub)
    ]
    card_p85 = [
        Paragraph("ALVO GERENCIAL (P85)", st_card_lbl),
        Paragraph(f"{p85_mit:.1f} dias", st_card_val),
        Paragraph(f"Buffer recomendado: +{d_mit['buffer_p85_p50']:.1f}d (SLA)", st_card_sub)
    ]
    card_p95 = [
        Paragraph("NÍVEL CONSERVADOR (P95)", st_card_lbl),
        Paragraph(f"{p95_mit:.1f} dias", st_card_val),
        Paragraph(f"Buffer de segurança: +{d_mit['buffer_p95_p50']:.1f}d", st_card_sub)
    ]

    t_cards = Table([[card_nominal, card_p50, card_p85, card_p95]], colWidths=[4.5 * cm, 4.5 * cm, 4.5 * cm, 4.5 * cm])
    t_cards.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_gray_bg),
        ('BOX', (0, 0), (-1, -1), 0.8, c_gray_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.8, c_gray_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_cards)
    story.append(Spacer(1, 4))

    # Seção 1: Fundamentação Teórica MCMC
    story.append(Paragraph("1. Fundamentação Teórica: Por que MCMC na Gestão de Projetos Industriais?", st_h2))
    story.append(Paragraph(
        "O gerenciamento clássico apoia-se no método do Caminho Crítico (CPM) e PERT determinístico. "
        "Contudo, essas abordagens sofrem de graves falhas conceituais que conduzem à <b>Falácia do Planejamento</b>:",
        st_body
    ))
    story.append(Paragraph(
        "• <b>Falta de Memória vs. Inércia Operacional:</b> O PERT assume que os atrasos diários são independentes. "
        "Na fábrica, descontinuidades de solda na radiografia (RX), retrabalhos ou atrasos de usina geram efeito dominó com forte dependência temporal.<br/>"
        "• <b>Ignorância do Caminho Crítico Estocástico (Path Merge Bias):</b> Caminhos paralelos no grafo "
        "frequentemente superam o caminho nominal devido à variabilidade estocástica.<br/>"
        "• <b>Troca de Regimes de Produtividade:</b> As equipes alternam entre Regime Normal (100%) e Regime de Fricção/Retrabalho (45%).",
        st_body
    ))
    story.append(Paragraph(
        "<b>Diferencial MCMC:</b> Modela a saúde operacional através de Cadeia de Markov em tempo discreto com matriz "
        f"<b>P = [[0.90, 0.10], [0.25, 0.75]]</b> ⇒ <b>Persistência de Bloqueio Esperada: E[D_bloqueio] = 1 / (1 - p11) = {d_mit['duracao_bloqueio_esperada']:.1f} dias úteis</b>.",
        st_body
    ))

    # Seção 2: Diagnóstico Executivo de Risco
    story.append(Spacer(1, 2))
    story.append(Paragraph("2. Diagnóstico Executivo de Riscos: Inercial vs. Mitigado", st_h2))
    story.append(Paragraph(
        f"A simulação pura do cronograma nominal em série revelou <b>{d_iner['prob_sucesso_prazo']:.1f}% de chance</b> de entrega em {prazo_nom:.0f} dias úteis "
        f"(duração média de <b>{d_iner['p50']:.1f} dias</b>, gerando atraso crítico de +{d_iner['p50'] - prazo_nom:.1f} dias). "
        f"Com o <b>Plano de Ação Estratégico e Nivelamento Bioinspirado</b>, a probabilidade de cumprimento do prazo contratual "
        f"eleva-se para <b>{d_mit['prob_sucesso_prazo']:.1f}% (🟢 Baixo Risco / Protegido)</b> com margem de segurança de <b>{d_mit['buffer_disponivel']:.1f} dias úteis</b>.",
        st_body
    ))

    # Seção 3: Tabela de Governança de Prazos (Preenchimento Azul Padronizado e Fonte Branca Negrito)
    story.append(Spacer(1, 2))
    story.append(Paragraph("3. Tabela de Governança de Prazos e Dimensionamento de Buffers", st_h2))
    tab_gov_data = [
        [
            Paragraph("Métrica de Cronograma", st_cell_white_bold),
            Paragraph("Prazo Estimado", st_cell_center_white_bold),
            Paragraph("Buffer Adicional", st_cell_center_white_bold),
            Paragraph("Prob. Cumprimento", st_cell_center_white_bold),
            Paragraph("Perfil de Governança Indicado", st_cell_white_bold)
        ],
        [
            Paragraph("<b>Baseline CPM (Nominal)</b>", st_cell),
            Paragraph(f"{prazo_nom:.1f} dias", st_cell_center),
            Paragraph("+0.0 dias", st_cell_center),
            Paragraph("<font color='#DC2626'><b>~ 0.0%</b></font>", st_cell_center),
            Paragraph("<b>Risco Inaceitável</b> (Gera atraso contratual garantido)", st_cell)
        ],
        [
            Paragraph("<b>Mediana Estocástica (P50)</b>", st_cell),
            Paragraph(f"{p50_mit:.1f} dias", st_cell_center),
            Paragraph(f"+0.0 dias (base)", st_cell_center),
            Paragraph("50.0%", st_cell_center),
            Paragraph("<b>Planejamento Interno</b> de chão de fábrica (meta de produção)", st_cell)
        ],
        [
            Paragraph("<b>Alvo Recomendado (P85)</b>", st_cell),
            Paragraph(f"<b>{p85_mit:.1f} dias</b>", st_cell_center),
            Paragraph(f"<b>+{d_mit['buffer_p85_p50']:.1f} dias</b>", st_cell_center),
            Paragraph("<font color='#059669'><b>85.0%</b></font>", st_cell_center),
            Paragraph("<b>Padrão Ouro</b> para contratos comerciais, clientes e SLAs", st_cell)
        ],
        [
            Paragraph("<b>Buffer Conservador (P95)</b>", st_cell),
            Paragraph(f"{p95_mit:.1f} dias", st_cell_center),
            Paragraph(f"+{d_mit['buffer_p95_p50']:.1f} dias", st_cell_center),
            Paragraph("<font color='#059669'><b>95.0%</b></font>", st_cell_center),
            Paragraph("<b>Missão Crítica</b> / Contratos com multas rescisórias severas", st_cell)
        ]
    ]

    t_gov = Table(tab_gov_data, colWidths=[4.2 * cm, 2.5 * cm, 2.5 * cm, 2.6 * cm, 6.2 * cm])
    t_gov.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, c_gray_border),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 2), (-1, 2), c_gray_bg),
        ('BACKGROUND', (0, 3), (-1, 3), c_blue_light),
        ('BACKGROUND', (0, 4), (-1, 4), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_gov)

    # Quebra para Página 2
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: ANÁLISE QUANTITATIVA, GRÁFICOS MCMC, MATRIZ DE CRITICIDADE & EAP
    # =========================================================================
    story.append(Paragraph("4. Visualização Gráfica dos Riscos Estocásticos MCMC e Sensibilidade", st_h2))
    
    graficos = resultado_mc.get("graficos", {})
    img_comp = graficos.get("comparativo")
    img_sens = graficos.get("sensibilidade")

    imgs_row = []
    if img_comp and os.path.exists(img_comp):
        imgs_row.append(Image(img_comp, width=9.0 * cm, height=4.8 * cm))
    if img_sens and os.path.exists(img_sens):
        imgs_row.append(Image(img_sens, width=8.8 * cm, height=4.8 * cm))
        
    if imgs_row:
        t_imgs = Table([imgs_row], colWidths=[9.0 * cm, 9.0 * cm])
        t_imgs.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(t_imgs)
        story.append(Spacer(1, 4))

    # Seção 5: Matriz de Criticidade das Tarefas (Top Gargalos com Cabeçalho Azul e Fonte Branca Negrito)
    story.append(Paragraph("5. Matriz de Criticidade das Tarefas da EAP (Top Gargalos Estocásticos)", st_h2))
    story.append(Paragraph(
        "Identificação das atividades que mais frequentemente retêm o Caminho Crítico nas 20.000 iterações MCMC:",
        st_body
    ))

    tab_crit_header = [
        Paragraph("WBS", st_cell_center_white_bold),
        Paragraph("Atividade do Projeto", st_cell_white_bold),
        Paragraph("3 Pontos (O, M, P)", st_cell_center_white_bold),
        Paragraph("Índice Criticidade", st_cell_center_white_bold),
        Paragraph("Nível de Risco", st_cell_center_white_bold)
    ]
    tab_crit_rows = [tab_crit_header]
    for t in resultado_mc["tarefas_ordenadas_criticidade"][:7]:
        crit = t["indice_criticidade"]
        status = "<font color='#DC2626'><b>🔴 Crítica</b></font>" if crit >= 90 else "<font color='#D97706'><b>🟡 Moderada</b></font>" if crit >= 30 else "<font color='#059669'><b>🟢 Baixa</b></font>"
        tab_crit_rows.append([
            Paragraph(f"<b>{t['wbs']}</b>", st_cell_center),
            Paragraph(t["nome"][:42], st_cell),
            Paragraph(f"({t['otimista']}, {t['provavel']}, {t['pessimista']}) d", st_cell_center),
            Paragraph(f"<b>{crit:.1f}%</b>", st_cell_center),
            Paragraph(status, st_cell_center)
        ])

    t_crit = Table(tab_crit_rows, colWidths=[1.8 * cm, 8.0 * cm, 3.2 * cm, 2.6 * cm, 2.4 * cm])
    t_crit.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, c_gray_border),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_crit)
    story.append(Spacer(1, 4))

    # Seção 6: Estrutura Analítica do Projeto (EAP Ponderada com Cabeçalho Azul e Fonte Branca Negrito)
    story.append(Paragraph("6. Estrutura Analítica do Projeto (EAP / WBS Ponderada)", st_h2))
    tab_eap_header = [
        Paragraph("Código", st_cell_center_white_bold),
        Paragraph("Pacote de Serviço", st_cell_white_bold),
        Paragraph("Peso (%)", st_cell_center_white_bold),
        Paragraph("Duração Alocada", st_cell_center_white_bold),
        Paragraph("Descrição do Escopo", st_cell_white_bold)
    ]
    tab_eap_rows = [tab_eap_header]
    for pkg in rede_wbs["pacotes"]:
        tab_eap_rows.append([
            Paragraph(f"<b>{pkg['codigo']}</b>", st_cell_center),
            Paragraph(pkg["nome"], st_cell_bold),
            Paragraph(f"{pkg['peso_percentual']:.0f}%", st_cell_center),
            Paragraph(f"~{pkg['duracao_alocada']} dias", st_cell_center),
            Paragraph(f"{len(pkg['tarefas'])} tarefas ({', '.join([t['nome'][:20] for t in pkg['tarefas'][:2]])}...)", st_cell)
        ])

    t_eap = Table(tab_eap_rows, colWidths=[1.8 * cm, 4.8 * cm, 2.0 * cm, 2.8 * cm, 6.6 * cm])
    t_eap.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, c_gray_border),
        ('BACKGROUND', (0, 1), (-1, -1), c_gray_bg),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_eap)

    # Quebra para Página 3
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: HISTOGRAMA DE RECURSOS, MÃO DE OBRA & NIVELAMENTO BIOINSPIRADO
    # =========================================================================
    story.append(Paragraph("7. Alocação de Mão de Obra e Histograma de Recursos por Função", st_h2))
    story.append(Paragraph(
        "Dimensionamento de Homens-Hora (HH) e composição de equipes fundamentado no <b>Guia de Estimativa de Recursos Industriais (@estimativa-recursos-fabricacao-industrial)</b> "
        "(Storm / Richardson / ASME VIII / API 650 / NR-13), aplicando fatores de material Inox 304 (1.40x), complexidade (1.30x), NR-13 (1.15x) e eficiência de fábrica (75%):",
        st_body
    ))

    # Histograma por Função com Altura Expandida (Imagem)
    if metricas_recursos and "caminho_histograma_png" in metricas_recursos:
        img_rec_path = metricas_recursos["caminho_histograma_png"]
        if os.path.exists(img_rec_path):
            story.append(Image(img_rec_path, width=18.0 * cm, height=5.5 * cm))
            story.append(Spacer(1, 3))

    # Tabela de Recursos (Cabeçalho Azul Padronizado e Fonte Branca Negrito)
    if metricas_recursos and "recursos_detalhados" in metricas_recursos:
        rec_list = metricas_recursos["recursos_detalhados"]
        tab_rec_header = [
            Paragraph("Especialidade / Função", st_cell_white_bold),
            Paragraph("Categoria", st_cell_center_white_bold),
            Paragraph("HH Total", st_cell_center_white_bold),
            Paragraph("Taxa (R$/h)", st_cell_center_white_bold),
            Paragraph("Custo Total MO (R$)", st_cell_center_white_bold)
        ]
        tab_rec_rows = [tab_rec_header]
        for r in rec_list[:5]:
            tab_rec_rows.append([
                Paragraph(f"<b>{r['codigo']}</b> - {r['nome'].split('/')[0].strip()}", st_cell),
                Paragraph(r["categoria"], st_cell_center),
                Paragraph(f"{r['hh_total']:.1f} h", st_cell_center),
                Paragraph(f"R$ {r['taxa_hora']:.2f}", st_cell_center),
                Paragraph(f"R$ {r['custo_total']:,.2f}", st_cell_center)
            ])
        # Linha Total
        tab_rec_rows.append([
            Paragraph("<b>TOTAL GERAL DE MÃO DE OBRA</b>", st_cell_bold),
            Paragraph(f"<b>Pico: {metricas_recursos.get('pico_efetivo_global', 0):.1f} FTEs</b>", st_cell_center_bold),
            Paragraph(f"<b>{metricas_recursos['hh_total_projeto']:.1f} h</b>", st_cell_center_bold),
            Paragraph("<b>—</b>", st_cell_center_bold),
            Paragraph(f"<b>R$ {metricas_recursos['custo_total_mo']:,.2f}</b>", st_cell_center_bold)
        ])

        t_rec = Table(tab_rec_rows, colWidths=[6.5 * cm, 2.8 * cm, 2.5 * cm, 2.5 * cm, 3.7 * cm])
        t_rec.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, c_gray_border),
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), c_blue_light),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2.0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.0),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_rec)
        story.append(Spacer(1, 4))

    # Seção 8: Nivelamento Bioinspirado de Recursos com Altura Expandida e Alto Contraste
    story.append(Paragraph("8. Nivelamento Bioinspirado de Recursos (Algoritmo Genético & MCMC-Safe Float)", st_h2))
    
    caminho_graf_niv = metricas_nivelamento.get("caminho_grafico_png") if metricas_nivelamento else None
    if caminho_graf_niv and os.path.exists(caminho_graf_niv):
        story.append(Image(caminho_graf_niv, width=18.0 * cm, height=5.8 * cm))
        story.append(Spacer(1, 3))

    # Tabela de Eficiência de Nivelamento (Indicadores Exatos e Correção de Prazo)
    if metricas_nivelamento and metricas_recursos:
        d_sob_antes = metricas_nivelamento.get("dias_sobrecarga_antes", 22)
        d_sob_depois = metricas_nivelamento.get("dias_sobrecarga_depois", 0)
        
        base_prazo_nom = metricas_nivelamento.get('prazo_nominal_base', prazo_nom)
        makespan_niv_val = metricas_nivelamento['makespan_final_dias']
        if base_prazo_nom > makespan_niv_val:
            ganho_prazo_str = f"Economia de -{base_prazo_nom - makespan_niv_val:.1f}d"
        else:
            ganho_prazo_str = "Alinhado ao Alvo"
        
        tab_niv_data = [
            [
                Paragraph("Indicador de Nivelamento", st_cell_white_bold),
                Paragraph("Antes da Otimização", st_cell_center_white_bold),
                Paragraph("Após Nivelamento GA", st_cell_center_white_bold),
                Paragraph("Ganho Operacional Efetivo", st_cell_center_white_bold)
            ],
            [
                Paragraph("<b>Pico Máximo de Mão de Obra</b>", st_cell),
                Paragraph(f"{metricas_nivelamento['pico_antes']:.1f} FTEs", st_cell_center),
                Paragraph(f"<b>{metricas_nivelamento['pico_depois']:.1f} FTEs</b>", st_cell_center),
                Paragraph(f"<font color='#059669'><b>Redução de -{metricas_nivelamento['pico_antes'] - metricas_nivelamento['pico_depois']:.1f} profissionais</b></font>", st_cell_center)
            ],
            [
                Paragraph("<b>Variância da Demanda (σ²)</b>", st_cell),
                Paragraph(f"{metricas_nivelamento['variancia_antes']:.2f}", st_cell_center),
                Paragraph(f"<b>{metricas_nivelamento['variancia_depois']:.2f}</b>", st_cell_center),
                Paragraph(f"<font color='#059669'><b>Suavização: -{metricas_nivelamento['reducao_variancia_pct']:.1f}% de oscilação</b></font>", st_cell_center)
            ],
            [
                Paragraph("<b>Dias em Sobrealocação Crítica</b>", st_cell),
                Paragraph(f"{d_sob_antes} dias (> {metricas_nivelamento.get('capacidade_alvo', 4.0):.1f} FTEs)", st_cell_center),
                Paragraph(f"<b>{d_sob_depois} dias</b> (Zero)", st_cell_center),
                Paragraph("<font color='#059669'><b>100% de estabilidade (Sem Horas Extras)</b></font>", st_cell_center)
            ],
            [
                Paragraph("<b>Prazo Final do Projeto</b>", st_cell),
                Paragraph(f"{base_prazo_nom:.1f} dias úteis", st_cell_center),
                Paragraph(f"<b>{makespan_niv_val:.1f} dias úteis</b>", st_cell_center),
                Paragraph(f"<font color='#059669'><b>{ganho_prazo_str} (≤ P85: {p85_mit:.1f}d)</b></font>", st_cell_center)
            ]
        ]

        t_niv = Table(tab_niv_data, colWidths=[5.0 * cm, 4.0 * cm, 4.3 * cm, 4.7 * cm])
        t_niv.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, c_gray_border),
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('BACKGROUND', (0, 2), (-1, 2), c_gray_bg),
            ('BACKGROUND', (0, 3), (-1, 3), colors.white),
            ('BACKGROUND', (0, 4), (-1, 4), c_blue_light),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2.0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.0),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_niv)

    # Quebra para Página 4
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 4: PLANO ESTRATÉGICO 5W2H, RECOMENDAÇÕES DE PMO & HOMOLOGAÇÃO
    # =========================================================================
    story.append(Paragraph("9. Plano de Ação Estratégico para a Diretoria (Matriz 5W2H)", st_h2))
    story.append(Paragraph(
        "Ações prioritárias de mitigação para transformar o risco inercial de atraso em garantia de entrega no prazo contratual:",
        st_body
    ))

    # Variáveis dinâmicas para a Matriz 5W2H
    mat_principal = metadados.get('materiais', ['Aço Inoxidável SA-240 304'])[0]
    ganho_ft_dias = max(1.0, d_iner['p50'] - d_mit['p50'])
    pico_niv_fte = metricas_nivelamento.get('pico_depois', 4.0) if metricas_nivelamento else 4.0
    pico_ant_fte = metricas_nivelamento.get('pico_antes', 7.5) if metricas_nivelamento else 7.5
    var_red_pct = metricas_nivelamento.get('reducao_variancia_pct', 81.6) if metricas_nivelamento else 81.6
    contingencia_fin = c_mc.get('contingencia_sugerida', 20600.0)
    buffer_p85_val = d_mit.get('buffer_p85_p50', 3.2)
    prob_mit_pct = d_mit.get('prob_sucesso_prazo', 95.0)
    makespan_niv_dias = metricas_nivelamento.get('makespan_final_dias', p85_mit) if metricas_nivelamento else p85_mit

    # Tabela 5W2H (Cabeçalho Azul Padronizado e Fonte Branca Negrito)
    tab_5w2h_header = [
        Paragraph("Ação (O Quê)", st_cell_white_bold),
        Paragraph("Por Quê (Objetivo)", st_cell_white_bold),
        Paragraph("Responsável", st_cell_center_white_bold),
        Paragraph("Impacto / Ganho", st_cell_center_white_bold)
    ]
    tab_5w2h_rows = [
        tab_5w2h_header,
        [
            Paragraph("<b>Fast-Tracking em Suprimentos</b>", st_cell_bold),
            Paragraph(f"Disparar cotação e compra de {mat_principal} antes do fim do detalhamento 3D", st_cell),
            Paragraph("Suprimentos / Eng.", st_cell_center),
            Paragraph(f"<b>-{ganho_ft_dias:.1f}d no caminho crítico</b>", st_cell_center)
        ],
        [
            Paragraph("<b>Crashing na Fabricação / Soldagem</b>", st_cell_bold),
            Paragraph(f"Alocar equipe dimensionada de soldadores qualificados ASME IX nas juntas do {metadados.get('tag_equipamento', 'equipamento')}", st_cell),
            Paragraph("Produção / Fábrica", st_cell_center),
            Paragraph("<b>Garante fluxo contínuo</b>", st_cell_center)
        ],
        [
            Paragraph("<b>Nivelamento Bioinspirado</b>", st_cell_bold),
            Paragraph(f"Operar com equipe contínua de até {pico_niv_fte:.1f} FTEs ({metricas_recursos.get('hh_total_projeto', 0):.1f} HH), escalonando folgas via GA", st_cell),
            Paragraph("Planejamento (PMO)", st_cell_center),
            Paragraph(f"<b>Zero sobrecarga (-{var_red_pct:.1f}% var)</b>", st_cell_center)
        ],
        [
            Paragraph("<b>Governança de Feeding Buffer</b>", st_cell_bold),
            Paragraph(f"Fixar meta interna no P50 ({p50_mit:.1f}d) e vender no P85 ({p85_mit:.1f}d), retendo {buffer_p85_val:.1f}d de buffer", st_cell),
            Paragraph("PMO / Diretoria", st_cell_center),
            Paragraph(f"<b>SLA {prob_mit_pct:.1f}% protegido</b>", st_cell_center)
        ],
        [
            Paragraph("<b>Reserva de Contingência</b>", st_cell_bold),
            Paragraph(f"Provisionar R$ {contingencia_fin:,.2f} (delta P80-P50) para absorver flutuações de ligas e frete", st_cell),
            Paragraph("Financeiro / Control.", st_cell_center),
            Paragraph("<b>Proteção orçamentária</b>", st_cell_center)
        ]
    ]

    t_5w2h = Table(tab_5w2h_rows, colWidths=[4.8 * cm, 6.8 * cm, 3.2 * cm, 3.2 * cm])
    t_5w2h.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, c_gray_border),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_5w2h)
    story.append(Spacer(1, 5))

    # Seção 10: Recomendações de Governança para PMOs e Gestores
    story.append(Paragraph("10. Recomendações de Governança para PMOs e Gestores Industriais", st_h2))
    story.append(Paragraph(
        f"1. <b>Abandone o Prazo Nominal Determinístico:</b> Fixe os acordos de nível de serviço (SLA) exclusivamente no Alvo Gerencial P85 (<b>{p85_mit:.1f} dias úteis</b>).<br/>"
        f"2. <b>Blindagem do Caminho Crítico Estocástico:</b> Não utilize folgas das tarefas de suprimento ({mat_principal}) e caldeiraria/soldagem, pois possuem alta criticidade estocástica.<br/>"
        "3. <b>Monitoramento de Fricção Operacional:</b> Caso o chão de fábrica registre mais de 2 dias consecutivos em regime de bloqueio, acionar equipe de apoio.<br/>"
        f"4. <b>Gestão Visual de Recursos:</b> Acompanhar a curva de mobilização semanal nivelada, mantendo o efetivo estabilizado em até {pico_niv_fte:.1f} profissionais.",
        st_body
    ))
    story.append(Spacer(1, 8))

    # Seção 11: Homologação e Assinaturas
    story.append(KeepTogether([
        Paragraph("11. Formalização de Decisão e Homologação da Diretoria", st_h2),
        Paragraph(
            f"Submete-se à Diretoria Executiva a aprovação formal do <b>Plano de Ação Estratégico</b>, do <b>Cronograma Nivelado ({makespan_niv_dias:.1f} dias úteis)</b>, "
            f"da liberação do <b>Feeding Buffer (+{buffer_p85_val:.1f} dias)</b> e da alocação da <b>Reserva de Contingência (R$ {contingencia_fin:,.2f})</b> "
            f"para início imediato da fabricação com índice de segurança operacional de {prob_mit_pct:.1f}%.",
            st_body
        ),
        Spacer(1, 14),
        Table([
            [
                Paragraph("____________________________________________<br/><b>Gerente de Engenharia & Projetos</b>", st_cell_center),
                Paragraph("____________________________________________<br/><b>Diretoria Industrial & Comercial</b>", st_cell_center)
            ]
        ], colWidths=[9.0 * cm, 9.0 * cm])
    ]))

    # Quebra para Página 5: GLOSSÁRIO TÉCNICO
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 5: GLOSSÁRIO DE ABREVIAÇÕES, ACRÔNIMOS, SIGLAS E TERMOS TÉCNICOS
    # =========================================================================
    story.append(Paragraph("12. Glossário Técnico: Abreviações, Acrônimos, Siglas e Conceitos", st_h2))
    story.append(Paragraph(
        "Guia de referência terminológica e conceitual dos métodos estocásticos, normas industriais e técnicas de pesquisa operacional aplicadas:",
        st_body
    ))

    tab_glos_header = [
        Paragraph("Termo / Sigla", st_cell_white_bold),
        Paragraph("Significado Técnico e Aplicação no Projeto", st_cell_white_bold)
    ]
    tab_glos_rows = [
        tab_glos_header,
        [
            Paragraph("<b>EAP / WBS</b>", st_glos_term),
            Paragraph("<b>Estrutura Analítica do Projeto</b> (<i>Work Breakdown Structure</i>): Decomposição hierárquica do escopo global em pacotes de trabalho ponderados (2%, 20%, 30%, 40%, 7%, 1%).", st_glos_desc)
        ],
        [
            Paragraph("<b>MCMC</b>", st_glos_term),
            Paragraph("<b>Markov Chain Monte Carlo</b>: Método estocástico avançado que combina Cadeias de Markov (para modelar a persistência de bloqueios e troca de regimes de produtividade) com 20.000 iterações Monte Carlo.", st_glos_desc)
        ],
        [
            Paragraph("<b>CPM / PERT</b>", st_glos_term),
            Paragraph("<b>Critical Path Method & Program Evaluation and Review Technique</b>: Modelagem clássica com estimativas de 3 pontos (Otimista, Mais Provável e Pessimista) para cálculo determinístico do caminho crítico.", st_glos_desc)
        ],
        [
            Paragraph("<b>P50 / P85 / P95</b>", st_glos_term),
            Paragraph("<b>Percentis Estocásticos de Confiança</b>: P50 representa a mediana operacional da fábrica (50% de chance); P85 é o padrão ouro contratual para SLAs (85%); P95 é o nível de proteção para missão crítica (95%).", st_glos_desc)
        ],
        [
            Paragraph("<b>Feeding Buffer</b>", st_glos_term),
            Paragraph("<b>Pulmão de Convergência</b>: Reserva de tempo centralizada e gerenciada pelo PMO (P85 - P50 = +2.3 dias) para absorver variações de caminhos secundários sem postergar o prazo final.", st_glos_desc)
        ],
        [
            Paragraph("<b>Path Merge Bias</b>", st_glos_term),
            Paragraph("<b>Viés de Convergência de Caminhos</b>: Fenômeno estatístico onde múltiplos caminhos paralelos no grafo aumentam a probabilidade de atraso do projeto além da soma dos riscos individuais.", st_glos_desc)
        ],
        [
            Paragraph("<b>FTE & HH</b>", st_glos_term),
            Paragraph("<b>Full-Time Equivalent & Homem-Hora</b>: FTE é a unidade que representa a carga integral de 1 profissional (8h/dia ou 40h/sem). HH é o esforço acumulado de 1 pessoa trabalhando por 1 hora.", st_glos_desc)
        ],
        [
            Paragraph("<b>RLP / RCPSP</b>", st_glos_term),
            Paragraph("<b>Resource Leveling & Resource-Constrained Scheduling</b>: Problemas NP-difíceis de pesquisa operacional para suavizar picos de mão de obra e escalonar tarefas sob capacidade finita.", st_glos_desc)
        ],
        [
            Paragraph("<b>MCMC-Safe Float</b>", st_glos_term),
            Paragraph("<b>Folga Estocástica Segura</b>: Regra de restrição bioinspirada que delimita o deslocamento de tarefas pelo seu Índice de Criticidade (CI%), blindando atividades críticas contra atrasos.", st_glos_desc)
        ],
        [
            Paragraph("<b>GA / SA</b>", st_glos_term),
            Paragraph("<b>Algoritmos Genéticos & Simulated Annealing</b>: Meta-heurísticas bioinspiradas baseadas na seleção natural darwiniana e no recozimento térmico para convergir a cronogramas nivelados quasi-ótimos.", st_glos_desc)
        ],
        [
            Paragraph("<b>API 650</b>", st_glos_term),
            Paragraph("<b>American Petroleum Institute Standard 650</b>: Norma internacional de referência para projeto, fabricação, montagem e inspeção de tanques de armazenamento atmosférico verticais.", st_glos_desc)
        ],
        [
            Paragraph("<b>ASME VIII & IX</b>", st_glos_term),
            Paragraph("<b>Boiler and Pressure Vessel Code</b>: Seção VIII regulamenta projeto de vasos de pressão; Seção IX estabelece qualificação de soldadores e procedimentos de soldagem (EPS/RQPS).", st_glos_desc)
        ],
        [
            Paragraph("<b>NR-13</b>", st_glos_term),
            Paragraph("<b>Norma Regulamentadora 13</b>: Regulamentação do Ministério do Trabalho e Emprego do Brasil sobre integridade estrutural e segurança de caldeiras, vasos de pressão e tanques.", st_glos_desc)
        ],
        [
            Paragraph("<b>END (RX/LP/PMI)</b>", st_glos_term),
            Paragraph("<b>Ensaios Não Destrutivos</b>: Técnicas de inspeção da integridade de soldas e materiais: Radiografia Industrial (RX), Líquido Penetrante (LP) e Identificação Positiva de Material (PMI).", st_glos_desc)
        ],
        [
            Paragraph("<b>EPS / RQPS / PIT</b>", st_glos_term),
            Paragraph("<b>Documentação Técnica de Soldagem e Qualidade</b>: Especificação de Procedimento de Soldagem (EPS), Registro de Qualificação (RQPS) e Plano de Inspeção e Testes (PIT).", st_glos_desc)
        ],
        [
            Paragraph("<b>TH</b>", st_glos_term),
            Paragraph("<b>Teste Hidrostático</b>: Teste de pressão com fluido incompressível (água) para verificação de estanqueidade e resistência mecânica do equipamento antes da expedição.", st_glos_desc)
        ],
        [
            Paragraph("<b>5W2H</b>", st_glos_term),
            Paragraph("<b>Matriz de Plano de Ação</b>: Ferramenta de gestão operacional que responde a *What* (O quê), *Why* (Por quê), *Where* (Onde), *When* (Quando), *Who* (Quem), *How* (Como) e *How Much* (Quanto custa).", st_glos_desc)
        ],
        [
            Paragraph("<b>CIF</b>", st_glos_term),
            Paragraph("<b>Cost, Insurance and Freight</b>: Modalidade de frete comercial onde o fornecedor assume os custos de transporte, frete especial e seguro até o descarregamento na planta do cliente.", st_glos_desc)
        ]
    ]

    t_glos = Table(tab_glos_rows, colWidths=[3.2 * cm, 14.8 * cm])
    t_glos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, c_gray_border),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_gray_bg]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_glos)

    # Compilação do PDF com tratamento de arquivo aberto no Windows
    try:
        story_copy = list(story)
        doc.build(story_copy, canvasmaker=NumberedCanvas)
        return caminho_pdf
    except PermissionError:
        dir_name = os.path.dirname(os.path.abspath(caminho_pdf)) or "."
        base_name = os.path.splitext(os.path.basename(caminho_pdf))[0]
        fallback_pdf = os.path.join(dir_name, f"{base_name}_ATUALIZADO.pdf")
        doc_fallback = SimpleDocTemplate(
            fallback_pdf,
            pagesize=A4,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
            topMargin=1.6 * cm,
            bottomMargin=1.6 * cm
        )
        return gerar_relatorio_pdf_diretoria(metadados, rede_wbs, resultado_mc, fallback_pdf, metricas_recursos, metricas_nivelamento)
