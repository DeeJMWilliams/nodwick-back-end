from flask import Flask
from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv
import os
from mockfirestore import MockFirestore
from flask_cors import CORS
import json

load_dotenv()
initialize_app(credentials.Certificate(json.loads(os.environ.get('KEY'))))
db = firestore.client()
mock_db = MockFirestore()

# Initialize Flask app
def create_app(test_config=None):
    app = Flask(__name__)

    if test_config:
        global db
        app.config['ENV'] = 'development'
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        db = mock_db
    else:
        app.config['databaseURL'] = os.environ.get('DB')

    from .routes import user_bp, game_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(game_bp)

    CORS(app)

    if __name__ == '__main__':
        app.run(port=int(os.environ.get('PORT')))

    return app

