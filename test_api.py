import unittest
from app import app, db, ClassSchedule, Booking
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class TestBookingAPI(unittest.TestCase):
    def setUp(self):
        """Set up test environment with in-memory database."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up test environment by dropping the database."""
        with app.app_context():
            db.drop_all()

    def create_sample_class(self, past_class=False):
        """Helper to create a sample class for testing."""
        with app.app_context():
            date_time = (
                datetime.now(ZoneInfo("Asia/Kolkata")) - timedelta(days=1)
                if past_class
                else datetime.now(ZoneInfo("Asia/Kolkata")) + timedelta(days=1)
            )
            cls = ClassSchedule(
                name='Yoga',
                instructor='Jane Doe',
                date_time=date_time,
                capacity=10
            )
            db.session.add(cls)
            db.session.commit()
            return cls.id

    def test_create_class(self):
        """Test creating a new class."""
        response = self.client.post('/api/classes', json={
            'name': 'Yoga',
            'instructor': 'Jane Doe',
            'date_time': '2025-06-08T10:00:00',
            'capacity': 10
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)

    def test_create_class_invalid_type(self):
        """Test creating a class with an invalid class type."""
        response = self.client.post('/api/classes', json={
            'name': 'Pilates',  # Not Yoga, Zumba, or HIIT
            'instructor': 'Jane Doe',
            'date_time': '2025-06-08T10:00:00',
            'capacity': 10
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid class type', response.json['error'])

    def test_get_classes(self):
        """Test retrieving upcoming classes."""
        self.create_sample_class()
        response = self.client.get('/api/classes')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['name'], 'Yoga')

    def test_get_classes_with_timezone(self):
        """Test retrieving classes with a different timezone."""
        self.create_sample_class()
        response = self.client.get('/api/classes?timezone=America/New_York')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertIn('-04:00', response.json[0]['date_time'])  # New York timezone offset

    def test_create_booking(self):
        """Test creating a booking for a class."""
        class_id = self.create_sample_class()
        response = self.client.post('/api/book', json={
            'class_id': class_id,
            'user_name': 'John Doe',
            'user_email': 'john@example.com'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)

    def test_create_booking_invalid_email(self):
        """Test creating a booking with an invalid email."""
        class_id = self.create_sample_class()
        response = self.client.post('/api/book', json={
            'class_id': class_id,
            'user_name': 'John Doe',
            'user_email': 'invalid-email'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid email format', response.json['error'])

    def test_create_booking_past_class(self):
        """Test creating a booking for a past class."""
        class_id = self.create_sample_class(past_class=True)
        response = self.client.post('/api/book', json={
            'class_id': class_id,
            'user_name': 'John Doe',
            'user_email': 'john@example.com'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Cannot book a past class', response.json['error'])

    def test_create_booking_overbooked(self):
        """Test creating a booking when the class is fully booked."""
        class_id = self.create_sample_class()
        with app.app_context():
            cls = ClassSchedule.query.get(class_id)
            cls.capacity = 1
            booking = Booking(
                class_id=class_id,
                user_name='Jane Doe',
                user_email='jane@example.com'
            )
            db.session.add(booking)
            db.session.commit()

        response = self.client.post('/api/book', json={
            'class_id': class_id,
            'user_name': 'John Doe',
            'user_email': 'john@example.com'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Class is fully booked', response.json['error'])

    def test_get_bookings(self):
        """Test retrieving bookings for a specific email."""
        class_id = self.create_sample_class()
        with app.app_context():
            booking = Booking(
                class_id=class_id,
                user_name='John Doe',
                user_email='john@example.com'
            )
            db.session.add(booking)
            db.session.commit()

        response = self.client.get('/api/bookings?email=john@example.com')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['user_email'], 'john@example.com')

if __name__ == '__main__':
    unittest.main()