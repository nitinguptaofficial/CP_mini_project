from routes.auth_routes import auth_bp
from routes.core_routes import core_bp
from routes.student_routes import student_bp
from routes.teacher_routes import teacher_bp


def register_blueprints(app):
    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
