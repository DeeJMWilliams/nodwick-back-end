from flask import Flask
from firebase_admin import credentials, firestore, initialize_app

initialize_app(credentials.Certificate('key.json'))
db = firestore.client()

# Initialize Flask app
def create_app(test_config=None):
    app = Flask(__name__)

    from .routes import user_bp
    app.register_blueprint(user_bp)

    return app

