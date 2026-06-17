USE ProjetoConciliacao;
GO

CREATE OR ALTER PROCEDURE sp_conciliar_dattos
AS
BEGIN
    -- 1. Preparação: Limpa a tabela de resultados para rodar a conciliação do dia zerada
    TRUNCATE TABLE tb_conciliacao_resultado;

    -- 2. Cruzamento de Dados e Inserção na tabela final
    INSERT INTO tb_conciliacao_resultado (
        ID_Transacao, Data_Venda, Valor_Sistema, Data_Processamento_Banco, Valor_Banco, Diferenca_Valor, Status_Conciliacao
    )
    SELECT 
        i.ID_Transacao,
        i.Data_Venda,
        i.Valor_BRL AS Valor_Sistema,
        b.Data_Processamento,
        b.Valor_Recebido AS Valor_Banco,
        ISNULL(i.Valor_BRL - b.Valor_Recebido, i.Valor_BRL) AS Diferenca_Valor,
        
        CASE 
            WHEN b.ID_Transacao IS NULL THEN 'Não Encontrado no Banco'
            WHEN i.Valor_BRL = b.Valor_Recebido THEN 'Conciliado Automático'
            ELSE 'Divergência de Valor/Taxa'
        END AS Status_Conciliacao

    FROM stg_base_interna i
    LEFT JOIN stg_extrato_banco b ON i.ID_Transacao = b.ID_Transacao;

    -- 3. G0vernança: Gera o Log da Auditoria 
    DECLARE @TotalProcessado INT = (SELECT COUNT(*) FROM stg_base_interna);
    DECLARE @TotalConciliado INT = (SELECT COUNT(*) FROM tb_conciliacao_resultado WHERE Status_Conciliacao = 'Conciliado Automático');
    DECLARE @TotalDivergencia INT = (SELECT COUNT(*) FROM tb_conciliacao_resultado WHERE Status_Conciliacao = 'Divergência de Valor/Taxa');
    DECLARE @TotalFaltante INT = (SELECT COUNT(*) FROM tb_conciliacao_resultado WHERE Status_Conciliacao = 'Não Encontrado no Banco');

    INSERT INTO tb_log_auditoria (Total_Processado, Total_Conciliado, Total_Divergencia, Total_Faltante_Banco)
    VALUES (@TotalProcessado, @TotalConciliado, @TotalDivergencia, @TotalFaltante);
    
    PRINT 'Conciliação finalizada e Log gerado com sucesso!';
END;
GO

EXEC sp_conciliar_dattos;

SELECT TOP 20 * FROM tb_conciliacao_resultado;
SELECT * FROM tb_log_auditoria;