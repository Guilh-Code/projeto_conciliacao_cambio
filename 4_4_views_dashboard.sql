USE ProjetoConciliacao;
GO

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
GO



-- 2. Viwe de Metricas de Eficiência
CREATE OR ALTER VIEW vw_relatorio_eficiencia_processo AS
SELECT 
    ID_Log,
    CONVERT(VARCHAR, Data_Execucao, 103) AS Data_Processamento,
    Total_Processado,
    Total_Conciliado,
    ROUND((CAST(Total_Conciliado AS FLOAT) / Total_Processado) * 100, 2) AS Taxa_Acerto_Percentual,
    Total_Divergencia,
    ROUND((CAST(Total_Divergencia AS FLOAT) / Total_Processado) * 100, 2) AS Taxa_Divergencia_Percentual,
    Total_Faltante_Banco,
    ROUND((CAST(Total_Faltante_Banco AS FLOAT) / Total_Processado) * 100, 2) AS Taxa_Ausencia_Banco_Percentual
FROM tb_log_auditoria;
GO


SELECT * FROM vw_relatorio_eficiencia_processo;
SELECT TOP 20 * FROM vw_auditoria_critica_perdas ORDER BY Prejuizo_Taxa_BRL DESC;