from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Unit, Classtime,Schedule, db
from datetime import datetime
import csv
from io import TextIOWrapper
import json 
schedule_bp = Blueprint('schedule', __name__)


@schedule_bp.route('/',methods=['POST'])
@login_required
def generation():
    if request.method == 'POST':
        # Get selected unit IDs from the form
        selected_unit_ids = request.form.get('selected_units')
        selected_unit_ids = json.loads(selected_unit_ids)  # Parse JSON string into a Python list
        print(f"Selected unit IDs: {selected_unit_ids}")

        # Query the database for the selected units and their class times
        selected_units = Unit.query.filter(Unit.id.in_(selected_unit_ids)).all()
        print(f"Selected units: {selected_units}")
        # Pass the selected units to the schedule page
         # Prepare the data to pass to the schedule page
        schedule_data = []
        for unit in selected_units:
            for timeslot in unit.class_times:
                schedule_data.append({
                    "unit_name": unit.name,
                    "day_of_week": timeslot.day_of_week,
                    "start_time": timeslot.start_time.strftime('%H:%M'),
                    "end_time": timeslot.end_time.strftime('%H:%M'),
                    "type": timeslot.type
                })
        print(f"Schedule data: {schedule_data}")
        return render_template('schedule.html', selected_units=selected_units,schedule_data=schedule_data)

@schedule_bp.route('/generate_schedule', methods=['POST'])
#@login_required
def generate_schedule():
    # 1) Pull the JSON arrays you sent from the front end
    selected_classtime_ids = json.loads(request.form.get('selected_classtime_ids', '[]'))
    unavailable_slots = json.loads(request.form.get('unavailable_slots', '[]'))
    print(f"Selected classtime IDs: {selected_classtime_ids}")
    print(f"Unavailable slots: {unavailable_slots}")
     # 2) Create and persist the Schedule
    sched = Schedule(user_id=1, name="Auto-Generated")
    db.session.add(sched)

    # 3) For each selected class-timeslot, look up its Classtime record
    classtimes = Classtime.query.filter(Classtime.id.in_(selected_classtime_ids)).all()
    print(f"Selected classtimes: {classtimes}")
    sched.classtimes.extend(classtimes)
    db.session.add(sched)
    db.session.commit()
    flash("Schedule generated successfully!", "success")

    return redirect(url_for('myschedule.my_schedules'))