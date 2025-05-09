from flask import Flask
from flask_cors import CORS
from .models import db

def create_app():
    app = Flask(__name__)
    CORS(app)  # 允许跨域请求
    app.config.from_object('config.Config')

    # 初始化数据库
    db.init_app(app)
    with app.app_context():
        db.create_all()

    from . import routes
    app.register_blueprint(routes.bp)

    return app