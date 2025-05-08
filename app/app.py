from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from models import User, Unit, Classtime, Schedule, Sharedschedule, Comment
from config import Config
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from insert_sample_data import insert_sample_data
from routes.unit import unit_bp
from models import db
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize db and migrate
db.init_app(app)
migrate = Migrate(app, db)

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
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            return redirect(url_for('ShareSchedule'))
        flash('Username or Password is invalid')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Password mismatch', 'danger')
            return render_template('register.html')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('The username has been occupied', 'danger')
            return render_template('register.html')

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/resetpw', methods=['GET', 'POST'])
def resetpw():
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            flash('The reset link has been sent', 'info')
            return redirect(url_for('login'))
        else:
            flash('Please enter your email address', 'danger')
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
    return render_template('ShareSchedule.html', username=current_user.username)

@app.route('/api/posts', methods=['GET'])
@login_required
def get_posts():
    posts = Sharedschedule.query.order_by(Sharedschedule.created_at.desc()).all()
    return jsonify([{
        'id': post.id,
        'title': post.title,
        'description': post.description,
        'file_url': post.file_url,
        'user': post.author.username,
        'created_at': post.created_at.isoformat(),
        'comments': [{'id': c.id, 'content': c.content, 'file_url': c.file_url, 'user': c.author.username} for c in post.comments]
    } for post in posts])

@app.route('/api/posts', methods=['POST'])
@login_required
def create_post():
    data = request.form
    title = data.get('title')
    description = data.get('description')
    schedule_id = data.get('schedule_id', 1)  
    if not (title and description):
        return jsonify({'error': 'Title and content are required fields'}), 400
    if len(title) > 150:
        return jsonify({'error': 'The length of the title cannot exceed 150 characters'}), 400

    file_url = None
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_url = f'/static/uploads/{filename}'

    post = Sharedschedule(
        schedule_id=schedule_id,
        user_id=current_user.id,
        title=title,
        description=description,
        file_url=file_url
    )
    db.session.add(post)
    db.session.commit()
    return jsonify({'message': 'The post was successfully created.', 'id': post.id}), 201

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    post = Sharedschedule.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized deletion'}), 403
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'The post has been deleted'}), 200

@app.route('/api/comments', methods=['POST'])
@login_required
def create_comment():
    data = request.form
    shared_schedule_id = data.get('shared_schedule_id')
    content = data.get('content')
    if not (shared_schedule_id and content):
        return jsonify({'error': 'The comment content is a required field'}), 400

    file_url = None
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_url = f'/static/uploads/{filename}'

    comment = Comment(
        shared_schedule_id=shared_schedule_id,
        user_id=current_user.id,
        content=content,
        file_url=file_url
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({'message': 'The comment was added successfully', 'id': comment.id}), 201

app.register_blueprint(unit_bp, url_prefix='/unit')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # insert_sample_data(db)
    app.run(debug=True)