from flask import Flask
from app.telegram_webhook import bp as telegram_bp
from app.twilio_webhook import bp as twilio_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(telegram_bp)
    app.register_blueprint(twilio_bp)
    return app
