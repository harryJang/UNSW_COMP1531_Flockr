'''
Importing InputError and AccessError to deal with raised errors
Importing data structure for users, channels etc.
Importing helper functions from helper.py to streamline user finding process
'''

from error import InputError, AccessError
from global_vars import data
from helper import find_user, find_user_in_all, find_user_in_owners
from error_checks import check_channel_id, check_u_id
def channel_invite(token, channel_id, u_id):
    '''Function invites a user (with user id u_id) to join a channel with ID.
    Once invited the user is added to the channel immediately. This function is
    essentially the same as channel_join, but is used when the authorised user
    is prompting someone else to join the channel'''

    # Error checking:
    check_channel_id(channel_id)
    check_u_id(u_id)
    if find_user_in_all(u_id, channel_id):
        # User is already in this channel. Do nothing.
        raise InputError(description="Cannot invite somebody already in this channel")

    # Check whether the person inviting (authorised user) is a member of the channel
    # Loop through the users of the channel and check if any match given token
    auth_user = find_user(token)
    is_member = find_user_in_all(auth_user['u_id'], channel_id)
    if not is_member:
        raise AccessError(description="You are not a member of this channel")

    # Creating dict of details for the new member
    user = data['users'][u_id - 1]
    details_to_add = ['u_id', 'name_first', 'name_last', 'profile_img_url']
    new_channel_member = {}
    for detail in details_to_add:
        new_channel_member[detail] = user[detail]

    # Making the invited user a member of the channel
    channel = data['channels'][channel_id - 1]
    channel['all_members'].append(new_channel_member)

    # Checking if the invited person is a flockr owner, if yes, then give them
    # owner permissions to the channel as well
    if user['permission_id'] == 1:
        channel['owner_members'].append(new_channel_member)

    return {
    }

def channel_details(token, channel_id):
    '''Given a Channel with ID channel_id that the authorised user is part of,
    provide basic details about the channel'''
    check_channel_id(channel_id)

    # Check whether the person inviting (authorised user) is a member of the channel
    # Loop through the users of the channel and check if any match given token
    user = find_user(token)
    auth_u_id = user['u_id']
    is_member = find_user_in_all(auth_u_id, channel_id)
    if is_member is False:
        raise AccessError(description="You are not a member of this channel")

    channel = data['channels'][channel_id - 1]
    return {
        'name': channel['name'], 'owner_members': channel['owner_members'], \
        'all_members': channel['all_members']
    }

def channel_messages(token, channel_id, start):
    '''Given a Channel with ID channel_id that the authorised user is part of,
    return up to 50 messages between index "start" and "start + 50".
    Message with index 0 is the most recent message in the channel.
    This function returns a new index "end" which is the value of "start + 50",
    or, if this function has returned the least recent messages in the channel,
    returns -1 in "end" to indicate there are no more messages to load after
    this return'''

    check_channel_id(channel_id)

    num_of_messages = len(data['channels'][channel_id - 1]['messages'])

    # Check whether the person inviting (authorised user) is a member of the channel
    user = find_user(token)
    auth_u_id = user['u_id']
    is_member = find_user_in_all(auth_u_id, channel_id)
    if is_member is False:
        raise AccessError(description="You are not a member of this channel")

    if num_of_messages == 0:
        return {
            'messages': [],
            'start': 0,
            'end': -1
        }

    # Check whether starting index for messages is valid
    if start >= num_of_messages:
        raise InputError(description='Invalid starting index for messages')

    if start + 50 >= num_of_messages:
        end = -1
    else:
        end = start + 50

    # Loop through to see which messages the user has reacted
    messages = data['channels'][channel_id - 1]['messages'][start:start + 50]
    for message in messages:
        if user['u_id'] in message['reacts'][0]['u_ids']:
            message['reacts'][0]['is_this_user_reacted'] = True
        else:
            message['reacts'][0]['is_this_user_reacted'] = False

    return {
        'messages': messages,
        'start': start,
        'end': end,
    }

def channel_leave(token, channel_id):
    '''Removes authorised user from channel'''
    # InputError if channel does not exist
    check_channel_id(channel_id)

    user = find_user(token)

    # Remove the user from that channel
    channel = data['channels'][channel_id - 1]
    for member in channel['all_members']:
        if member['u_id'] == user['u_id']:
            channel['all_members'].remove(member)
            if member in channel['owner_members']:
                channel['owner_members'].remove(member)
            return {}
    raise AccessError(description='You are not part of this channel')

def channel_join(token, channel_id):
    '''Adds authorised user as a member of channel'''
    check_channel_id(channel_id)

    user = find_user(token)
    channel = data['channels'][channel_id - 1]
    if not channel['is_public'] and user['permission_id'] == 2:
        raise AccessError(description="You cannot join a private channel")

    # Add the user to all_members
    details_to_add = ['u_id', 'name_first', 'name_last', 'profile_img_url']
    new_channel_member = {}
    for detail in details_to_add:
        new_channel_member[detail] = user[detail]
    channel['all_members'].append(new_channel_member)

    # Check if user is the flockr owner. If so, give user owner permissions.
    if user['permission_id'] == 1:
        channel['owner_members'].append(new_channel_member)

    return {}

def channel_addowner(token, channel_id, u_id):
    '''Authorised user adds a member to owner_members'''
    check_channel_id(channel_id)
    channel = data['channels'][channel_id - 1]
    # Find u_id of authorised user with token
    auth_user = find_user(token)
    auth_u_id = auth_user['u_id']
    user_is_owner = find_user_in_owners(auth_u_id, channel_id)
    if not user_is_owner and auth_user['permission_id'] != 1:
        raise AccessError(description="You do not have permissions to do this")

    in_owners = find_user_in_owners(u_id, channel_id)
    if in_owners is True:
        raise InputError(description="User with user id u_id is already an owner of the channel")

    details_to_add = ['u_id', 'name_first', 'name_last', 'profile_img_url']
    user_to_add = data['users'][u_id - 1]
    new_channel_owner = {}
    for detail in details_to_add:
        new_channel_owner[detail] = user_to_add[detail]
    channel['owner_members'].append(new_channel_owner)

    return {}

def channel_removeowner(token, channel_id, u_id):
    '''Authorised user removes a member from owner_members'''
    check_channel_id(channel_id)

    auth_user = find_user(token)
    if not find_user_in_owners(auth_user['u_id'], channel_id) and auth_user['permission_id'] == 2:
        raise AccessError(description="You do not have permissions to do this")

    # Remove u_id from owner_members list
    channel = data['channels'][channel_id - 1]
    for member in channel['owner_members']:
        if member['u_id'] == u_id:
            channel['owner_members'].remove(member)
            return {}
    raise InputError(description="You do not have permissions to do this")
