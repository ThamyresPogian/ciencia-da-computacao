--Tabela Clientes
CREATE TABLE clientes(
	id_cliente int auto_increment PRIMARY KEY,
	nome varchar (30) NOT NULL,
	telefone varchar (11) NOT NULL,
);

--Tabela Cardápio
CREATE TABLE cardapio(
	id_cardapio int auto_increment PRIMARY	KEY,
	nome_prato varchar(100) NOT NULL,
	descricao text NOT NULL,
	preco DEC (5,2) NOT NULL CHECK (preco > 0)
);

--Tabela Pedidos
CREATE TABLE pedidos (
	id_pedido int auto_increment PRIMARY KEY,
	data_pedido datetime NOT NULL,
	status varchar (8) NOT NULL CHECK (status = 'RECEBIDO' OR status = 'FAZENDO' OR status = 'ENTREGUE')
);

--Tabela Itens do Pedido
CREATE TABLE itens_pedidos (
	id_item int auto_increment PRIMARY KEY,
	quantidade int NOT NULL CHECK (quantidade > 0)
);

--Tabela Mesas
CREATE TABLE mesas (
	id_mesa int auto_increment PRIMARY KEY,
	num_mesa int NOT NULL,
	status varchar (7) NOT NULL DEFAULT 'LIVRE' CHECK (status = 'LIVRE' OR status = 'OCUPADA')
);

ALTER TABLE PEDIDOS
ADD COLUMN id_cliente int;

ALTER TABLE ITENS_PEDIDOS
ADD COLUMN id_pedido int NOT NULL;

ALTER TABLE ITENS_PEDIDOS
ADD COLUMN id_cardapio int NOT NULL;

ALTER TABLE PEDIDOS
ADD CONSTRAINT fk_pedidos_clientes FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente)
ON DELETE SET NULL;

ALTER TABLE ITENS_PEDIDOS
ADD CONSTRAINT fk_itens_pedidos FOREIGN KEY (id_pedido) REFERENCES pedidos (id_pedido)
ON DELETE CASCADE;

ALTER TABLE ITENS_PEDIDOS
ADD CONSTRAINT fk_itens_cardapio FOREIGN KEY (id_cardapio) REFERENCES cardapio (id_cardapio)
ON DELETE CASCADE;
