from flask import Flask
from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv
import os
from mockfirestore import MockFirestore

load_dotenv()
initialize_app(credentials.Certificate('key.json'))
db = firestore.client()

# Initialize Flask app
def create_app(test_config=None):
    app = Flask(__name__)

    if test_config:
        global db
        app.config['ENV'] = 'development'
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.config['databaseURL'] = os.environ.get('TEST_DB')
        db = MockFirestore()
    else:
        app.config['databaseURL'] = os.environ.get('DB')

    from .routes import user_bp, game_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(game_bp)

    return app

