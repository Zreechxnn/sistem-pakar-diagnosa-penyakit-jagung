from flask import Flask, render_template
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)  # Aktifkan CORS (untuk berjaga-jaga)

    # Register API blueprint
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Route untuk frontend
    @app.route('/')
    def index():
        return render_template('index.html')

    return app