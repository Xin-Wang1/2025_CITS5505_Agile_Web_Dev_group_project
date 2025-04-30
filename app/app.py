from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, User
from config import Config
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('home.html', name=current_user.username)
    else:
        return render_template('home.html', name="Guest")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken', 'danger')
            return render_template('register.html')

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/resetpw', methods=['GET', 'POST'])
def resetpw():
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            # 这里可以加发送重置密码邮件的逻辑
            flash('If the email is registered, a reset link has been sent.', 'info')
            return redirect(url_for('login'))
        else:
            flash('Please enter your email address.', 'danger')
    return render_template('resetpw.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/unit')
@login_required
def unit():
    return render_template('Unit.html')

@app.route('/schedule')
@login_required
def schedule():
    return render_template('Schedule.html')

@app.route('/My_Schedule')
@login_required
def My_Schedule():
    return render_template('My_Schedule.html')

@app.route('/ShareSchedule')
@login_required
def ShareSchedule():
    return render_template('ShareSchedule.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
