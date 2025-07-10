CREATE TABLE IF NOT EXIST tb_user(
    use_id int auto_increment primary key not null,
    use_nome varchar(100) not null,
    use_email varchar(100) not null,
    use_senha varchar(100) not null
);