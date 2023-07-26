from google.cloud.firestore_v1.base_query import FieldFilter

def remove_item_from_location(games_ref, game_id, item_id, loc_id):
    loc_ref = games_ref.document(game_id).collection('locations')
    location = loc_ref.document(loc_id).get().to_dict()
    location['item_ids'] = list(filter(lambda x: x != item_id, location['item_ids']))
    loc_ref.document(loc_id).set(location)
    return location

def add_item_to_location(games_ref, game_id, item_id, loc_id):
    loc_ref = games_ref.document(game_id).collection('locations')
    location = loc_ref.document(loc_id).get().to_dict()
    location['item_ids'].append(item_id)
    loc_ref.document(loc_id).set(location)
    return location

def change_item_location(games_ref, game_id, item_id, loc_id):
    item_ref = games_ref.document(game_id).collection('items')
    item = item_ref.document(item_id).get().to_dict()
    item['lid'] = loc_id
    item_ref.document(item_id).set(item)
    return item

def get_unassigned(loc_ref):
    #!!! Reveert for deployment
    # unassigned_ref = loc_ref.where(filter=FieldFilter('name', '==', 'Unassigned'))
    unassigned_ref = loc_ref.where('name', '==', 'Unassigned')
    unassigned_id = list(unassigned_ref.get())[0].to_dict()['lid']
    return unassigned_id

