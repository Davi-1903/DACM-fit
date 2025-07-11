from flask_login import UserMixin
from utils import script_sql


class User(UserMixin):
    def __init__(self, id: str, nome: str, email: str):
        self.id = id
        self.nome = nome
        self.email = email
    
    @classmethod
    def get(cls, user_id: str) -> 'User':
        user = script_sql(f'SELECT * FROM tb_usuario WHERE usu_id = ?', (user_id,))
        if user:
            return cls(id=user[0], nome=user[1], email=user[2])
