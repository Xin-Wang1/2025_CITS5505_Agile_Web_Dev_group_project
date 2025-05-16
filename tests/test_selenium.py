# tests/test_ui_register_chrome.py

import unittest
import subprocess
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

class RegisterUITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Launching Flask server subprocess...")

        cls.flask_process = subprocess.Popen(
            ["python", "run.py"],
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

        # 启动 Chrome 浏览器
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(5)

    def test_register_flow(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/register")

        # 填写注册表单
        driver.find_element(By.NAME, "username").send_keys("selenium_user")
        driver.find_element(By.NAME, "password").send_keys("123456")
        driver.find_element(By.NAME, "confirm_password").send_keys("123456")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # 等待页面跳转
        time.sleep(1)

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
