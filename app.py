from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db


def create_app():
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Extensions ──
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)
    db.init_app(app)

    # ── Register Blueprints ──
    from routes.auth_routes import auth_bp
    from routes.profile_routes import profile_bp
    from routes.meal_routes import meal_bp
    from routes.progress_routes import progress_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.recommend_routes import recommend_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(meal_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(recommend_bp)

    # ── Create tables ──
    with app.app_context():
        db.create_all()

    # ── Health check ──
    @app.route("/api/health", methods=["GET"])
    def health():
        return {"status": "ok", "message": "AI Nutrition API is running"}, 200

    return app
