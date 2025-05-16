# tests/test_unit.py

import unittest
from app.app import app
from app.models import db, User, Unit, Classtime
from werkzeug.security import generate_password_hash
from tests.config_test import TestConfig
from datetime import time
import io


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


class FeatureTestCase(BaseTestCase):
    def test_upload_unit_csv(self):
        csv_content = """Unit Code,Unit Name,Credit Points,Description,Class Type,Day of Week,Start Time,End Time
CITS5505,Agile Web Dev,6,Test unit,Lecture,Monday,09:00,11:00
"""
        data = {
            'file': (io.BytesIO(csv_content.encode('utf-8')), 'test_units.csv')
        }

        with self.client:
            self.client.post('/auth/register', data={
                'username': 'uploaduser',
                'password': '123456',
                'confirm_password': '123456'
            }, follow_redirects=True)
            self.client.post('/auth/login', data={
                'username': 'uploaduser',
                'password': '123456'
            }, follow_redirects=True)

            response = self.client.post('/unit/', data=data, content_type='multipart/form-data', follow_redirects=True)
            self.assertIn(b'Upload complete', response.data)

    def test_generate_schedule(self):
        with self.client:
            self.client.post('/auth/register', data={
                'username': 'scheduser',
                'password': '123456',
                'confirm_password': '123456'
            }, follow_redirects=True)
            self.client.post('/auth/login', data={
                'username': 'scheduser',
                'password': '123456'
            }, follow_redirects=True)

            with app.app_context():
                unit = Unit(code='CITS5506', name='Data Mining', credit_points=6, created_by=1)
                db.session.add(unit)
                db.session.commit()

                classtime = Classtime(unit_id=unit.id, type='Lecture', day_of_week='Tuesday',
                                    start_time=time(10, 0), end_time=time(12, 0))
                db.session.add(classtime)
                db.session.commit()
                unit_id = unit.id

            # ✅ 提交课程 ID
            response = self.client.post('/schedule/schedule/generation', data={
                'selected_units': f'[{unit_id}]'
            }, follow_redirects=True)

            # ✅ 检查课程名是否出现在最终渲染页面中
            self.assertIn(b'Data Mining', response.data)
            self.assertIn(b'10:00', response.data)


    def test_send_message(self):
        with app.app_context():
            u1 = User(username='sender', password_hash=generate_password_hash('123'))
            u2 = User(username='receiver', password_hash=generate_password_hash('456'))
            db.session.add_all([u1, u2])
            db.session.commit()

        self.client.post('/auth/login', data={
            'username': 'sender',
            'password': '123'
        }, follow_redirects=True)

        response = self.client.post('/messages/send', data={
            'receiver_id': 2,
            'content': 'Hi there!',
        }, follow_redirects=True)

        self.assertIn(b'Sent successfully', response.data)


if __name__ == '__main__':
    unittest.main()
