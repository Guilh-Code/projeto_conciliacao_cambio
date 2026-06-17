# %%

import os
import time
from sqlalchemy import create_engine, text
import urllib

# 1. Configuração da Conexão com o SQL Server
params = urllib.parse.quote_plus(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=ProjetoConciliacao;'
    'Trusted_Connection=yes;'
    'TrustServerCertificate=yes;'
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

def executar_automacao():
    print("="*50)
    print("🚀 INICIANDO PIPELINE DE CONCILIAÇÃO 🚀")
    print("="*50)
    
    start_total = time.time()

    # PASSO A: Gerar novos arquivos "sujos" do dia
    print("\n[Passo 1/3] Simulando chegada de novos arquivos de transações...")
    os.system('python 1_gerador_dados.py') 

    # PASSO B: Fazer a ingestão no banco
    print("\n[Passo 2/3] Ingerindo dados nas tabelas de Staging do SQL Server...")
    os.system('python 3_ingestao_dados.py')

    # PASSO C: Acordar o "Robô" de Conciliação no SQL Server
    print("\n[Passo 3/3] Acionando a Stored Procedure de Conciliação e Governança...")
    
    try:
        with engine.begin() as conn:
            conn.execute(text("EXEC sp_conciliar_dattos"))
        print("✅ Stored Procedure executada com sucesso! Log de auditoria gerado.")
    except Exception as e:
        print(f"❌ Erro ao executar a conciliação: {e}")

    end_total = time.time()
    print("\n" + "="*50)
    print(f"🏁 PIPELINE FINALIZADO EM {round(end_total - start_total, 2)} SEGUNDOS 🏁")
    print("="*50)

if __name__ == "__main__":
    executar_automacao()

# %%
