# %%

import pandas as pd
from sqlalchemy import create_engine
import urllib
import time

print("Iniciando a leitura dos arquivos CSV...")

# 1. Lendo os arquivos gerados no Passo 1
df_interna = pd.read_csv('base_interna_cambio.csv')
df_banco = pd.read_csv('extrato_banco.csv')

# 2. Configurando a conexão com o SQL Server
params = urllib.parse.quote_plus(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=ProjetoConciliacao;'
    'Trusted_Connection=yes;'
    'TrustServerCertificate=yes;'
)

# Cria o "motor" de conexão
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

print("Conectado ao SQL Server. Iniciando a ingestão de dados... Isso pode levar alguns segundos.")
start_time = time.time()

# 3. Injetando os dados nas tabelas de Staging
df_interna.to_sql('stg_base_interna', engine, if_exists='append', index=False)
print(f"✅ {len(df_interna)} registros inseridos na stg_base_interna!")

df_banco.to_sql('stg_extrato_banco', engine, if_exists='append', index=False)
print(f"✅ {len(df_banco)} registros inseridos na stg_extrato_banco!")

end_time = time.time()
print(f"Ingestão concluída com sucesso em {round(end_time - start_time, 2)} segundos!")
# %%
