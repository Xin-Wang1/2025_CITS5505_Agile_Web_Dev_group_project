import unittest
from app.app import app, db
from app.models import User
from werkzeug.security import generate_password_hash


class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["WTF_CSRF_ENABLED"] = False
        self.app = app.test_client()

        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()
            if not User.query.filter_by(username="testuser").first():
                user = User(
                    username="testuser",
                    password_hash=generate_password_hash("testpass"),
                )
                db.session.add(user)
                db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_homepage_guest(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login", response.data)

    def test_login_valid_user(self):
        response = self.app.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome", response.data)

    def test_login_invalid_user(self):
        response = self.app.post(
            "/login",
            data={"username": "wronguser", "password": "wrongpass"},
            follow_redirects=True,
        )
        self.assertIn(b"Invalid credentials", response.data)

    def test_unit_route_logged_in(self):
        with self.app:
            self.app.post(
                "/login", data={"username": "testuser", "password": "testpass"}
            )
            response = self.app.get("/unit/")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Schedule", response.data)

    def test_my_schedule_route_logged_in(self):
        with self.app:
            self.app.post(
                "/login", data={"username": "testuser", "password": "testpass"}
            )
            response = self.app.get("/My_Schedule/")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"My Schedule", response.data)

    def test_messages_route_logged_in(self):
        with self.app:
            self.app.post(
                "/login", data={"username": "testuser", "password": "testpass"}
            )
            response = self.app.get("/messages/")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Share", response.data)

    def test_unit_route_guest(self):
        response = self.app.get("/unit/", follow_redirects=True)
        self.assertIn(b"Login", response.data)

    def test_my_schedule_route_guest(self):
        response = self.app.get("/My_Schedule/", follow_redirects=True)
        self.assertIn(b"Login", response.data)

    def test_messages_route_guest(self):
        response = self.app.get("/messages/", follow_redirects=True)
        self.assertIn(b"Login", response.data)

    def test_register_new_user(self):
        response = self.app.post(
            "/register",
            data={
                "username": "newuser",
                "password": "newpass",
                "confirm_password": "newpass",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration successful", response.data)

    def test_register_existing_user(self):
        # First registration
        self.app.post(
            "/register",
            data={
                "username": "duplicateuser",
                "password": "pass123",
                "confirm_password": "pass123",
            },
            follow_redirects=True,
        )

        # Second attempt with same username
        response = self.app.post(
            "/register",
            data={
                "username": "duplicateuser",
                "password": "pass456",
                "confirm_password": "pass456",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"This username is already taken", response.data)

    def test_register_password_mismatch(self):
        response = self.app.post(
            "/register",
            data={
                "username": "user123",
                "password": "pass123",
                "confirm_password": "differentpass",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Passwords must match", response.data)

    def test_reset_password_flow(self):
        # Trigger password reset
        response = self.app.post(
            "/resetpw", data={"username": "testuser"}, follow_redirects=True
        )
        self.assertIn(
            b"reset", response.data.lower()
        )  # Loose check assuming template includes "reset"

        # Actually reset password
        response = self.app.post(
            "/resetpw/testuser",
            data={"new_password": "newpass123", "confirm_password": "newpass123"},
            follow_redirects=True,
        )
        self.assertIn(b"Password reset successful", response.data)

    def test_reset_password_mismatch(self):
        self.app.post("/resetpw", data={"username": "testuser"}, follow_redirects=True)
        response = self.app.post(
            "/resetpw/testuser",
            data={"new_password": "pass1", "confirm_password": "pass2"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Passwords do not match", response.data)

    def test_send_message(self):
        with app.app_context():
            from app.models import User

            user2 = User(
                username="anotheruser", password_hash=generate_password_hash("testpass")
            )
            db.session.add(user2)
            db.session.commit()
            receiver_id = user2.id

        self.app.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=True,
        )

        response = self.app.post(
            "/messages/send",
            data={
                "receiver_id": receiver_id,
                "content": "Hello there!",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sent successfully", response.data)

    def test_send_empty_message(self):
        with app.app_context():
            user2 = User(
                username="emptymsguser",
                password_hash=generate_password_hash("testpass"),
            )
            db.session.add(user2)
            db.session.commit()
            receiver_id = user2.id

        self.app.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=True,
        )

        response = self.app.post(
            "/messages/send",
            data={"receiver_id": receiver_id, "content": ""},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Message content cannot be empty", response.data)

    def test_unit_upload_and_schedule_generation(self):
        self.app.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=True,
        )

        # Test uploading with missing data
        response = self.app.post(
            "/schedule/generation",
            data={"selected_units": ""},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please select at least one unit", response.data)

        # Now try with invalid JSON
        response = self.app.post(
            "/schedule/generation",
            data={"selected_units": "not_a_json"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"invalid selection", response.data)

        # Now insert dummy units and test with valid input
        from app.models import Unit

        with app.app_context():
            unit = Unit(code="TEST1001", name="Test Unit", credit_points=6)
            db.session.add(unit)
            db.session.commit()
            valid_units_json = f"[{unit.id}]"

        response = self.app.post(
            "/schedule/generation",
            data={"selected_units": valid_units_json},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Schedule", response.data)


if __name__ == "__main__":
    unittest.main()

    def test_password_hashing(self):
        from werkzeug.security import generate_password_hash, check_password_hash

        with app.app_context():
            user = User(username="hashuser")
            user.password_hash = generate_password_hash("secure123")
            db.session.add(user)
            db.session.commit()
            retrieved = User.query.filter_by(username="hashuser").first()
            self.assertTrue(check_password_hash(retrieved.password_hash, "secure123"))

    def test_delete_schedule_permission_denied(self):
        # Create a different user and schedule
        from app.models import Schedule
        from werkzeug.security import generate_password_hash

        with app.app_context():
            user2 = User(username="user2", password_hash=generate_password_hash("pass"))
            db.session.add(user2)
            db.session.commit()

            schedule = Schedule(name="Fake Schedule", user_id=user2.id)
            db.session.add(schedule)
            db.session.commit()
            schedule_id = schedule.id

        self.app.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=True,
        )
        response = self.app.post(f"/schedule/delete/{schedule_id}")
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"No permission", response.data)

    def test_register_empty_fields(self):
        response = self.app.post(
            "/register",
            data={"username": "", "password": "", "confirm_password": ""},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            b"This field is required" in response.data or b"required" in response.data
        )

    def test_send_message_to_self(self):
        from werkzeug.security import generate_password_hash

        with app.app_context():
            testuser = User.query.filter_by(username="testuser").first()
            if not testuser:
                testuser = User(
                    username="testuser",
                    password_hash=generate_password_hash("testpass"),
                )
                db.session.add(testuser)
                db.session.commit()
            user_id = testuser.id

        self.app.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=True,
        )
        response = self.app.post(
            "/messages/send",
            data={"receiver_id": user_id, "content": "Hi me!"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid recipient", response.data)

    def test_schedule_generation_invalid_json(self):
        self.app.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=True,
        )
        response = self.app.post(
            "/schedule/generation",
            data={"selected_units": "not_json"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"invalid selection", response.data)
