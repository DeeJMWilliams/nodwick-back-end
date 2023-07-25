from flask import Flask
from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv

initialize_app(credentials.Certificate('key.json'), {'databaseURL': 'https://nodwick-inventory-manager.firebaseio.com'})
db = firestore.client()
load_dotenv()

# Initialize Flask app
def create_app():
    app = Flask(__name__)

    app.config['ENV'] = 'development'
    app.config['DEBUG'] = True
    app.config['TESTING'] = True

    #!!! Remove above for deployment

    from .routes import user_bp, game_bp, loc_bp, item_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(loc_bp)
    app.register_blueprint(item_bp)

    return app

