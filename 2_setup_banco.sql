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
GO

CREATE TABLE stg_extrato_banco (
    ID_Transacao VARCHAR(50),
    Data_Processamento DATE,
    Valor_Recebido DECIMAL(10,2)
);
GO
