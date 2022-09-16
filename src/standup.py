'''
Functions for the implementation of standup.
'''
from datetime import datetime, timedelta
import threading
from global_vars import data
from error import InputError, AccessError
from helper import find_user, find_user_in_all, existing_msg_ids
from error_checks import check_channel_id, check_message_len

def standup_start(token, channel_id, length):
    '''Adds standup details to data when standup_start() is run. Calls package_standup
    to package and messages'''
    check_channel_id(channel_id)

    # Check if a standup is running
    if data['channels'][channel_id - 1]['standup']['is_active'] is True:
        raise InputError(description='An active standup is currently running in this channel')

    # Edit standup dictionary when a standup is started
    start_time = datetime.now()
    finish_time = (start_time + timedelta(seconds=length)).timestamp()
    data['channels'][channel_id - 1]['standup'] = {'is_active': True,
                                                   'time_start': start_time.timestamp(),
                                                   'time_finish': finish_time,
                                                   'messages': []}

    # Wait for standup to finish before sending messages
    standup = threading.Timer(length, package_standup, args=(token, channel_id))
    standup.start()


    return {'time_finish': finish_time}

def package_standup(token, channel_id):
    '''Package messages sent during a standup and send them to channel
    after standup is finished'''
    if len(data['channels'][channel_id - 1]['standup']['messages']) != 0:
        # Package messages sent by standup_send
        standup_message = ''
        for message in data['channels'][channel_id - 1]['standup']['messages']:
            standup_message += message['handle'] + ': ' + message['message']
            standup_message += '\n'

        standup_message = standup_message[:-1]

        # If messages were sent during the standup, send the messages
        # Cannot use message_send() becase of 1000 character length cap
        msg_ids = existing_msg_ids()
        message_id = 1
        while message_id in msg_ids:
            message_id += 1

        user = find_user(token)
        # Creating and appending the new message
        time_created = data['channels'][channel_id - 1]['standup']['time_finish']
        reacts = [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}]
        # Change the timestamp to time_finish
        new_message = {'message_id': message_id, 'u_id': user['u_id'], 'message': standup_message,
                       'time_created': time_created, 'reacts': reacts, 'is_pinned': False}
        data['channels'][channel_id - 1]['messages'].insert(0, new_message)

    # Turn standup off
    data['channels'][channel_id - 1]['standup'] = {'is_active': False,
                                                   'time_start': None,
                                                   'time_finish': None,
                                                   'messages': []}

def standup_active(token, channel_id):
    '''Check if standup is active and return time it finishes. If not, return
    None'''
    check_channel_id(channel_id)
    standup = data['channels'][channel_id - 1]['standup']
    return {'is_active': standup['is_active'], 'time_finish': standup['time_finish']}

def standup_send(token, channel_id, message):
    '''Send a message to standup queue if there is a standup active'''
    check_channel_id(channel_id)
    check_message_len(message)

    # InputError if there is no standup active
    if data['channels'][channel_id - 1]['standup']['is_active'] is False:
        raise InputError(description='There is no active standup currently running\
                             in this channel')

    # AccessError if authorised user is not a memeber of channel
    user = find_user(token)
    if find_user_in_all(user['u_id'], channel_id) is False:
        raise AccessError(description="You are not part of this channel")

    message = {'handle': user['handle_str'], 'message': message}
    data['channels'][channel_id - 1]['standup']['messages'].append(message)

    return {}
