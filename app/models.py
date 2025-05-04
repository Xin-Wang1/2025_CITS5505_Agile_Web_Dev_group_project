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
    # Default table name 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    units = db.relationship('Unit', backref='creator', lazy=True)
    schedules = db.relationship('Schedule', backref='owner', lazy=True)
    shared_posts = db.relationship('Sharedschedule', backref='author', lazy=True)
    reset_tokens = db.relationship('PasswordResetToken', backref='user', lazy=True)

class PasswordResetToken(db.Model):
    # Default table name 'passwordresettoken'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

class Unit(db.Model):
    # Default table name 'unit'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    credit_points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Each unit can have multiple class time slots
    class_times = db.relationship('Classtime', backref='unit', lazy=True)

class Classtime(db.Model):
    # Default table name 'classtime'
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., Lecture, Tutorial, Lab
    day_of_week = db.Column(db.String(10), nullable=False)  # e.g., "Monday"
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    schedules = db.relationship('Schedule', secondary=schedule_classtime, back_populates='classtimes')

class Schedule(db.Model):
    # Default table name 'schedule'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Selected class slots via association table
    classtimes = db.relationship('Classtime', secondary=schedule_classtime, back_populates='schedules')

class Sharedschedule(db.Model):
    # Default table name 'sharedschedule'
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    schedule = db.relationship('Schedule', backref='shares')

class Comment(db.Model):
    # Default table name 'comment'
    id = db.Column(db.Integer, primary_key=True)
    shared_schedule_id = db.Column(db.Integer, db.ForeignKey('sharedschedule.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User')
    shared_post = db.relationship('Sharedschedule', backref='comments')
