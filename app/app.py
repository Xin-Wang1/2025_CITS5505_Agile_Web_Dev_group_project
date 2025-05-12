from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from models import User, Unit, Classtime, Schedule, Sharedschedule
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
from routes.schedule import schedule_bp
from routes.myschedule import myschedule_bp
from models import db
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize db and migrate
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

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
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password_hash, request.form["password"]):
            login_user(user)
            return redirect(url_for("home"))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template("register.html")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken", "danger")
            return render_template("register.html")

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

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

        return render_template("resetpw_form.html", username=username)

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
    # find all schedules for the current user
    schedules = Schedule.query.filter_by(user_id=current_user.id).all()
    
    # transform schedules data for rendering
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
        return jsonify({"success": False, "message": "Have no right to delete this course schedule!"}), 403
    
    try:
        db.session.delete(schedule)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/ShareSchedule")
@login_required
def ShareSchedule():
    return render_template("ShareSchedule.html")

@app.route("/ShareSchedule/<int:id>")
@login_required
def view_shared_schedule(id):
    post = Sharedschedule.query.get_or_404(id)
    return render_template("ShareSchedule.html", post=post)

def ShareSchedule(id):
    # fetch the shared schedule or 404 if not found
    post = Sharedschedule.query.get_or_404(id)
    return render_template("ShareSchedule.html", post=post)

@app.route("/blog")
def blog():
    schedules = Sharedschedule.query.order_by(Sharedschedule.created_at.desc()).all()
    return render_template("blog.html", schedules=schedules, name=current_user.username)

app.register_blueprint(unit_bp, url_prefix="/unit")
app.register_blueprint(schedule_bp, url_prefix="/schedule")
app.register_blueprint(myschedule_bp, url_prefix='/myschedule')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # insert_sample_data(db)
    app.run(debug=True)