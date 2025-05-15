from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Unit, Classtime, Schedule, db
from datetime import datetime
import csv
from io import TextIOWrapper

myschedule_bp = Blueprint("myschedule", __name__)


@myschedule_bp.route("/My_Schedule/")
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
            classtimes.append(
                {
                    "id": classtime.id,
                    "unit_id": classtime.unit_id,
                    "unit_name": (
                        classtime.unit.name if classtime.unit else "Unknown Unit"
                    ),
                    "type": classtime.type,
                    "day_of_week": classtime.day_of_week,
                    "start_time": (
                        classtime.start_time.strftime("%H:%M")
                        if classtime.start_time
                        else None
                    ),
                    "end_time": (
                        classtime.end_time.strftime("%H:%M")
                        if classtime.end_time
                        else None
                    ),
                    "created_at": (
                        classtime.created_at.isoformat()
                        if classtime.created_at
                        else None
                    ),
                }
            )
        schedules_data.append(
            {
                "id": schedule.id,
                "name": schedule.name,
                "created_at": (
                    schedule.created_at.isoformat() if schedule.created_at else None
                ),
                "classtimes": classtimes,
            }
        )

    return render_template("My_Schedule.html", schedules=schedules_data)
