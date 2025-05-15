# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # 自动加载 .env 文件中的变量

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(BASE_DIR, 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
