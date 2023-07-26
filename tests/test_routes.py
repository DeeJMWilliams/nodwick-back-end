import pytest

### HELPERS ###

def get_id(arr, target, id_type):
    for item in arr:
        if item['name'] == target:
            result = item[id_type]
            break
    return result

### SETUP ###

def create_three_users(client):
    steve = client.post('/users', json={'name': 'Steve', 'email': 'steve@gmail.com'}).get_json()
    jaehyun = client.post('/users', json={'name': 'Jaehyun', 'email': 'jaehyun@gmail.com'}).get_json()
    sarah = client.post('/users', json={'name': 'Sarah', 'email': 'sarah@gmail.com'}).get_json()

    return {'steve': steve, 'jaehyun': jaehyun, 'sarah': sarah}

def create_three_games(client):
    pathfinder = client.post('/games', json={'name': 'Pathfinder 2e'}).get_json()
    delta_green = client.post('/games', json={'name': 'Delta Green'}).get_json()
    paranoia = client.post('/games', json={'name': 'Paranoia'}).get_json()

    return {'paranoia': paranoia, 'delta_green': delta_green, 'pathfinder': pathfinder}

def associate_games_and_users(client):
    users = create_three_users(client)
    games = create_three_games(client)
    #Define games
    pathfinder = games['pathfinder']
    delta_green = games['delta_green']
    paranoia = games['paranoia']
    #Define users
    steve = users['steve']
    jaehyun = users['jaehyun']
    sarah = users['sarah']
    #Add all users to pathfinder game
    client.patch(f'/users?user_id={steve["uid"]}&game_id={pathfinder["gid"]}')
    client.patch(f'/users?user_id={jaehyun["uid"]}&game_id={pathfinder["gid"]}')
    client.patch(f'/users?user_id={sarah["uid"]}&game_id={pathfinder["gid"]}')
    #Add steve and sarah to delta green game
    client.patch(f'/users?user_id={steve["uid"]}&game_id={delta_green["gid"]}')
    client.patch(f'/users?user_id={sarah["uid"]}&game_id={delta_green["gid"]}')
    #Add sarah and jaehyun to paranoia game
    client.patch(f'/users?user_id={sarah["uid"]}&game_id={paranoia["gid"]}')
    client.patch(f'/users?user_id={jaehyun["uid"]}&game_id={paranoia["gid"]}')

### USERS ###

@pytest.mark.users
def test_get_all_users(client):
    associate_games_and_users(client)
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
def test_get_user_by_id(client):
    #Get all users to extract user ID
    associate_games_and_users(client)
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
def test_create_user(client):
    response = client.post('/users', json={'name': 'Jamal', 'email': 'jamal@gmail.com'})
    response_body = response.get_json()

    assert isinstance(response_body, dict)
    assert 'uid' in response_body.keys()
    assert 'name' in response_body.keys()
    assert 'email' in response_body.keys()
    assert 'timestamp' in response_body.keys()
    assert 'game_ids' in response_body.keys()

@pytest.mark.users
def test_add_user_to_db(client):
    associate_games_and_users(client)
    client.post('/users', json={'name': 'Jamal', 'email': 'jamal@gmail.com'})
    response = client.get('/users')
    response_body = response.get_json()

    assert len(response_body) == 4

@pytest.mark.users
def test_delete_user(client):
    associate_games_and_users(client)
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
def test_get_games(client):
    associate_games_and_users(client)
    response = client.get('/games')
    response_body = response.get_json()

    assert len(response_body) == 3
    for game in response_body:
        assert 'gid' in game.keys()
        assert 'name' in game.keys()
        assert 'timestamp' in game.keys()
        assert 'user_ids' in game.keys()

@pytest.mark.games
def test_get_game_by_id(client):
    associate_games_and_users(client)
    games = client.get('/games').get_json()
    game_id = get_id(games, 'Pathfinder 2e', 'gid')
    response = client.get(f'/games?game_id={game_id}')
    response_body = response.get_json()

    assert response_body['name'] == 'Pathfinder 2e'
    assert response_body['gid'] == game_id
    assert 'timestamp' in response_body.keys()
    assert 'user_ids' in response_body.keys()

@pytest.mark.games
def test_delete_game(client):
    associate_games_and_users(client)
    games = client.get('/games').get_json()
    game_id = get_id(games, 'Pathfinder 2e', 'gid')
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
def test_read_games_from_user(client):
    associate_games_and_users(client)
    users = client.get('/users').get_json()
    user_id = get_id(users, 'Jaehyun', 'uid')
    
    response = client.get(f'/users/games?user_id={user_id}')
    response_body = response.get_json()

    assert len(response_body) == 2
    for game in response_body:
        assert user_id in game['user_ids']

### LOCATIONS ###

@pytest.mark.locations
def test_create_location_in_game(client):
    associate_games_and_users(client)
    games = client.get('/games').get_json()
    game_id = get_id(games, 'Delta Green', 'gid')
    
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
def test_delete_location(client):
    associate_games_and_users(client)
    games = client.get('/games').get_json()
    game_id = get_id(games, 'Paranoia', 'gid')
    #Add temporary location
    location = client.post(f'/games/locations?game_id={game_id}', json={'name': 'Closet'}).get_json()
    loc_id = location['lid']

    response = client.delete(f'/games/locations?game_id={game_id}&loc_id={loc_id}')
    response_body = response.get_json()

    assert response_body['success'] == True

    locations = client.get(f'/games/locations?game_id={game_id}').get_json()
    assert len(locations) == 1

    #!!! Add tests for item unassignment

