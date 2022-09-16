'''
Import global variable data
Import jwt to decode tokens
'''
import jwt
from global_vars import data, SECRET
from helper import find_user, find_user_in_all
from error import AccessError, InputError
from error_checks import check_u_id, check_permission_id
def clear():
    '''Function clears stored data'''
    data['users'] = []
    data['channels'] = []
    data['online'] = []
    return {}

def users_all(token):
    '''Takes in a token and return all users in the flockr'''
    find_user(token)

    # Get user details without password, token and permission_id
    # Add this to a new list of all users
    all_users = []
    for user in data['users']:
        details = {'u_id' : user['u_id'], 'email': user['email'], \
                   'name_first' : user['name_first'], 'name_last' : user['name_last'], \
                   'handle_str': user['handle_str']}
        all_users.append(details)

    return {'users' : all_users}

def admin_userpermission_change(token, u_id, permission_id):
    '''Change u_id's permissions to new permission described by permission_id'''
    auth_user = find_user(token)
    if auth_user['permission_id'] == 2:
        raise AccessError(description="You are not a flockr owner")
    check_permission_id(permission_id)
    check_u_id(u_id)

    # Give u_id permission_id
    data['users'][u_id - 1]['permission_id'] = permission_id
    return {}

def search(token, query_str):
    '''Takes a query string and returns messages in channels the user has joined
    that match that string'''
    user = find_user(token)
    match = []
    # Look through each channel's messages
    for channel in data['channels']:
        if find_user_in_all(user['u_id'], channel['channel_id']):
            for message in channel['messages']:
                # Make query string and message lower case to see if test is the same
                query_str_lower = query_str.lower()
                message_lower = message['message'].lower()
                if query_str_lower in message_lower:
                    match.append(message)
    return {'messages': match,}
