from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table linking schedules to selected class time slots
schedule_classtime = db.Table(
    'schedule_classtime',
    db.Column('schedule_id', db.Integer, db.ForeignKey('schedule.id'), primary_key=True),
    db.Column('classtime_id', db.Integer, db.ForeignKey('classtime.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    units = db.relationship('Unit', backref='creator', lazy=True)
    schedules = db.relationship('Schedule', backref='owner', lazy=True)
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)
    reset_tokens = db.relationship('PasswordResetToken', backref='user', lazy=True)

class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    credit_points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    class_times = db.relationship('Classtime', backref='unit', lazy=True)

class Classtime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    schedules = db.relationship('Schedule', secondary=schedule_classtime, back_populates='classtimes')

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    classtimes = db.relationship('Classtime', secondary=schedule_classtime, back_populates='schedules')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    schedule = db.relationship('Schedule', backref='messages')