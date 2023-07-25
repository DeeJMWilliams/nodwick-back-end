from flask import request, jsonify, make_response, abort, Blueprint
from app import db

#Blueprints
user_bp = Blueprint("user", __name__, url_prefix="/users")
game_bp = Blueprint("game", __name__, url_prefix="/games")
loc_bp = Blueprint("location", __name__, url_prefix="/locations")
item_bp = Blueprint("item", __name__, url_prefix="/items")

### USERS ###
users_ref = db.collection('users')

#!!! Can you initialize user with blank list/collection (for games?) & vice versa
#!!! Need to autoincrement IDs for all collections

@user_bp.route('', methods=['POST'])
def create_user():
    #Verify presence of ID
    try:
        id = request.json['id']
    except Exception as e:
        return f"An Error Occurred: {e}"
    #Verify presence of email and password
    if 'email' not in request.json.keys():
        abort(make_response(jsonify({"message": "Email not found"}), 404))
    if 'password' not in request.json.keys():
        abort(make_response(jsonify({"message": "Password not found"}), 404))
    #Create user
    users_ref.document(id).set(request.json)
    return jsonify({"success": True}), 200

@user_bp.route('', methods=['GET'])
def read_users():
    #Returns all users if no param "id", else searches for user by ID
    try:
        # Check if ID was passed to URL query
        user_id = request.args.get('id')
        if user_id:
            user = users_ref.document(user_id).get()
            return jsonify(user.to_dict()), 200
        else:
            all_users = [doc.to_dict() for doc in users_ref.stream()]
            return jsonify(all_users), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@user_bp.route('', methods=['DELETE'])
def remove_user():
    try:
        # Check for ID in URL query
        user_id = request.args.get('id')
        users_ref.document(user_id).delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"
    
#!!! Add game to user's list/collection of games (or create list/collection of games)
    
### GAMES ###

games_ref = db.collection('games')

#!!! Create game w/ default "unassigned" item location

#!!! Delete game

#!!! Get game or list of games

#!!! Add user to game's list/collection of users

### LOCATIONS ###

locs_ref = db.collection('locations')

#!!! Create location w/ game ID

#!!! Delete location (& move all items to unassigned)

#!!! Get location or list of locations

### ITEMS ###

items_ref = db.collection('items')

#!!! Create item w/ location ID

#!!! Delete item

#!!! Move (reassign) item and change location ID

#!!! Get item or list of items




