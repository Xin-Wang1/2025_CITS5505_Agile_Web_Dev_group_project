# tests/test_auth.py
import unittest
from app.app import app
from app.models import db

from tests.config_test import TestConfig
from app.models import User
from werkzeug.security import generate_password_hash

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object(TestConfig)
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

class AuthTestCase(BaseTestCase):
    def test_register_user(self):
        response = self.client.post('/auth/register', data={
            'username': 'testuser',
            'password': '123456',
            'confirm_password': '123456'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

    def test_login_user(self):
        with app.app_context():
            user = User(username='loginuser', password_hash=generate_password_hash('password'))
            db.session.add(user)
            db.session.commit()

        response = self.client.post('/auth/login', data={
            'username': 'loginuser',
            'password': 'password'
        }, follow_redirects=True)
        self.assertIn(b'Welcome', response.data)

    def test_login_fail(self):
        response = self.client.post('/auth/login', data={
            'username': 'wronguser',
            'password': 'wrongpass'
        }, follow_redirects=True)
        self.assertIn(b'Invalid credentials', response.data)

if __name__ == '__main__':
    unittest.main()