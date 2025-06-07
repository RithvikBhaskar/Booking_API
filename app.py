from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
# import logging
from zoneinfo import ZoneInfo
import os

app = Flask(__name__)

# Ensure the 'data' directory exists
base_dir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(base_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

# Use an absolute path for the SQLite database
db_path = os.path.join(data_dir, 'fitness_studio.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     filename='app.log',
#     format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
# )

# Database Models
class ClassSchedule(db.Model):
    """Model representing a fitness class schedule."""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    instructor = db.Column(db.String(100), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)  # Stored in IST
    capacity = db.Column(db.Integer, nullable=False)
    bookings = db.relationship('Booking', backref='class_schedule', lazy=True, cascade="all, delete-orphan")

class Booking(db.Model):
    """Model representing a booking for a fitness class."""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = db.Column(db.String(36), db.ForeignKey('class_schedule.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    booking_time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")))

# # Initialize database with error handling
# try:
#     with app.app_context():
#         db.create_all()
#     print("Database initialized successfully")
# except Exception as e:
#     print(f"Error initializing database: {e}")
#     raise

# Helper Functions
def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_class_type(name: str) -> bool:
    """Validate that the class type is Yoga, Zumba, or HIIT."""
    allowed_classes = ['Yoga', 'Zumba', 'HIIT']
    return name in allowed_classes

def convert_to_timezone(dt: datetime, tz_name: str) -> str:
    """Convert a datetime object to the specified timezone and return ISO format."""
    try:
        target_tz = ZoneInfo(tz_name)
        return dt.astimezone(target_tz).isoformat()
    except Exception as e:
        print(f"Timezone conversion error: {str(e)}")
        return dt.isoformat()

# API Endpoints
@app.route('/api/classes', methods=['GET'])
def get_classes():
    """
    Retrieve a list of upcoming fitness classes.

    Query Parameters:
        - timezone (optional): Timezone name (e.g., 'America/New_York'). Defaults to 'Asia/Kolkata'.

    Returns:
        - 200: JSON list of classes with id, name, instructor, date_time, capacity, and available_slots.
        - 500: Error message if something goes wrong.
    """
    try:
        tz_name = request.args.get('timezone', 'Asia/Kolkata')
        classes = ClassSchedule.query.filter(
            ClassSchedule.date_time >= datetime.now(ZoneInfo("Asia/Kolkata"))
        ).all()
        result = [
            {
                'id': cls.id,
                'name': cls.name,
                'instructor': cls.instructor,
                'date_time': convert_to_timezone(cls.date_time, tz_name),
                'capacity': cls.capacity,
                'available_slots': cls.capacity - len(cls.bookings)
            }
            for cls in classes
        ]
        print(f"Retrieved {len(result)} upcoming classes for timezone {tz_name}")
        return jsonify(result), 200
    except Exception as e:
        print(f"Error in get_classes: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/book', methods=['POST'])
def create_booking():
    """
    Create a booking for a fitness class.

    Request Body:
        - class_id (str): ID of the class to book.
        - user_name (str): Name of the client.
        - user_email (str): Email of the client.

    Returns:
        - 201: JSON with booking details if successful.
        - 400: Error message for invalid input or booking constraints.
        - 500: Error message if something goes wrong.
    """
    data = request.get_json()
    try:
        required_fields = ['class_id', 'user_name', 'user_email']
        if not all(field in data for field in required_fields):
            print(f"Missing fields in booking request: {data}")
            return jsonify({'error': 'Missing required fields'}), 400

        if not validate_email(data['user_email']):
            print(f"Invalid email in booking request: {data['user_email']}")
            return jsonify({'error': 'Invalid email format'}), 400

        if not data['user_name'].strip():
            print("Empty user_name in booking request")
            return jsonify({'error': 'User name cannot be empty'}), 400

        cls = ClassSchedule.query.get_or_404(data['class_id'])
        if cls.date_time < datetime.now(ZoneInfo("Asia/Kolkata")):
            print(f"Attempt to book past class: {cls.id}")
            return jsonify({'error': 'Cannot book a past class'}), 400

        if len(cls.bookings) >= cls.capacity:
            print(f"Attempt to overbook class: {cls.id}")
            return jsonify({'error': 'Class is fully booked'}), 400

        existing_booking = Booking.query.filter_by(
            class_id=data['class_id'], user_email=data['user_email']
        ).first()
        if existing_booking:
            print(f"Duplicate booking attempt by {data['user_email']} for class {cls.id}")
            return jsonify({'error': 'User already booked this class'}), 400

        new_booking = Booking(
            class_id=data['class_id'],
            user_name=data['user_name'],
            user_email=data['user_email']
        )
        db.session.add(new_booking)
        db.session.commit()
        print(f"Booking created: {new_booking.id} for class {cls.id}")
        return jsonify({
            'id': new_booking.id,
            'class_id': new_booking.class_id,
            'user_name': new_booking.user_name,
            'user_email': new_booking.user_email,
            'booking_time': new_booking.booking_time.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_booking: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """
    Retrieve all bookings for a specific email address.

    Query Parameters:
        - email (required): Email address of the client.
        - timezone (optional): Timezone name (e.g., 'America/New_York'). Defaults to 'Asia/Kolkata'.

    Returns:
        - 200: JSON list of bookings with id, class_id, class_name, date_time, user_name, user_email, and booking_time.
        - 400: Error message if email is invalid or missing.
        - 500: Error message if something goes wrong.
    """
    try:
        email = request.args.get('email')
        if not email or not validate_email(email):
            print(f"Invalid or missing email in get_bookings: {email}")
            return jsonify({'error': 'Valid email parameter required'}), 400

        bookings = Booking.query.filter_by(user_email=email).all()
        result = [
            {
                'id': b.id,
                'class_id': b.class_id,
                'class_name': b.class_schedule.name,
                'date_time': convert_to_timezone(
                    b.class_schedule.date_time, request.args.get('timezone', 'Asia/Kolkata')
                ),
                'user_name': b.user_name,
                'user_email': b.user_email,
                'booking_time': b.booking_time.isoformat()
            }
            for b in bookings
        ]
        print(f"Retrieved {len(result)} bookings for {email}")
        return jsonify(result), 200
    except Exception as e:
        print(f"Error in get_bookings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/classes', methods=['POST'])
def create_class():
    """
    Create a new fitness class (for seeding/testing purposes).

    Request Body:
        - name (str): Name of the class (Yoga, Zumba, HIIT).
        - instructor (str): Name of the instructor.
        - date_time (str): ISO format datetime (e.g., '2025-06-08T10:00:00').
        - capacity (int): Maximum number of slots.

    Returns:
        - 201: JSON with class details if successful.
        - 400: Error message for invalid input.
        - 500: Error message if something goes wrong.
    """
    data = request.get_json()
    try:
        required_fields = ['name', 'instructor', 'date_time', 'capacity']
        if not all(field in data for field in required_fields):
            print(f"Missing fields in create_class: {data}")
            return jsonify({'error': 'Missing required fields'}), 400

        if not validate_class_type(data['name']):
            print(f"Invalid class type: {data['name']}")
            return jsonify({'error': 'Invalid class type. Must be Yoga, Zumba, or HIIT'}), 400

        date_time = datetime.fromisoformat(data['date_time']).replace(tzinfo=ZoneInfo("Asia/Kolkata"))
        if date_time < datetime.now(ZoneInfo("Asia/Kolkata")):
            print(f"Attempt to schedule past class: {data['date_time']}")
            return jsonify({'error': 'Cannot schedule class in the past'}), 400

        if data['capacity'] <= 0:
            print(f"Invalid capacity: {data['capacity']}")
            return jsonify({'error': 'Capacity must be positive'}), 400

        new_class = ClassSchedule(
            name=data['name'],
            instructor=data['instructor'],
            date_time=date_time,
            capacity=data['capacity']
        )
        db.session.add(new_class)
        db.session.commit()
        print(f"Class created: {new_class.id}")
        return jsonify({
            'id': new_class.id,
            'name': new_class.name,
            'instructor': new_class.instructor,
            'date_time': new_class.date_time.isoformat(),
            'capacity': new_class.capacity
        }), 201
    except ValueError:
        print(f"Invalid date format: {data.get('date_time')}")
        return jsonify({'error': 'Invalid date format. Use ISO format (e.g., 2025-06-07T15:00:00)'}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_class: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting Flask server...")
    try:
        app.run(debug=False, host='127.0.0.1', port=5000)
        print("Flask server started on http://127.0.0.1:5000")
    except Exception as e:
        print(f"Failed to start Flask server: {e}")