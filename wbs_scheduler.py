#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Estruturação WBS e Distribuição Ponderada de Cronograma
==============================================================
Aplica a EAP padrão da organização com os pesos percentuais fixos:
  1.0 ATIVIDADES            ( 2%)
  2.0 METODOS E PROCESSOS   (20%)
  3.0 SUPRIMENTOS           (30%)
  4.0 FABRICAÇÃO E MONTAGEM (40%)
  5.0 PINTURA               ( 7%)
  6.0 EXPEDIÇÃO             ( 1%)
  TOTAL                     (100%)

Distribui a duração total por pacote de serviço e gera estimativas de 3 pontos
(Otimista, Mais Provável, Pessimista) e a malha de precedências (FS).
"""

from typing import Dict, Any, List, Tuple
import math


# Pesos oficiais da EAP (Soma = 1.0)
PESOS_WBS = {
    "1.0": {"nome": "ATIVIDADES", "peso": 0.02},
    "2.0": {"nome": "METODOS E PROCESSOS", "peso": 0.20},
    "3.0": {"nome": "SUPRIMENTOS", "peso": 0.30},
    "4.0": {"nome": "FABRICAÇÃO E MONTAGEM", "peso": 0.40},
    "5.0": {"nome": "PINTURA", "peso": 0.07},
    "6.0": {"nome": "EXPEDIÇÃO", "peso": 0.01},
}


def gerar_rede_wbs(metadados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gera a estrutura completa de tarefas agrupadas pela WBS com durações ponderadas.
    """
    prazo_total_uteis = metadados.get("prazo_dias_uteis", 72)
    tag = metadados.get("tag_equipamento", "TQ-960-30/1")
    cliente = metadados.get("cliente", "Cliente")

    # 1. Cálculo do tempo disponível por pacote (em dias úteis)
    tempos_pacotes = {}
    for codigo, info in PESOS_WBS.items():
        dias_pacote = max(1.0, round(prazo_total_uteis * info["peso"], 1))
        tempos_pacotes[codigo] = dias_pacote

    # 2. Definição do catálogo de atividades detalhadas por pacote
    # Estrutura de cada item: (id_tarefa, nome, proporcao_intra_pacote, deps_ids)
    estrutura_base = {
        "1.0": [
            ("1.1", f"Kick-off Meeting & Alinhamento de Requisitos ({cliente})", 0.5, []),
            ("1.2", "Formalização do Termo de Abertura do Projeto (TAP) & Governança", 0.5, ["1.1"]),
        ],
        "2.0": [
            ("2.1", f"Projeto Executivo & Detalhamento Mecânico 2D/3D ({tag})", 0.30, ["1.2"]),
            ("2.2", "Memórias de Cálculo Estrutural e Pressão (API 650 / ASME)", 0.25, ["2.1"]),
            ("2.3", "Elaboração do PIT (Plano de Inspeção e Testes) e EPS/RQPS", 0.20, ["2.2"]),
            ("2.4", "Submissão, Análise e Aprovação Técnica pelo Cliente", 0.25, ["2.3"]),
        ],
        "3.0": [
            ("3.1", "Requisição de Compras & Cotação de Matérias-Primas Inox", 0.15, ["2.1"]),
            ("3.2", "Aquisição de Chapas Inox SA-240 304, Tubos e Flanges", 0.40, ["3.1"]),
            ("3.3", "Aquisição de Acessórios Aço Carbono, Juntas PTFE e Estojos", 0.20, ["3.1"]),
            ("3.4", "Recebimento, Inspeção Dimensional e Rastreabilidade de MP", 0.25, ["3.2", "3.3"]),
        ],
        "4.0": [
            ("4.1", "Traçado, Corte a Plasma e Chanfro das Chapas do Costado e Fundo", 0.15, ["2.4", "3.4"]),
            ("4.2", "Calandragem das Virolas e Pré-Montagem dos Aneis do Costado", 0.15, ["4.1"]),
            ("4.3", "Soldagem das Juntas Longitudinais e Circunferencias (ASME IX)", 0.20, ["4.2"]),
            ("4.4", "Montagem e Soldagem do Fundo Plano e Teto Cônico Autoportante", 0.15, ["4.3"]),
            ("4.5", "Fabricação/Instalação de Bocais A1-W1, Boca de Visita M1 e Guarda-Corpo", 0.15, ["4.4"]),
            ("4.6", "Execução de Ensaios END (Radiografia RX, LP, Caixa de Vácuo e PMI)", 0.10, ["4.5"]),
            ("4.7", "Preparação e Execução do Teste Hidrostático (TH) Fabril", 0.10, ["4.6"]),
        ],
        "5.0": [
            ("5.1", "Decapagem Química e Passivação Integral das Superfícies em Aço Inox", 0.50, ["4.7"]),
            ("5.2", "Jateamento e Pintura Externa dos Acessórios em Aço Carbono (Munsell 5Y 8/12)", 0.50, ["5.1"]),
        ],
        "6.0": [
            ("6.1", "Emissão, Compilação e Aprovação do Data Book Final com ART (SOP-BRA-019-01)", 0.40, ["4.7", "5.2"]),
            ("6.2", "Embalagem Especial, Fabricação do Berço e Carregamento", 0.30, ["6.1"]),
            ("6.3", "Transporte Rodoviário Especial CIF e Entrega Técnica no Polo Camaçari/BA", 0.30, ["6.2"]),
        ]
    }

    # 3. Dimensionamento de durações de 3 pontos (otimista, provável, pessimista)
    tarefas_finais = []
    pacotes_finais = []

    for cod_pacote, itens in estrutura_base.items():
        nome_pacote = PESOS_WBS[cod_pacote]["nome"]
        peso_pct = PESOS_WBS[cod_pacote]["peso"] * 100
        dur_pacote = tempos_pacotes[cod_pacote]

        tarefas_do_pacote = []
        for tid, nome_t, prop, deps in itens:
            dur_m = max(1, int(round(dur_pacote * prop)))
            # Estimativa de 3 pontos com dispersão assimétrica honesta de engenharia
            dur_o = max(1, int(math.floor(dur_m * 0.75)))
            dur_p = max(dur_m + 1, int(math.ceil(dur_m * 1.50)))

            tarefa_dict = {
                "id": tid,
                "wbs": tid,
                "pacote_codigo": cod_pacote,
                "pacote_nome": nome_pacote,
                "nome": nome_t,
                "deps": deps,
                "otimista": dur_o,
                "provavel": dur_m,
                "pessimista": dur_p,
                "duracao_base": dur_m
            }
            tarefas_finais.append(tarefa_dict)
            tarefas_do_pacote.append(tarefa_dict)

        pacotes_finais.append({
            "codigo": cod_pacote,
            "nome": nome_pacote,
            "peso_percentual": peso_pct,
            "duracao_alocada": dur_pacote,
            "tarefas": tarefas_do_pacote
        })

    return {
        "projeto": metadados.get("nome_projeto", "Projeto"),
        "cliente": cliente,
        "tag": tag,
        "prazo_total_uteis": prazo_total_uteis,
        "prazo_total_corridos": metadados.get("prazo_dias_corridos", 100),
        "orcamento_total": metadados.get("orcamento_total", 395500.0),
        "pacotes": pacotes_finais,
        "tarefas": tarefas_finais
    }


if __name__ == "__main__":
    from projeto_extractor import extrair_metadados_projeto
    meta = extrair_metadados_projeto("convertidos")
    rede = gerar_rede_wbs(meta)
    print("=" * 70)
    print(f" REDE WBS GERADA - {rede['projeto']}")
    print(f" Prazo Total: {rede['prazo_total_uteis']} dias úteis ({rede['prazo_total_corridos']} dias corridos)")
    print("=" * 70)
    for pkg in rede["pacotes"]:
        print(f"\n📦 [{pkg['codigo']}] {pkg['nome']} (Peso: {pkg['peso_percentual']}% -> ~{pkg['duracao_alocada']} dias úteis)")
        for t in pkg["tarefas"]:
            deps_str = ", ".join(t["deps"]) if t["deps"] else "Nenhum"
            print(f"   • {t['id']:<4} {t['nome']:<55} | 3P: ({t['otimista']}, {t['provavel']}, {t['pessimista']}) d | Deps: {deps_str}")
