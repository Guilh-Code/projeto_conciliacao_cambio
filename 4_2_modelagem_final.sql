USE ProjetoConciliacao;
GO


-- Tabela Final de Conciliação

CREATE TABLE tb_conciliacao_resultado (
    ID_Transacao VARCHAR(50),
    Data_Venda DATE,
    Valor_Sistema DECIMAL(10,2),
    Data_Processamento_Banco DATE,
    Valor_Banco DECIMAL(10,2),
    Diferenca_Valor DECIMAL(10,2),
    Status_Conciliacao VARCHAR(50)
);
GO


-- Tabela de Auditoria

CREATE TABLE tb_log_auditoria (
    ID_Log INT IDENTITY(1,1) PRIMARY KEY,
    Data_Execucao DATETIME DEFAULT GETDATE(),
    Total_Processado INT,
    Total_Conciliado INT,
    Total_Divergencia INT,
    Total_Faltante_Banco INT
);
GO