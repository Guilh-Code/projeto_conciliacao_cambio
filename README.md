# projeto_conciliacao_cambio

# 🚀 Sistema Automatizado de Conciliação Financeira e Governança de Dados

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/SQL_Server-2022-CC2927?style=for-the-badge&logo=microsoft-sql-server&logoColor=white" alt="SQL Server">
  <img src="https://img.shields.io/badge/Pandas-ETL-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/SQLAlchemy-ORM-D71F27?style=for-the-badge&logo=redhat&logoColor=white" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/Git-Controle_de_Versão-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git">
</p>

## 📋 Visão Geral do Projeto

Este repositório contém um **Pipeline de Engenharia e Governança de Dados** completo de ponta a ponta (*End-to-End*), desenvolvido para resolver um dos problemas mais críticos e complexos de instituições financeiras e corretoras de câmbio: a **Conciliação Automatizada de Transações em Larga Escala**.

O objetivo principal deste projeto é atuar como um motor customizado de auditoria interna, capaz de receber milhares de registros brutos de vendas (sistemas internos) e confrontá-los com os extratos consolidados dos bancos liquidantes. O sistema identifica discrepâncias de valores causadas por tarifas ocultas, atrasos de processamento bancário e transações não reconhecidas, gerando métricas de eficiência operacional e logs de auditoria automatizados.

---

## 🏗️ Arquitetura e Fluxo do Pipeline

O projeto foi estruturado utilizando o conceito moderno de esteira cronológica e desacoplamento de estágios, garantindo que cada script execute uma função única e essencial dentro do fluxo de dados:

```text
[ Camada Local ]          [ Área de Pouso ]         [ Camada Analítica ]         [ Governança ]
1_gerador_dados.py  --->  2_setup_banco.sql  --->   4_3_logica_conciliacao.sql ---> 4_4_views_relatorios.sql
      |                         ▲                           ▲                          
      └── (CSV brutos) ─────────┘                           │
                 │                                          │
        3_ingestao_dados.py (ETL) ──────────────────────────┘
```

---

## 📁 Estrutura do Repositório

A organização das pastas e arquivos segue uma ordem cronológica estrita de execução (`1_` a `5_`), o que simplifica a manutenção técnica e a governança do código:

```text
├── .vscode/                   # Configurações do ambiente de desenvolvimento
├── 1_gerador_dados.py         # Script Python de simulação e engenharia de dados "sujos"
├── 2_setup_banco.sql          # Script DDL de criação do banco de dados e tabelas de Staging
├── 3_ingestao_dados.py        # Pipeline de ingestão ETL usando Pandas e SQLAlchemy
├── 4_1_exploracao.sql         # Consultas de validação e análise exploratória das tabelas
├── 4_2_modelagem_final.sql    # Criação das tabelas de destino e log de auditoria
├── 4_3_logica_conciliacao.sql   # Stored Procedure com regras de negócio e cruzamento
├── 4_4_views_relatorios.sql   # Views operacionais de auditoria e cálculo de impacto
├── 5_automacao_main.py        # Orquestrador unificado (Maestro do pipeline)
├── base_interna_cambio.csv    # Arquivo gerado simulando os dados do sistema interno
├── extrato_banco.csv          # Arquivo gerado simulando o extrato do banco processador
└── README.md                  # Documentação oficial do projeto
```

---

## 🛠️ Detalhamento Prático Passo a Passo

### 1. Geração de Dados e Injeção de Anomalias (`1_gerador_dados.py`)
Para testar a resiliência física do banco de dados, este script Python utiliza a biblioteca `Faker` para criar **15.000 transações financeiras diárias fictícias altamente realistas**, injetando anomalias intencionais simulando falhas operacionais reais:
* **Sujeira Cadastral:** CPFs gerados com e sem pontuação aleatoriamente para forçar tratamento de strings.
* **Transações Órfãs:** Cerca de 5% das transações enviadas internamente são removidas do extrato bancário (simulando quebra de fluxo ou falha no gateway).
* **Atraso de Processamento:** Transações bancárias recebem um atraso aleatório de até 3 dias úteis em relação à venda interna.
* **Divergência de Tarifas:** Cerca de 10% das transações sofrem descontos arbitrários de R$ 1,50 a R$ 5,00 no valor do banco, simulando taxas bancárias não provisionadas.

### 2. Infraestrutura e Área de Pouso (`2_setup_banco.sql`)
Criação física da base de dados e das tabelas de **Staging (`stg_`)**. Seguindo as melhores práticas de Engenharia de Dados, as tabelas de staging atuam como zonas de pouso de dados brutos e possuem tipagem flexível (`VARCHAR`), sem chaves primárias restritivas, para garantir que nenhuma carga falhe devido à despadronização dos arquivos de origem.

### 3. Pipeline de Carga ETL (`3_ingestao_dados.py`)
Script automatizado que lê os arquivos locais `.csv`, abre uma conexão segura com o Microsoft SQL Server via `SQLAlchemy/pyodbc` utilizando autenticação integrada do Windows, e realiza o carregamento em lote utilizando performance otimizada com o método `.to_sql()`.

### 4. Motor de Regras e Auditoria (`4_3_logica_conciliacao.sql`)
O coração analítico do projeto é a Stored Procedure **`sp_conciliar_dattos`**. Ela executa comandos DML pesados e realiza um `LEFT JOIN` entre as tabelas de staging. O motor categoriza cada registro em tempo de execução utilizando uma estrutura condicional `CASE WHEN`:
* **Conciliado Automático:** ID da transação e valor exato batem 100%.
* **Divergência de Valor/Taxa:** O ID existe de ambos os lados, mas o valor creditado no banco é menor.
* **Não Encontrado no Banco:** A transação foi efetuada internamente, mas o dinheiro nunca deu entrada no banco liquidante.

Toda execução armazena o histórico quantitativo na tabela de governança `tb_log_auditoria`, registrando a data/hora exata, total processado, sucessos e falhas estruturadas.

### 5. Visões Operacionais de Governança (`4_4_views_relatorios.sql`)
Em vez de depender de interfaces visuais de terceiros, o projeto consolida as métricas críticas em duas **Views de Banco de Dados** de alto desempenho:
1. **`vw_relatorio_eficiencia_processo`**: Transforma números brutos em indicadores de desempenho (KPIs), calculando em tempo real a *Taxa de Acerto %*, *Taxa de Divergência %* e *Taxa de Ausência no Banco %*.
2. **`vw_auditoria_critica_perdas`**: Mapeia cirurgicamente todas as transações com diferenças de valores, ordenando o prejuízo absoluto e calculando o **Percentual de Impacto** financeiro sobre o valor original da venda, permitindo que o time de Governança foque nos desvios mais críticos.

### 6. O Orquestrador Unificado (`5_automacao_main.py`)
O "Maestro" do projeto. Um script centralizado que realiza a automação completa do pipeline. Ao ser executado, ele aciona sequencialmente todas as etapas por meio de chamadas de sistema, limpa a memória do terminal e dispara a execução remota da Stored Procedure dentro do SQL Server, reduzindo o esforço operacional de processamento de dados diários para **um único clique**.

---

## 📈 Resultados Gerenciais Obtidos (Exemplo de Output)

Após a orquestração do pipeline, o painel interno de controle de Governança (via consulta na view de eficiência) exibe o seguinte panorama operacional consolidado:

#### Eficiência Estatística do Processamento (`vw_relatorio_eficiencia_processo`):
| ID_Log | Data_Processamento | Total_Processado | Total_Conciliado | Taxa_Acerto_Percentual | Total_Divergencia | Taxa_Divergencia_Percentual | Total_Faltante_Banco | Taxa_Ausencia_Banco_Percentual |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 17/06/2026 | 15.000 | 12.850 | **85,67%** | 1.406 | **9,37%** | 744 | **4,96%** |

#### Análise Crítica de Perdas por Transação (`vw_auditoria_critica_perdas`):
| ID_Transacao | Data_Venda | Valor_Sistema | Valor_Banco | Prejuizo_Taxa_BRL | Percentual_Impacto |
| :--- | :---: | :---: | :---: | :---: | :---: |
| TRX-004424 | 2026-06-07 | R$ 12.292,54 | R$ 12.287,54 | R$ 5,00 | 0,04% (Tarifa Baixa) |
| TRX-004950 | 2026-05-24 | R$ 574,07 | R$ 569,08 | R$ 4,99 | **0,87% (Tarifa Crítica)** |

---

## 🧠 Lições Aprendidas & Engenharia de Produção

### ⚠️ O Fenômeno da Explosão Cartesiana
Durante os testes de estresse da automação, foi identificado um comportamento anômalo: ao reexecutar o orquestrador sequencialmente sem a limpeza prévia das tabelas de staging, o volume de dados divergiu exponencialmente (pulando de 15.000 para mais de 290.000 registros). 

**Diagnóstico Técnico:** Como o gerador recriava IDs semelhantes e o script de ingestão aplicava um comando de `append` (acumulando dados históricos de staging), o `LEFT JOIN` da Procedure gerou um produto cartesiano ao cruzar múltiplas chaves repetidas em ambos os lados da equação.

**Resolução Aplicada:** Implementou-se uma regra de governança rígida na arquitetura: **as tabelas de Staging são efêmeras**. Adicionou-se o comando `TRUNCATE TABLE` no início da rotina de conciliação e ingestão, garantindo que a área de pouso seja totalmente limpa a cada novo ciclo de processamento, assegurando a idempotência do pipeline de dados.

---

### 🚀 Como Executar o Projeto Localmente

**Pré-requisitos**
* Python 3.10 ou superior instalado.
* Microsoft SQL Server configurado localmente.
* Extensão **SQL Server (mssql)** instalada no ambiente de edição de código.

**Modo de Execução:**
1. Configure o banco executando o arquivo `2_setup_banco.sql` no servidor.
2. Instale as bibliotecas necessárias via terminal: `pip install pandas sqlalchemy pyodbc faker`
3. Execute o maestro de orquestração: `python 5_automacao_main.py`
4. Acompanhe a execução diretamente via terminal e valide as métricas geradas no banco!