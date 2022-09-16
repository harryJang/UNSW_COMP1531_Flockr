"""
Imported data dictionary to store data
Imported helper functions from helper.py to check validity of tokens, whether
authorised user is part of the channel and count the number of messages in all
channels.
Imported datetime functions to calculate time of messages
Imported errors from error.py to handle exceptions
"""
from datetime import datetime, timedelta
import time
from global_vars import data
from helper import find_user, find_user_in_all, find_user_in_owners, \
                   existing_msg_ids, requested_msg
from error import InputError, AccessError
from channels import channels_list
from error_checks import check_channel_id, check_message_len, check_react_id

def message_send(token, channel_id, message):
    """
    Send a message from the authorised user to the channel with the given
    channel id
    """
    # Error checking
    user = find_user(token)
    if not find_user_in_all(user['u_id'], channel_id):
        raise AccessError(description='You are not part of this channel')
    check_message_len(message)

    # Assigning new message id
    msg_ids = existing_msg_ids()
    message_id = 1
    while message_id in msg_ids:
        message_id += 1

    # Creating and appending the new message
    time_created = datetime.now().timestamp()
    reacts = [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}]
    new_message = {'message_id': message_id, 'u_id': user['u_id'], 'message': message,
                   'time_created': time_created, 'reacts': reacts, 'is_pinned': False}
    data['channels'][channel_id - 1]['messages'].insert(0, new_message)

    return {'message_id': message_id}

def message_remove(token, message_id):
    """Remove a message from the channel with the given channel id"""
    # Error checking
    user = find_user(token)
    msg, channel_id = requested_msg(message_id)
    if msg is None:
        raise InputError(description='Message no longer exists')
    if user['u_id'] != msg['u_id'] and not find_user_in_owners(user['u_id'], channel_id) \
    and user['permission_id'] != 1:
        raise AccessError(description='You do not have the authority to remove this message')

    # Removing the requested message
    data['channels'][channel_id - 1]['messages'].remove(msg)
    return {}

def message_edit(token, message_id, message):
    """Function to edit messages"""
    user = find_user(token)
    msg, channel_id = requested_msg(message_id)
    if user['u_id'] != msg['u_id'] and not find_user_in_owners(user['u_id'], channel_id) \
    and user['permission_id'] != 1:
        raise AccessError(description='You do not have the authority to edit this message')
    # If edit string is empty, delete the message, else replace
    check_message_len(message)
    if message == '':
        data['channels'][channel_id - 1]['messages'].remove(msg)
    else:
        msg['message'] = message

    return {}

def message_sendlater(token, channel_id, message, time_sent):
    """Send a message at the given time"""
    # Error checking
    user = find_user(token)
    check_channel_id(channel_id)
    if not find_user_in_all(user['u_id'], channel_id):
        raise AccessError(description="You are not part of this channel")
    check_message_len(message)
    if datetime.now().timestamp() > time_sent:
        raise InputError(description="Please choose a time in the future!")
    # Waiting until the specified time
    curr_time = datetime.now().timestamp()
    time_until_send = timedelta(seconds=time_sent - curr_time).total_seconds()
    time.sleep(time_until_send)
    # Generating and sending message
    msg_ids = existing_msg_ids()
    message_id = 1
    while message_id in msg_ids:
        message_id += 1
    reacts = [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}]
    new_message = {'message_id': message_id, 'u_id': user['u_id'], 'message': message,
                   'time_created': time_sent, 'reacts': reacts}
    data['channels'][channel_id - 1]['messages'].insert(0, new_message)

    return {
        'message_id': message_id
    }

def message_react(token, message_id, react_id):
    """React with react id to the message with message id"""
    # Error  checking
    user = find_user(token)
    check_react_id(react_id)
    user_channels = channels_list(token)['channels']
    for channel in user_channels:
        for message in data['channels'][channel['channel_id'] - 1]['messages']:
            if message['message_id'] == message_id:
                if user['u_id'] in message['reacts'][0]['u_ids']:
                    raise InputError(description="Message already reacted")
                message['reacts'][0]['u_ids'].append(user['u_id'])
                return {}
    raise InputError(description="No matching messages found in user's channels")

def message_unreact(token, message_id, react_id):
    """Unreact with react id to the message with message id"""
    # Error checking
    user = find_user(token)
    check_react_id(react_id)
    user_channels = channels_list(token)['channels']
    for channel in user_channels:
        for message in data['channels'][channel['channel_id'] - 1]['messages']:
            if message['message_id'] == message_id:
                if user['u_id'] not in message['reacts'][0]['u_ids']:
                    raise InputError(description="Message not yet reacted")
                message['reacts'][0]['u_ids'].remove(user['u_id'])
                return {}
    raise InputError(description="No matching messages found in user's channels")

def message_pin(token, message_id):
    """Pin message with message id within a channel"""
    # Error checking
    user = find_user(token)
    channel_id = None
    msg = None
    for channel in data['channels']:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                msg = message
                channel_id = channel['channel_id']

    if channel_id is None:
        raise InputError(description="Message does not exist")

    if not find_user_in_all(user['u_id'], channel_id):
        raise AccessError(description="You are not part of this channel")

    if not find_user_in_owners(user['u_id'], channel_id):
        raise AccessError(description="You are not an owner")

    if msg['is_pinned']:
        raise InputError(description="Message already pinned")

    msg['is_pinned'] = True
    return {}

def message_unpin(token, message_id):
    """Unpin message with message id within a channel"""
    # Error checking
    user = find_user(token)
    channel_id = None
    msg = None
    for channel in data['channels']:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                msg = message
                channel_id = channel['channel_id']

    if channel_id is None:
        raise InputError(description="Message does not exist")

    if not find_user_in_all(user['u_id'], channel_id):
        raise AccessError(description="You are not part of this channel")

    if not find_user_in_owners(user['u_id'], channel_id):
        raise AccessError(description="You are not an owner")

    if not msg['is_pinned']:
        raise InputError(description="Message is already unpinned")

    msg['is_pinned'] = False
    return {}
