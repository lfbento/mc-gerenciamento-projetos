#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Relatório Executivo em PDF para a Diretoria
======================================================
Produz um documento formal, executivo e de alto padrão visual com base nos
resultados da Simulação de Monte Carlo, comparativo de cenários de risco
e Plano de Ação Estratégico (Fast-Tracking, Crashing e Buffer de Projeto).
"""

import os
from datetime import date
from typing import Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas com numeração de páginas 'Página X de Y' e cabeçalho institucional."""
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
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Cabeçalho (Páginas > 1)
        if self._pageNumber > 1:
            self.drawString(1.5 * cm, 28.5 * cm, "RELATÓRIO EXECUTIVO DE RISCOS & MONTE CARLO | NACIONAL INDÚSTRIA")
            self.drawRightString(19.5 * cm, 28.5 * cm, "CONFIDENCIAL - DIRETORIA")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(1.5 * cm, 28.3 * cm, 19.5 * cm, 28.3 * cm)

        # Rodapé (Todas as páginas)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(1.5 * cm, 1.5 * cm, 19.5 * cm, 1.5 * cm)
        self.drawString(1.5 * cm, 1.1 * cm, "Nacional Indústria Mecânica S/A — Gestão de Projetos & Engenharia")
        self.drawRightString(19.5 * cm, 1.1 * cm, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()


def gerar_relatorio_pdf_diretoria(
    metadados: Dict[str, Any],
    rede_wbs: Dict[str, Any],
    resultado_mc: Dict[str, Any],
    caminho_pdf: str = "RELATORIO_DIRETORIA_MONTE_CARLO.pdf"
) -> str:
    """Gera o PDF executivo de alta qualidade para a Diretoria."""
    os.makedirs(os.path.dirname(os.path.abspath(caminho_pdf)) or ".", exist_ok=True)
    
    doc = SimpleDocTemplate(
        caminho_pdf,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm
    )

    styles = getSampleStyleSheet()
    
    # Estilos customizados
    azul_escuro = colors.HexColor("#0F172A")
    azul_corp = colors.HexColor("#1E3A8A")
    verde_sucesso = colors.HexColor("#065F46")
    vermelho_alerta = colors.HexColor("#991B1B")
    cinza_fundo = colors.HexColor("#F8FAFC")
    
    style_titulo = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=azul_corp,
        spaceAfter=4
    )
    
    style_subtitulo = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12
    )

    style_h2 = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=azul_corp,
        spaceBefore=12,
        spaceAfter=6
    )

    style_body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6
    )

    style_body_bold = ParagraphStyle(
        "BodyBold",
        parent=style_body,
        fontName="Helvetica-Bold"
    )

    style_cell = ParagraphStyle(
        "CellText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1E293B")
    )

    style_cell_bold = ParagraphStyle(
        "CellTextBold",
        parent=style_cell,
        fontName="Helvetica-Bold"
    )

    style_cell_center = ParagraphStyle(
        "CellTextCenter",
        parent=style_cell,
        alignment=1
    )

    style_cell_center_bold = ParagraphStyle(
        "CellTextCenterBold",
        parent=style_cell_bold,
        alignment=1
    )

    story = []

    # 1. Cabeçalho Executivo
    story.append(Paragraph("RELATÓRIO EXECUTIVO PARA A DIRETORIA", ParagraphStyle("Tag", fontName="Helvetica-Bold", fontSize=9, textColor=colors.HexColor("#2563EB"), spaceAfter=2)))
    story.append(Paragraph("Análise de Riscos & Plano de Ação Estratégico (Monte Carlo)", style_titulo))
    story.append(Paragraph(f"<b>Projeto:</b> {rede_wbs['projeto']} | <b>TAG:</b> {rede_wbs['tag']} | <b>Cliente:</b> {rede_wbs['cliente']}", style_subtitulo))
    story.append(HRFlowable(width="100%", thickness=1.5, color=azul_corp, spaceBefore=0, spaceAfter=10))

    # 2. Resumo dos Metadados do Contrato
    dados_header = [
        [
            Paragraph("<b>Data da Análise:</b> " + date.today().strftime('%d/%m/%Y'), style_cell),
            Paragraph("<b>Prazo Contratual:</b> 100 dias corridos (~71 dias úteis)", style_cell),
            Paragraph(f"<b>Orçamento Aprovado:</b> R$ {metadados.get('orcamento_total', 395500.0):,.2f}", style_cell)
        ],
        [
            Paragraph(f"<b>Norma Técnica:</b> {metadados.get('norma_principal', 'API 650')}", style_cell),
            Paragraph("<b>Simulações Monte Carlo:</b> 20.000 iterações", style_cell),
            Paragraph("<b>Destino Final:</b> Pólo Petroquímico de Camaçari/BA", style_cell)
        ]
    ]
    t_header = Table(dados_header, colWidths=[6.0 * cm, 6.0 * cm, 6.0 * cm])
    t_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), cinza_fundo),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 10))

    # 3. Diagnóstico e Parecer Executivo de Risco
    d_inercial = resultado_mc["duracao"]
    d_mitigado = resultado_mc["cenario_mitigado"]
    c_mc = resultado_mc["custo"]

    story.append(Paragraph("1. Diagnóstico de Risco & Parecer da Engenharia", style_h2))
    story.append(Paragraph(
        "A simulação estocástica de Monte Carlo sobre o cronograma determinístico tradicional (sequencial rígido) "
        "revelou um <b>Alto Risco de Atraso</b>: a probabilidade de entregar a obra no prazo contratual de 71 dias úteis "
        f"é de <b>{d_inercial['prob_sucesso_prazo']:.1f}%</b>, com duração média projetada de <b>{d_inercial['p50']:.1f} dias úteis</b> "
        f"(atraso de +{d_inercial['p50'] - d_inercial['prazo_alvo']:.1f} dias úteis).",
        style_body
    ))
    story.append(Paragraph(
        "<b>Causa Raiz:</b> O acúmulo de incertezas nos 6 pacotes de serviço em série e a assimetria natural de atrasos "
        "(fornecimento de chapas de inox pela usina, qualificação ASME IX e inspeções END/TH) empurram fatalmente a entrega final caso não haja gestão de paralelismo.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Solução Recomendada:</b> Adoção imediata do <b>Plano de Ação Estratégico</b> estruturado pela Engenharia "
        "(Fast-Tracking em suprimentos de longo prazo + reforço de turnos na soldagem + buffer de projeto de 16 dias úteis), "
        f"o que eleva a probabilidade de cumprimento do prazo contratual para <b>{d_mitigado['prob_sucesso_prazo']:.1f}% (🟢 Baixo Risco)</b>.",
        style_body
    ))
    story.append(Spacer(1, 6))

    # 4. Tabela Comparativa de Decisão para a Diretoria
    story.append(Paragraph("2. Quadro Comparativo de Decisão: Inercial vs. Mitigado", style_h2))
    
    tabela_cenarios = [
        [
            Paragraph("<b>Métrica de Gestão</b>", style_cell_bold),
            Paragraph("<b>Cenário Inercial<br/>(Sem Mitigação)</b>", style_cell_center_bold),
            Paragraph("<b>Cenário Otimizado<br/>(Com Plano de Ação)</b>", style_cell_center_bold),
            Paragraph("<b>Impacto / Decisão para a Diretoria</b>", style_cell_bold)
        ],
        [
            Paragraph("<b>Prazo Central Mais Provável (P50)</b>", style_cell),
            Paragraph(f"{d_inercial['p50']:.1f} dias úteis", style_cell_center),
            Paragraph(f"<b>{d_mitigado['p50']:.1f} dias úteis</b>", style_cell_center),
            Paragraph(f"<b>Ganho de {d_inercial['p50'] - d_mitigado['p50']:.1f} dias úteis</b> no caminho crítico fabril.", style_cell)
        ],
        [
            Paragraph("<b>Duração Segura (P90)</b>", style_cell),
            Paragraph(f"{d_inercial['p90']:.1f} dias úteis", style_cell_center),
            Paragraph(f"<b>{d_mitigado['p90']:.1f} dias úteis</b>", style_cell_center),
            Paragraph("Garante entrega antes do prazo contratual de 71 dias.", style_cell)
        ],
        [
            Paragraph("<b>Probabilidade de Cumprir Prazo Contratual</b>", style_cell),
            Paragraph(f"<font color='#DC2626'><b>{d_inercial['prob_sucesso_prazo']:.1f}%</b></font>", style_cell_center),
            Paragraph(f"<font color='#059669'><b>{d_mitigado['prob_sucesso_prazo']:.1f}%</b></font>", style_cell_center),
            Paragraph("Elimina multas contratuais e preserva o SLA do cliente.", style_cell)
        ],
        [
            Paragraph("<b>Margem / Buffer de Proteção</b>", style_cell),
            Paragraph(f"<font color='#DC2626'>Déficit de {d_inercial['buffer_necessario']:.1f} d</font>", style_cell_center),
            Paragraph(f"<font color='#059669'><b>Sobram {d_mitigado['buffer_disponivel']:.1f} dias</b></font>", style_cell_center),
            Paragraph("Buffer operacional alocado antes da expedição CIF.", style_cell)
        ],
        [
            Paragraph("<b>Custo P50 / Contingência Sugerida</b>", style_cell),
            Paragraph(f"R$ {c_mc['p50']/1000.0:.1f}k", style_cell_center),
            Paragraph(f"R$ {c_mc['p50']/1000.0:.1f}k", style_cell_center),
            Paragraph(f"Reserva recomendada: <b>R$ {c_mc['contingencia_sugerida']/1000.0:.1f}k</b> (P80-P50).", style_cell)
        ]
    ]

    t_cenarios = Table(tabela_cenarios, colWidths=[4.5 * cm, 3.2 * cm, 3.2 * cm, 7.1 * cm])
    t_cenarios.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 2), (-1, 2), cinza_fundo),
        ('BACKGROUND', (0, 3), (-1, 3), colors.white),
        ('BACKGROUND', (0, 4), (-1, 4), cinza_fundo),
        ('BACKGROUND', (0, 5), (-1, 5), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_cenarios)
    story.append(Spacer(1, 10))

    # 5. Gráficos Comparativos
    graficos = resultado_mc.get("graficos", {})
    if graficos.get("comparativo") and os.path.exists(graficos["comparativo"]):
        story.append(Paragraph("3. Comparativo Visual de Probabilidade (Monte Carlo - 20.000 Sims)", style_h2))
        story.append(Image(graficos["comparativo"], width=17.5 * cm, height=8.2 * cm))
        story.append(Spacer(1, 10))

    # 6. Matriz do Plano de Ação Estratégico (5W2H)
    story.append(Paragraph("4. Plano de Ação para Aprovação da Diretoria (5W2H)", style_h2))
    
    plano_acao_dados = [
        [
            Paragraph("<b>#</b>", style_cell_center_bold),
            Paragraph("<b>Ação Estratégica (O quê)</b>", style_cell_bold),
            Paragraph("<b>Como / Justificativa</b>", style_cell_bold),
            Paragraph("<b>Responsável</b>", style_cell_bold),
            Paragraph("<b>Impacto no Prazo</b>", style_cell_center_bold)
        ],
        [
            Paragraph("1", style_cell_center),
            Paragraph("<b>Fast-Tracking em Suprimentos</b>", style_cell),
            Paragraph("Disparar pedido e cotação de chapas inox (SA-240 304) e tubos assim que o projeto 2D/3D preliminar for concluído, sem aguardar a aprovação burocrática final.", style_cell),
            Paragraph("Suprimentos / Eng. Projetos", style_cell),
            Paragraph("<b>- 8.0 dias</b>", style_cell_center_bold)
        ],
        [
            Paragraph("2", style_cell_center),
            Paragraph("<b>Crashing na Soldagem (Turno Duplo)</b>", style_cell),
            Paragraph("Alocar 2 soldadores qualificados ASME IX em paralelo nas soldas longitudinais e circunferenciais do costado.", style_cell),
            Paragraph("Gerência de Produção", style_cell),
            Paragraph("<b>- 4.0 dias</b>", style_cell_center_bold)
        ],
        [
            Paragraph("3", style_cell_center),
            Paragraph("<b>Governança de Buffer de Projeto</b>", style_cell),
            Paragraph("Fixar a meta de chão de fábrica em 55 dias úteis, mantendo 16 dias úteis de contingência oculta para absorver eventuais retestes END e logística especial.", style_cell),
            Paragraph("Gerente do Projeto", style_cell),
            Paragraph("<b>Proteção Total</b>", style_cell_center_bold)
        ],
        [
            Paragraph("4", style_cell_center),
            Paragraph("<b>Reserva de Contingência Financeira</b>", style_cell),
            Paragraph("Provisionar R$ 20.146,39 (P80-P50) para cobrir flutuações de preços de ligas nobres e frete especial CIF.", style_cell),
            Paragraph("Diretoria Financeira", style_cell),
            Paragraph("<b>Risco Orçamentário Mitigado</b>", style_cell_center)
        ]
    ]

    t_plano = Table(plano_acao_dados, colWidths=[0.8 * cm, 4.2 * cm, 7.8 * cm, 3.2 * cm, 2.0 * cm])
    t_plano.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), azul_corp),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 2), (-1, 2), cinza_fundo),
        ('BACKGROUND', (0, 3), (-1, 3), colors.white),
        ('BACKGROUND', (0, 4), (-1, 4), cinza_fundo),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_plano)
    story.append(Spacer(1, 12))

    # 7. Assinaturas e Aprovação da Diretoria
    story.append(KeepTogether([
        Paragraph("5. Recomendações e Formalização de Decisão", style_h2),
        Paragraph(
            "Submete-se à Diretoria Executiva a aprovação das ações de <b>Fast-Tracking</b> e alocação da <b>Reserva de Contingência</b> "
            "para início imediato da mobilização com índice de segurança de 94.8%.",
            style_body
        ),
        Spacer(1, 15),
        Table([
            [
                Paragraph("____________________________________________<br/><b>Gerente de Engenharia & Projetos</b>", style_cell_center),
                Paragraph("____________________________________________<br/><b>Diretoria Industrial / Comercial</b>", style_cell_center)
            ]
        ], colWidths=[9.0 * cm, 9.0 * cm])
    ]))

    # Compilação do PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    return caminho_pdf


if __name__ == "__main__":
    from projeto_extractor import extrair_metadados_projeto
    from wbs_scheduler import gerar_rede_wbs
    from mc_engine import simular_monte_carlo_rede

    meta = extrair_metadados_projeto("convertidos")
    rede = gerar_rede_wbs(meta)
    res_mc = simular_monte_carlo_rede(rede, n_sim=20000, plot=True)
    pdf_path = gerar_relatorio_pdf_diretoria(meta, rede, res_mc, "RELATORIO_DIRETORIA_MONTE_CARLO.pdf")
    print(f"PDF Executivo para a Diretoria gerado com sucesso: {pdf_path}")
