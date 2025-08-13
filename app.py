from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_database
from utils import script_sql, script_sql_all
from modelo import User
import json


app = Flask(__name__)

app.secret_key = 'SENHASUPERHIMPERMEGABLASTERSECRETA'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

init_database()


@login_manager.user_loader
def load_user(user_id: str) -> User:
    return User.get(user_id)

@app.errorhandler(404)
def pagina_inexistente(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def erro_interno(e):
    return render_template('500.html'), 500

@app.route('/')
def index():
    if request.cookies:
        if 'nome' in request.cookies:
            nome = request.cookies.get('nome', None)
            return render_template('index.html', nome=nome)
        nome = request.cookies.get('new_user', None)
        return render_template('index.html', new_user=nome)
        
    return render_template('index.html')

@app.route('/ajuda')
def ajuda():
    return render_template('ajuda.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        user = script_sql(f'SELECT * FROM tb_usuario WHERE usu_email = ?', (email,))
        if user:
            flash('Você já esta logado', category='error')
            return redirect(url_for('login'))
        new_id = (script_sql('SELECT max(usu_id) FROM tb_usuario')[0] or 0) + 1 # Criando o próximo ID
        script_sql(f'INSERT INTO tb_usuario (usu_id, usu_nome, usu_email, usu_senha) VALUES(?, ?, ?, ?)', (new_id, nome, email, generate_password_hash(senha)))
        usuario = User(new_id, nome, email)
        login_user(usuario)
        response = make_response(redirect(url_for('dados_pessoais')))
        response.set_cookie('new_user', nome)
        return response
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        user = script_sql(f'SELECT * FROM tb_usuario WHERE usu_email = ?', (email,))
        if not user or not check_password_hash(user['usu_senha'], senha):
            flash('Dados incorretos', category='error')
            return redirect(url_for('login'))
        nome = user['usu_nome']
        login_user(User(id=user['usu_id'], nome=user['usu_nome'], email=user['usu_email']))
        response = make_response(redirect(url_for('index')))
        response.set_cookie('nome', nome)
        return response
    return render_template('login.html')

@app.route('/dados_pessoais', methods=['GET', 'POST'])
def dados_pessoais():
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
        flash('Cadastro realizado com sucesso', category='sucess')
        return redirect(url_for('index'))
    return render_template('avaliacao_fisica.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    response = make_response(redirect(url_for('index')))
    response.delete_cookie('nome', None)
    response.delete_cookie('new_user', None)
    return response

@app.route('/deletar_conta', methods=['GET', 'POST'])
@login_required
def deletar_conta():
    if request.method == 'POST':
        senha = request.form['senha']
        user = script_sql(f'SELECT * FROM tb_usuario WHERE usu_id = ?', (current_user.id,))
        if check_password_hash(user['usu_senha'], senha):
            script_sql('delete from tb_registro_treino where reg_usu_id = ?;', (current_user.id,))
            script_sql('delete from tb_usuario where usu_id = ?;', (current_user.id,))
            logout_user()
            response = make_response(redirect(url_for('index')))
            response.delete_cookie('nome', None)
            response.delete_cookie('new_user', None)
            return response
        flash('Senha incorreta. Faça o passo novamente.', category='error')
        return redirect(url_for('deletar_conta'))
        
    return render_template('deletar_conta.html')

@app.route('/editar', methods=['GET', 'POST'])
@login_required
def editar():
    id_user = current_user.id
    user = script_sql(f'SELECT * FROM tb_usuario WHERE usu_id = ?', (id_user,))
    if request.method == 'POST':
        email = request.form['email']
        nome = request.form['nome']
        peso = request.form['peso']
        altura = request.form['altura']
        telefone = request.form['telefone']
        data = request.form['data']
        sexo = request.form['sexo']
        endereco = request.form['endereco']
        tipo_treino = request.form['tipo_treino']
        senha = request.form['senha']
        if check_password_hash(user['usu_senha'], senha):
            script_sql(f'UPDATE tb_usuario SET usu_nome = ?, usu_peso = ?, usu_altura = ?, usu_telefone = ?, usu_data_nascimento = ?, usu_sexo = ?, usu_endereco = ?, usu_tipo_treino = ?, usu_email = ? WHERE usu_id = ?;', (nome, peso, altura, telefone, data, sexo, endereco, tipo_treino, email, id_user))
            return redirect(url_for('index'))
        flash('Senha incorreta. Faça o passo novamente.', category='error')
        return redirect(url_for('editar'))
    return render_template('formulario_edicao.html', user=user)

@app.route('/alterar_senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    id_user = current_user.id
    user = script_sql(f'SELECT * FROM tb_usuario WHERE usu_id = ?', (id_user,))
    if request.method == 'POST':
        senha = request.form['senha']
        senha_ant = request.form['senha_ant']
        if check_password_hash(user['usu_senha'], senha):
            flash('Sua senha precisa ser diferente', category='error')
            return redirect(url_for('alterar_senha'))
        if not check_password_hash(user['usu_senha'], senha_ant):
            flash('Insira a senha correta.', category='error')
            return redirect(url_for('alterar_senha'))
        script_sql(f'UPDATE tb_usuario SET usu_senha = ? WHERE usu_id = ?', (generate_password_hash(senha), id_user))
        return redirect(url_for('index'))
    
    return render_template('alterar_senha.html', user=user)

@app.route('/treino')
@login_required
def tabela_treino():
    tipo_treino = script_sql(f'SELECT * FROM tb_usuario WHERE usu_id = ?', (current_user.id,))
    if tipo_treino['usu_endereco'] is None:
        flash('Termine o cadastro.', category='error')
        return redirect(url_for('dados_pessoais'))
    if tipo_treino['usu_peso'] is None:
        flash('Termine o cadastro.', category='error')
        return redirect(url_for('avaliacao'))
    with open('database/treino.json', encoding='utf-8') as f:
        treinos = json.load(f)
    return render_template('tabela_treino.html', treino = treinos[tipo_treino['usu_tipo_treino']])

@app.route('/informes')
@login_required
def informes():
    return render_template('informes.html')

@app.route('/registrar_treino', methods=['GET', 'POST'])
@login_required
def registrar_treino():
    if request.method == 'POST':
        data = request.form['data']
        if 'treinou' in request.form:
            treinou = 'Sim'
        else:
            treinou = 'Não'
        tempo = request.form['tempo']
        obs = request.form['observacoes']
        tempo = request.form.get('tempo')
        verificar = script_sql(f'SELECT * FROM tb_registro_treino WHERE reg_data = ?', (data, ))
        if not verificar:
            script_sql(f'INSERT INTO tb_registro_treino (reg_treinou, reg_data, reg_observacao, reg_tempo, reg_usu_id) VALUES (?, ?, ?, ?, ?)', (treinou, data, obs, tempo, current_user.id))
            flash('Registro realizado com sucesso', category='success')
            return redirect(url_for('exibir_registro_treino'))
        flash('Já houve registros nessa data.', category='error')
        return redirect(url_for('registrar_treino'))
    return render_template('registrar_treino.html')

@app.route('/exibir_registro_treino')
@login_required
def exibir_registro_treino():
    registros = script_sql_all(f'SELECT * FROM tb_registro_treino WHERE reg_usu_id = ?', (current_user.id, ))
    if registros:
        return render_template('exibir_registro_treino.html', lista=registros)
    return render_template('exibir_registro_treino.html')

@app.route('/perfil')
@login_required
def perfil():
    user = script_sql('SELECT * FROM tb_usuario WHERE usu_id = ?', (current_user.id,))
    return render_template('perfil.html', user=user)
    
if __name__ == '__main__':
    app.run(debug=True)