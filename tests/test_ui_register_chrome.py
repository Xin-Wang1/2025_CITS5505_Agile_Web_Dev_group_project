from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import unittest

class RegisterUITest(unittest.TestCase):
    def setUp(self):
        # 启动 Chrome 浏览器
        self.driver = webdriver.Chrome()
        self.driver.get("http://127.0.0.1:5000/register")

    def test_register_flow(self):
        driver = self.driver

        # 找到输入框并输入内容
        driver.find_element(By.NAME, "username").send_keys("selenium_user")
        driver.find_element(By.NAME, "password").send_keys("123456")
        driver.find_element(By.NAME, "confirm_password").send_keys("123456")

        # 提交注册表单
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        time.sleep(1)  # 等待页面加载完成（可以用 WebDriverWait 替代）

        # 断言跳转后页面含有登录提示
        body_text = driver.page_source
        self.assertIn("Login", body_text)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()