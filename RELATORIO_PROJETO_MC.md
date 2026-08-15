# 📊 Relatório Executivo de Planejamento & Análise de Riscos (Monte Carlo)

**Projeto:** Fabricação e Fornecimento do Tanque de Armazenamento TQ-960-30/1 (API 650) – Obra 2026-000037  
**TAG do Equipamento:** `TQ-0960-30` | **Cliente:** `Oxiteno S.A. / Grupo Indorama`  
**Data da Análise:** 14/08/2026 | **Normas:** `API 650 / NR-13`  

---

## 1. Resumo Executivo e Decisões de Gestão

| Métrica de Cronograma | Valor Calculado | Diretriz de Ação |
| :--- | :---: | :--- |
| **Prazo Contratual Alvo** | **71 dias úteis** (100 dias corridos) | Meta base para medição |
| **Duração Mais Provável (P50)** | **63.6 dias úteis** | Duração central da fabricação |
| **Duração de Segurança (P90)** | **67.5 dias úteis** | Data segura de entrega operacional |
| **Probabilidade de Cumprir Prazo** | **99.4%** | 🟢 Baixo Risco |
| **Buffer de Cronograma Sugerido (P90 − P50)** | **3.9 dias úteis** | Inserir antes da expedição CIF |

| Métrica Financeira | Valor Calculado | Diretriz de Ação |
| :--- | :---: | :--- |
| **Orçamento Base Aprovado** | **R$ 395,500.00** | Preço de venda / baseline |
| **Custo Mais Provável (P50)** | **R$ 418,403.02** | Custo operacional estimado |
| **Contingência Sugerida (P80 − P50)** | **R$ 21,399.86** | Reserva gerencial de contingência |
| **Probabilidade de Estouro Orçamentário** | **82.8%** | Nível de exposição a variações de matéria-prima |

---

## 2. Estrutura Analítica do Projeto (EAP / WBS Ponderada)

Distribuição do tempo global do projeto conforme pesos oficiais dos pacotes de serviço:

| Código | Pacote de Serviço | Peso (%) | Duração Alocada | Atividades Chave |
| :---: | :--- | :---: | :---: | :--- |
| `1.0` | **ATIVIDADES** | **2%** | ~1.4 dias úteis | 2 tarefas (Kick-off Meeting & Alinhamento de R..., Formalização do Termo de Abertura d...) |
| `2.0` | **METODOS E PROCESSOS** | **20%** | ~14.2 dias úteis | 4 tarefas (Projeto Executivo & Detalhamento Me..., Memórias de Cálculo Estrutural e Pr...) |
| `3.0` | **SUPRIMENTOS** | **30%** | ~21.3 dias úteis | 4 tarefas (Requisição de Compras & Cotação de ..., Aquisição de Chapas Inox SA-240 304...) |
| `4.0` | **FABRICAÇÃO E MONTAGEM** | **40%** | ~28.4 dias úteis | 7 tarefas (Traçado, Corte a Plasma e Chanfro d..., Calandragem das Virolas e Pré-Monta...) |
| `5.0` | **PINTURA** | **7%** | ~5.0 dias úteis | 2 tarefas (Decapagem Química e Passivação Inte..., Jateamento e Pintura Externa dos Ac...) |
| `6.0` | **EXPEDIÇÃO** | **1%** | ~1.0 dias úteis | 3 tarefas (Emissão, Compilação e Aprovação do ..., Embalagem Especial, Fabricação do B...) |

---

## 3. Matriz de Criticidade de Atividades (Top Gargalos)

Atividades com maior probabilidade de travar o cronograma global (presença no Caminho Crítico durante as 20.000 iterações):

| WBS | Atividade | 3 Pontos (O, M, P) | Índice de Criticidade | Nível de Atenção |
| :---: | :--- | :---: | :---: | :--- |
| `1.1` | Kick-off Meeting & Alinhamento de Requisitos (Oxiteno S.A. / Grupo Indorama) | `(1, 1, 2) d` | **100.0%** | 🔴 Crítica (100%) |
| `1.2` | Formalização do Termo de Abertura do Projeto (TAP) & Governança | `(1, 1, 2) d` | **100.0%** | 🔴 Crítica (100%) |
| `2.1` | Projeto Executivo & Detalhamento Mecânico 2D/3D (TQ-0960-30) | `(3, 4, 6) d` | **100.0%** | 🔴 Crítica (100%) |
| `4.1` | Traçado, Corte a Plasma e Chanfro das Chapas do Costado e Fundo | `(3, 4, 6) d` | **100.0%** | 🔴 Crítica (100%) |
| `4.2` | Calandragem das Virolas e Pré-Montagem dos Aneis do Costado | `(3, 4, 6) d` | **100.0%** | 🔴 Crítica (100%) |
| `4.3` | Soldagem das Juntas Longitudinais e Circunferencias (ASME IX) | `(4, 6, 9) d` | **100.0%** | 🔴 Crítica (100%) |
| `4.4` | Montagem e Soldagem do Fundo Plano e Teto Cônico Autoportante | `(3, 4, 6) d` | **100.0%** | 🔴 Crítica (100%) |
| `4.5` | Fabricação/Instalação de Bocais A1-W1, Boca de Visita M1 e Guarda-Corpo | `(3, 4, 6) d` | **100.0%** | 🔴 Crítica (100%) |
| `4.6` | Execução de Ensaios END (Radiografia RX, LP, Caixa de Vácuo e PMI) | `(2, 3, 5) d` | **100.0%** | 🔴 Crítica (100%) |
| `4.7` | Preparação e Execução do Teste Hidrostático (TH) Fabril | `(2, 3, 5) d` | **100.0%** | 🔴 Crítica (100%) |

---

## 4. Integração e Entregáveis Gerados

- **Arquivo MS Project XML:** [`cronograma_tanque_tq960.xml`](file:///C:/bento/prg/mc-gerenciamento-projetos/exemplos/cronograma_tanque_tq960.xml): Compatível com MS Project 2010+ com árvore hierárquica WBS e campos Text1..Text5.
- **Histograma de Cronograma:** `assets/mc_cronograma_wbs.png`
- **Histograma de Custos:** `assets/mc_custo_wbs.png`

---
*Relatório gerado automaticamente pelo pipeline inteligente de cronograma e Monte Carlo.*