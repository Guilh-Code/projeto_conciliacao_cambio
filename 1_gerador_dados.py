# %%

import pandas as pd
import random
from faker import Faker
from datetime import timedelta

# Inicializa o Faker para gerar dados falsos realistas (pt_BR para CPFs do Brasil)
fake = Faker('pt_BR')

# Configurações do nosso lote de dados
QTD_TRANSACOES = 15000 # Vamos gerar 15 mil transações!

def gerar_dados_cambio():
    print("Iniciando a geração de dados de Câmbio...")
    
    dados_internos = []
    dados_banco = []

    for i in range(1, QTD_TRANSACOES + 1):
        # 1. GERANDO A TRANSAÇÃO ORIGINAL (BASE INTERNA)
        id_transacao = f"TRX-{str(i).zfill(6)}"
        data_venda = fake.date_between(start_date='-30d', end_date='today')
        
        # Sujeira intencional: Alguns CPFs terão pontuação, outros não
        cpf = fake.cpf() if random.choice([True, False]) else fake.cpf().replace('.', '').replace('-', '')
        
        tipo_op = random.choice(['Papel Moeda', 'Cartão Pré-pago', 'Remessa Internacional'])
        moeda = random.choice(['USD', 'EUR', 'GBP'])
        valor_brl = round(random.uniform(500.0, 15000.0), 2)

        # Adiciona na lista do sistema interno
        dados_internos.append([id_transacao, data_venda, cpf, tipo_op, moeda, valor_brl])

        # 2. GERANDO A TRANSAÇÃO DO BANCO (COM INCONSISTÊNCIAS PROPOSITAIS)
        
        # Anomalia 1: Transações "Órfãs" (Aconteceu no interno, mas não caiu no banco ainda)
        # Vamos fazer com que 5% das transações sumam do banco
        if random.random() < 0.05:
            continue # Pula para a próxima repetição do loop, não adiciona no banco

        # Anomalia 2: Atraso de dias úteis
        # O banco processa no mesmo dia ou com até 3 dias de atraso
        dias_atraso = random.randint(0, 3)
        data_processamento = data_venda + timedelta(days=dias_atraso)

        # Anomalia 3: Divergência de Valores (Taxas bancárias não previstas)
        # 10% das transações terão uma tarifa bancária descontada (ex: 1.50 a 5.00 reais a menos)
        valor_recebido = valor_brl
        if random.random() < 0.10:
            valor_recebido = round(valor_recebido - random.uniform(1.50, 5.00), 2)

        # Adiciona na lista do banco
        dados_banco.append([id_transacao, data_processamento, valor_recebido])

    # 3. TRANSFORMANDO EM DATAFRAMES E SALVANDO EM CSV
    df_interno = pd.DataFrame(dados_internos, columns=['ID_Transacao', 'Data_Venda', 'CPF_Cliente', 'Tipo_Operacao', 'Moeda_Estrangeira', 'Valor_BRL'])
    df_banco = pd.DataFrame(dados_banco, columns=['ID_Transacao', 'Data_Processamento', 'Valor_Recebido'])

    # Salvando na mesma pasta do projeto
    df_interno.to_csv('base_interna_cambio.csv', index=False, encoding='utf-8')
    df_banco.to_csv('extrato_banco.csv', index=False, encoding='utf-8')

    print(f"Sucesso! Gerados {len(df_interno)} registros na Base Interna e {len(df_banco)} no Extrato do Banco.")

# Executa a função
if __name__ == "__main__":
    gerar_dados_cambio()

# %%
