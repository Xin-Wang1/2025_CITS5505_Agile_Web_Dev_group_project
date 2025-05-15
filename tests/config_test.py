# config_test.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class TestConfig:
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # 使用内存数据库，测试完自动清除
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False  # 禁用 CSRF 便于表单测试
