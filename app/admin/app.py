from flask import Flask
from app.databases.database import SessionLocal, engine
from flask_login import LoginManager
from app.admin import models
from app.admin.blueprint.main import main as main_blueprint
from app.admin.blueprint.auth import auth as auth_blueprint


db = SessionLocal()
models.user.Base.metadata.create_all(bind=engine)


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.query(models.user.User).get(int(user_id))

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    return app
