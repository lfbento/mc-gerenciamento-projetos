# 📊 Relatório Executivo de Planejamento & Análise de Riscos (Monte Carlo)

**Projeto:** Fabricação e Fornecimento do Tanque de Armazenamento TQ-960-30/1 (API 650) – Obra 2026-000037  
**TAG do Equipamento:** `TQ-0960-30` | **Cliente:** `Oxiteno S.A. / Grupo Indorama`  
**Data da Análise:** 14/08/2026 | **Normas:** `API 650 / NR-13`  

---

## 1. Resumo Executivo e Decisões de Gestão

| Métrica de Cronograma | Valor Calculado | Diretriz de Ação |
| :--- | :---: | :--- |
| **Prazo Contratual Alvo** | **71 dias úteis** (100 dias corridos) | Meta base para medição |
| **Duração Mais Provável (P50)** | **81.3 dias úteis** | Duração central da fabricação |
| **Duração de Segurança (P90)** | **85.3 dias úteis** | Data segura de entrega operacional |
| **Probabilidade de Cumprir Prazo** | **0.0%** | 🔴 Alto Risco de Atraso |
| **Buffer de Cronograma Sugerido (P90 − P50)** | **4.0 dias úteis** | Inserir antes da expedição CIF |

| Métrica Financeira | Valor Calculado | Diretriz de Ação |
| :--- | :---: | :--- |
| **Orçamento Base Aprovado** | **R$ 395,500.00** | Preço de venda / baseline |
| **Custo Mais Provável (P50)** | **R$ 413,384.55** | Custo operacional estimado |
| **Contingência Sugerida (P80 − P50)** | **R$ 19,972.62** | Reserva gerencial de contingência |
| **Probabilidade de Estouro Orçamentário** | **77.8%** | Nível de exposição a variações de matéria-prima |

---

## 2. Estrutura Analítica do Projeto (EAP / WBS Ponderada)

Distribuição do tempo global do projeto conforme pesos oficiais dos pacotes de serviço:

| Código | Pacote de Serviço | Peso (%) | Duração Alocada | Atividades Chave |
| :---: | :--- | :---: | :---: | :--- |
| `1.0` | **ATIVIDADES** | **2%** | ~1.4 dias úteis | 2 tarefas (Kick-off Meeting & Alinhamento de R..., Formalização do Termo de Abertura d...) |
| `2.0` | **METODOS E PROCESSOS** | **20%** | ~14.2 dias úteis | 4 tarefas (Projeto Executivo & Detalhamento Me..., Memórias de Cálculo Estrutural e Pr...) |
| `3.0` | **SUPRIMENTOS** | **30%** | ~21.3 dias úteis | 4 tarefas (Requisição de Compras & Cotação de ..., Fabricação e Entrega de Chapas Inox...) |
| `4.0` | **FABRICAÇÃO E MONTAGEM** | **40%** | ~28.4 dias úteis | 7 tarefas (Traçado, Corte a Plasma e Chanfro d..., Calandragem das Virolas e Pré-Monta...) |
| `5.0` | **PINTURA** | **7%** | ~5.0 dias úteis | 2 tarefas (Decapagem Química e Passivação Inte..., Jateamento e Pintura Externa dos Ac...) |
| `6.0` | **EXPEDIÇÃO** | **1%** | ~0.7 dias úteis | 3 tarefas (Emissão, Compilação e Aprovação do ..., Embalagem Especial, Fabricação do B...) |

---

## 3. Matriz de Criticidade de Atividades (Top Gargalos)

Atividades com maior probabilidade de travar o cronograma global (presença no Caminho Crítico durante as 20.000 iterações):

| WBS | Atividade | 3 Pontos (O, M, P) | Índice de Criticidade | Nível de Atenção |
| :---: | :--- | :---: | :---: | :--- |
| `1.1` | Kick-off Meeting & Alinhamento de Requisitos (Oxiteno S.A. / Grupo Indorama) | `(0.8, 1.0, 1.5) d` | **100.0%** | 🔴 Crítica (100%) |
| `1.2` | Formalização do Termo de Abertura do Projeto (TAP) & Governança | `(0.8, 1.0, 1.5) d` | **100.0%** | 🔴 Crítica (100%) |
| `2.1` | Projeto Executivo & Detalhamento Mecânico 2D/3D (TQ-0960-30) | `(3.4, 4.3, 6.4) d` | **100.0%** | 🔴 Crítica (100%) |
| `2.2` | Memórias de Cálculo Estrutural e Pressão (API 650 / ASME) | `(2.9, 3.6, 5.4) d` | **100.0%** | 🔴 Crítica (100%) |
| `2.3` | Elaboração do PIT (Plano de Inspeção e Testes) e EPS/RQPS | `(2.2, 2.8, 4.2) d` | **100.0%** | 🔴 Crítica (100%) |
| `2.4` | Submissão, Análise e Aprovação Técnica pelo Cliente | `(2.9, 3.6, 5.4) d` | **100.0%** | 🔴 Crítica (100%) |
| `3.1` | Requisição de Compras & Cotação de Matérias-Primas Inox | `(2.6, 3.2, 4.8) d` | **100.0%** | 🔴 Crítica (100%) |
| `3.2` | Fabricação e Entrega de Chapas Inox SA-240 304 e Tubos pela Usina | `(10.2, 12.8, 19.2) d` | **100.0%** | 🔴 Crítica (100%) |
| `3.4` | Recebimento, Inspeção Dimensional e Rastreabilidade de MP na Fábrica | `(4.2, 5.3, 7.9) d` | **100.0%** | 🔴 Crítica (100%) |
| `4.1` | Traçado, Corte a Plasma e Chanfro das Chapas do Costado e Fundo | `(3.4, 4.3, 6.4) d` | **100.0%** | 🔴 Crítica (100%) |

---

## 4. Integração e Entregáveis Gerados

- **Arquivo MS Project XML:** [`cronograma_tanque_tq960.xml`](file:///C:/bento/prg/mc-gerenciamento-projetos/exemplos/cronograma_tanque_tq960.xml): Compatível com MS Project 2010+ com árvore hierárquica WBS e campos Text1..Text5.
- **Histograma de Cronograma:** `assets/mc_cronograma_wbs.png`
- **Histograma de Custos:** `assets/mc_custo_wbs.png`

---
*Relatório gerado automaticamente pelo pipeline inteligente de cronograma e Monte Carlo.*