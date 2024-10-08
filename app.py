from flask import Flask, render_template, redirect, url_for, flash
from flask_migrate import Migrate
from models import db, ToDo, User
from forms import ToDoForm, RegistrationForm, LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '8e1a0fb96cd1a982453a37f15487e613f0266c40565198b4'

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login Successful!', 'success')
            return redirect(url_for('index'))  # Redirect ke index setelah login berhasil
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)  # Render login.html jika tidak ada POST yang valid

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/')
def index():
    if current_user.is_authenticated:
        todos = ToDo.query.filter_by(user_id=current_user.id).all()
        form = ToDoForm()
        return render_template('todo.html', todos=todos, form=form)
    else:
        return redirect(url_for('login'))  # Arahkan ke halaman login jika belum login

@app.route('/add', methods=['POST'])
@login_required  # Hanya pengguna yang sudah login yang bisa menambah tugas
def add_todo():
    form = ToDoForm()
    if form.validate_on_submit():
        new_todo = ToDo(task=form.task.data, user_id=current_user.id)  # Menyimpan user_id
        db.session.add(new_todo)
        db.session.commit()
        flash('New task has been added!', 'success')  # Memberi tahu pengguna
        return redirect(url_for('index'))
    flash('Failed to add task. Please try again.', 'danger')  # Memberi tahu jika gagal
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
