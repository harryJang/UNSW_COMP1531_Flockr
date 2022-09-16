import re
from global_vars import data
from error import InputError

def check_valid_email(email):
    """Check validity of email"""
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if not bool(re.search(regex, email)):
        raise InputError(description='Invalid email')

def check_existing_email(email):
    '''Check whether the given email already exists'''
    for user in data['users']:
        if user['email'] == email:
            raise InputError(description='This email has been taken')

def check_password_len(password):
    '''Check if password length is too short'''
    if len(password) < 6:
        raise InputError(description='Your password is too short')

def check_first_name(name_first):
    '''Check whether first name is of appropriate length'''
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description='First name needs to be between 1-50 characters in length')

def check_last_name(name_last):
    '''Check whether last name is of appropriate length'''
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description='Last name needs to be between 1-50 characters in length')

def check_u_id(u_id):
    '''Check whether there exists a user with the given u+id'''
    if u_id > len(data['users']):
        raise InputError(description="Specified u_id does not exist")

def check_channel_id(channel_id):
    '''Check whether there exists a channel with the given channel id'''
    if channel_id > len(data['channels']):
        raise InputError(description="Specified channel does not exist")

def check_channel_name_len(name):
    '''Check if channel name is of appropriate length'''
    if len(name) > 20:
        raise InputError(description='Name longer than 20 characters is not permitted.')

MAX_MESSAGE_LEN = 1000

def check_message_len(message):
    '''Check whether the message is too long'''
    if len(message) > MAX_MESSAGE_LEN:
        raise InputError(description='Message is too long (More than 1000 characters')

def check_react_id(react_id):
    '''Check whether react id is valid'''
    if react_id != 1:
        raise InputError(description="Invalid react ID")

def check_permission_id(permission_id):
    '''Check whether permission id is valid'''
    if permission_id not in (1, 2):
        raise InputError(description="permission_id does not refer to a value permission")
