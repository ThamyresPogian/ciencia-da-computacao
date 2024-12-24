--Total de vendas por período

SELECT 
    FORMATDATETIME(data_pedido, 'dd-MM-yyyy HH:00:00') AS período,
    COUNT(*) AS quantidade_vendas
FROM 
    pedidos
GROUP BY 
    FORMATDATETIME(data_pedido, 'dd-MM-yyyy HH:00:00')
ORDER BY 
    período;

--Itens mais pedidos

SELECT
	c.nome_prato,
	SUM(ip.QUANTIDADE) AS Feitos 
FROM ITENS_PEDIDOS ip
INNER JOIN CARDAPIO c ON ip.ID_CARDAPIO = c.ID_CARDAPIO
GROUP BY c.NOME_PRATO
ORDER BY Feitos;


--Status da mesas livres

SELECT
	num_mesa AS Número_Mesa,
	status AS Status
FROM MESAS
WHERE status = 'LIVRE';

--Pedidos com status recebido

SELECT
	p.ID_PEDIDO AS Número_Pedido,
	c.NOME_PRATO,
	ip.QUANTIDADE AS Quantidade
FROM PEDIDOS p
INNER JOIN ITENS_PEDIDOS ip ON ip.ID_PEDIDO = p.ID_PEDIDO
INNER JOIN CARDAPIO c  ON c.ID_CARDAPIO = ip.ID_CARDAPIO
WHERE p.STATUS = 'RECEBIDO'
ORDER BY p.id_pedido;

--Telefone da cliente Eduarda Lima que esqueceu o cartão

SELECT
	nome,
	telefone
FROM CLIENTES c
WHERE c.nome = 'Eduarda Lima';

--Pratos até R$20,00

SELECT 
	ID_CARDAPIO AS Número_Prato,
	NOME_PRATO,
	DESCRICAO AS Descrição,
	preco AS Preço
FROM CARDAPIO c
WHERE c.PRECO <= 20;
