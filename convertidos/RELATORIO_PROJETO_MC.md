# 📊 Relatório Executivo de Planejamento & Análise de Riscos (MCMC & Governança)

**Projeto:** Fabricação e Fornecimento do Tanque de Armazenamento TQ-960-30/1 (API 650) – Obra 2026-000037  
**TAG do Equipamento:** `TQ-0960-30` | **Cliente:** `Oxiteno S.A. / Grupo Indorama`  
**Data da Análise:** 25/08/2026 | **Normas:** `API 650 / NR-13`  

---

## 1. Cards de Governança de Prazos (Modelagem MCMC)

| PRAZO NOMINAL (CPM) | PREVISÃO MEDIANA (P50) | ALVO GERENCIAL (P85) | NÍVEL CONSERVADOR (P95) |
| :---: | :---: | :---: | :---: |
| **71 dias úteis**<br/>(Soma teórica determinística) | **65.5 dias úteis**<br/>(Meta de chão de fábrica) | **68.7 dias úteis**<br/>(Buffer recomendado: +3.2d) | **70.7 dias úteis**<br/>(Buffer de segurança: +5.2d) |

---

## 2. Quadro de Governança e Perfis de Decisão (Inercial vs. Mitigado)

| Métrica de Cronograma | Prazo Estimado | Buffer Adicional | Prob. Cumprimento | Perfil de Governança Indicado |
| :--- | :---: | :---: | :---: | :--- |
| **Baseline CPM (Nominal)** | **71.0 dias** | +0.0 d | **< 0.1%** | 🔴 **Risco Inaceitável** (Atraso contratual quase garantido) |
| **Mediana Estocástica (P50)** | **65.5 dias** | +0.0 d (base) | **50.0%** | 🟡 **Planejamento Interno** (Meta operacional da fábrica) |
| **Alvo Recomendado (P85)** | **68.7 dias** | **+3.2 d** | 🟢 **85.0%** | 🏆 **Padrão Ouro** para contratos comerciais e SLAs |
| **Buffer Conservador (P95)** | **70.7 dias** | **+5.2 d** | 🟢 **95.0%** | 🛡️ **Missão Crítica** / Multas rescisórias severas |

---

## 3. Estrutura Analítica do Projeto (EAP / WBS Ponderada)

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

## 4. Matriz de Criticidade de Atividades (Top Gargalos Estocásticos)

Atividades com maior probabilidade de travar o cronograma global (presença no Caminho Crítico durante as 20.000 iterações MCMC):

| WBS | Atividade | 3 Pontos (O, M, P) | Índice de Criticidade | Nível de Atenção |
| :---: | :--- | :---: | :---: | :--- |
| `1.1` | Kick-off Meeting & Alinhamento de Requisitos (Oxiteno S.A. / Grupo Indorama) | `(0.8, 1.0, 1.5) d` | **100.0%** | 🔴 Crítica (>90%) |
| `1.2` | Formalização do Termo de Abertura do Projeto (TAP) & Governança | `(0.8, 1.0, 1.5) d` | **100.0%** | 🔴 Crítica (>90%) |
| `2.1` | Projeto Executivo & Detalhamento Mecânico 2D/3D (TQ-0960-30) | `(3.4, 4.3, 6.4) d` | **100.0%** | 🔴 Crítica (>90%) |
| `2.2` | Memórias de Cálculo Estrutural e Pressão (API 650 / ASME) | `(2.9, 3.6, 5.4) d` | **100.0%** | 🔴 Crítica (>90%) |
| `2.3` | Elaboração do PIT (Plano de Inspeção e Testes) e EPS/RQPS | `(2.2, 2.8, 4.2) d` | **100.0%** | 🔴 Crítica (>90%) |
| `2.4` | Submissão, Análise e Aprovação Técnica pelo Cliente | `(2.9, 3.6, 5.4) d` | **100.0%** | 🔴 Crítica (>90%) |
| `3.1` | Requisição de Compras & Cotação de Matérias-Primas Inox | `(2.6, 3.2, 4.8) d` | **100.0%** | 🔴 Crítica (>90%) |
| `3.4` | Recebimento, Inspeção Dimensional e Rastreabilidade de MP na Fábrica | `(4.2, 5.3, 7.9) d` | **100.0%** | 🔴 Crítica (>90%) |
| `4.1` | Traçado, Corte a Plasma e Chanfro das Chapas do Costado e Fundo | `(3.4, 4.3, 6.4) d` | **100.0%** | 🔴 Crítica (>90%) |
| `4.2` | Calandragem das Virolas e Pré-Montagem dos Aneis do Costado | `(3.4, 4.3, 6.4) d` | **100.0%** | 🔴 Crítica (>90%) |

---

## 5. Plano de Ação Estratégico para a Diretoria (5W2H)

1. **Fast-Tracking em Suprimentos:** Disparar pedido e cotação de chapas inox (SA-240 304) e tubos assim que o projeto preliminar for concluído (**economia de ~8 dias**).
2. **Crashing na Soldagem ASME IX:** Alocar 2 soldadores qualificados em paralelo nas soldas do costado (**economia de ~4 dias**).
3. **Governança de Feeding Buffer:** Fixar meta de fábrica no P50 (65.5d) e contratar no P85 (68.7d), mantendo a margem de 2.3 dias como proteção do PMO.
4. **Reserva de Contingência Financeira:** Provisionar **R$ 20,602.44** (P80-P50) para absorver flutuações de ligas e frete.

---

## 6. Entregáveis Gerados

- **Relatório Executivo para a Diretoria (PDF 3 Páginas):** [`RELATORIO_DIRETORIA_MONTE_CARLO.pdf`](file:///C:/bento/prg/mc-gerenciamento-projetos/convertidos/RELATORIO_DIRETORIA_MONTE_CARLO.pdf)
- **Arquivo MS Project XML:** [`cronograma_tq-0960-30.xml`](file:///C:/bento/prg/mc-gerenciamento-projetos/convertidos/cronograma_tq-0960-30.xml)
- **Gráficos em Assets:** Comparativo de Cenários MCMC, Sensibilidade do Caminho Crítico e Riscos de Custos.

---
*Relatório gerado automaticamente pelo motor estocástico MCMC da skill cronograma-mc.*