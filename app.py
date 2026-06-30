import os
from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db, User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize Config directories
    Config.init_app()
    
    # Initialize Database
    db.init_app(app)
    
    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Register blueprints
    from routes.auth import auth_bp
    from routes.project import project_bp
    from routes.compiler import compiler_bp
    from routes.editor import editor_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(compiler_bp)
    app.register_blueprint(editor_bp)
    app.register_blueprint(admin_bp)
    
    # Homepage route (Landing page introduction)
    @app.route('/')
    def index():
        return render_template('index.html')
        
    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
        
    # Create DB tables
    with app.app_context():
        db.create_all()
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
