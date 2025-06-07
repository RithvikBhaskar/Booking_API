from app import db, ClassSchedule, app
from datetime import datetime
from zoneinfo import ZoneInfo
import os

# Ensure the 'data' directory exists
base_dir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(base_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

def seed_data():
    """Populate the database with sample fitness classes."""
    # Clear existing data
    db.drop_all()
    db.create_all()

    # Sample classes in IST
    classes = [
        {
            'name': 'Yoga',
            'instructor': 'Jane Doe',
            'date_time': datetime(2025, 6, 8, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata")),
            'capacity': 10
        }
    ]

    for cls in classes:
        new_class = ClassSchedule(
            name=cls['name'],
            instructor=cls['instructor'],
            date_time=cls['date_time'],
            capacity=cls['capacity']
        )
        db.session.add(new_class)

    db.session.commit()
    print("Seed data added successfully")

if __name__ == '__main__':
    with app.app_context():
        seed_data()