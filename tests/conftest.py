import pytest
from app import create_app, db
from flask.signals import request_finished

@pytest.fixture
def app():
    app = create_app({"TESTING": True})

    @request_finished.connect_via(app)
    def expire_session(sender, response, **extra):
        pass
        #db.reset()

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def setup_db(client):
    #Create three users
    steve = client.post('/users', json={'name': 'Steve', 'email': 'steve@gmail.com', 'uid': '1'}).get_json()
    jaehyun = client.post('/users', json={'name': 'Jaehyun', 'email': 'jaehyun@gmail.com', 'uid': '2'}).get_json()
    sarah = client.post('/users', json={'name': 'Sarah', 'email': 'sarah@gmail.com', 'uid': '3'}).get_json()
    #Create three games
    pathfinder = client.post('/games', json={'name': 'Pathfinder 2e'}).get_json()
    delta_green = client.post('/games', json={'name': 'Delta Green'}).get_json()
    paranoia = client.post('/games', json={'name': 'Paranoia'}).get_json()
    #Add all users to pathfinder game
    client.patch(f'/users/games?user_id={steve["uid"]}&game_id={pathfinder["gid"]}')
    client.patch(f'/users/games?user_id={jaehyun["uid"]}&game_id={pathfinder["gid"]}')
    client.patch(f'/users/games?user_id={sarah["uid"]}&game_id={pathfinder["gid"]}')
    #Add users to delta green game
    client.patch(f'/users/games?user_id={steve["uid"]}&game_id={delta_green["gid"]}')
    client.patch(f'/users/games?user_id={sarah["uid"]}&game_id={delta_green["gid"]}')
    #Add users to paranoia game
    client.patch(f'/users/games?user_id={sarah["uid"]}&game_id={paranoia["gid"]}')
    client.patch(f'/users/games?user_id={jaehyun["uid"]}&game_id={paranoia["gid"]}')
    #Create two locations in Pathfinder game
    arthrax = client.post(f'/games/locations?game_id={pathfinder["gid"]}', json={'name': 'Arthrax', 'type':'character'}).get_json()
    balerion = client.post(f'/games/locations?game_id={pathfinder["gid"]}', json={'name': 'Balerion', 'type':'character'}).get_json()
    #Add an item to one location
    client.post(f'/games/items?game_id={pathfinder["gid"]}&loc_id={arthrax["lid"]}', json={'name': 'Staff of Blizzards'})
    #Add two items to one location
    client.post(f'/games/items?game_id={pathfinder["gid"]}&loc_id={balerion["lid"]}', json={'name': 'Marauding Axe'})
    client.post(f'/games/items?game_id={pathfinder["gid"]}&loc_id={balerion["lid"]}', json={'name': 'Rivening Shield'})