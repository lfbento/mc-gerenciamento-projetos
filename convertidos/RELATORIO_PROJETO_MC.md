# 📊 Relatório Executivo de Planejamento, MCMC & Nivelamento Bioinspirado

**Projeto:** Fabricação e Fornecimento do Tanque de Armazenamento TQ-960-30/1 (API 650) – Obra 2026-000037  
**TAG do Equipamento:** `TQ-0960-30` | **Cliente:** `Oxiteno S.A. / Grupo Indorama`  
**Data da Análise:** 26/08/2026 | **Normas:** `API 650 / NR-13`  

---

## 1. Cards de Governança de Prazos (Modelagem MCMC)

| PRAZO NOMINAL (CPM) | PREVISÃO MEDIANA (P50) | ALVO GERENCIAL (P85) | NÍVEL CONSERVADOR (P95) |
| :---: | :---: | :---: | :---: |
| **63 dias úteis**<br/>(Soma teórica determinística) | **61.4 dias úteis**<br/>(Meta de chão de fábrica) | **64.3 dias úteis**<br/>(Buffer recomendado: +3.0d) | **66.2 dias úteis**<br/>(Buffer de segurança: +4.9d) |

---

## 2. Quadro de Governança e Perfis de Decisão (Inercial vs. Mitigado)

| Métrica de Cronograma | Prazo Estimado | Buffer Adicional | Prob. Cumprimento | Perfil de Governança Indicado |
| :--- | :---: | :---: | :---: | :--- |
| **Baseline CPM (Nominal)** | **63.0 dias** | +0.0 d | **< 0.1%** | 🔴 **Risco Inaceitável** (Atraso contratual quase garantido) |
| **Mediana Estocástica (P50)** | **61.4 dias** | +0.0 d (base) | **50.0%** | 🟡 **Planejamento Interno** (Meta operacional da fábrica) |
| **Alvo Recomendado (P85)** | **64.3 dias** | **+3.0 d** | 🟢 **85.0%** | 🏆 **Padrão Ouro** para contratos comerciais e SLAs |
| **Buffer Conservador (P95)** | **66.2 dias** | **+4.9 d** | 🟢 **95.0%** | 🛡️ **Missão Crítica** / Multas rescisórias severas |

---

## 3. Estrutura Analítica do Projeto (EAP / WBS Ponderada)

Distribuição do tempo global do projeto conforme pesos oficiais dos pacotes de serviço:

| Código | Pacote de Serviço | Peso (%) | Duração Alocada | Atividades Chave |
| :---: | :--- | :---: | :---: | :--- |
| `1.0` | **ATIVIDADES** | **2%** | ~1.3 dias úteis | 2 tarefas (Kick-off Meeting & Alinhamento de R..., Formalização do Termo de Abertura d...) |
| `2.0` | **METODOS E PROCESSOS** | **20%** | ~12.6 dias úteis | 4 tarefas (Projeto Executivo & Detalhamento Me..., Memórias de Cálculo Estrutural e Pr...) |
| `3.0` | **SUPRIMENTOS** | **30%** | ~18.9 dias úteis | 4 tarefas (Requisição de Compras & Cotação de ..., Fabricação e Entrega de Chapas Inox...) |
| `4.0` | **FABRICAÇÃO E MONTAGEM** | **40%** | ~25.2 dias úteis | 7 tarefas (Traçado, Corte a Plasma e Chanfro d..., Calandragem das Virolas e Pré-Monta...) |
| `5.0` | **PINTURA** | **7%** | ~4.4 dias úteis | 2 tarefas (Decapagem Química e Passivação Inte..., Jateamento e Pintura Externa dos Ac...) |
| `6.0` | **EXPEDIÇÃO** | **1%** | ~0.6 dias úteis | 3 tarefas (Emissão, Compilação e Aprovação do ..., Embalagem Especial, Fabricação do B...) |

---

## 4. Dimensionamento de Mão de Obra e Alocação de Recursos (Storm / SENAI)

| Especialidade / Função | Categoria | HH Total | Taxa Horária | Custo Total de M.O. |
| :--- | :---: | :---: | :---: | :---: |
| **AJUD-OP** - Ajudante Operacional de Caldeiraria e Fábrica | Apoio | 364.0 h | R$ 30.00/h | R$ 10,920.00 |
| **SOLD-ASME** - Soldador Qualificado ASME IX (TIG/MIG/SAW) | Soldagem | 161.6 h | R$ 65.00/h | R$ 10,504.00 |
| **CALD-MONT** - Caldeireiro Montador / Ajustador de Equipamentos | Montagem | 113.6 h | R$ 55.00/h | R$ 6,248.00 |
| **ENG-PROJ** - Engenheiro Mecânico de Projetos / Cálculos | Engenharia | 94.8 h | R$ 110.00/h | R$ 10,428.00 |
| **INSP-END** - Inspetor de Soldagem / END Nível II (SNQC) | Qualidade | 92.0 h | R$ 90.00/h | R$ 8,280.00 |
| **COMP-TEC** - Comprador Técnico Industrial / Diligenciamento | Suprimentos | 69.8 h | R$ 55.00/h | R$ 3,839.00 |
| **PROJ-CAD** - Projetista Mecânico / Modelador 3D | Engenharia | 38.4 h | R$ 65.00/h | R$ 2,496.00 |
| **PINT-IND** - Pintor Industrial / Tratador de Superfície Inox | Tratamento | 35.2 h | R$ 45.00/h | R$ 1,584.00 |
| **CALD-PREP** - Caldeireiro de Traçado e Corte Plasma | Caldeiraria | 30.4 h | R$ 50.00/h | R$ 1,520.00 |
| **OPER-CAL** - Operador de Calandra e Conformação | Caldeiraria | 30.4 h | R$ 50.00/h | R$ 1,520.00 |
| **RIG-LOG** - Rigger / Operador de Carga, Berço e Expedição | Logística | 16.0 h | R$ 45.00/h | R$ 720.00 |
| **TOTAL GERAL DE MÃO DE OBRA** | **Pico Inicial: 4.7 FTEs** | **1046.2 h** | — | **R$ 58,059.00** |

---

## 5. Nivelamento Bioinspirado de Recursos (Algoritmo Genético & MCMC-Safe Float)

| Indicador de Nivelamento | Antes da Otimização (Nominal) | Após Nivelamento Bioinspirado | Ganho Operacional Efetivo |
| :--- | :---: | :---: | :--- |
| **Pico Máximo de Mão de Obra** | 7.5 FTEs | **4.0 FTEs** | 🟢 **Redução de -3.5 profissionais no pico** |
| **Variância da Demanda (σ²)** | 4.62 | **0.85** | 🟢 **Suavização: -81.6% de oscilação** |
| **Carga Total de Trabalho (HH)** | 1046.2 h | **1046.2 h** | **100% de aderência ao escopo fabril** |
| **Prazo Final do Projeto** | 74.2 dias úteis | **61.6 dias úteis** | 🟢 **Redução de -12.6d (≤ Alvo P85)** |

---

## 6. Matriz de Criticidade de Atividades (Top Gargalos Estocásticos)

Atividades com maior probabilidade de travar o cronograma global (presença no Caminho Crítico durante as 20.000 iterações MCMC):

| WBS | Atividade | 3 Pontos (O, M, P) | Índice de Criticidade | Nível de Atenção |
| :---: | :--- | :---: | :---: | :--- |
| `1.1` | Kick-off Meeting & Alinhamento de Requisitos (Oxiteno S.A. / Grupo Indorama) | `(0.8, 1.0, 1.5) d` | **100.0%** | 🔴 Crítica (Ação Imediata) |
| `1.2` | Formalização do Termo de Abertura do Projeto (TAP) & Governança | `(0.8, 1.0, 1.5) d` | **100.0%** | 🔴 Crítica (Ação Imediata) |
| `2.1` | Projeto Executivo & Detalhamento Mecânico 2D/3D (TQ-0960-30) | `(3.0, 3.8, 5.7) d` | **100.0%** | 🔴 Crítica (Ação Imediata) |
| `2.2` | Memórias de Cálculo Estrutural e Pressão (API 650 / ASME) | `(2.6, 3.2, 4.8) d` | **100.0%** | 🔴 Crítica (Ação Imediata) |
| `2.3` | Elaboração do PIT (Plano de Inspeção e Testes) e EPS/RQPS | `(2.0, 2.5, 3.8) d` | **100.0%** | 🔴 Crítica (Ação Imediata) |
| `2.4` | Submissão, Análise e Aprovação Técnica pelo Cliente | `(2.6, 3.2, 4.8) d` | **100.0%** | 🔴 Crítica (Ação Imediata) |
| `3.1` | Requisição de Compras & Cotação de Matérias-Primas Inox | `(2.2, 2.8, 4.2) d` | **100.0%** | 🔴 Crítica (Ação Imediata) |
| `3.4` | Recebimento, Inspeção Dimensional e Rastreabilidade de MP na Fábrica | `(3.8, 4.7, 7.1) d` | **100.0%** | 🔴 Crítica (Ação Imediata) |
| `4.1` | Traçado, Corte a Plasma e Chanfro das Chapas do Costado e Fundo | `(3.0, 3.8, 5.7) d` | **100.0%** | 🔴 Crítica (Ação Imediata) |
| `4.2` | Calandragem das Virolas e Pré-Montagem dos Aneis do Costado | `(3.0, 3.8, 5.7) d` | **100.0%** | 🔴 Crítica (Ação Imediata) |

---

## 7. Plano de Ação Estratégico para a Diretoria (5W2H)

1. **Fast-Tracking em Suprimentos:** Disparar pedido e cotação de chapas inox (SA-240 304) e tubos assim que o projeto preliminar for concluído (**economia de ~8 dias**).
2. **Crashing na Soldagem ASME IX:** Alocar 2 soldadores qualificados em paralelo nas soldas do costado (**economia de ~4 dias**).
3. **Nivelamento de Equipe Fábrica:** Operar com efetivo estável de ~3 a 4 pessoas, evitando custos com horas extras ou contratações de pico temporárias.
4. **Governança de Feeding Buffer:** Fixar meta de fábrica no P50 (61.4d) e contratar no P85 (64.3d), mantendo a margem de -1.3 dias como proteção do PMO.
5. **Reserva de Contingência Financeira:** Provisionar **R$ 20,602.44** (P80-P50) para absorver flutuações de ligas e frete.

---

## 8. Glossário Técnico (Abreviações, Siglas e Conceitos)

| Termo / Sigla | Definição e Aplicação Técnica no Projeto |
| :--- | :--- |
| **EAP / WBS** | **Estrutura Analítica do Projeto** (*Work Breakdown Structure*): Decomposição hierárquica do escopo em pacotes de trabalho ponderados (2%, 20%, 30%, 40%, 7%, 1%). |
| **MCMC** | **Markov Chain Monte Carlo**: Método estocástico que modela a persistência de bloqueios operacionais e alternância de regimes de produtividade. |
| **CPM / PERT** | **Critical Path Method & PERT**: Modelagem clássica determinística baseada em estimativas de 3 pontos (Otimista, Mais Provável, Pessimista). |
| **P50 / P85 / P95** | **Percentis de Confiança Estocástica**: P50 = Mediana interna de fábrica; P85 = Padrão ouro contratual (SLA); P95 = Buffer conservador de missão crítica. |
| **Feeding Buffer** | **Pulmão de Convergência**: Reserva gerenciada pelo PMO (+2.3 dias) para absorver variações sem postergar a entrega final. |
| **FTE & HH** | **Full-Time Equivalent & Homem-Hora**: FTE = dedicação integral de 1 profissional (8h/dia); HH = esforço total de 1 hora de trabalho. |
| **RLP / RCPSP** | **Resource Leveling & Resource-Constrained Scheduling**: Problemas de otimização combinatória para suavização de carga e restrição de recursos. |
| **MCMC-Safe Float** | **Folga Estocástica Segura**: Regra bioinspirada que delimita os deslocamentos pelo Índice de Criticidade ($CI$), blindando tarefas críticas. |
| **GA / SA** | **Algoritmos Genéticos & Simulated Annealing**: Meta-heurísticas bioinspiradas de otimização combinatória. |
| **API 650 & ASME** | Normas técnicas internacionais para tanques de armazenamento atmosférico e qualificação de procedimentos de soldagem (ASME IX). |
| **END (RX/LP/PMI)** | Ensaios Não Destrutivos: Radiografia Industrial (RX), Líquido Penetrante (LP) e Identificação Positiva de Material (PMI). |
| **5W2H** | Matriz de plano de ação estruturada (What, Why, Where, When, Who, How, How Much). |

---

## 9. Entregáveis Gerados

- **Relatório Executivo para a Diretoria (PDF 3 Páginas):** [`RELATORIO_DIRETORIA_MONTE_CARLO.pdf`](file:///C:/bento/prg/mc-gerenciamento-projetos/convertidos/RELATORIO_DIRETORIA_MONTE_CARLO.pdf)
- **Arquivo MS Project XML Nivelado:** [`cronograma_tq-0960-30.xml`](file:///C:/bento/prg/mc-gerenciamento-projetos/convertidos/cronograma_tq-0960-30.xml)
- **Gráfico Comparativo de Nivelamento:** `assets/mc_nivelamento_recursos_comparativo.png`
- **Histograma de Recursos por Função:** `assets/mc_histograma_recursos.png`
- **Gráficos em Assets:** Comparativo MCMC, Sensibilidade de Caminho Crítico e Riscos de Custos.

---
*Relatório gerado automaticamente pelo motor estocástico MCMC e Nivelamento Bioinspirado da skill cronograma-mc.*