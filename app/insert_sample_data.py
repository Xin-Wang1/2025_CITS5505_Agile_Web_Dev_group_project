from app.models import User, Unit, Classtime, Schedule
from werkzeug.security import generate_password_hash
from datetime import time

def insert_sample_data(db):
    # Clear existing data (optional)
    db.drop_all()
    db.create_all()

    # Insert sample users
    user1 = User(username="test1", password_hash=generate_password_hash("password123"))
    user2 = User(username="test2", password_hash=generate_password_hash("securepass"))

    db.session.add(user1)
    db.session.add(user2)

    # Insert sample units
    unit1 = Unit(code="CITS5505", name="Agile Web Development", credit_points=6, description="Learn Agile and Web Development", created_by=user1.id)
    unit2 = Unit(code="CITS5551", name="Data Science", credit_points=6, description="Learn Data Science concepts", created_by=user2.id)

    db.session.add(unit1)
    db.session.add(unit2)

    # Insert sample class times
    class_time1 = Classtime(unit_id=1, type="Lecture", day_of_week="Monday", start_time=time(9, 0), end_time=time(11, 0))
    class_time2 = Classtime(unit_id=2, type="Tutorial", day_of_week="Wednesday", start_time=time(14, 0), end_time=time(16, 0))

    db.session.add(class_time1)
    db.session.add(class_time2)

    # Insert sample schedules
    schedule1 = Schedule(user_id=1, name="John's Schedule")
    schedule1.class_times.append(class_time1)

    schedule2 = Schedule(user_id=2, name="Jane's Schedule")
    schedule2.class_times.append(class_time2)

    db.session.add(schedule1)
    db.session.add(schedule2)

    # Commit changes
    db.session.commit()

    print("Sample data inserted successfully!")