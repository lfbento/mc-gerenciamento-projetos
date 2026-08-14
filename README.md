# Monte Carlo para Gerenciamento de Projetos

Simulação de Monte Carlo aplicada a cronograma e custo de projetos,
com exportação direta para o **MS Project** (Project XML / MSPDI).

Exemplo realista embutido: fabricação de 2 trocadores de calor
casco-e-tubo (caldeiraria, padrão ASME) para cliente Petrobras.

## O que os scripts fazem

| Script | Função |
|---|---|
| `mc_projetos.py` | Simula 20.000 iterações de cronograma (PERT/CPM + triangular) e custo; gera histogramas com percentis P10/P50/P90, probabilidade de cumprir prazo, índice de criticidade e contingência (P80−P50) |
| `gerar_msproject.py` | Converte a mesma rede de tarefas em arquivo `.xml` que o MS Project abre nativamente, com vínculos FS, campos customizados (Otimista/Provável/Pessimista) e resumo do MC nos metadados |

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

# opcoes do gerador
python3 gerar_msproject.py --inicio 2026-09-01   # data de inicio custom
python3 gerar_msproject.py --base p50            # duracoes = P50 do MC
python3 gerar_msproject.py --prazo 50            # prazo p/ relatorio MC
```

No MS Project: **Arquivo → Abrir** e selecionar o `.xml` (o Project converte
para `.mpp` ao salvar).

## Exemplo de saída (cronograma)

```
 Duracao do projeto (dias):
   Media:   40.7 | P10:  34.3 | P50:  40.4 | P90:  47.7
 P(terminar <= 45 dias):  78.9%
 Indice de criticidade (caminho critico em % das simulacoes):
   A Detalhamento / desenhos de fabricacao      100.0%
   B Compra de materiais (casco, espelhos, tubos) 100.0%
   E Montagem do feixe tubular (expansao)         3.7%
```

## Por que XML e não .mpp?

`.mpp` é formato binário proprietário da Microsoft — não existe gerador
confiável fora do Windows. O **Project XML (MSPDI)** é o formato oficial de
intercâmbio e é aberto nativamente pelo MS Project 2010+. No Windows, também
é possível gerar `.mpp` direto via COM (`pywin32`).

## Estrutura

```
mc-gerenciamento-projetos/
├── mc_projetos.py              # simulacao de Monte Carlo
├── gerar_msproject.py          # gerador de Project XML
├── requirements.txt
└── exemplos/
    └── cronograma_trocadores.xml   # cronograma gerado (abrir no MS Project)
```

## Licença

MIT
