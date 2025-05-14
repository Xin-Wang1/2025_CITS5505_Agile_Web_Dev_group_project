from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from models import User, Unit, Classtime, Schedule, Message
from config import Config
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from insert_sample_data import insert_sample_data
from routes.unit import unit_bp
from routes.myschedule import myschedule_bp
from models import db
from flask_migrate import Migrate
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename
from forms import LoginForm, RegisterForm, ResetPasswordForm
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object(Config)

# Initialize db and migrate
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    if current_user.is_authenticated:
        return render_template("home.html", name=current_user.username)
    else:
        return render_template("home.html", name="Guest")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for("home"))
        flash("Invalid credentials", "danger")

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already taken", "danger")
            return render_template("register.html", form=form)

        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)

@app.route("/resetpw", methods=["GET", "POST"])
def resetpw():
    if request.method == "POST":
        username = request.form.get("username")
        user = User.query.filter_by(username=username).first()
        if user:
            return redirect(url_for("resetpw_username", username=username))
        else:
            flash("Username not found.", "danger")
            return render_template("resetpw.html")
    return render_template("resetpw.html")

@app.route("/resetpw/<username>", methods=["GET", "POST"])
def resetpw_username(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("Invalid username.", "danger")
        return redirect(url_for("resetpw"))

    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("resetpw_form.html", username=username)

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Password reset successful. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("resetpw_form.html", username=username)

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", name=current_user.username)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route('/My_Schedule')
@login_required
def My_Schedule():
    print(f"Request path: {request.path}")  
    # Find all schedules for the current user
    schedules = Schedule.query.filter_by(user_id=current_user.id).all()
    
    # Transform schedules data for rendering
    schedules_data = []
    for schedule in schedules:
        classtimes = []
        for classtime in schedule.classtimes:
            classtimes.append({
                'id': classtime.id,
                'unit_id': classtime.unit_id,
                'unit_name': classtime.unit.name if classtime.unit else 'Unknown Unit',
                'type': classtime.type,
                'day_of_week': classtime.day_of_week,
                'start_time': classtime.start_time.strftime('%H:%M') if classtime.start_time else None,
                'end_time': classtime.end_time.strftime('%H:%M') if classtime.end_time else None,
                'created_at': classtime.created_at.isoformat() if classtime.created_at else None
            })
        schedules_data.append({
            'id': schedule.id,
            'name': schedule.name,
            'created_at': schedule.created_at.isoformat() if schedule.created_at else None,
            'classtimes': classtimes
        })
    
    return render_template("My_Schedule.html", schedules=schedules_data)

@app.route("/schedule/delete/<int:schedule_id>", methods=["POST"])
@login_required
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    if schedule.user_id != current_user.id:
        return jsonify({"success": False, "message": "No permission to delete this schedule!"}), 403
    
    try:
        db.session.delete(schedule)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# Upload unit
@app.route("/schedule/generation", methods=["POST"])
@login_required
def schedule_generation():
    # Get selected unit IDs from the request
    selected_unit_ids = request.form.get('selected_units')
    
    # Check if selected_unit_ids is None or empty
    if not selected_unit_ids:
        flash('Please select at least one unit!', 'danger')
        return redirect(url_for('unit.upload_unit'))
    
    try:
        # Try to parse the JSON string into a Python list
        selected_unit_ids = json.loads(selected_unit_ids)
        # Check if the list is empty
        if not selected_unit_ids:
            flash('Please select at least one unit!', 'danger')
            return redirect(url_for('unit.upload_unit'))
    except json.JSONDecodeError:
        # Catch JSON parsing errors
        flash('Please try again, invalid selection!', 'danger')
        return redirect(url_for('unit.upload_unit'))
    
    # Create a new schedule
    new_schedule = Schedule(
        user_id=current_user.id,
        name=f"Schedule {current_user.username} {len(current_user.schedules) + 1}",
        created_at=datetime.utcnow()
    )
    db.session.add(new_schedule)
    
    # Link selected units to the new schedule
    for unit_id in selected_unit_ids:
        classtimes = Classtime.query.filter_by(unit_id=unit_id).all()
        for classtime in classtimes:
            new_schedule.classtimes.append(classtime)
    
    db.session.commit()
    
    flash('Schedule generated successfully!', 'success')
    # Redirect with selected_unit_ids as query parameter
    return redirect(url_for('generate_schedule', unit_ids=','.join(map(str, selected_unit_ids))))

@app.route("/schedule/generate_schedule", methods=["GET", "POST"])
@login_required
def generate_schedule():
    if request.method == "POST":
        selected_classtime_ids = json.loads(request.form.get('selected_classtime_ids', '[]'))
        unit_ids = request.form.getlist('unit_ids')
        
        # Create or update schedule
        new_schedule = Schedule(
            user_id=current_user.id,
            name=f"Schedule {current_user.username} {len(current_user.schedules) + 1}",
            created_at=datetime.utcnow()
        )
        db.session.add(new_schedule)
        
        # Link selected classtimes
        for classtime_id in selected_classtime_ids:
            classtime = Classtime.query.get(classtime_id)
            if classtime:
                new_schedule.classtimes.append(classtime)
        
        db.session.commit()
        flash('Schedule saved successfully!', 'success')
        return redirect(url_for('My_Schedule'))
    
    # GET request: Render Schedule.html with selected units
    selected_unit_ids = request.args.get('unit_ids', '').split(',') if request.args.get('unit_ids') else []
    selected_units = Unit.query.filter(Unit.id.in_(selected_unit_ids)).all() if selected_unit_ids else []
    total_credits = sum(unit.credit_points for unit in selected_units)

    # Transform selected_units to a serializable format
    serialized_units = []
    for unit in selected_units:
        # Convert class_times to a list of dictionaries
        class_times = [
            {
                'id': classtime.id,
                'unit_id': classtime.unit_id,
                'type': classtime.type,
                'day_of_week': classtime.day_of_week,
                'start_time': classtime.start_time.strftime('%H:%M') if classtime.start_time else None,
                'end_time': classtime.end_time.strftime('%H:%M') if classtime.end_time else None,
                'created_at': classtime.created_at.isoformat() if classtime.created_at else None
            }
            for classtime in unit.class_times
        ]
        serialized_units.append({
            'id': unit.id,
            'name': unit.name,
            'credit_points': unit.credit_points,
            'class_times': class_times
        })
    
    return render_template('Schedule.html',
                         selected_units=serialized_units,
                         total_credits=total_credits)

@app.route("/messages")
@login_required
def messages():
    # Get sent and received messages
    sent_messages = Message.query.filter_by(sender_id=current_user.id).order_by(Message.created_at.desc()).all()
    received_messages = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.created_at.desc()).all()
    return render_template("ShareSchedule.html", sent_messages=sent_messages, received_messages=received_messages)

@app.route("/messages/send", methods=["POST"])
@login_required
def send_message():
    receiver_username = request.form.get("receiver_username").strip()
    content = request.form.get("content").strip()
    file = request.files.get("file")

    # Validate input
    if not receiver_username or not content:
        flash("Recipient and message content cannot be empty！", "danger")
        return redirect(url_for("messages"))

    # Find receiver
    receiver = User.query.filter_by(username=receiver_username).first()
    if not receiver:
        flash("Recipient does not exist！", "danger")
        return redirect(url_for("messages"))
    if receiver.id == current_user.id:
        flash("Can't send messages to myself！", "danger")
        return redirect(url_for("messages"))

    # Handle file upload
    file_url = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file_url = f"/{file_path}"

    # Create new message
    new_message = Message(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        content=content,
        file_url=file_url,
        created_at=datetime.utcnow()
    )
    db.session.add(new_message)
    db.session.commit()

    flash("Sent successfully！", "success")
    return redirect(url_for("messages"))

@app.route("/messages/search", methods=["GET"])
@login_required
def search_users():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])
    users = User.query.filter(User.username.ilike(f"%{query}%")).all()
    return jsonify([{"id": user.id, "username": user.username} for user in users])

app.register_blueprint(unit_bp, url_prefix="/unit")
app.register_blueprint(myschedule_bp, url_prefix='/myschedule')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # insert_sample_data(db)
    app.run(debug=True)