from flask import request, jsonify, make_response, abort, Blueprint
from app import db
import uuid
import datetime

#Blueprints
user_bp = Blueprint("user", __name__, url_prefix="/users")
game_bp = Blueprint("game", __name__, url_prefix="/games")
loc_bp = Blueprint("location", __name__, url_prefix="/locations")
item_bp = Blueprint("item", __name__, url_prefix="/items")

### USERS ###
users_ref = db.collection('users')

@user_bp.route('', methods=['POST'])
def create_user():
    #Verify presence of email and password
    if 'email' not in request.json.keys():
        abort(make_response(jsonify({"message": "Email not found"}), 404))
    if 'password' not in request.json.keys():
        abort(make_response(jsonify({"message": "Password not found"}), 404))
    #Create user with id, games, and timestamp fields
    new_user = request.json
    id = str(uuid.uuid4())
    new_user['game_ids'] = []
    new_user['uid'] = id
    new_user['timestamp'] = str(datetime.datetime.now())
    users_ref.document(id).set(new_user)
    return jsonify({"success": True}), 200

@user_bp.route('', methods=['GET'])
def read_users():
    #Returns all users if no param "id", else searches for user by ID
    try:
        # Check if ID was passed to URL query
        user_id = request.args.get('user_id')
        if user_id:
            user = users_ref.document(user_id).get()
            return jsonify(user.to_dict()), 200
        else:
            all_users = [doc.to_dict() for doc in users_ref.stream()]
            return jsonify(all_users), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

#!!! Remove user from any games to which they were added
@user_bp.route('', methods=['DELETE'])
def delete_user():
    try:
        user_id = request.args.get('id')
        users_ref.document(user_id).delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"
    
#Add game ID to user's list of games
@user_bp.route('', methods=['PATCH'])
def add_game_to_user():
    try:
        game_id = request.args.get('game_id')
        user_id = request.args.get('user_id')
    except Exception as e:
        return f"An Error Occurred: {e}"
    user = users_ref.document(user_id).get().to_dict()
    user['game_ids'].append(game_id)
    users_ref.document(user_id).set(user)
    return jsonify({"success": True}), 200

### GAMES ###

games_ref = db.collection('games')

@game_bp.route('', methods=['POST'])
def create_game():
    if 'name' not in request.json.keys():
        abort(make_response(jsonify({"message": "Game name not found"}), 404))
    new_game = request.json
    id = str(uuid.uuid4())
    new_game['gid'] = id
    new_game['user_ids'] = []
    new_game['timestamp'] = str(datetime.datetime.now())
    games_ref.document(id).set(new_game)

    #Create 'unassigned' location
    lid = str(uuid.uuid4())
    loc_ref = games_ref.document(id).collection('locations')
    loc_data = {'lid':lid, 'name': 'Unassigned', 'timestamp': str(datetime.datetime.now())}
    loc_ref.document(lid).set(loc_data)
    return jsonify({'success': True}), 200

@game_bp.route('', methods=['DELETE'])
def remove_game():  
    try:
        game_id = request.args.get('game_id')
        games_ref.document(game_id).delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@game_bp.route('', methods=['GET'])
def read_games():
    try:
        game_id = request.args.get('game_id')
        if game_id:
            game = games_ref.document(game_id).get()
            return jsonify(game.to_dict()), 200
        else:
            all_games = [doc.to_dict() for doc in games_ref.stream()]
            return jsonify(all_games), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

@user_bp.route('/games', methods=['GET'])
def read_games_from_user():
    try: 
        user_id = request.args.get('user_id')
    except Exception as e:
        return f"An Error Occurred: {e}"
    games_list = []
    for game_id in users_ref.document(user_id).get().to_dict()['game_ids']:
        game = games_ref.document(game_id).get()
        games_list.append(game.to_dict())
    return jsonify({'games':games_list})

#Add user to game
@game_bp.route('', methods=['PATCH'])
def add_user_to_game():
    try:
        game_id = request.args.get('game_id')
        user_id = request.args.get('user_id')
    except Exception as e:
        return f"An Error Occurred: {e}"
    game = games_ref.document(game_id).get().to_dict()
    game['user_ids'].append(user_id)
    games_ref.document(game_id).set(game)
    return jsonify({"success": True}), 200

### LOCATIONS ###

#!!! Create location w/ game ID

#!!! Delete location (& move all items to unassigned)

#!!! Get location or list of locations

### ITEMS ###

#!!! Create item w/ location ID

#!!! Delete item

#!!! Move (reassign) item and change location ID

#!!! Get item or list of items




