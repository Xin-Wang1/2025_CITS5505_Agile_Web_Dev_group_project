# tests/test_ui_register_chrome.py

import unittest
import subprocess
import time
import requests
import uuid
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class RegisterUITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Launching Flask server subprocess...")
        import sys
        cls.flask_process = subprocess.Popen(
            [sys.executable, "run.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("Waiting for server...")

        for _ in range(10):
            try:
                r = requests.get("http://127.0.0.1:5000")
                if r.status_code == 200:
                    print("✅ Flask server is running.")
                    break
            except:
                time.sleep(1)
        else:
            stdout, stderr = cls.flask_process.communicate(timeout=5)
            print("❌ Flask server failed to start.")
            print("=== STDOUT ===")
            print(stdout)
            print("=== STDERR ===")
            print(stderr)
            raise RuntimeError("Flask server did not respond.")

        # open Chrome browser
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(5)

        cls.username = f"selenium_user_{uuid.uuid4().hex[:6]}"

    def test_01_register_flow(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/auth/register")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        # register a new user
        driver.find_element(By.NAME, "username").send_keys(self.__class__.username)
        driver.find_element(By.NAME, "password").send_keys("123456")
        driver.find_element(By.NAME, "confirm_password").send_keys("123456")

        WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='submit']"))
    )
        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        # wait for the page to load
        time.sleep(1)

        self.assertIn("Login", driver.page_source)

    def test_02_login_flow(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/auth/login")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        driver.find_element(By.NAME, "username").send_keys(self.__class__.username)
        driver.find_element(By.NAME, "password").send_keys("123456")

        # wait for the submit button to be clickable
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='submit']"))
        )
        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        # once logged in, check if the page contains "My Schedule"
        WebDriverWait(driver, 5).until(
            EC.url_to_be("http://127.0.0.1:5000/")
        )
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/")

    def test_03_upload_csv_file(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/unit/")

        # wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "file"))
        )

        # upload a CSV file
        test_csv_path = os.path.abspath("tests/test_units.csv")
        driver.find_element(By.ID, "file").send_keys(test_csv_path)

           
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # check if the upload was successful
        WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Upload")
        )

    def test_04_share_schedule_to_another_user(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/messages/")

        # wait for the page to load
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "receiver_id"))
        )

        # prepare a message to send
        sent_message = f"This is a Selenium message {uuid.uuid4().hex[:6]}"

        # select a receiver and send a message
        Select(driver.find_element(By.NAME, "receiver_id")).select_by_value("2")
        driver.find_element(By.NAME, "content").send_keys(sent_message)

        # submit the form
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        ).click()

        # wait for the message to be sent
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//div[@id='sentMessages']//*[contains(text(), '{sent_message}')]"
            ))
        )

        # wait for the page to load
        self.assertIn(sent_message, driver.page_source)



    def test_05_logout_and_protected_page(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/")

        # logout
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))
        ).click()

        # redirect to home page
        WebDriverWait(driver, 5).until(
            EC.url_to_be("http://127.0.0.1:5000/")
        )
        self.assertIn("Smart Course Selection Tool", driver.page_source)

        # try to access a protected page
        driver.get("http://127.0.0.1:5000/myschedule/My_Schedule/")

        # should redirect to login page
        WebDriverWait(driver, 5).until(
            EC.url_contains("/auth/login")
        )
        self.assertIn("Login", driver.page_source)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        print("🧹 Stopping Flask server...")
        cls.flask_process.terminate()
        try:
            cls.flask_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls.flask_process.kill()

if __name__ == "__main__":
    unittest.main(verbosity=2)
