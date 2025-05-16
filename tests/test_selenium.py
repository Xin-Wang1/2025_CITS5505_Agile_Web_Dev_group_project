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

        # 启动 Chrome 浏览器
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(5)

        cls.username = f"selenium_user_{uuid.uuid4().hex[:6]}"

    def test_01_register_flow(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/auth/register")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        # 填写注册表单
        driver.find_element(By.NAME, "username").send_keys(self.__class__.username)
        driver.find_element(By.NAME, "password").send_keys("123456")
        driver.find_element(By.NAME, "confirm_password").send_keys("123456")

        WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='submit']"))
    )
        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        # 等待页面跳转
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

        # 等待并点击登录按钮
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='submit']"))
        )
        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        # 可选断言（检查是否跳转成功，比如显示用户名或“Logout”按钮）
        WebDriverWait(driver, 5).until(
            EC.url_to_be("http://127.0.0.1:5000/")
        )
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/")

    def test_03_upload_csv_file(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/unit/")

        # 等待文件上传输入框出现
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "file"))
        )

        # 上传测试 CSV 文件（请确保文件路径正确）
        test_csv_path = os.path.abspath("tests/test_units.csv")
        driver.find_element(By.ID, "file").send_keys(test_csv_path)

        # 提交上传
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # 判断上传是否成功（可通过提示消息或新增 unit 名称）
        WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Upload")
        )

    def test_04_share_schedule_to_another_user(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/messages/")

        # 等待页面加载“发送消息”表单
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "receiver_id"))
        )

        # 准备发送消息的内容（唯一标识，避免断言冲突）
        sent_message = f"This is a Selenium message {uuid.uuid4().hex[:6]}"

        # 向用户 ID 2 发送消息（你需要确保 ID=2 的用户存在）
        Select(driver.find_element(By.NAME, "receiver_id")).select_by_value("2")
        driver.find_element(By.NAME, "content").send_keys(sent_message)

        # 点击“发送”按钮
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        ).click()

        # 等待“Sent”区域出现刚才发送的内容
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//div[@id='sentMessages']//*[contains(text(), '{sent_message}')]"
            ))
        )

        # 严格断言消息内容确实出现在页面中
        self.assertIn(sent_message, driver.page_source)



    def test_05_logout_and_protected_page(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/")

        # 点击头像 → Logout
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))
        ).click()

        # 确认跳转回首页
        WebDriverWait(driver, 5).until(
            EC.url_to_be("http://127.0.0.1:5000/")
        )
        self.assertIn("Smart Course Selection Tool", driver.page_source)

        # 尝试访问受限页
        driver.get("http://127.0.0.1:5000/myschedule/My_Schedule/")

        # 应跳转回登录页或提示未授权
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
