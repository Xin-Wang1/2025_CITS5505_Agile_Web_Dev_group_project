# cleanup.py
from flask import Flask
from app import app
from app.models import Classtime, db
from collections import defaultdict

def delete_duplicate_classtimes():
    print("Searching for duplicate classtimes...")

    seen = defaultdict(list)
    duplicates = []

    all_classtimes = Classtime.query.all()
    for ct in all_classtimes:
        key = (ct.unit_id, ct.type, ct.day_of_week, ct.start_time, ct.end_time)
        seen[key].append(ct)

    for key, group in seen.items():
        if len(group) > 1:
            duplicates.extend(group[1:])

    print(f"Found {len(duplicates)} duplicate classtimes.")
    for dup in duplicates:
        db.session.delete(dup)

    db.session.commit()
    print("Duplicate classtimes deleted.")

if __name__ == "__main__":
    with app.app_context():
        delete_duplicate_classtimes()
