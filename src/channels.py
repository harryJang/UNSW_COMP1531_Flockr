'''
This file contains channels_list, channels_listall and channels_create
'''
from global_vars import data
from helper import find_user
from error import InputError
from error_checks import check_channel_name_len

def channels_list(token):
    '''
    This function
    Looks for channels user is part of.
    '''
    # Check if token is valid or not.
    # If token is valid, record u_id
    user = find_user(token)

    list_of_channels = []
    # Traverse the data dictionary.
    for channel in data['channels']:
        # Find the channels user is part of.
        # Assign them to a list_of_channels.
        for user_in_channel in channel['all_members']:
            if user['u_id'] == user_in_channel['u_id']:
                list_of_channels.append({'channel_id': channel['channel_id'],
                                         'name': channel['name']})

    # when everything is successful, return the list_of_channels.
    return {'channels' : list_of_channels}

def channels_listall(token):
    '''
    This function
    Looks for all channels.
    '''
    # Check if token is valid or not.
    find_user(token)
    list_of_channels = [{'channel_id': ch['channel_id'], 'name': ch['name']} \
    for ch in data['channels']]
    # when everything is successful, return dictionary of channels.
    return {'channels' : list_of_channels}

def channels_create(token, name, is_public):
    '''
    This function
    Creates new channel and add it into the data.
    '''
    # Check if name is valid or not.
    check_channel_name_len(name)

    # Check if token is valid or not.
    user = find_user(token)

    # Make new channel with proper details.
    channel_id = len(data['channels']) + 1
    channel_creator = {'u_id' : user['u_id'], 'name_first' : user['name_first'],\
                       'name_last' : user['name_last'],\
                       'profile_img_url': user['profile_img_url']}
    new_channel = {'channel_id' : channel_id,
                   'name' : name,
                   'owner_members' : [channel_creator],
                   'all_members' : [channel_creator],
                   'is_public' : is_public,
                   'messages': [],
                   'standup':{'is_active': False, 'time_start': None, 'time_finish': None,\
                              'messages': []}}

    # Add them into data.
    data['channels'].append(new_channel)
    return {'channel_id': channel_id}
