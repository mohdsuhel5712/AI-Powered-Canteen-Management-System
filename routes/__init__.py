from .auth_routes import auth
from .admin_routes import admin

def register_blueprints(app):
    app.register_blueprint(auth)
    app.register_blueprint(admin)