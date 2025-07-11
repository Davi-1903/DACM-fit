CREATE TABLE IF NOT EXISTS tb_usuario(
    usu_id int auto_increment primary key not null,
    usu_nome varchar(100) not null,
    usu_email varchar(100) not null unique,
    usu_senha varchar(200) not null -- O tamanho do hash é 162, mas 200 é um número mais redondo :)
);