PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS tb_usuario(
    usu_id integer primary key autoincrement not null,
    usu_nome varchar(100) not null,
    usu_email varchar(100) not null unique,
    usu_senha varchar(200) not null, -- O tamanho do hash é 162, mas 200 é um número mais redondo :)
    usu_endereco varchar(50),
    usu_telefone varchar(20), 
    usu_sexo varchar(15),
    usu_data_nascimento date,
    usu_peso float,
    usu_altura float,
    usu_tipo_treino varchar(20)
);

CREATE TABLE IF NOT EXISTS tb_registro_treino(
    reg_id integer primary key autoincrement not null,
    reg_treinou varchar(3) not null,
    reg_data date,
    reg_tempo integer,
    reg_observacao text,
    reg_usu_id integer not null,
    foreign key (reg_usu_id) references tb_usuario(usu_id)
);