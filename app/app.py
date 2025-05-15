from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from app.models import User, Unit, Classtime, Schedule, Message
from app.config import Config
from app.models import User, Unit, Classtime, Schedule, Message
from app.config import Config
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from app.insert_sample_data import insert_sample_data
from app.routes.unit import unit_bp
from app.routes.myschedule import myschedule_bp
from app.routes.schedule import schedule_bp
from app.routes.auth import auth_bp
from app.models import db
from flask_migrate import Migrate
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename
from app.forms import LoginForm, RegisterForm, ResetPasswordForm
from app.forms import LoginForm, RegisterForm, ResetPasswordForm
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(auth_bp, url_prefix="/auth")

# Initialize db and migrate
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# File upload configuration
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB limit


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


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
            form = ResetPasswordForm()
            return render_template("resetpw_form.html", username=username, form=form)

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Password reset successful. You can now log in.", "success")
        return redirect(url_for("login"))

    form = ResetPasswordForm()
    return render_template("resetpw_form.html", username=username, form=form)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", name=current_user.username)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/messages/")
@login_required
def messages():
    # Get sent and received messages
    users = User.query.all()
    sent_messages = (
        Message.query.filter_by(sender_id=current_user.id)
        .order_by(Message.created_at.desc())
        .all()
    )
    received_messages = (
        Message.query.filter_by(receiver_id=current_user.id)
        .order_by(Message.created_at.desc())
        .all()
    )

    received_schedule_ids = {
        msg.schedule_id for msg in received_messages if msg.schedule_id  # skip None
    }
    schedules = Schedule.query.filter(Schedule.id.in_(received_schedule_ids)).all()
    schedules_data = []
    for schedule in schedules:
        class_list = []
        for ct in schedule.classtimes:
            class_list.append(
                {
                    "id": ct.id,
                    "unit_id": ct.unit_id,
                    "unit_name": ct.unit.name or "Unknown",
                    "type": ct.type,
                    "day_of_week": ct.day_of_week,
                    "start_time": ct.start_time.strftime("%H:%M"),
                    "end_time": ct.end_time.strftime("%H:%M"),
                }
            )
        schedules_data.append(
            {"id": schedule.id, "name": schedule.name, "classtimes": class_list}
        )
    return render_template(
        "ShareSchedule.html",
        sent_messages=sent_messages,
        received_messages=received_messages,
        users=users,
        schedules=schedules_data,
    )


@app.route("/messages/send", methods=["POST"])
@login_required
def send_message():
    receiver_id = request.form.get("receiver_id")
    if not receiver_id:
        flash("Please select a recipient.", "danger")
        return redirect(url_for("messages"))
    receiver = User.query.get(int(receiver_id))
    if not receiver or receiver.id == current_user.id:
        flash("Invalid recipient.", "danger")
        return redirect(url_for("messages"))

    schedule_id = request.form.get("schedule_id")
    schedule = None
    if schedule_id:
        schedule = Schedule.query.filter_by(
            id=int(schedule_id), user_id=current_user.id
        ).first()
        if not schedule:
            flash("Invalid schedule selected.", "danger")
            return redirect(url_for("messages"))

    # 3) Message content
    content = request.form.get("content", "").strip()
    if not content:
        flash("Message content cannot be empty.", "danger")
        return redirect(url_for("messages"))

    # Create new message
    new_message = Message(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        content=content,
        schedule_id=schedule.id if schedule else None,
        created_at=datetime.utcnow(),
    )
    db.session.add(new_message)
    db.session.commit()

    flash("Sent successfully！", "success")
    return redirect(url_for("messages"))


app.register_blueprint(unit_bp, url_prefix="/unit")
app.register_blueprint(myschedule_bp, url_prefix="/myschedule")
app.register_blueprint(schedule_bp, url_prefix="/schedule")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
