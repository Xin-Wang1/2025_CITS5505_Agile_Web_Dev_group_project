from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Unit, Classtime,Schedule, db
from datetime import datetime
import csv
from io import TextIOWrapper
import json 
schedule_bp = Blueprint('schedule', __name__)


@schedule_bp.route("/schedule/generation", methods=["POST"])
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
   
    
    # Link selected units to the new schedule
    for unit_id in selected_unit_ids:
        classtimes = Classtime.query.filter_by(unit_id=unit_id).all()
        for classtime in classtimes:
            new_schedule.classtimes.append(classtime)
     
    flash('Schedule generated successfully!', 'success')
    # Redirect with selected_unit_ids as query parameter
    return redirect(url_for('schedule.generate_schedule', unit_ids=','.join(map(str, selected_unit_ids))))

@schedule_bp.route("/schedule/generate_schedule", methods=["GET", "POST"])
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



@schedule_bp.route("/schedule/delete/<int:schedule_id>", methods=["POST"])
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
