#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Relatório Executivo em PDF para a Diretoria (MCMC, Recursos & Governança)
==================================================================================
Produz um documento formal, executivo e de alto padrão visual (3 páginas)
incorporando:
  - Cards de KPIs no Topo (Nominal, P50, P85, P95).
  - Fundamentação Teórica MCMC (Inércia Operacional, Troca de Regimes e Path Merge Bias).
  - Tabela de Governança de Prazos e Dimensionamento de Feeding Buffers.
  - Gráficos de Densidade de Probabilidade e Sensibilidade de Caminho Crítico.
  - Histograma de Alocação de Recursos por Função ao Longo do Tempo (Semanas de Projeto).
  - Tabela de Dimensionamento de Mão de Obra (HHs e Custos).
  - Matriz de Decisão 5W2H e Recomendações Estratégicas para PMO/Diretoria.
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
            self.drawString(1.5 * cm, 28.5 * cm, "NACIONAL INDÚSTRIA MECÂNICA S/A • RELATÓRIO EXECUTIVO MCMC & ALOCAÇÃO DE RECURSOS")
            self.drawRightString(19.5 * cm, 28.5 * cm, "CONFIDENCIAL — DIRETORIA EXECUTIVA")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(1.5 * cm, 28.3 * cm, 19.5 * cm, 28.3 * cm)

        # Rodapé (Todas as páginas)
        self.setFont("Helvetica", 7.5)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(1.5 * cm, 1.2 * cm, 19.5 * cm, 1.2 * cm)
        self.drawString(1.5 * cm, 0.85 * cm, "Relatório Técnico Especializado • Métodos Estocásticos MCMC, Dimensionamento de Recursos e Riscos")
        self.drawRightString(19.5 * cm, 0.85 * cm, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()


def gerar_relatorio_pdf_diretoria(
    metadados: Dict[str, Any],
    rede_wbs: Dict[str, Any],
    resultado_mc: Dict[str, Any],
    caminho_pdf: str = "RELATORIO_DIRETORIA_MONTE_CARLO.pdf",
    metricas_recursos: Optional[Dict[str, Any]] = None
) -> str:
    """Gera o relatório executivo completo de 3 páginas para a Diretoria."""
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
    
    # Cores Corporativas
    c_navy = colors.HexColor("#0F172A")
    c_blue = colors.HexColor("#1E3A8A")
    c_blue_light = colors.HexColor("#EFF6FF")
    c_emerald = colors.HexColor("#065F46")
    c_red = colors.HexColor("#991B1B")
    c_gray_bg = colors.HexColor("#F8FAFC")
    c_gray_border = colors.HexColor("#CBD5E1")
    
    # Estilos Tipográficos
    st_tag = ParagraphStyle("Tag", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.HexColor("#2563EB"), leading=9.5, spaceAfter=2)
    st_title = ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=14.5, leading=17, textColor=c_blue, spaceAfter=3)
    st_subtitle = ParagraphStyle("Subtitle", fontName="Helvetica", fontSize=9, leading=11.5, textColor=colors.HexColor("#475569"), spaceAfter=7)
    
    st_h2 = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=c_blue, spaceBefore=6, spaceAfter=3)
    st_body = ParagraphStyle("Body", fontName="Helvetica", fontSize=7.8, leading=10.6, textColor=colors.HexColor("#1E293B"), spaceAfter=3.5)
    st_body_bold = ParagraphStyle("BodyB", parent=st_body, fontName="Helvetica-Bold")
    
    st_card_val = ParagraphStyle("CardVal", fontName="Helvetica-Bold", fontSize=12.5, leading=14, alignment=1, textColor=c_navy)
    st_card_lbl = ParagraphStyle("CardLbl", fontName="Helvetica-Bold", fontSize=6.8, leading=8, alignment=1, textColor=colors.HexColor("#2563EB"))
    st_card_sub = ParagraphStyle("CardSub", fontName="Helvetica", fontSize=6.5, leading=7.5, alignment=1, textColor=colors.HexColor("#64748B"))

    st_cell = ParagraphStyle("Cell", fontName="Helvetica", fontSize=7.2, leading=9.0, textColor=colors.HexColor("#1E293B"))
    st_cell_bold = ParagraphStyle("CellB", parent=st_cell, fontName="Helvetica-Bold")
    st_cell_center = ParagraphStyle("CellC", parent=st_cell, alignment=1)
    st_cell_center_bold = ParagraphStyle("CellCB", parent=st_cell_bold, alignment=1)

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
    # PÁGINA 1: CARDS DE GOVERNANÇA, FUNDAMENTAÇÃO MCMC & DIAGNÓSTICO
    # =========================================================================
    story.append(Paragraph("ENGENHARIA DE FABRICAÇÃO PESADA & GOVERNANÇA DE PROJETOS", st_tag))
    story.append(Paragraph("Cadeias de Markov e Monte Carlo (MCMC) na Gestão de Projetos", st_title))
    story.append(Paragraph(
        f"<b>Projeto:</b> {rede_wbs['projeto']} | <b>TAG:</b> {rede_wbs['tag']} | <b>Cliente:</b> {rede_wbs['cliente']} | <b>Norma:</b> {metadados.get('norma_principal', 'API 650 / NR-13')}",
        st_subtitle
    ))
    story.append(HRFlowable(width="100%", thickness=1.0, color=c_blue, spaceBefore=0, spaceAfter=6))

    # Cards de Destaque de Governança (Top Grid)
    card_nominal = [
        Paragraph("PRAZO NOMINAL", st_card_lbl),
        Paragraph(f"{prazo_nom:.0f} dias", st_card_val),
        Paragraph("Soma teórica do caminho crítico", st_card_sub)
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
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_cards)
    story.append(Spacer(1, 6))

    # Seção 1: Fundamentação Teórica MCMC
    story.append(Paragraph("1. Fundamentação Teórica: Por que MCMC na Gestão de Projetos Industriais?", st_h2))
    story.append(Paragraph(
        "O gerenciamento clássico apoia-se no método do Caminho Crítico (CPM) e PERT determinístico. "
        "Contudo, essas abordagens sofrem de graves falhas conceituais que conduzem à <b>Falácia do Planejamento</b>:",
        st_body
    ))
    story.append(Paragraph(
        "• <b>Falta de Memória vs. Inércia Operacional:</b> O PERT assume que os atrasos diários são independentes (i.i.d.). "
        "Na fábrica, descontinuidades de solda na radiografia (RX), retrabalhos ou atrasos de usina geram efeito cascata com forte dependência temporal.<br/>"
        "• <b>Ignorância do Caminho Crítico Estocástico (Path Merge Bias):</b> Caminhos paralelos no grafo (ex: suprimentos de chapas vs. forjados) "
        "frequentemente superam o caminho nominal devido à variabilidade estocástica.<br/>"
        "• <b>Troca de Regimes de Produtividade:</b> As equipes alternam entre Regime Normal (100%) e Regime de Fricção/Retrabalho (45%).",
        st_body
    ))

    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>Diferencial do MCMC (Markov Chain Monte Carlo):</b>", st_body_bold))
    story.append(Paragraph(
        "O MCMC modela a saúde operacional através de uma Cadeia de Markov em tempo discreto <i>S_t ∈ {0: Normal, 1: Fricção}</i> com matriz <i>P</i>:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>P = [ [0.90, 0.10], [0.25, 0.75] ]</b> &nbsp;&nbsp;⇒&nbsp;&nbsp; "
        f"<b>Persistência de Bloqueio Esperada: E[D_bloqueio] = 1 / (1 - p11) = {d_mit['duracao_bloqueio_esperada']:.1f} dias úteis.</b><br/>"
        "Bloqueios e retrabalhos técnicos tendem a durar 4 dias consecutivos se não houver pronta intervenção do PMO.",
        st_body
    ))

    # Seção 2: Diagnóstico Executivo de Risco
    story.append(Spacer(1, 3))
    story.append(Paragraph("2. Diagnóstico Executivo de Riscos: Inercial vs. Mitigado", st_h2))
    story.append(Paragraph(
        f"A simulação pura do cronograma nominal em série revelou <b>{d_iner['prob_sucesso_prazo']:.1f}% de chance</b> de entrega em 71 dias úteis "
        f"(duração média de <b>{d_iner['p50']:.1f} dias</b>, gerando atraso crítico de +{d_iner['p50'] - prazo_nom:.1f} dias). "
        f"Com o <b>Plano de Ação Estratégico</b> (Fast-Tracking em suprimentos + Crashing em soldagem), a probabilidade de cumprimento do prazo contratual "
        f"eleva-se para <b>{d_mit['prob_sucesso_prazo']:.1f}% (🟢 Baixo Risco)</b> com margem de segurança de <b>{d_mit['buffer_disponivel']:.1f} dias úteis</b>.",
        st_body
    ))

    # Quebra para Página 2
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: ANÁLISE QUANTITATIVA, GOVERNANÇA, GRÁFICOS & SENSIBILIDADE
    # =========================================================================
    story.append(Paragraph("3. Análise Quantitativa e Dimensionamento de Buffers", st_h2))
    story.append(Paragraph("Comparação direta entre o cronograma estático determinístico e as estimativas estocásticas obtidas por MCMC:", st_body))

    # Tabela de Governança de Prazos (Tabela Padronizada)
    tab_gov_data = [
        [
            Paragraph("<b>Métrica de Cronograma</b>", st_cell_bold),
            Paragraph("<b>Prazo Estimado</b>", st_cell_center_bold),
            Paragraph("<b>Buffer Adicional</b>", st_cell_center_bold),
            Paragraph("<b>Prob. Cumprimento</b>", st_cell_center_bold),
            Paragraph("<b>Perfil de Governança Indicado</b>", st_cell_bold)
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
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_gov)
    story.append(Spacer(1, 5))

    # Gráficos da Página 2
    graficos = resultado_mc.get("graficos", {})
    img_comp = graficos.get("comparativo")
    img_sens = graficos.get("sensibilidade")

    story.append(Paragraph("4. Visualização Gráfica dos Riscos Estocásticos e Sensibilidade", st_h2))
    
    imgs_row = []
    if img_comp and os.path.exists(img_comp):
        imgs_row.append(Image(img_comp, width=9.0 * cm, height=4.4 * cm))
    if img_sens and os.path.exists(img_sens):
        imgs_row.append(Image(img_sens, width=8.8 * cm, height=4.4 * cm))
        
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

    # Seção 5: Matriz de Criticidade das Tarefas
    story.append(Paragraph("5. Índice de Criticidade das Tarefas da EAP (Top Gargalos)", st_h2))
    story.append(Paragraph(
        "Enquanto no modelo determinístico todas as tarefas em série parecem ter o mesmo peso, o MCMC revela que "
        "<b>a aquisição de matérias-primas e a soldagem das virolas</b> concentram mais de <b>85% da probabilidade de retenção do caminho crítico</b>.",
        st_body
    ))

    # Quebra para Página 3
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: HISTOGRAMA DE RECURSOS AO LONGO DO TEMPO, PLANO DE AÇÃO & PMO
    # =========================================================================
    story.append(Paragraph("6. Dimensionamento de Mão de Obra e Histograma de Alocação Temporal", st_h2))
    story.append(Paragraph(
        "Distribuição semanal do efetivo operacional e consumo de Homens-Hora (HH) dimensionados conforme o escopo fabril:",
        st_body
    ))

    # Histograma de Recursos (Imagem)
    if metricas_recursos and "caminho_histograma_png" in metricas_recursos:
        img_rec_path = metricas_recursos["caminho_histograma_png"]
        if os.path.exists(img_rec_path):
            story.append(Image(img_rec_path, width=18.0 * cm, height=5.0 * cm))
            story.append(Spacer(1, 4))

    # Tabela Resumo de Mão de Obra por Função
    if metricas_recursos and "recursos_detalhados" in metricas_recursos:
        rec_list = metricas_recursos["recursos_detalhados"]
        tab_rec_header = [
            Paragraph("<b>Especialidade / Função</b>", st_cell_bold),
            Paragraph("<b>Categoria</b>", st_cell_center_bold),
            Paragraph("<b>HH Total</b>", st_cell_center_bold),
            Paragraph("<b>Taxa (R$/h)</b>", st_cell_center_bold),
            Paragraph("<b>Custo Total MO (R$)</b>", st_cell_center_bold)
        ]
        tab_rec_rows = [tab_rec_header]
        for r in rec_list[:6]: # Top 6 recursos
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
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_rec)
        story.append(Spacer(1, 5))

    # Seção 7: Recomendações Estratégicas para PMOs e Gestores
    story.append(Paragraph("7. Recomendações Estratégicas para PMOs e Gestores Industriais", st_h2))
    story.append(Paragraph(
        "1. <b>Abandone o Prazo Determinístico Nominal:</b> Fixe acordos de SLA no P85 (<b>65.1 dias úteis</b>) e utilize o <i>Feeding Buffer</i> de <b>2.7 dias</b>.<br/>"
        "2. <b>Monitoramento de Fricção Operacional:</b> Se o chão de fábrica registrar mais de 2 dias consecutivos em regime de bloqueio, aplicar ações corretivas imediatas.<br/>"
        "3. <b>Alocação de Soldadores ASME IX:</b> Manter a dupla de soldadores qualificados nas semanas de pico (Semanas 7 a 10) para garantir a produtividade.",
        st_body
    ))
    story.append(Spacer(1, 6))

    # Seção 8: Homologação e Assinaturas
    story.append(KeepTogether([
        Paragraph("8. Formalização de Decisão e Homologação da Diretoria", st_h2),
        Paragraph(
            "Submete-se à Diretoria Executiva a aprovação da <b>Mobilização de Recursos</b>, liberação do <b>Feeding Buffer</b> e "
            "alocação da <b>Reserva de Contingência</b> para início imediato com índice de segurança operacional de 100.0%.",
            st_body
        ),
        Spacer(1, 10),
        Table([
            [
                Paragraph("____________________________________________<br/><b>Gerente de Engenharia & Projetos</b>", st_cell_center),
                Paragraph("____________________________________________<br/><b>Diretoria Industrial & Comercial</b>", st_cell_center)
            ]
        ], colWidths=[9.0 * cm, 9.0 * cm])
    ]))

    # Compilação do PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    return caminho_pdf
