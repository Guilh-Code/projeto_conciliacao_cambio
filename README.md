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

Este repositório contém um **Pipeline de Engenharia e Governança de Dados** completo de ponta a ponta, desenvolvido para resolver um dos problemas mais críticos e complexos de instituições financeiras: a **Conciliação Automatizada de Transações em Larga Escala**.

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
Para testar a resiliência física do banco de dados, este script Python utiliza a biblioteca `Faker` para criar **15.000 transações financeiras diárias fictícias altamente realistas**, injetando anomalias intencionais para simular falhas operacionais reais:
* **Sujeira Cadastral:** CPFs gerados com e sem pontuação aleatoriamente para forçar tratamento de strings.
* **Transações Órfãs:** Cerca de 5% das transações enviadas internamente são removidas do extrato bancário (simulando quebra de fluxo).
* **Atraso de Processamento:** Transações bancárias recebem um atraso aleatório de até 3 dias úteis em relação à venda interna.
* **Divergência de Tarifas:** Cerca de 10% das transações sofrem descontos arbitrários de R$ 1,50 a R$ 5,00 no valor do banco, simulando taxas bancárias não provisionadas.

```python
# Snippet do laço de geração e injeção de anomalias de valores
for i in range(1, QTD_TRANSACOES + 1):
    id_transacao = f"TRX-{str(i).zfill(6)}"
    data_venda = fake.date_between(start_date='-30d', end_date='today')
    cpf = fake.cpf() if random.choice([True, False]) else fake.cpf().replace('.', '').replace('-', '')
    valor_brl = round(random.uniform(500.0, 15000.0), 2)
    dados_internos.append([id_transacao, data_venda, cpf, tipo_op, moeda, valor_brl])

    if random.random() < 0.05:
        continue # Simula transação órfã (não chega no banco)

    # Simula divergência de taxas bancárias
    valor_recebido = valor_brl
    if random.random() < 0.10:
        valor_recebido = round(valor_recebido - random.uniform(1.50, 5.00), 2)
    dados_banco.append([id_transacao, data_processamento, valor_recebido])
```

### 2. Infraestrutura e Área de Pouso (`2_setup_banco.sql`)
Criação física da base de dados e das tabelas de **Staging (`stg_`)**. Seguindo as melhores práticas de Engenharia de Dados, as tabelas de staging atuam como zonas de pouso de dados brutos e possuem tipagem flexível (`VARCHAR`), sem chaves primárias restritivas, para garantir que nenhuma carga falhe devido à despadronização dos arquivos de origem.

```sql
CREATE DATABASE ProjetoConciliacao;
GO
USE ProjetoConciliacao;
GO

CREATE TABLE stg_base_interna (
    ID_Transacao VARCHAR(50),
    Data_Venda DATE,
    CPF_Cliente VARCHAR(20),
    Tipo_Operacao VARCHAR(50),
    Moeda_Estrangeira VARCHAR(10),
    Valor_BRL DECIMAL(10,2)
);

CREATE TABLE stg_extrato_banco (
    ID_Transacao VARCHAR(50),
    Data_Processamento DATE,
    Valor_Recebido DECIMAL(10,2)
);
```

### 3. Pipeline de Carga ETL (`3_ingestao_dados.py`)
Script automatizado que lê os arquivos locais `.csv`, abre uma conexão segura com o Microsoft SQL Server via `SQLAlchemy/pyodbc` utilizando autenticação integrada do Windows, e realiza o carregamento em lote utilizando performance otimizada com o método `.to_sql()`.

```python
# Conexão via SQLAlchemy e inserção em lote (Bulk Insert)
params = urllib.parse.quote_plus(
    'DRIVER={SQL Server};SERVER=localhost;DATABASE=ProjetoConciliacao;Trusted_Connection=yes;'
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# Carga de Staging com estratégia de Append
df_interna.to_sql('stg_base_interna', engine, if_exists='append', index=False)
df_banco.to_sql('stg_extrato_banco', engine, if_exists='append', index=False)
```

### 4. Motor de Regras e Auditoria (`4_3_logica_conciliacao.sql`)
O coração analítico do projeto é uma **Stored Procedure**. Ela executa comandos DML pesados e realiza um `LEFT JOIN` entre as tabelas de staging. O motor categoriza cada registro em tempo de execução utilizando uma estrutura condicional `CASE WHEN` e salva o histórico quantitativo na tabela de governança `tb_log_auditoria`.

```sql
-- Lógica central de cruzamento e classificação de status
INSERT INTO tb_conciliacao_resultado (...)
SELECT 
    i.ID_Transacao,
    i.Data_Venda,
    i.Valor_BRL AS Valor_Sistema,
    b.Valor_Recebido AS Valor_Banco,
    ISNULL(i.Valor_BRL - b.Valor_Recebido, i.Valor_BRL) AS Diferenca_Valor,
    CASE 
        WHEN b.ID_Transacao IS NULL THEN 'Não Encontrado no Banco'
        WHEN i.Valor_BRL = b.Valor_Recebido THEN 'Conciliado Automático'
        ELSE 'Divergência de Valor/Taxa'
    END AS Status_Conciliacao
FROM stg_base_interna i
LEFT JOIN stg_extrato_banco b ON i.ID_Transacao = b.ID_Transacao;


DECLARE @TotalProcessado INT = (SELECT COUNT(*) FROM stg_base_interna);
    DECLARE @TotalConciliado INT = (SELECT COUNT(*) FROM tb_conciliacao_resultado WHERE Status_Conciliacao = 'Conciliado Automático');
    DECLARE @TotalDivergencia INT = (SELECT COUNT(*) FROM tb_conciliacao_resultado WHERE Status_Conciliacao = 'Divergência de Valor/Taxa');
    DECLARE @TotalFaltante INT = (SELECT COUNT(*) FROM tb_conciliacao_resultado WHERE Status_Conciliacao = 'Não Encontrado no Banco');

    INSERT INTO tb_log_auditoria (Total_Processado, Total_Conciliado, Total_Divergencia, Total_Faltante_Banco)
    VALUES (@TotalProcessado, @TotalConciliado, @TotalDivergencia, @TotalFaltante);
```

### 5. Visões Operacionais de Governança (`4_4_views_relatorios.sql`)
O projeto consolida as métricas críticas em **Views de Banco de Dados** de alto desempenho, permitindo avaliar a saúde da operação com um simples `SELECT` gerencial.

```sql
-- 1. View de análise de risco e impacto financeiro
CREATE OR ALTER VIEW vw_auditoria_critica_perdas AS
SELECT
    ID_Transacao,
    Data_Venda,
    Valor_Sistema,
    Valor_Banco,
    Diferenca_Valor AS Prejuizo_Taxa_BRL,
    ROUND((Diferenca_Valor / Valor_Sistema) * 100, 2) AS Percentual_Impacto
FROM tb_conciliacao_resultado
WHERE Status_Conciliacao = 'Divergência de Valor/Taxa'


-- 2. Viwe de Metricas de Eficiência
CREATE OR ALTER VIEW vw_relatorio_eficiencia_processo AS
SELECT 
    ID_Log,
    CONVERT(VARCHAR, Data_Execucao, 103) AS Data_Processamento,
    Total_Processado,
    ROUND((CAST(Total_Conciliado AS FLOAT) / Total_Processado) * 100, 2) AS Taxa_Acerto_Percentual,
    ROUND((CAST(Total_Divergencia AS FLOAT) / Total_Processado) * 100, 2) AS Taxa_Divergencia_Percentual,
    ROUND((CAST(Total_Faltante_Banco AS FLOAT) / Total_Processado) * 100, 2) AS Taxa_Ausencia_Banco_Percentual
FROM tb_log_auditoria;
```

### 6. O Orquestrador Unificado (`5_automacao_main.py`)
O "Maestro" do projeto. Um script centralizado que realiza a automação completa do pipeline. Ao ser executado, ele aciona sequencialmente todas as etapas por meio de chamadas de sistema, limpa a memória do terminal e dispara a execução remota da Stored Procedure dentro do SQL Server, reduzindo o esforço operacional de processamento de dados para **um único clique**.

```python
# Execução sequencial e centralizada de toda a esteira de dados
def executar_automacao():
    os.system('python 1_gerador_dados.py') # Gera os arquivos
    os.system('python 3_ingestao_dados.py') # Ingestão via ETL
    
    # Execução da inteligência direto no banco de dados
    with engine.begin() as conn:
        conn.execute(text("EXEC sp_conciliar_transacoes"))
    print("✅ Pipeline executado e finalizado com sucesso!")
```

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

Durante o desenvolvimento deste projeto, saí da zona de conforto de apenas executar consultas básicas de visualização e mergulhei na arquitetura de uma solução de dados real. As principais lições consolidadas foram:

* **O Poder do SQL além do `SELECT`:** Aprendi a estruturar um banco de dados do zero, criando tabelas de *Staging* para receber arquivos brutos e construindo *Stored Procedures* (robôs de banco de dados). Entendi na prática como utilizar `LEFT JOIN` e `CASE WHEN` para criar regras de negócio robustas que cruzam bases e classificam status de forma massiva.
* **A Lógica da Conciliação Financeira:** Compreendi o núcleo da Governança de Dados. Conciliar não é apenas fazer os números "baterem", mas sim mapear e auditar os desvios: identificar taxas bancárias não previstas, transações órfãs e atrasos de processamento, registrando tudo em logs automatizados para garantir a integridade financeira.
* **Visão Macro de Automação com Python:** Mesmo utilizando inteligência artificial como apoio para a sintaxe avançada do código, consolidei o entendimento lógico de como o Python atua como o "maestro" de um pipeline (ETL). Entendi perfeitamente como ele pode simular a chegada de dados, conectar-se ao banco para fazer a ingestão e acionar rotinas SQL de forma sequencial, transformando um processo manual e demorado em uma execução de um único clique.

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
