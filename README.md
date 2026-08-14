# Monte Carlo para Gerenciamento de Projetos

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Deps](https://img.shields.io/badge/deps-numpy%20%2B%20matplotlib-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Repo](https://img.shields.io/badge/GitHub-lfbento%2Fmc--gerenciamento--projetos-181717?logo=github)

Simulação de **Monte Carlo aplicada a cronograma e custo de projetos**,
com exportação direta para o **MS Project** (Project XML / MSPDI).

O exemplo embutido é realista: fabricação de **2 trocadores de calor
casco-e-tubo** (caldeiraria, padrão ASME) para cliente Petrobras — mas a
lógica serve para qualquer projeto com estimativas de 3 pontos.

## O que os scripts fazem

| Script | Função |
|---|---|
| `mc_projetos.py` | Simula 20.000 iterações de cronograma (PERT/CPM + distribuição triangular) e custo; calcula percentis P10/P50/P90, probabilidade de cumprir prazo, índice de criticidade e contingência (P80−P50); gera histogramas |
| `gerar_msproject.py` | Converte a rede de tarefas em arquivo `.xml` que o MS Project abre nativamente: vínculos FS, campos customizados (Otimista/Provável/Pessimista) e resumo do MC nos metadados |
| `openproject_to_xml.py` | Puxa tarefas de um projeto do **OpenProject** (API v3) e gera o mesmo Project XML — pipeline OpenProject → MS Project |

## Resultados (cronograma)

![Cronograma - Monte Carlo](assets/mc_cronograma.png)

```
 Duracao do projeto (dias):
   Media:   40.7 | P10:  34.3 | P50:  40.4 | P90:  47.7
 P(terminar <= 45 dias):  78.9%
 P(estourar > 50 dias):   4.5%

 Indice de criticidade (caminho critico em % das simulacoes):
   A Detalhamento / desenhos de fabricacao       100.0%
   B Compra de materiais (casco, espelhos, tubos) 100.0%
   E Montagem do feixe tubular (expansao)          3.7%
```

## Resultados (custo)

![Custo - Monte Carlo](assets/mc_custo.png)

```
 Custo total (R$ mil):
   Media: 480.2 | P50: 479.2 | P80: 505.3 | P90: 519.7
 Contingencia sugerida (P80 - P50): R$ 26.1 mil
 P(estourar o orcamento de 520): 9.8%
```

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

```bash
# 1) Rodar o Monte Carlo (cronograma + custo)
python3 mc_projetos.py

# 2) Gerar cronograma para MS Project (inicio = proxima segunda-feira)
python3 gerar_msproject.py

#    opcoes do gerador
python3 gerar_msproject.py --inicio 2026-09-01   # data de inicio custom
python3 gerar_msproject.py --base p50            # duracoes = P50 do MC
python3 gerar_msproject.py --prazo 50            # prazo p/ relatorio MC

# 3) Integracao com OpenProject (API v3)
python3 openproject_to_xml.py --projetos                         # lista projetos
python3 openproject_to_xml.py --url http://192.168.100.65:8080 \
        --key SUA_API_KEY --projeto 1                            # gera o XML
python3 openproject_to_xml.py --mock                             # testa sem servidor
```

No MS Project: **Arquivo → Abrir** e selecionar o `.xml` (o Project
converte para `.mpp` ao salvar).

## Metodologia

1. **Estimativas de 3 pontos** por atividade: `(otimista, provável, pessimista)`
   — o "pessimista" honesto é onde a incerteza mora (fornecedor atrasando,
   retrabalho de solda, inspeção)
2. **Distribuição triangular** para amostragem (ou PERT/beta para caudas
   mais suaves)
3. **PERT/CPM com forward/backward pass** por iteração → distribuição da
   duração total, caminho crítico por simulação e **índice de criticidade**
   (% das simulações em que a tarefa trava o projeto)
4. **Decisões**: buffer de cronograma (P90 − P50), contingência de custo
   (P80 − P50), atacar as tarefas com maior variância

## Integração OpenProject — limitações honestas

- O OpenProject nativo não tem estimativa de 3 pontos: o script usa
  `estimatedTime` como "provável" e deriva otimista/pessimista (0.7×/1.6×).
  Se o projeto tiver campos customizados, use `--campo-o/--campo-m/--campo-p`.
- Vínculos de precedência não são expostos na API v3 sem consultar relações
  por pacote: por padrão as tarefas são encadeadas em **FS na ordem de
  exibição** (simplificação documentada).

## FAQ

**Por que XML e não `.mpp`?**
`.mpp` é formato binário proprietário da Microsoft — não existe gerador
confiável fora do Windows. O **Project XML (MSPDI)** é o formato oficial de
intercâmbio, aberto nativamente pelo MS Project 2010+. No Windows, também é
possível gerar `.mpp` direto via COM (`pywin32`).

**Por que a duração média (40,7) é maior que o P50 (40,4)?**
A distribuição do projeto tem cauda à direita (atrasos pesam mais que
adiantamentos) — a média é puxada pelos cenários ruins. Por isso o P50/P90
são mais informativos que a média.

**O que é o índice de criticidade?**
Em cada uma das 20.000 simulações, o caminho crítico pode mudar. O índice
diz em quantos % das simulações a tarefa esteve no caminho crítico —
100% = sempre crítica, 3,7% = quase nunca trava o projeto.

## Estrutura

```
mc-gerenciamento-projetos/
├── mc_projetos.py              # simulacao de Monte Carlo
├── gerar_msproject.py          # gerador de Project XML
├── openproject_to_xml.py       # integracao OpenProject -> Project XML
├── requirements.txt
├── assets/                     # histogramas gerados
│   ├── mc_cronograma.png
│   └── mc_custo.png
└── exemplos/
    └── cronograma_trocadores.xml   # cronograma gerado (abrir no MS Project)
```

## Licença

MIT
