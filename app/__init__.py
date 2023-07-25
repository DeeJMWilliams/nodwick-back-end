from flask import Flask
from firebase_admin import credentials, firestore, initialize_app

initialize_app(credentials.Certificate('key.json'), {'databaseURL': 'https://nodwick-inventory-manager.firebaseio.com'})
db = firestore.client()

# Initialize Flask app
def create_app(test_config=None):
    app = Flask(__name__)

    from .routes import user_bp, game_bp, loc_bp, item_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(loc_bp)
    app.register_blueprint(item_bp)

    return app

