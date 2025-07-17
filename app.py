from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_database
from utils import script_sql
from modelo import User


app = Flask(__name__)

app.secret_key = 'SENHASUPERHIMPERMEGABLASTERSECRETA'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

init_database()


@login_manager.user_loader
def load_user(user_id: str) -> User:
    return User.get(user_id)


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        user = script_sql(f'SELECT * FROM tb_usuario WHERE usu_email = ?', (email,))
        if user:
            return redirect(url_for('login'))

        new_id = (script_sql('SELECT max(usu_id) FROM tb_usuario')[0] or 0) + 1 # Criando o próximo ID
        script_sql(f'INSERT INTO tb_usuario (usu_id, usu_nome, usu_email, usu_senha) VALUES(?, ?, ?, ?)', (new_id, nome, email, generate_password_hash(senha)))
        usuario = User(new_id, nome, email)
        login_user(usuario)
        return redirect(url_for('dados_pessoal'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        user = script_sql(f'SELECT * FROM tb_usuario WHERE usu_email = ?', (email,))
        if not user or not check_password_hash(user['usu_senha'], senha):
            return redirect(url_for('register'))

        login_user(User(id=user['usu_id'], nome=user['usu_nome'], email=user['usu_email']))
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/dados_pessoal', methods=['GET', 'POST'])
def dados_pessoal():
    if request.method == 'POST':
        sexo = request.form.get('sexo')
        endereco = request.form.get('endereco')
        telefone = request.form.get('telefone')
        script_sql(f'UPDATE tb_usuario SET usu_endereco = ?, usu_sexo = ?, usu_telefone = ? WHERE usu_id = ?', (endereco, sexo, telefone, current_user.id))
        return render_template('avaliacao_fisica.html')
    return render_template('dados_pessoais.html')


@app.route('/avaliacao_fisica', methods=['GET', 'POST'])
def avaliacao():
    if request.method == 'POST':
        peso = request.form.get('peso')
        altura = request.form.get('altura')
        data_nascimento = request.form.get('data_nascimento')
        tipo_treino = request.form.get('tipo_treino')
        script_sql(f'UPDATE tb_usuario SET usu_peso = ?, usu_altura = ?, usu_data_nascimento = ?, usu_tipo_treino = ? WHERE usu_id = ?', (peso, altura, data_nascimento, tipo_treino, current_user.id))
        return redirect(url_for('index'))
    return render_template('avaliacao_fisica.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_required
@app.route('/deletar_conta', methods=['GET', 'POST'])
def deletar_conta():
    if request.method == 'POST':
        script_sql('delete from tb_usuario where usu_id = ?;', (current_user.id,))
        logout_user()
        return redirect(url_for('index'))
    return render_template('deletar_conta.html')

@login_required
@app.route('/editar', methods=['GET', 'POST'])
def editar():
    id_user = current_user.id
    if request.method == 'POST':
        nome = request.form['nome']
        peso = request.form['peso']
        altura = request.form['altura']
        telefone = request.form['telefone']
        data = request.form['data']
        sexo = request.form['sexo']
        endereco = request.form['endereco']
        tipo_treino = request.form['tipo_treino']
        script_sql(f'UPDATE tb_usuario SET usu_nome = ?, usu_peso = ?, usu_altura = ?, usu_telefone = ?, usu_data_nascimento = ?, usu_sexo = ?, usu_endereco = ?, usu_tipo_treino = ? WHERE usu_id = ?;', (nome, peso, altura, telefone, data, sexo, endereco, tipo_treino, id_user))
        return redirect(url_for('index'))
    user = script_sql(f'SELECT * FROM tb_usuario WHERE usu_id = ?', (id_user,))
    return render_template('formulario_edicao.html', user=user)

@login_required
@app.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    id_user = current_user.id
    user = script_sql(f'SELECT * FROM tb_usuario WHERE usu_id = ?', (id_user,))
    if request.method == 'POST':
        senha = request.form['senha']
        if check_password_hash(user['usu_senha'], senha):
            return 'Sua senha não pode ser igual'
    return render_template('alterar_senha.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
