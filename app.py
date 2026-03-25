import os

from flask import Flask

from config import Config
from routes import register_blueprints
from utils.extensions import bcrypt, csrf, db, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    register_blueprints(app)

    @app.context_processor
    def inject_globals():
        return {"app_name": "College Management System"}

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
