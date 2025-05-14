import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class RegisterEdgeTest(unittest.TestCase):
    def setUp(self):
        # 启动 Edge 浏览器（确保你已配置 msedgedriver 到系统 PATH）
        self.driver = webdriver.Edge()
        self.driver.get("http://127.0.0.1:5000/register")  # Flask 项目必须已运行

    def test_register_with_edge(self):
        driver = self.driver

        # 等待表单输入框
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        driver.find_element(By.NAME, "username").send_keys("edge_user")
        driver.find_element(By.NAME, "password").send_keys("123456")
        driver.find_element(By.NAME, "confirm_password").send_keys("123456")

        # 等待并点击提交按钮
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        )
        submit_button.click()


        # 等待登录页加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        self.assertIn("Login", driver.page_source)

    def tearDown(self):
        time.sleep(1)  # 可选，短暂停留观察页面
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
