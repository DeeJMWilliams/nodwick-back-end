from flask import request, jsonify, make_response, abort, Blueprint
from app import db
import uuid
import copy
import datetime
from .helpers import remove_item_from_location, add_item_to_location, change_item_location, get_unassigned

#Blueprints
user_bp = Blueprint("user", __name__, url_prefix="/users")
game_bp = Blueprint("game", __name__, url_prefix="/games")

### USERS ###
users_ref = db.collection('users')

#Create new user
@user_bp.route('', methods=['POST'])
def create_user():
    #Verify presence of name and email
    if 'email' not in request.json.keys():
        abort(make_response(jsonify({"message": "Email not found"}), 404))
    if 'name' not in request.json.keys():
        abort(make_response(jsonify({"message": "Name not found"}), 404))
    #Create user with id, games, and timestamp fields
    new_user = request.json
    user_id = request.json['uid']
    new_user['game_ids'] = []
    new_user['timestamp'] = str(datetime.datetime.now())
    users_ref.document(user_id).set(new_user)
    return jsonify(new_user), 200

#Read users (all or by ID)
@user_bp.route('', methods=['GET'])
def read_users():
    #Returns all users if no param "id", else searches for user by ID
    user_id = request.args.get('user_id')
    if user_id:
        user = users_ref.document(user_id).get()
        return jsonify(user.to_dict()), 200
    else:
        all_users = [doc.to_dict() for doc in users_ref.stream()]
        return jsonify(all_users), 200

#Delete user and remove them from all games
@user_bp.route('', methods=['DELETE'])
def delete_user():
    user_id = request.args.get('user_id')
    game_ids = users_ref.document(user_id).get().to_dict()['game_ids']
    for game_id in game_ids:
        #Remove user from game's list of user IDs for each game
        game = games_ref.document(game_id).get().to_dict()
        game['user_ids'] = list(filter(lambda x: x != user_id, game['user_ids']))
        games_ref.document(game_id).set(game)
    users_ref.document(user_id).delete()
    return jsonify({"success": True}), 200
    
#Add user to game
@user_bp.route('/games', methods=['PATCH'])
def add_game_to_user():
    game_id = request.args.get('game_id')
    user_id = request.args.get('user_id')
    #Add game ID to user's list of game IDs
    user = users_ref.document(user_id).get().to_dict()
    if game_id not in user['game_ids']:
        user['game_ids'].append(game_id)
        users_ref.document(user_id).set(user)
    #Add user ID to game's list of user IDs
    game = games_ref.document(game_id).get().to_dict()
    if user_id not in game['user_ids']:
        game['user_ids'].append(user_id)
        games_ref.document(game_id).set(game)
    return jsonify(game), 200

#Edit user's name
@user_bp.route('', methods=['PATCH'])
def rename_user():
    user_id = request.args.get('user_id')
    user = users_ref.document(user_id).get().to_dict()
    name = request.json['name']
    user['name'] = name
    users_ref.document(user_id).set(user)
    return jsonify(user), 200

### GAMES ###

games_ref = db.collection('games')

#Create a new game
@game_bp.route('', methods=['POST'])
def create_game():
    if 'name' not in request.json.keys():
        abort(make_response(jsonify({"message": "Game name not found"}), 404))
    new_game = request.json
    game_id = str(uuid.uuid4())
    new_game['gid'] = game_id
    new_game['user_ids'] = []
    new_game['timestamp'] = str(datetime.datetime.now())
    games_ref.document(game_id).set(new_game)

    #Create default 'unassigned' location for game
    loc_id = str(uuid.uuid4())
    loc_ref = games_ref.document(game_id).collection('locations')
    loc_data = {'lid':loc_id, 'gid': game_id, 'type': 'location', 'item_ids': [], 'name': 'Unassigned', 'timestamp': str(datetime.datetime.now())}
    loc_ref.document(loc_id).set(loc_data)
    return jsonify(new_game), 200

#Delete a game
@game_bp.route('', methods=['DELETE'])
def remove_game():  
    game_id = request.args.get('game_id')
    user_ids = games_ref.document(game_id).get().to_dict()['user_ids']
    #Remove item and location collections
    loc_ref = games_ref.document(game_id).collection('locations')
    for doc in loc_ref.stream():
        loc_id = doc.to_dict()['lid']
        loc_ref.document(loc_id).delete()
    item_ref = games_ref.document(game_id).collection('items')
    for doc in item_ref.stream():
        item_id = doc.to_dict()['iid']
        item_ref.document(item_id).delete()
    #Remove game from each user
    for user_id in user_ids:
        user = users_ref.document(user_id).get().to_dict()
        user['game_ids'] = list(filter(lambda x: x != game_id, user['game_ids']))
        users_ref.document(user_id).set(user)
    games_ref.document(game_id).delete()
    return jsonify({"success": True}), 200

#Read games (all or by ID)
@game_bp.route('', methods=['GET'])
def read_games():
    game_id = request.args.get('game_id')
    if game_id:
        game = games_ref.document(game_id).get()
        return jsonify(game.to_dict()), 200
    else:
        all_games = [doc.to_dict() for doc in games_ref.stream()]
        return jsonify(all_games), 200

#Read games from specific user
@user_bp.route('/games', methods=['GET'])
def read_games_from_user():
    user_id = request.args.get('user_id')
    games_list = []
    for game_id in users_ref.document(user_id).get().to_dict()['game_ids']:
        game = games_ref.document(game_id).get()
        games_list.append(game.to_dict())
    return jsonify(games_list)

#Rename game
@game_bp.route('', methods=['PATCH'])
def rename_game():
    game_id = request.args.get('game_id')
    name = request.json['name']
    game = games_ref.document(game_id).get().to_dict()
    new_game = copy.deepcopy(game)
    new_game['name'] = name
    games_ref.document(game_id).set(new_game)
    return jsonify(new_game), 200

#Get list of users in game
@game_bp.route('/users', methods=['GET'])
def get_game_users():
    game_id = request.args.get('game_id')
    game = games_ref.document(game_id).get().to_dict()
    user_ids = [users_ref.document(user_id).get().to_dict() for user_id in game['user_ids']]
    return jsonify(user_ids), 200

#Remove user from game
@game_bp.route('/users', methods=['PATCH'])
def remove_user_from_game():
    game_id = request.args.get('game_id')
    user_id = request.args.get('user_id')
    #Handle game
    game = games_ref.document(game_id).get().to_dict()
    game['user_ids'] = [id for id in game['user_ids'] if id != user_id]
    games_ref.document(game_id).set(game)
    #Handle user
    user = users_ref.document(user_id).get().to_dict()
    user['game_ids'] = [id for id in user['game_ids'] if id != game_id]
    users_ref.document(user_id).set(user)
    return jsonify(game), 200

### LOCATIONS ###

#Create location within game
@game_bp.route('/locations', methods=['POST'])
def add_location():
    game_id = request.args.get('game_id')
    name = request.json['name']
    type_name = request.json['type']
    loc_id = str(uuid.uuid4())
    loc_ref = games_ref.document(game_id).collection('locations')
    loc_data = {'name': name, 'lid': loc_id, 'gid': game_id, 'type': type_name, 'item_ids': [], 'timestamp': str(datetime.datetime.now())}
    loc_ref.document(loc_id).set(loc_data)
    return jsonify(loc_data), 200

#Delete location and unassign all items
@game_bp.route('locations', methods=['DELETE'])
def delete_location():
    #Get all items from location
    game_id = request.args.get('game_id')
    loc_id = request.args.get('loc_id')
    loc_ref = games_ref.document(game_id).collection('locations')
    item_ids = loc_ref.document(loc_id).get().to_dict()['item_ids']
    unassigned_id = get_unassigned(loc_ref)
    #Move every item in location to 'Unassigned'
    for item_id in item_ids:
        change_item_location(games_ref, game_id, item_id, unassigned_id)
        add_item_to_location(games_ref, game_id, item_id, unassigned_id)
    loc_ref.document(loc_id).delete()
    return jsonify({'success': True}), 200


#Get location or list of locations
@game_bp.route('/locations', methods=['GET'])
def read_locations():
    game_id = request.args.get('game_id')
    loc_id = request.args.get('loc_id')
    loc_ref = games_ref.document(game_id).collection('locations')
    if loc_id:
        loc = loc_ref.document(loc_id).get()
        return jsonify(loc.to_dict()), 200
    else:
        all_locs = [doc.to_dict() for doc in loc_ref.stream()]
        return jsonify(all_locs), 200
    
#Rename location
@game_bp.route('/locations', methods=['PATCH'])
def rename_location():
    game_id = request.args.get('game_id')
    loc_id = request.args.get('loc_id')
    name = request.json['name']
    loc_ref = games_ref.document(game_id).collection('locations')
    new_loc = loc_ref.document(loc_id).get().to_dict()
    new_loc['name'] = name
    loc_ref.document(loc_id).set(new_loc)
    return jsonify(new_loc)

### ITEMS ###

#Create item w/ location ID (default to unassigned)
@game_bp.route('/items', methods=['POST'])
def create_item():
    game_id = request.args.get('game_id')
    loc_id = request.args.get('loc_id')
    loc_ref = games_ref.document(game_id).collection('locations')
    item_ref = games_ref.document(game_id).collection('items')
    item_id = str(uuid.uuid4())
    if not loc_id:
        loc_id = get_unassigned(loc_ref)
    #Add new item to items collection of game
    new_item = request.json
    new_item['lid'] = loc_id
    new_item['gid'] = game_id
    new_item['iid'] = item_id
    new_item['timestamp'] = str(datetime.datetime.now())
    item_ref.document(item_id).set(new_item)
    #Add item to location's item ID list
    add_item_to_location(games_ref, game_id, item_id, loc_id)
    return jsonify(new_item), 200
    
#Delete item
@game_bp.route('/items', methods=['DELETE'])
def delete_item():
    game_id = request.args.get('game_id')
    item_id = request.args.get('item_id')
    #Get loc ID of item
    item_ref = games_ref.document(game_id).collection('items')
    loc_id = item_ref.document(item_id).get().to_dict()['lid']
    remove_item_from_location(games_ref, game_id, item_id, loc_id)
    #Delete item
    item_ref.document(item_id).delete()
    return jsonify({'success': True}), 200

# Change location of item
@game_bp.route('/items/locations', methods=['PATCH'])
def update_item_location():
    game_id = request.args.get('game_id')
    item_id = request.args.get('item_id')
    loc_id = request.args.get('loc_id')
    new_loc = request.json['loc_id']
    item = change_item_location(games_ref, game_id, item_id, new_loc)
    remove_item_from_location(games_ref, game_id, item_id, loc_id)
    add_item_to_location(games_ref, game_id, item_id, new_loc)
    return jsonify(item), 200

# Change name/type of item
@game_bp.route('/items', methods=['PATCH'])
def update_item_fields():
    game_id = request.args.get('game_id')
    item_id = request.args.get('item_id')
    items = games_ref.document(game_id).collection('items')
    item = items.document(item_id).get().to_dict()
    data = request.json

    for field, value in data.items():
        item[field] = value
    
    items.document(item_id).set(item)

    return jsonify(item), 200

#Get item or list of items
@game_bp.route('/items', methods=['GET'])
def read_items():
    game_id = request.args.get('game_id')
    item_id = request.args.get('item_id')
    item_ref = games_ref.document(game_id).collection('items')
    if item_id:
        item = item_ref.document(item_id).get()
        return jsonify(item.to_dict()), 200
    else:
        all_items = [doc.to_dict() for doc in item_ref.stream()]
        return jsonify(all_items), 200

#Read items from location
@game_bp.route('/locations/items', methods=['GET'])
def read_items_from_location():
    game_id = request.args.get('game_id')
    loc_id = request.args.get('loc_id')
    loc_ref = games_ref.document(game_id).collection('locations')
    location = loc_ref.document(loc_id).get().to_dict()
    item_ref = games_ref.document(game_id).collection('items')
    item_ids = location['item_ids']
    items = []
    for item_id in item_ids:
        items.append(item_ref.document(item_id).get().to_dict())
    return jsonify(items), 200






