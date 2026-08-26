# Guia de Estimativa de Recursos para Fabricação Industrial

## Prompt para LLM: Dimensionamento de Recursos e Cronograma

> **Objetivo:** Este documento serve como base de conhecimento para que um LLM consiga estimar recursos (mão de obra, materiais, tempo, custos) e montar cronogramas de fabricação para estruturas metálicas, equipamentos industriais e tubulação industrial.

---

## 1. ESCOPO DE APLICAÇÃO

Este guia cobre três grandes áreas da fabricação industrial:

1. **Estruturas Metálicas** — plataformas, escadas, guarda-corpos, suportes, racks de tubulação, estruturas de suporte de equipamentos
2. **Equipamentos Industriais** — vasos de pressão, trocadores de calor, tanques, colunas, reatores, condensadores, feixes tubulares
3. **Tubulação Industrial** — tubos processuais, linhas de vapor, utilidades, instrumentação, suportes de tubulação

---

## 2. REFERÊNCIAS BIBLIOGRÁFICAS

### 2.1 Livros Fundamentais

| Livro | Autor/Editora | Uso Principal |
|-------|---------------|---------------|
| Industrial Piping and Equipment Estimating Manual (2ª ed.) | Kenneth Storm / Elsevier | **Referência primária** — tabelas de HH para tubulação e equipamentos |
| Process Plant Construction Estimating Standards | Richardson Engineering / IHS | Bíblia da indústria petroquímica — HH por item |
| Pressure Vessel Design Manual (4ª ed.) | Dennis R. Moss / Gulf Professional | Fabricação de vasos e trocadores |
| Pressure Vessel Design Handbook | Henry H. Bednar | Métodos de fabricação e fatores de custo |
| Piping Estimating Manual | M.D. Rowe / McGraw-Hill | HH para fabricação e montagem de tubulação |
| Piping Handbook (7ª ed.) | Mohinder L. Nayyar / McGraw-Hill | Referência completa de tubulação |
| Means Mechanical Estimating | RSMeans / Gordian | Unidades de trabalho para mecânica/tubulação |
| Cost Estimation: Methods and Tools | Kenneth Humphreys / AACE | Metodologias formais de estimativa |
| Welding Metallurgy | Sindo Kou / Wiley | Processos de soldagem para estimativa de tempo |
| Manual de Soldagem | SENAI | Tabelas de HH para contexto brasileiro |
| Apostila de Caldeiraria | SENAI/SESI | Tabelas de HH para fabricação industrial |

### 2.2 Normas Técnicas

#### ASME (American Society of Mechanical Engineers)
- **ASME BPVC Section VIII** — Projeto e fabricação de vasos de pressão (Div. 1 e 2)
- **ASME B31.1** — Tubulação de potência
- **ASME B31.3** — Tubulação de processo (principal para petroquímica)
- **ASME B16.5 / B16.47** — Flanges
- **ASME PCC-1** — Montagem de juntas flangeadas
- **ASME PCC-2** — Reparo de equipamentos pressurizados

#### AWS (American Welding Society)
- **AWS D1.1** — Código de soldagem estrutural (aço)
- **AWS D1.2** — Código de soldagem estrutural (alumínio)
- **AWS B2.1** — Especificações de procedimentos de soldagem (WPS)
- **AWS A3.0** — Termos e definições de soldagem

#### API (American Petroleum Institute)
- **API 650** — Tanques soldados para armazenamento de óleo
- **API 660** — Trocadores de calor casco-tubo
- **API 661** — Trocadores de calor a ar
- **API 620** — Tanques grandes de baixa pressão
- **API 560** — Fornos de processo
- **API 510 / 653** — Inspeção de vasos/tanques

#### TEMA (Tubular Exchanger Manufacturers Association)
- **Classe R** — Refinaria (mais rigorosa)
- **Classe C** — Comercial/geral
- **Classe B** — Processo químico

#### Normas Brasileiras (ABNT/NR)
- **NBR 8800** — Projeto de estruturas de aço e mistas
- **NBR 8400** — Cargas para cálculo de estruturas
- **NBR 14762** — Estruturas de aço formadas a frio
- **NBR 13476** — Requisitos de execução para estruturas de aço
- **NBR 13537** — Projeto de vasos de pressão
- **NBR 15923** — Trocadores de calor
- **NR-12** — Segurança em máquinas e equipamentos
- **NR-13** — Caldeiras, vasos de pressão e tubulações (obrigatória — adiciona 10-20% ao custo)

#### Normas Petrobras (N-Series)
- **N-133** — Soldagem
- **N-169** — Inspeção
- **N-258** — Ensaio Não Destrutivo (END)

---

## 3. METODOLOGIAS DE ESTIMATIVA

### 3.1 Classificação de Estimativas (AACE International)

| Classe | Maturidade do Projeto | Precisão | Método |
|--------|----------------------|----------|--------|
| 5 | 0–2% definido | ±50% | Fatoração por capacidade, ratios |
| 4 | 1–15% definido | ±30% | Paramétrico, taxa unitária |
| 3 | 10–40% definido | ±15% | Semi-detalhado |
| 2 | 30–70% definido | ±10% | Detalhado |
| 1 | 50–100% definido | ±5% | Totalmente detalhado com cotações |

### 3.2 Métodos de Estimativa

| Método | Melhor Para | Precisão |
|--------|-------------|----------|
| Peso (MH/ton) | Vasos, trocadores, estruturas | ±20–30% |
| Tabelas Richardson/RSMeans | Tubulação, mecânica | ±15–25% |
| Volume de solda | Trabalho intensivo em soldagem | ±10–20% |
| Paramétrico (fatoração) | Estimativas iniciais | ±30–50% |
| Bottom-up (detalhado) | Orçamentos finais | ±5–10% |
| Dados históricos | Trabalho repetitivo/similar | ±10–15% |

---

## 4. FÓRMULAS E TABELAS DE ESTIMATIVA

### 4.1 Soldagem (Fator Mais Crítico)

#### Fórmula Base
```
Homem-hora (MH) = Volume da solda (cm³) / Taxa de deposição (cm³/hr) × (1 + Fator de overhead)
```

#### Volume de Solda (Junta em V simples)
```
V = (t × w × L) / 2
Onde:
  t = espessura da chapa (mm)
  w = largura do chanfro (mm)
  L = comprimento da solda (mm)
```

#### Taxas de Deposição por Processo

| Processo | Taxa (kg/hr) | Taxa (cm³/hr) | Aplicação Típica |
|----------|-------------|---------------|------------------|
| SMAW (Eletrodo revestido) | 1.0–2.5 | 130–325 | Campo, manutenção, reparos |
| FCAW (Arco com fluxo) | 2.5–5.0 | 325–650 | Estruturas, vasos (multipassagem) |
| GMAW (MIG/MAG) | 2.5–6.0 | 325–780 | Estruturas, chapa, produção |
| SAW (Submerso) | 5–25 | 650–3250 | Vasos, tanques (juntas longas) |
| GTAW (TIG) | 0.5–1.5 | 65–195 | Raiz, acabamento, ligas especiais |

#### HH por Solda (Tabelas Richardson)

| Tipo de Junta | Espessura | SMAW (HH) | FCAW (HH) | SAW (HH) |
|---------------|-----------|-----------|-----------|----------|
| Filete (1/4") | — | 0.08–0.12/pe | 0.04–0.06/pe | — |
| Filete (3/8") | — | 0.15–0.22/pe | 0.08–0.12/pe | — |
| Bisel simples | 1/4" | 0.20–0.30/pe | 0.12–0.18/pe | 0.06–0.10/pe |
| Bisel simples | 1/2" | 0.45–0.65/pe | 0.25–0.38/pe | 0.12–0.20/pe |
| Bisel simples | 1" | 1.0–1.5/pe | 0.6–0.9/pe | 0.3–0.5/pe |
| Bisel duplo | 1" | 0.7–1.0/pe | 0.4–0.6/pe | 0.2–0.35/pe |
| Bisel duplo | 2" | 1.8–2.5/pe | 1.0–1.5/pe | 0.5–0.8/pe |

### 4.2 Estruturas Metálicas

#### Método Peso (AISC)
```
Custo fabricação = Peso (ton) × $/ton (taxa loja)
Custo montagem   = Peso (ton) × $/ton (taxa campo)
```

#### Faixas de Referência (valores EUA — aplicar fatores de localização)

| Item | Fabricação Loja | Montagem Campo |
|------|----------------|----------------|
| Estruturas simples | $1,500–$2,500/ton | $800–$1,500/ton |
| Estruturas médias | $2,500–$3,500/ton | $1,500–$2,000/ton |
| Estruturas complexas | $3,500–$5,000/ton | $2,000–$3,000/ton |
| Plataformas/escadas | $3,000–$4,500/ton | $1,800–$2,500/ton |

#### Fatores de Produtividade (MH/100kg)

| Tipo de Elemento | MH/100kg |
|------------------|----------|
| Vigas simples | 0.15–0.25 |
| Conexões complexas | 0.40–0.80 |
| Plataformas/escadas | 0.50–1.20 |
| Suportes de tubulação | 0.30–0.60 |
| Guarda-corpos | 0.40–0.70 |

#### Custo de Conexões
- Parafusos: $15–$40/conexão
- Solda: $25–$80/conexão

### 4.3 Vasos de Pressão e Trocadores de Calor

#### Método Peso com Fatores
```
MH = MH/ton base × Peso (ton) × Fator Complexidade × Fator Material
```

#### Fatores de Complexidade

| Equipamento | Fator |
|-------------|-------|
| Vaso horizontal simples | 1.0 |
| Vaso vertical com pratos | 1.2–1.5 |
| Vaso de alta pressão (>100 bar) | 1.5–2.5 |
| Trocador U-tube | 1.3–1.8 |
| Trocador cabeça flutuante | 1.5–2.0 |
| Trocador cabeça fixa | 1.0–1.3 |
| Coluna com pratos | 1.3–1.8 |
| Reator com agitação | 1.8–2.5 |
| Condensador | 1.2–1.5 |
| Feixe tubular | 1.3–1.7 |

#### Fatores de Material

| Material | Fator |
|----------|-------|
| Aço carbono | 1.0 |
| Aço inox 304/316 | 1.3–1.6 |
| Duplex | 1.5–2.0 |
| Inconel/Monel | 2.0–3.0 |
| Titânio | 2.5–4.0 |
| Hastelloy | 2.5–3.5 |
| Aço baixa liga (Cr-Mo) | 1.2–1.5 |

#### Estimativa por TEMA (Trocadores)
```
Custo = f(Diâmetro casco, Comprimento tubo, Nº tubos, Pressão, Classe TEMA, Materiais)
```

#### MH Base por Tipo de Equipamento (referência — vaso de 1 ton em aço carbono)

| Equipamento | MH/ton base |
|-------------|-------------|
| Vaso de pressão simples | 40–60 |
| Vaso com internals | 60–90 |
| Trocador de calor | 50–80 |
| Tanque atmosférico | 25–40 |
| Coluna | 50–70 |
| Reator | 70–120 |

### 4.4 Tanques (API 650)

```
Custo = f(diâmetro, altura, espessura casco, espessura fundo, material, tipo teto)
```

#### MH para Solda do Casco
```
MH = Circunferência × Nº de fiadas × Área seção solda / Taxa deposição
```

#### Referência de MH/ton para Tanques

| Volume | MH/ton (aço carbono) |
|--------|---------------------|
| < 100 m³ | 30–45 |
| 100–500 m³ | 20–35 |
| 500–5000 m³ | 15–25 |
| > 5000 m³ | 10–20 |

### 4.5 Tubulação Industrial

#### Método Richardson/RSMeans
```
MH = Σ(Comprimento × MH/m por diâmetro/tabela/material)
   + Σ(Nº soldas × MH/solda por tipo/diâmetro)
   + Σ(Nº conexões × MH/conexão)
   + Σ(Nº flanges × MH/flange)
   + Σ(Nº suportes × MH/suporte)
```

#### Método Diameter-Inch (DI)
```
MH = Σ(Nº juntas × Diâmetro em polegadas × Fator DI)
Fator DI típico: 0.08–0.15 MH/DI (depende do processo e material)
```

#### MH por Metro Linear (fabricação loja — aço carbono)

| Diâmetro | Schedule | MH/m |
|----------|----------|------|
| 2" (50mm) | Sch 40 | 0.10–0.16 |
| 3" (80mm) | Sch 40 | 0.15–0.25 |
| 4" (100mm) | Sch 40 | 0.20–0.35 |
| 6" (150mm) | Sch 40 | 0.30–0.50 |
| 8" (200mm) | Sch 40 | 0.45–0.70 |
| 10" (250mm) | Sch 40 | 0.60–0.90 |
| 12" (300mm) | Sch 40 | 0.75–1.10 |
| 16" (400mm) | Sch 40 | 1.00–1.50 |
| 20" (500mm) | Sch 40 | 1.30–2.00 |
| 24" (600mm) | Sch 40 | 1.60–2.50 |

#### Multiplicadores por Material

| Material | Multiplicador |
|----------|--------------|
| Aço carbono | 1.0 |
| Aço inox 304/316 | 1.3–1.5 |
| Duplex | 1.5–1.8 |
| Liga Cr-Mo | 1.2–1.4 |
| Inconel | 1.8–2.5 |
| Titânio | 2.0–3.0 |

#### Fator de Montagem Campo
- Acessível: +30–50%
- Elevado: +50–70%
- Congestionado: +60–80%
- Confined space: +80–120%

#### HH por Tipo de Conexão (solda — aço carbono)

| Conexão | 2" | 4" | 6" | 8" | 12" |
|---------|-----|-----|-----|-----|------|
| Solda butt | 0.15 | 0.35 | 0.60 | 0.90 | 1.50 |
| Solda socket | 0.10 | 0.25 | 0.40 | — | — |
| Flange slip-on | 0.12 | 0.30 | 0.50 | 0.75 | 1.20 |
| Flange weld-neck | 0.20 | 0.45 | 0.75 | 1.10 | 1.80 |
| Tee soldada | 0.25 | 0.55 | 0.90 | 1.35 | 2.20 |

### 4.6 Custo de Material

```
Custo Material = Peso × (Preço base + Prêmio processamento + Fator desperdício)
```

#### Fatores de Desperdício

| Material | Desperdício |
|----------|------------|
| Chapa | 5–10% |
| Perfis estruturais | 3–5% |
| Tubo | 5–8% |
| Conexões/flanges | 2–3% |
| Solda (eletrodo/arame) | 8–15% |

#### Impostos Brasil (sobre material)
- ICMS + IPI + PIS + COFINS: **25–40%** adicionais
- Material importado: **+60–100%** (impostos + frete + desembaraço)

---

## 5. FATORES DE AJUSTE

### 5.1 Produtividade

| Fator | Impacto | Observação |
|-------|---------|------------|
| Clima (frio/chuva) | +10–30% | Trabalho externo |
| Congestão de pessoal | +15–40% | Muitas equipes no mesmo local |
| Elevação (acima de 6m) | +10–25% | Trabalho em altura |
| Horas extras | +5–15% | Após 8h/dia ou 44h/semana |
| Turno noturno | +10–20% | 22h–06h |
| Aprendizado (curva) | -10–20% | Nas primeiras semanas |
| Remoto (longe da base) | +15–30% | Mobilização, alojamento |

### 5.2 Fatores de Localização (vs EUA)

| País/Região | Mão de Obra | Material |
|-------------|------------|----------|
| Brasil (Sudeste) | 0.4–0.7× | 1.0–1.3× |
| Brasil (Norte/Nordeste) | 0.3–0.5× | 1.2–1.5× |
| China | 0.2–0.4× | 0.6–0.8× |
| Índia | 0.15–0.3× | 0.5–0.7× |
| Europa | 0.8–1.2× | 1.0–1.2× |
| Oriente Médio | 0.3–0.6× | 1.1–1.4× |

### 5.3 Fator NR-13 (Brasil — obrigatório)
- Documentação adicional: +5–10%
- Soldadores qualificados: +5–15%
- Inspeções obrigatórias: +5–10%
- **Total NR-13: +10–20% sobre fabricação de vasos/tubulações**

### 5.4 Fator Petrobras (normas N-Series)
- N-133 (soldagem): +5–10%
- N-169 (inspeção): +5–10%
- N-258 (END): +3–8%
- **Total Petrobras: +10–25% adicional**

---

## 6. ESTRUTURA DO CRONOGRAMA

### 6.1 Fases Típicas de Fabricação

```
1. ENGENHARIA E DETALHAMENTO (10–20% do tempo total)
   ├── Detalhamento de fabricação
   ├── Elaboração de WPS/PQR
   ├── Desenhos de fabricação (shop drawings)
   └── Compra de materiais

2. AQUISIÇÃO DE MATERIAL (15–30% do tempo total)
   ├── Chapas e perfis (2–6 semanas)
   ├── Tubos e conexões (4–12 semanas)
   ├── Flanges e varetas (4–8 semanas)
   ├── Solda (eletrodo/arame) (1–2 semanas)
   └── Componentes especiais (8–20 semanas)

3. FABRICAÇÃO EM OFICINA (30–50% do tempo total)
   ├── Corte e preparação
   ├── Soldagem
   ├── Montagem
   ├── Tratamento térmico (se necessário)
   ├── Ensaio não destrutivo (END)
   ├── Teste hidrostático (vasos/tanques)
   └── Acabamento e pintura

4. MONTAGEM EM CAMPO (15–30% do tempo total)
   ├── Recebimento e conferência
   ├── Montagem/ereção
   ├── Soldagem de campo
   ├── Testes de campo
   └── Punch list e liberação
```

### 6.2 Sequência de Fabricação — Vaso de Pressão

```
1. Corte de chapas (1–3 dias)
2. Calandragem (1–2 dias)
3. Soldagem longitudinal do casco (2–5 dias)
4. Montagem de anéis (1–3 dias)
5. Soldagem circunferencial (3–7 dias)
6. Fabricação de fundos (2–4 dias)
7. Soldagem de fundos (2–4 dias)
8. Fabricação de flanges/bocais (3–5 dias)
9. Soldagem de bocais (3–7 dias)
10. Montagem de internals (2–5 dias)
11. Tratamento térmico (1–3 dias)
12. Teste hidrostático (1–2 dias)
13. Inspeção final e documentação (2–5 dias)
14. Pintura/acabamento (2–4 dias)
```

### 6.3 Sequência de Fabricação — Trocador de Calor

```
1. Corte de casco e tubos (2–3 dias)
2. Calandragem do casco (1–2 dias)
3. Soldagem longitudinal do casco (2–3 dias)
4. Fabricação dos espelhos/tubais (3–5 dias)
5. Furação dos espelhos (2–4 dias)
6. Montagem de tubos no espelho (3–7 dias)
7. Expansão de tubos (2–4 dias)
8. Soldagem tubo-espelho (3–7 dias)
9. Montagem do casco (2–3 dias)
10. Soldagem circunferencial (3–5 dias)
11. Soldagem de bocais (3–5 dias)
12. Teste hidrostático (1–2 dias)
13. Inspeção e documentação (2–3 dias)
14. Pintura (2–3 dias)
```

### 6.4 Sequência de Fabricação — Estrutura Metálica

```
1. Corte de perfis e chapas (2–5 dias)
2. Furação/marcação (1–3 dias)
3. Soldagem de sub-módulos (3–7 dias)
4. Montagem de módulos (3–5 dias)
5. Inspeção de solda (1–2 dias)
6. Pintura (2–4 dias)
7. Transporte (1–3 dias)
8. Montagem em campo (5–15 dias)
9. Soldagem de campo (3–7 dias)
10. Inspeção final (1–2 dias)
```

### 6.5 Sequência de Fabricação — Tubulação

```
1. Corte de tubos (contínuo)
2. Preparação de extremidades (contínuo)
3. Soldagem em oficina (spools) (contínuo)
4. END de spools (contínuo)
5. Pintura/revestimento (contínuo)
6. Transporte para campo (logística)
7. Montagem de spools em campo (contínuo)
8. Soldagem de campo (contínuo)
9. END de campo (contínuo)
10. Teste hidrostático/pneumático (por sistema)
11. Punch list e liberação (por sistema)
```

---

## 7. DADOS HISTÓRICOS DE REFERÊNCIA

### 7.1 Benchmarks de Produtividade

| Item | Produtividade Típica |
|------|---------------------|
| Corte oxicorte (chapa 12mm) | 3–5 m/hr |
| Corte plasma | 8–15 m/hr |
| Calandragem (chapa 12mm) | 2–4 peças/hr |
| Soldagem SAW (vaso, circunferencial) | 1.5–3.0 m/hr |
| Soldagem FCAW (estrutura) | 0.8–1.5 m/hr |
| Montagem de tubos em espelho | 15–30 tubos/hr |
| Expansão de tubos | 20–40 tubos/hr |
| Furação de espelho (CNC) | 30–60 furos/hr |
| Pintura (spray) | 80–150 m²/hr |

### 7.2 Equipes Típicas

| Atividade | Equipe Típica |
|-----------|--------------|
| Soldagem estrutural | 1 soldador + 1 ajudante |
| Soldagem de vaso | 2 soldadores + 2 ajudantes |
| Montagem de tubulação | 1 soldador + 1 encanador + 1 ajudante |
| Corte/preparação | 1 torneiro/cortador + 1 ajudante |
| Pintura | 1 pintor + 1 ajudante |
| Inspeção END | 1 inspetor |

---

## 8. TEMPLATE DE ESTIMATIVA

### 8.1 Estrutura de WBS (Work Breakdown Structure)

```
PROJETO
├── 1. ENGENHARIA
│   ├── 1.1 Detalhamento
│   ├── 1.2 WPS/PQR
│   └── 1.3 Shop Drawings
├── 2. AQUISIÇÃO
│   ├── 2.1 Chapas e perfis
│   ├── 2.2 Tubos e conexões
│   ├── 2.3 Flanges e acessórios
│   └── 2.4 Material de solda
├── 3. FABRICAÇÃO — ESTRUTURAS
│   ├── 3.1 Corte e preparação
│   ├── 3.2 Soldagem
│   ├── 3.3 Montagem
│   ├── 3.4 Pintura
│   └── 3.5 Inspeção
├── 4. FABRICAÇÃO — EQUIPAMENTOS
│   ├── 4.1 Vasos de pressão
│   ├── 4.2 Trocadores de calor
│   ├── 4.3 Tanques
│   └── 4.4 Colunas/reatores
├── 5. FABRICAÇÃO — TUBULAÇÃO
│   ├── 5.1 Spools de oficina
│   ├── 5.2 Suportes
│   └── 5.3 Pintura/revestimento
├── 6. MONTAGEM EM CAMPO
│   ├── 6.1 Estruturas
│   ├── 6.2 Equipamentos
│   ├── 6.3 Tubulação
│   └── 6.4 Testes e liberação
└── 7. COMISSIONAMENTO
    ├── 7.1 Testes hidrostáticos
    ├── 7.2 Punch list
    └── 7.3 Documentação final
```

### 8.2 Template de Planilha de Estimativa

Para cada item, preencher:

| Campo | Descrição |
|-------|-----------|
| **Item** | Código WBS |
| **Descrição** | Nome do item |
| **Quantidade** | Peso (ton), comprimento (m), unidade |
| **MH/Unidade** | Homem-hora por unidade (das tabelas acima) |
| **MH Total** | Quantidade × MH/Unidade |
| **Fator Material** | Multiplicador por material |
| **Fator Complexidade** | Multiplicador por complexidade |
| **Fator Localização** | Multiplicador por região |
| **MH Ajustado** | MH Total × Fatores |
| **Equipe** | Nº de pessoas na equipe |
| **Duração** | MH Ajustado / (Equipe × 8h/dia × eficiência) |
| **Custo Mão de Obra** | MH Ajustado × $/MH |
| **Custo Material** | Peso × $/kg × (1 + desperdício) × (1 + impostos) |
| **Custo Total** | Mão de Obra + Material + Subcontratação |

---

## 9. EXEMPLO DE APLICAÇÃO

### 9.1 Exemplo: Vaso de Pressão (5 ton, aço carbono, ASME VIII Div.1)

```
Dados:
  Peso: 5 ton
  Material: Aço carbono SA-516 Gr.70
  Diâmetro: 1200mm
  Comprimento: 4000mm
  Pressão: 15 bar
  Complexidade: Vaso horizontal com 4 bocais

Cálculo:
  MH/ton base (vaso simples): 50 MH/ton
  Fator complexidade (com bocais): 1.3
  Fator material (aço carbono): 1.0
  Fator NR-13: 1.15

  MH fabricação = 50 × 5 × 1.3 × 1.0 × 1.15 = 373.75 MH

  Equipe: 2 soldadores + 2 ajudantes = 4 pessoas
  Eficiência: 75%
  Dias úteis = 373.75 / (4 × 8 × 0.75) = 15.6 dias ≈ 16 dias úteis

  Custo MH (Brasil): R$ 80/MH (média)
  Custo mão de obra: 373.75 × R$ 80 = R$ 29.900

  Material: 5 ton × R$ 8.000/ton = R$ 40.000
  Desperdício (7%): R$ 2.800
  Impostos (30%): R$ 12.840
  Custo material total: R$ 55.640

  Custo total estimado: R$ 85.540
  Duração: ~16 dias úteis (3.2 semanas)
```

### 9.2 Exemplo: Estrutura Metálica (20 ton, aço carbono)

```
Dados:
  Peso: 20 ton
  Tipo: Plataforma com escadas e guarda-corpos
  Material: Aço carbono ASTM A36

Cálculo:
  Fabricação loja:
    MH/ton (plataforma): 0.80 MH/100kg = 8 MH/ton
    MH loja = 8 × 20 = 160 MH
    Equipe: 2 soldadores + 2 ajudantes = 4
    Dias = 160 / (4 × 8 × 0.75) = 6.7 ≈ 7 dias

  Montagem campo:
    MH/ton (campo): 0.50 MH/100kg = 5 MH/ton
    MH campo = 5 × 20 = 100 MH
    Fator elevação (+15%): 115 MH
    Equipe: 2 montadores + 1 soldador + 1 ajudante = 4
    Dias = 115 / (4 × 8 × 0.70) = 5.1 ≈ 6 dias

  Total MH: 275 MH
  Duração total: ~13 dias úteis (2.6 semanas)

  Custo MH: 275 × R$ 80 = R$ 22.000
  Material: 20 ton × R$ 7.000/ton = R$ 140.000
  Impostos/desperdício: R$ 46.200
  Custo total: ~R$ 208.200
```

### 9.3 Exemplo: Tubulação (200m de 6" Sch40, aço carbono)

```
Dados:
  Comprimento: 200m
  Diâmetro: 6" Sch 40
  Material: Aço carbono API 5L Gr.B
  Soldas estimadas: ~80 juntas (a cada 2.5m em média)

Cálculo:
  Tubulação:
    MH/m (6" Sch40): 0.40 MH/m
    MH tubulação = 200 × 0.40 = 80 MH

  Soldas:
    MH/solda (6" butt): 0.60 MH
    MH soldas = 80 × 0.60 = 48 MH

  Conexões/flanges:
    Estimativa: 40 peças × 0.35 MH = 14 MH

  Suportes:
    Estimativa: 30 suportes × 0.50 MH = 15 MH

  Total loja: 157 MH
  Montagem campo (+50%): 235.5 MH
  Total: 392.5 MH

  Equipe: 1 soldador + 1 encanador + 1 ajudante = 3
  Dias = 392.5 / (3 × 8 × 0.75) = 21.8 ≈ 22 dias úteis

  Custo MH: 392.5 × R$ 80 = R$ 31.400
  Material: 200m × R$ 350/m + conexões = R$ 85.000
  Custo total: ~R$ 116.400
```

---

## 10. CHECKLIST DE ESTIMATIVA

Antes de finalizar uma estimativa, verificar:

- [ ] Quantidades conferidas (peso, comprimento, unidades)
- [ ] Material correto identificado (especificação, schedule, TEMA class)
- [ ] Fatores de complexidade aplicados
- [ ] Fatores de material aplicados
- [ ] Fatores de localização aplicados
- [ ] Impostos incluídos (ICMS, IPI, PIS, COFINS)
- [ ] Desperdício incluído
- [ ] NR-13 considerado (se aplicável)
- [ ] Normas do cliente consideradas (Petrobras N-series, etc.)
- [ ] Logística/transporte incluído
- [ ] Pintura/revestimento incluído
- [ ] END/testes incluídos
- [ ] Documentação incluída
- [ ] Contingência aplicada (5–15%)
- [ ] Curva de aprendizado considerada (se primeiro lote)
- [ ] Horas extras consideradas (se prazo apertado)
- [ ] Clima considerado (se trabalho externo)

---

## 11. SOFTWARES FERRAMENTAS

| Software | Uso |
|----------|-----|
| RSMeans / Gordian | Banco de dados de custos com código postal |
| Aspen Capital Cost Estimator (ACCE) | Estimativa de plantas de processo |
| Primavera (Oracle) | Cronograma e recursos |
| MS Project | Cronograma e recursos |
| HCSS HeavyBid | Estimativa para construção pesada |
| InEight Estimate | Estimativa industrial |
| STACK / PlanSwift / Bluebeam | Digital takeoff (medição de quantidades) |
| SAP PS | Planejamento de recursos |
| SINAPI | Índices de custo Brasil |
| CUB/INCC | Índices de custo construção Brasil |

---

## 12. REFERÊNCIAS WEB

- AACE International: https://www.aacei.org/
- RSMeans/Gordian: https://www.gordian.com/
- Richardson Engineering: https://www.ihs.com/
- TEMA Standards: https://www.tema.org/
- ASME: https://www.asme.org/
- AWS: https://www.aws.org/
- API: https://www.api.org/
- SINAPI: https://www.caixa.gov.br/voce/habitacao/sinapi/Paginas/default.aspx

---

*Documento gerado em 25/08/2026 — Hermes Agent para Bento*
*Baseado em pesquisa de literatura técnica, normas industriais e práticas de mercado*
