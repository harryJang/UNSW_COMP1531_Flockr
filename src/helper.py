"""
Imported re for valid email
Imported hashlib to encrypt passwords
Imported jwt for encoding and decoding tokens
"""
import re
import hashlib
import random
import string
import jwt
from global_vars import data, SECRET, code
from error import AccessError, InputError

# 1000 length message used in testing
LONG_MESSAGE = \
    """
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    111111111111111111111111111111111111111111111111111111111111
    """

# Helper functions for auth
def generate_token(u_id):
    '''Generate a token based on the u_id and append it to the online list'''
    token = jwt.encode({'u_id': u_id}, SECRET, algorithm='HS256').decode('utf-8')
    data['online'].append(token)
    return token

def find_user(token):
    '''Returns user dictionary with the input token'''
    if token not in data['online']:
        raise AccessError(description='Invalid token')
    u_id = jwt.decode(token.encode('UTF-8'), SECRET, algorithms=['HS256'])['u_id']
    return data['users'][u_id - 1]

def find_user_in_all(u_id, channel_id):
    '''Finds a user in all members of a channel'''
    is_member = False
    for member in data['channels'][channel_id - 1]['all_members']:
        if member['u_id'] == u_id:
            is_member = True
            break
    return is_member

def find_user_in_owners(u_id, channel_id):
    '''Finds a user in owner members of a channel'''
    user_is_owner = False
    for user in data['channels'][channel_id - 1]['owner_members']:
        if user['u_id'] == u_id:
            user_is_owner = True
            break
    return user_is_owner

def generate_handle_string(name_first, name_last):
    """Based on the first and last name, create a unique handle string"""
    name_first = name_first.lower()
    name_last = name_last.lower()
    name_full = name_first + name_last
    handle_str = name_full[:18]
    existing_codes = []
    for user in data['users']:
        if user['handle_str'][:-2] == handle_str:
            existing_codes.append(user['handle_str'][-2:])
    unique_code = 0
    while "{0:0=2d}".format(unique_code) in existing_codes:
        unique_code += 1
    unique_code = "{0:0=2d}".format(unique_code)
    handle_str += unique_code
    return handle_str

def encrypted(password):
    """Return the given password in an encrypted form"""
    return hashlib.sha256(password.encode()).hexdigest()

def existing_msg_ids():
    """Return a list of all the message ids in use (no order)"""
    msg_ids = []
    for channel in data['channels']:
        for message in channel['messages']:
            msg_ids.append(message['message_id'])
    return msg_ids

def requested_msg(message_id):
    """Find the message dictionary that matches the message id"""
    for channel in data['channels']:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                return message, channel['channel_id']
    return None, None

def get_reset_code():
    """Create a new reset code"""
    letters = string.ascii_letters
    letters = string.ascii_letters
    codes = [reset_code['code'] for reset_code in code]
    result_str = ''.join(random.choice(letters) for i in range(0, 8))
    while result_str in codes:
        result_str = ''.join(random.choice(letters) for i in range(0, 8))
    return result_str
