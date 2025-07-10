from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from utils import script_sql
from modelo import User


app = Flask(__name__)

app.secret_key = 'SENHASUPERHIMPERMEGABLASTERSECRETA'

login_manager = LoginManager(app)


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

        user = script_sql(f'SELECT * FROM tb_usuario WHERE usu_nome = \'{nome}\' AND usu_email = \'{email}\' AND usu_senha = \'{senha}\'')
        if user:
            return redirect(url_for('login'))

        new_id = script_sql('SELECT max(usu_id) FROM tb_usuario')[0] + 1 # Criando o próximo ID
        script_sql(f'INSERT INTO tb_usuario VALUES ({new_id!r}, {nome!r}, {email!r}, {senha!r})')
        login_user(User(new_id, nome, email, senha))
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        user = script_sql(f'SELECT * FROM tb_usuario WHERE usu_email = \'{email}\' AND usu_senha = \'{senha}\'') # Adicionar verificação com werkzeug
        if not user:
            return redirect(url_for('register'))

        login_user(User(*user))
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
