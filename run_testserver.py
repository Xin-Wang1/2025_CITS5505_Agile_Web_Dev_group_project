# run_testserver.py
from app.app import app
from app.models import db, User
from tests.config_test import TestConfig
from werkzeug.security import generate_password_hash

app.config.from_object(TestConfig)

with app.app_context():
    db.create_all()
    # 添加一个默认的用户（id=1）供分享用
    if not User.query.filter_by(username="receiver1").first():
        u = User(username="receiver1", password_hash=generate_password_hash("123456"))
        db.session.add(u)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=False)
