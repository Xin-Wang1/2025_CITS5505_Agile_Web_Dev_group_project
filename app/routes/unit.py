from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Unit, Classtime, db
from datetime import datetime
import csv
from io import TextIOWrapper

unit_bp = Blueprint("unit", __name__)


@unit_bp.route("/")
@login_required
def unit():
    # Fetch all units from the database
    units = Unit.query.all()
    return render_template("Unit.html", units=units)


# @unit_bp.route('/', methods=['POST'])
# @login_required
# def upload_unit():
#     if 'file' not in request.files:
#         flash('No file part', 'danger')
#         return redirect(url_for('unit.unit'))

#     file = request.files['file']
#     if file.filename == '':
#         flash('No selected file', 'danger')
#         return redirect(url_for('unit.unit'))

#     if file and file.filename.endswith('.csv'):
#         try:
#             csv_file = TextIOWrapper(file, encoding='utf-8')
#             csv_reader = csv.DictReader(csv_file)

#             for row in csv_reader:
#                 unit_code = row['Unit Code']
#                 unit_name = row['Unit Name']
#                 credit_points = int(row['Credit Points'])
#                 description = row['Description']

#                 unit = Unit.query.filter_by(code=unit_code).first()
#                 if not unit:
#                     unit = Unit(
#                         code=unit_code,
#                         name=unit_name,
#                         credit_points=credit_points,
#                         description=description,
#                         created_by=1,
#                         created_at=datetime.utcnow()
#                     )
#                     print(f"Adding unit: {unit}")
#                     db.session.add(unit)
#                     db.session.flush()

#                 class_type = row['Class Type']
#                 day_of_week = row['Day of Week']
#                 start_time = datetime.strptime(row['Start Time'], '%H:%M').time()
#                 end_time = datetime.strptime(row['End Time'], '%H:%M').time()
#                  # Check if the class time already exists for this unit
#                 existing_class_time = Classtime.query.filter_by(
#                     unit_id=unit.id,
#                     type=class_type,
#                     day_of_week=day_of_week,
#                     start_time=start_time,
#                     end_time=end_time
#                 ).first()

#                 if not existing_class_time:
#                     class_time = Classtime(
#                         unit_id=unit.id,
#                         type=class_type,
#                         day_of_week=day_of_week,
#                         start_time=start_time,
#                         end_time=end_time,
#                         created_at=datetime.utcnow()
#                     )
#                     print(f"Adding class time: {class_time.start_time}")
#                     db.session.add(class_time)
#                 else:
#                     print(f"Class time already exists: {existing_class_time.start_time}")

#             db.session.commit()
#             flash('Units and class times uploaded successfully!', 'success')
#         except Exception as e:
#             db.session.rollback()
#             flash(f'Error processing file: {str(e)}', 'danger')
#     else:
#         flash('Invalid file format. Please upload a CSV file.', 'danger')

#     return redirect(url_for('unit.unit'))


@unit_bp.route("/", methods=["POST"])
@login_required
def upload_unit():
    if "file" not in request.files:
        flash("No file part", "danger")
        return redirect(url_for("unit.unit"))

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file", "danger")
        return redirect(url_for("unit.unit"))

    if file and file.filename.endswith(".csv"):
        try:
            csv_file = TextIOWrapper(file, encoding="utf-8")
            csv_reader = list(csv.DictReader(csv_file))  # Convert to list to read twice

            new_units = 0
            new_classtimes = 0

            for row in csv_reader:
                unit_code = row["Unit Code"]
                unit_name = row["Unit Name"]
                credit_points = int(row["Credit Points"])
                description = row["Description"]

                unit = Unit.query.filter_by(code=unit_code).first()
                if not unit:
                    unit = Unit(
                        code=unit_code,
                        name=unit_name,
                        credit_points=credit_points,
                        description=description,
                        created_by=current_user.id,
                        created_at=datetime.utcnow(),
                    )
                    db.session.add(unit)
                    db.session.flush()  # Assigns unit.id
                    new_units += 1

                class_type = row["Class Type"]
                day_of_week = row["Day of Week"]
                start_time = datetime.strptime(row["Start Time"], "%H:%M").time()
                end_time = datetime.strptime(row["End Time"], "%H:%M").time()

                existing_class_time = Classtime.query.filter_by(
                    unit_id=unit.id,
                    type=class_type,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                ).first()

                if not existing_class_time:
                    class_time = Classtime(
                        unit_id=unit.id,
                        type=class_type,
                        day_of_week=day_of_week,
                        start_time=start_time,
                        end_time=end_time,
                        created_at=datetime.utcnow(),
                    )
                    db.session.add(class_time)
                    new_classtimes += 1

            if new_units == 0 and new_classtimes == 0:
                flash(
                    "Upload skipped: All units and class times already exist.", "info"
                )
            else:
                db.session.commit()
                flash(
                    f"Upload complete: {new_units} new unit(s), {new_classtimes} new class time(s) added.",
                    "success",
                )

        except Exception as e:
            db.session.rollback()
            flash(f"Error processing file: {str(e)}", "danger")
    else:
        flash("Invalid file format. Please upload a CSV file.", "danger")

    return redirect(url_for("unit.unit"))
