CREATE TABLE IF NOT EXISTS tb_usuario(
    usu_id int auto_increment primary key not null,
    usu_nome varchar(100) not null,
    usu_email varchar(100) not null,
    usu_senha varchar(100) not null
);