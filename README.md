Fitness Booking API
Overview
This project is a RESTful API for managing fitness class bookings, developed as part of the Omnify Python Developer Internship Assignment. It allows users to view upcoming fitness classes, book a class, and retrieve bookings by email. The API is built using Flask, SQLAlchemy with SQLite, and includes unit tests to ensure functionality.
Features

List Upcoming Classes: Retrieve a list of all upcoming fitness classes with details like name, date/time, instructor, and available slots.
Book a Class: Submit a booking request for a specific class, with validation for available slots.
View Bookings: Retrieve all bookings made by a specific email address.
Data Persistence: Uses SQLite to store class schedules and bookings.
Unit Tests: Includes 9 unit tests to verify API functionality.

Prerequisites

Python 3.12.3 or higher
pip (Python package manager)
Git (for cloning the repository)

Setup Instructions

Clone the Repository:
git clone <repository-url>
cd fitness-booking-api


Create a Virtual Environment:
python -m venv venv


On Windows:venv\Scripts\activate


On macOS/Linux:source venv/bin/activate




Install Dependencies:
pip install -r requirements.txt


Seed the Database:

Run the script to populate the SQLite database with sample classes:python seed_data.py




Run the Flask Server:
python app.py


The server will start on http://127.0.0.1:5000.



API Endpoints
GET /api/classes

Description: Retrieve a list of all upcoming fitness classes.
Query Parameters:
timezone (optional): Timezone name (e.g., America/New_York). Defaults to Asia/Kolkata.


Response (200 OK):[
    {
        "id": "cb1b090b-0409-42cd-97ee-158b41677cb6",
        "name": "Yoga",
        "instructor": "Jane Doe",
        "date_time": "2025-06-08T10:00:00+05:30",
        "capacity": 10,
        "available_slots": 10
    },
    ...
]


Example:curl http://127.0.0.1:5000/api/classes



POST /api/book

Description: Book a fitness class.
Request Body:{
    "class_id": "cb1b090b-0409-42cd-97ee-158b41677cb6",
    "user_name": "John Doe",
    "user_email": "john.doe@example.com"
}


Response (201 Created):{
    "id": "some-uuid",
    "class_id": "cb1b090b-0409-42cd-97ee-158b41677cb6",
    "user_name": "John Doe",
    "user_email": "john.doe@example.com",
    "booking_time": "2025-06-07T18:42:00+05:30"
}


Errors:
400: Invalid email, missing fields, class fully booked, past class, or duplicate booking.


Example (PowerShell):Invoke-WebRequest -Uri http://127.0.0.1:5000/api/book -Method POST -Headers @{ "Content-Type" = "application/json" } -Body '{"class_id":"cb1b090b-0409-42cd-97ee-158b41677cb6","user_name":"John Doe","user_email":"john.doe@example.com"}' | Select-Object -ExpandProperty Content



GET /api/bookings

Description: Retrieve all bookings for a specific email address.
Query Parameters:
email (required): Email address of the client.
timezone (optional): Timezone name (e.g., America/New_York). Defaults to Asia/Kolkata.


Response (200 OK):[
    {
        "id": "some-uuid",
        "class_id": "cb1b090b-0409-42cd-97ee-158b41677cb6",
        "class_name": "Yoga",
        "date_time": "2025-06-08T10:00:00+05:30",
        "user_name": "John Doe",
        "user_email": "john.doe@example.com",
        "booking_time": "2025-06-07T18:42:00+05:30"
    }
]


Errors:
400: Invalid or missing email.


Example (PowerShell):Invoke-WebRequest -Uri http://127.0.0.1:5000/api/bookings?email=john.doe@example.com | Select-Object -ExpandProperty Content



Running Unit Tests

Ensure the server is not running (or run tests in a separate terminal).
Run:python -m unittest test_api.py


Expected output: All 9 tests should pass.

Project Structure

app.py: Main Flask application with API endpoints.
seed_data.py: Script to populate the database with sample classes.
test_api.py: Unit tests for the API endpoints.
data/fitness_studio.db: SQLite database file.
app.log: Log file for API operations.
requirements.txt: List of dependencies.

Dependencies

Flask
Flask-SQLAlchemy
python-dateutil
(See requirements.txt for the full list)

Notes

The API uses SQLite for simplicity. In a production environment, consider using a more robust database like PostgreSQL.
Logging is implemented to app.log for debugging and monitoring.
Timezone support is included for flexibility (defaults to Asia/Kolkata).

Troubleshooting

Server Fails to Start: Check for port conflicts (netstat -aon | findstr :5000) and kill any process using port 5000.
No Classes in Response: Run python seed_data.py to populate the database.
Tests Fail: Ensure the database is seeded and dates in seed_data.py are in the future.

Submission Details

Author: C Rithvik Bhaskar
GitHub: https://github.com/RithvikBhaskar
Loom Video: https://www.loom.com/share/573b4763160441ca9251153003d91960?sid=70b4bf50-85f9-48bf-bf65-0f37a26865f8


