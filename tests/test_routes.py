import pytest

# NB:
# Tests must be run one at a time to operate correctly because
# the database doesn't clear between tests if they are run in
# a batch. I hope to fix this if I have time.

### HELPERS ###

def get_id(arr, target, id_type):
    for item in arr:
        if item['name'] == target:
            result = item[id_type]
            break
    return result

def get_game(client, name):
    games = client.get('/games').get_json()
    return get_id(games, name, 'gid')

def get_loc(client, game_id, name):
    locations = client.get(f'/games/locations?game_id={game_id}').get_json()
    return get_id(locations, name, 'lid')

def get_item(client, game_id, name):
    items = client.get(f'/games/items?game_id={game_id}').get_json()
    return get_id(items, name, 'iid')

### USERS ###

@pytest.mark.users
def test_get_all_users(client, setup_db):
    # setup_db(client)
    response = client.get('/users')
    response_body = response.get_json()

    assert len(response_body) == 3
    for user in response_body:
        assert 'uid' in user.keys()
        assert 'name' in user.keys()
        assert 'email' in user.keys()
        assert 'timestamp' in user.keys()
        assert 'game_ids' in user.keys()

@pytest.mark.users
def test_get_user_by_id(client, setup_db):
    #Get user ID of Sarah
    users = client.get('/users').get_json()
    user_id = get_id(users, 'Sarah', 'uid')

    #Run get request again on user ID
    response = client.get(f'/users?user_id={user_id}')
    user = response.get_json()

    assert isinstance(user, dict)
    assert user['name'] == 'Sarah'
    assert 'uid' in user.keys()
    assert 'email' in user.keys()
    assert 'timestamp' in user.keys()
    assert 'game_ids' in user.keys()

@pytest.mark.users
def test_create_user(client, setup_db):
    response = client.post('/users', json={'name': 'Jamal', 'email': 'jamal@gmail.com'})
    response_body = response.get_json()

    assert isinstance(response_body, dict)
    assert 'uid' in response_body.keys()
    assert 'name' in response_body.keys()
    assert 'email' in response_body.keys()
    assert 'timestamp' in response_body.keys()
    assert 'game_ids' in response_body.keys()


@pytest.mark.users
def test_add_user_to_db(client, setup_db):
    client.post('/users', json={'name': 'Jamal', 'email': 'jamal@gmail.com'})
    response = client.get('/users')
    response_body = response.get_json()

    assert len(response_body) == 4

@pytest.mark.users
def test_delete_user(client, setup_db):
    users = client.get('/users').get_json()
    user_id = get_id(users, 'Sarah', 'uid')
    #Delete Sarah
    response = client.delete(f'/users?user_id={user_id}')
    response_body = response.get_json()

    remaining_users = client.get('/users').get_json()

    assert response_body['success'] == True
    assert len(remaining_users) == 2
    for user in remaining_users:
        assert user['name'] != 'Sarah'
    #Verify Sarah has been removed from games
    games = client.get('/games').get_json()
    for game in games:
        assert user_id not in game['user_ids']

### GAMES ###

@pytest.mark.games
def test_get_games(client, setup_db):
    response = client.get('/games')
    response_body = response.get_json()

    assert len(response_body) == 3
    for game in response_body:
        assert 'gid' in game.keys()
        assert 'name' in game.keys()
        assert 'timestamp' in game.keys()
        assert 'user_ids' in game.keys()

@pytest.mark.games
def test_get_game_by_id(client, setup_db):
    game_id = get_game(client, 'Pathfinder 2e')
    response = client.get(f'/games?game_id={game_id}')
    response_body = response.get_json()

    assert response_body['name'] == 'Pathfinder 2e'
    assert response_body['gid'] == game_id
    assert 'timestamp' in response_body.keys()
    assert 'user_ids' in response_body.keys()

@pytest.mark.games
def test_delete_game(client, setup_db):
    game_id = get_game(client, 'Pathfinder 2e')
    response = client.delete(f'/games?game_id={game_id}')
    response_body = response.get_json()

    assert response_body['success'] == True
    
    remaining_games = client.get('/games').get_json()

    assert len(remaining_games) == 2
    for game in remaining_games:
        assert game['name'] != 'Pathfinder 2e'

    #Verify game has been removed from users
    users = client.get('/users').get_json()
    for user in users:
        assert game_id not in user['game_ids']

@pytest.mark.games
def test_read_games_from_user(client, setup_db):
    users = client.get('/users').get_json()
    user_id = get_id(users, 'Jaehyun', 'uid')
    
    response = client.get(f'/users/games?user_id={user_id}')
    response_body = response.get_json()

    assert len(response_body) == 2
    for game in response_body:
        assert user_id in game['user_ids']

### LOCATIONS ###

@pytest.mark.locations
def test_create_location_in_game(client, setup_db):
    game_id = get_game(client, 'Delta Green')
    
    response = client.post(f'/games/locations?game_id={game_id}', json={'name': 'Agent Smith'})
    response_body = response.get_json()

    assert response_body['name'] == 'Agent Smith'
    assert response_body['gid'] == game_id
    assert 'timestamp' in response_body.keys()
    assert 'lid' in response_body.keys()
    assert 'item_ids' in response_body.keys()

    locations = client.get(f'/games/locations?game_id={game_id}').get_json()
    assert len(locations) == 2

@pytest.mark.locations
def test_delete_location(client, setup_db):
    game_id = get_game(client, 'Pathfinder 2e')
    #Add temporary location
    loc_id = get_loc(client, game_id, 'Arthrax')
    items = client.get(f'/games/locations/items?game_id={game_id}&loc_id={loc_id}').get_json()

    response = client.delete(f'/games/locations?game_id={game_id}&loc_id={loc_id}')
    response_body = response.get_json()

    assert response_body['success'] == True

    locations = client.get(f'/games/locations?game_id={game_id}').get_json()
    assert len(locations) == 2

    #Verify items have been moved to Unassigned
    unassigned_id = get_id(locations, 'Unassigned', 'lid')
    unassigned_loc = client.get(f'/games/locations?game_id={game_id}&loc_id={unassigned_id}').get_json()
    for item in items:
        assert item['iid'] in unassigned_loc['item_ids']
        item_new = client.get(f'/games/items?game_id={game_id}&item_id={item["iid"]}').get_json()
        assert item_new['lid'] == unassigned_id

@pytest.mark.locations
def test_get_all_locations(client, setup_db):
    game_id = get_game(client, 'Pathfinder 2e')

    response = client.get(f'/games/locations?game_id={game_id}')
    response_body = response.get_json()

    assert len(response_body) == 3

@pytest.mark.locations
def test_get_location_by_id(client, setup_db):
    game_id = get_game(client, 'Pathfinder 2e')
    loc_id = get_loc(client, game_id, 'Balerion')

    response = client.get(f'/games/locations?game_id={game_id}&loc_id={loc_id}')
    response_body = response.get_json()

    assert response_body['name'] == 'Balerion'
    assert response_body['gid'] == game_id
    assert response_body['lid'] == loc_id
    assert len(response_body['item_ids']) == 2
    assert 'timestamp' in response_body.keys()
    
### ITEMS ###

@pytest.mark.items
def test_get_all_items(client, setup_db):
    game_id = get_game(client, 'Pathfinder 2e')

    response = client.get(f'/games/items?game_id={game_id}')
    response_body = response.get_json()

    assert len(response_body) == 3

@pytest.mark.items
def test_get_no_items(client, setup_db):
    game_id = get_game(client, 'Delta Green')

    response = client.get(f'/games/items?game_id={game_id}')
    response_body = response.get_json()

    assert len(response_body) == 0

@pytest.mark.items
def test_get_item_by_id(client, setup_db):
    game_id = get_game(client, 'Pathfinder 2e')
    item_id = get_item(client, game_id, 'Marauding Axe')

    response = client.get(f'/games/items?game_id={game_id}&item_id={item_id}')
    response_body = response.get_json()

    assert response_body['name'] == 'Marauding Axe'
    assert response_body['gid'] == game_id
    assert response_body['iid'] == item_id
    assert 'lid' in response_body.keys()
    assert 'timestamp' in response_body.keys()

@pytest.mark.items
def test_get_items_from_location(client, setup_db):
    game_id = get_game(client, 'Pathfinder 2e')
    loc_id = get_loc(client, game_id, 'Arthrax')

    response = client.get(f'/games/locations/items?game_id={game_id}&loc_id={loc_id}')
    response_body = response.get_json()

    assert len(response_body) == 1

@pytest.mark.items
def test_delete_item(client, setup_db):
    game_id = get_game(client, 'Pathfinder 2e')
    item_id = get_item(client, game_id, 'Marauding Axe')
    loc_id = client.get(f'/games/items?game_id={game_id}&item_id={item_id}').get_json()['lid']

    response = client.delete(f'/games/items?game_id={game_id}&item_id={item_id}')
    response_body = response.get_json()

    assert response_body['success'] == True
    location = client.get(f'/games/locations?game_id={game_id}&loc_id={loc_id}').get_json()
    assert item_id not in location['item_ids']

@pytest.mark.items
def test_move_item(client, setup_db):
    game_id = get_game(client, 'Pathfinder 2e')
    source_loc = get_loc(client, game_id, 'Balerion')
    dest_loc = get_loc(client, game_id, 'Arthrax')
    item_id = get_item(client, game_id, 'Rivening Shield')

    response = client.patch(f'/games/items?game_id={game_id}&loc_id={source_loc}&item_id={item_id}', json={'loc_id': dest_loc})
    response_body = response.get_json()

    assert response_body['name'] == 'Rivening Shield'
    assert response_body['lid'] == dest_loc
    assert response_body['gid'] == game_id
    assert response_body['iid'] == item_id
    assert 'timestamp' in response_body.keys()

    source = client.get(f'/games/locations?game_id={game_id}&loc_id={source_loc}').get_json()
    dest = client.get(f'/games/locations?game_id={game_id}&loc_id={dest_loc}').get_json()

    assert item_id not in source['item_ids']
    assert item_id in dest['item_ids']

@pytest.mark.items
def test_create_item_no_location(client, setup_db):
    game_id = get_game(client, 'Delta Green')
    
    response = client.post(f'/games/items?game_id={game_id}', json={'name': 'Tome of Yog-Sothoth', 'type': 'Tome'})
    response_body = response.get_json()

    assert response_body['name'] == 'Tome of Yog-Sothoth'
    assert response_body['gid'] == game_id
    assert 'timestamp' in response_body.keys()
    assert 'iid' in response_body.keys()
    assert 'type' in response_body.keys()

    loc_id = get_loc(client, game_id, 'Unassigned')
    location = client.get(f'/games/locations?game_id={game_id}&loc_id={loc_id}').get_json()
    item_id = get_item(client, game_id, 'Tome of Yog-Sothoth')

    assert response_body['lid'] == loc_id
    assert item_id in location['item_ids']

@pytest.mark.items
def test_create_item_with_location(client, setup_db):
    game_id = get_game(client, 'Pathfinder 2e')
    loc_id = get_loc(client, game_id, 'Arthrax')

    response = client.post(f'/games/items?game_id={game_id}&loc_id={loc_id}', json={'name': 'Robes of Invisibility'})
    response_body = response.get_json()

    assert response_body['name'] == 'Robes of Invisibility'
    assert response_body['gid'] == game_id
    assert response_body['lid'] == loc_id
    assert 'iid' in response_body.keys()
    assert 'timestamp' in response_body.keys()

    location = client.get(f'/games/locations?game_id={game_id}&loc_id={loc_id}').get_json()
    item_id = get_item(client, game_id, 'Robes of Invisibility')

    assert item_id in location['item_ids']