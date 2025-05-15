import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.app import db
from app.models import User
from werkzeug.security import generate_password_hash
from app.app import app


class SeleniumTestCase(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run browser in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Set up test user in the database
        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()
            if not User.query.filter_by(username="testuser").first():
                test_user = User(
                    username="testuser",
                    password_hash=generate_password_hash("testpass"),
                )
                db.session.add(test_user)
                db.session.commit()

        self.driver.get("http://127.0.0.1:5000/")

    def tearDown(self):
        self.driver.quit()

    def login_test_user(self):
        self.driver.get("http://127.0.0.1:5000/login")
        WebDriverWait(self.driver, 10).until(lambda d: d.title == "Login")
        self.driver.find_element("name", "username").send_keys("testuser")
        self.driver.find_element("name", "password").send_keys("testpass")
        self.driver.find_element("css selector", "form").submit()
        WebDriverWait(self.driver, 10).until(lambda d: d.title != "Login")

    def test_homepage_title(self):
        WebDriverWait(self.driver, 10).until(lambda driver: driver.title != "localhost")
        print("ACTUAL TITLE:", self.driver.title)
        print("PAGE SOURCE:", self.driver.page_source[:300])
        self.assertIn("Home", self.driver.title)

    def test_all_page_titles(self):
        self.login_test_user()
        pages = {
            "/": "Home",
            "/unit/": "Schedule",
            "/My_Schedule/": "My Schedule",
            "/messages/": "Share",
        }

        for route, expected_title in pages.items():
            self.driver.get(f"http://127.0.0.1:5000{route}")
            WebDriverWait(self.driver, 10).until(lambda d: d.title != "localhost")
            actual_title = self.driver.title
            print(
                f"Testing {route} -> Expected: '{expected_title}', Found: '{actual_title}'"
            )

    def test_invalid_login_attempt(self):
        self.driver.get("http://127.0.0.1:5000/login")
        WebDriverWait(self.driver, 10).until(lambda d: d.title == "Login")
        self.driver.find_element("name", "username").send_keys("invaliduser")
        self.driver.find_element("name", "password").send_keys("invalidpass")
        self.driver.find_element("css selector", "form").submit()
        WebDriverWait(self.driver, 10).until(lambda d: "Login" in d.title)
        page_source = self.driver.page_source
        self.assertIn("Invalid credentials", page_source)


if __name__ == "__main__":
    unittest.main()
