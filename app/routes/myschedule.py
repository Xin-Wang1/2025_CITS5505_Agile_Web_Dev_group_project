from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Unit, Classtime,Schedule, db
from datetime import datetime
import csv
from io import TextIOWrapper

myschedule_bp = Blueprint('myschedule', __name__)

@myschedule_bp.route('/')
#@login_required
def my_schedules():
    # Fetch all schedules created by the current user
    schedules = Schedule.query \
        .filter_by(user_id=current_user.id) \
        .order_by(Schedule.created_at.desc()) \
        .all()
    print(f"Schedules: {schedules}")
     # Prepare the data to pass to the template
    schedules_data = []
    for schedule in schedules:
        schedule_entry = {
            "id": schedule.id,
            "name": schedule.name,
            "created_at": schedule.created_at.strftime('%Y-%m-%d %H:%M:%S') if schedule.created_at else "Unknown",
            "classtimes": []
        }
        for classtime in schedule.classtimes:
            schedule_entry["classtimes"].append({
                "unit_name": classtime.unit.name or "Unknown Unit",
                "day_of_week": classtime.day_of_week or "Unknown Day",
                "start_time": classtime.start_time.strftime('%H:%M') if classtime.start_time else "00:00",
                "end_time": classtime.end_time.strftime('%H:%M') if classtime.end_time else "00:00",
                "type": classtime.type or "Unknown Type"
            })
        schedules_data.append(schedule_entry)

    print(f"Schedules data: {schedules_data}")
    return render_template('My_Schedule.html', schedules=schedules_data)