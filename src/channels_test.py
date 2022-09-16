'''
This file includes testing for the channels functions.
'''
# If there's more things to concern, add here !

#####################################Testing Starts Here#####################################

# Testing functions from channels.py which are
# channels_list, channels_listall and channels_create.
import pytest
from other import clear

from channels import channels_list, channels_listall, channels_create

from error import InputError, AccessError
from fixtures import register_3_users
# channels_list
# 1. when the user(calling the function) have joined one public channel (o)
# 2. when the user(calling the function) have joined one private channel (o)
# 3. when the user(calling the function) have joined multiple channels (o)
# 4. when the user(calling the function) have joined part of the channels (o)

def test_channels_list_one_public_channel():
    '''
    Condition : when the user have joined one public channel
    Exp result : Give the details of the channel.
    '''
    clear()
    # contains {user_id = 1 and token}
    registers = register_3_users()
    u_1 = registers[0]

    # contains {channel_id = 1}
    first_channel = channels_create(u_1['token'], "First channel", True)

    # contains list of {channel_id = 1 and name = First channel}
    channels = channels_list(u_1['token'])

    assert len(channels) == 1
    assert channels['channels'][0]['channel_id'] == first_channel['channel_id']
    assert channels['channels'][0]['name'] == "First channel"

def test_channels_list_one_private_channel():
    '''
    Condition : when the user have joined one private channel
    Exp result : Give the details of the channel.
    '''
    clear()
    # contains {user_id = 1 and token = '1'}
    registers = register_3_users()
    u_1 = registers[0]

    # contains {channel_id = 1}
    first_channel = channels_create(u_1['token'], "First channel", False)

    # contains list of {channel_id = 1 and name = First channel}
    channels = channels_list(u_1['token'])

    assert len(channels) == 1
    assert channels['channels'][0]['channel_id'] == first_channel['channel_id']
    assert channels['channels'][0]['name'] == "First channel"

def test_channels_list_multi_channels():
    '''
    Condition : when the user have joined multiple channels mixed with private and public.
    Exp result : Give the details of all channels.
    '''
    clear()
    # contains {user_id = 1 and token = '1'}
    registers = register_3_users()
    u_1 = registers[0]

    # contains {channel_id = 1}
    first_channel = channels_create(u_1['token'], "First channel", False)

    # contains {channel_id = 2}
    second_channel = channels_create(u_1['token'], "Second channel", True)

    # contains {channel_id = 3}
    third_channel = channels_create(u_1['token'], "Third channel", False)

    # contains list of {channel_id = 1 and name = First channel}
    #                  {channel_id = 2 and name = Second channel}
    #                  {channel_id = 3 and name = Third channel}
    channels = channels_list(u_1['token'])

    assert len(channels['channels']) == 3
    assert channels['channels'][0]['channel_id'] == first_channel['channel_id']
    assert channels['channels'][1]['channel_id'] == second_channel['channel_id']
    assert channels['channels'][2]['channel_id'] == third_channel['channel_id']
    assert channels['channels'][0]['name'] == "First channel"
    assert channels['channels'][1]['name'] == "Second channel"
    assert channels['channels'][2]['name'] == "Third channel"

def test_channels_list_partly_joined():
    '''
    Condition : when the user have joined not every channels but part of them.
    Exp result : Give the datails of the channels only user is part of.
    '''
    clear()
    # contains {user_id = 1 and token = '1'}
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]

    # contains {channel_id = 1}
    first_channel = channels_create(u_1['token'], "First channel", False)

    # contains {channel_id = 2}
    second_channel = channels_create(u_2['token'], "Second channel", True)

    # contains {channel_id = 3}
    third_channel = channels_create(u_1['token'], "Third channel", False)

    # contains list of {channel_id = 1 and name = First channel}
    #                  {channel_id = 3 and name = Third channel}
    channels = channels_list(u_1['token'])
    channels_1 = channels_list(u_2['token'])

    assert len(channels['channels']) == 2
    assert len(channels_1['channels']) == 1
    assert channels['channels'][0]['channel_id'] == first_channel['channel_id']
    assert channels['channels'][1]['channel_id'] == third_channel['channel_id']
    assert channels['channels'][0]['name'] == "First channel"
    assert channels['channels'][1]['name'] == "Third channel"
    assert channels_1['channels'][0]['channel_id'] == second_channel['channel_id']
    assert channels_1['channels'][0]['name'] == "Second channel"


# Access error :
# 1. when the token is not valid (o)

def test_channels_list_invalid_token():
    '''
    Condition : when the given token is not valid.
    Exp result : Access Error.
    '''
    clear()
    with pytest.raises(AccessError):
        assert channels_list('Invalid token')


# Edge cases :
# 1. when the user haven't joined any channel (o)

def test_channels_list_no_channel():
    '''
    Condition : when the user haven't joined any channel.
    Exp result : Give None.
    '''
    clear()

    registers = register_3_users()
    u_1 = registers[0]
    channels = channels_list(u_1['token'])

    assert len(channels['channels']) == 0




# channels_listall
# 1. when there is one channel overall (user included) (o)
# 2. when there are multiple channels overall (user included) (o)
# 3. when the user(calling the function) have joined few of existing channels (o)
# 4. when the user(calling the function) haven't joined any channel. (o)

def test_channels_listall_one_channel():
    '''
    Condition : When there exists one channel that user is part of.
    Exp result : Give the detials of the channel.
    '''
    clear()
    # contains {user_id = 1 and token = '1'}
    registers = register_3_users()
    u_1 = registers[0]

    # contains {channel_id = 1}
    first_channel = channels_create(u_1['token'], "First channel", True)

    # contains list of {channel_id = 1 and name = First channel}
    channels = channels_listall(u_1['token'])

    assert len(channels['channels']) == 1
    assert channels['channels'][0]['channel_id'] == first_channel['channel_id']
    assert channels['channels'][0]['name'] == "First channel"

def test_channels_listall_multi_channels():
    '''
    Condition : When there exist multiple channels that user is part of.
    Exp result : Give the detials of all channels.
    '''
    clear()
    # contains {user_id = 1 and token = '1'}
    registers = register_3_users()
    u_1 = registers[0]

    # contains {channel_id = 1}
    first_channel = channels_create(u_1['token'], "First channel", False)

    # contains {channel_id = 2}
    second_channel = channels_create(u_1['token'], "Second channel", True)

    # contains {channel_id = 3}
    third_channel = channels_create(u_1['token'], "Third channel", False)

    # contains list of {channel_id = 1 and name = First channel}
    #                  {channel_id = 2 and name = Second channel}
    #                  {channel_id = 3 and name = Third channel}
    channels = channels_listall(u_1['token'])

    assert len(channels['channels']) == 3
    assert channels['channels'][0]['channel_id'] == first_channel['channel_id']
    assert channels['channels'][1]['channel_id'] == second_channel['channel_id']
    assert channels['channels'][2]['channel_id'] == third_channel['channel_id']
    assert channels['channels'][0]['name'] == "First channel"
    assert channels['channels'][1]['name'] == "Second channel"
    assert channels['channels'][2]['name'] == "Third channel"

def test_channels_listall_user_partly_included():
    '''
    Condition : When there is multiple channels and user is part of few of them.
    Exp result : Give the details of all channels regardless of user's participation.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]

    # contains {channel_id = 1}
    first_channel = channels_create(u_2['token'], "First channel", False)

    # contains {channel_id = 2}
    second_channel = channels_create(u_1['token'], "Second channel", True)

    # contains {channel_id = 3}
    third_channel = channels_create(u_1['token'], "Third channel", False)

    # contains list of {channel_id = 1 and name = First channel}
    #                  {channel_id = 2 and name = Second channel}
    #                  {channel_id = 3 and name = Third channel}
    channels = channels_listall(u_1['token'])

    assert len(channels['channels']) == 3
    assert channels['channels'][0]['channel_id'] == first_channel['channel_id']
    assert channels['channels'][1]['channel_id'] == second_channel['channel_id']
    assert channels['channels'][2]['channel_id'] == third_channel['channel_id']
    assert channels['channels'][0]['name'] == "First channel"
    assert channels['channels'][1]['name'] == "Second channel"
    assert channels['channels'][2]['name'] == "Third channel"


def test_channels_listall_user_not_included():
    '''
    Condition : When there is multiple channels but user is part of none of them.
    Exp result : Give the details of all channels regardless of user's participation.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]

    # contains {channel_id = 1}
    first_channel = channels_create(u_2['token'], "First channel", False)

    # contains {channel_id = 2}
    second_channel = channels_create(u_2['token'], "Second channel", True)

    # contains {channel_id = 3}
    third_channel = channels_create(u_2['token'], "Third channel", False)

    # contains list of {channel_id = 1 and name = First channel}
    #                  {channel_id = 2 and name = Second channel}
    #                  {channel_id = 3 and name = Third channel}
    channels = channels_listall(u_1['token'])

    assert len(channels['channels']) == 3
    assert channels['channels'][0]['channel_id'] == first_channel['channel_id']
    assert channels['channels'][1]['channel_id'] == second_channel['channel_id']
    assert channels['channels'][2]['channel_id'] == third_channel['channel_id']
    assert channels['channels'][0]['name'] == "First channel"
    assert channels['channels'][1]['name'] == "Second channel"
    assert channels['channels'][2]['name'] == "Third channel"


# Access error :
# 1. when the token is not valid (o)

def test_channels_listall_invalid_token():
    '''
    Condition : when the given token is not valid.
    Exp result : Access Error.
    '''
    clear()
    with pytest.raises(AccessError):
        assert channels_listall('Invalid token')


# Edge cases :
# 1. when there's no channel (o)

def test_channels_listall_no_channel():
    '''
    Condition : There's no channel existing.
    Exp result : Give None.
    '''
    clear()
    # will contain None
    registers = register_3_users()
    u_1 = registers[0]
    channels = channels_listall(u_1['token'])

    assert len(channels['channels']) == 0



# channels_create
# 1. token is valid. wanting to make a private channel with a name less than 20 chars (o)
# 2. token is valid. wanting to make a public channel with a name less than 20 chars (o)

def test_channels_create_private():
    '''
    Condition : creating a private channel.
    Exp result : Give proper channel_id.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]

    # contains {channel_id = 1}
    first_channel = channels_create(u_1['token'], "First channel", False)
    assert first_channel['channel_id'] == 1
    #assert(first_channel['is_public'] == False)

def test_channels_create_public():
    '''
    Condition : creating a public channel.
    Exp result : Give proper channel_id.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]

    # contains {channel_id = 1}
    first_channel = channels_create(u_1['token'], "First channel", True)
    assert first_channel['channel_id'] == 1
    #assert(first_channel['is_public'] == True)

# Access error :
# 1. when the token is not valid (o)

def test_channels_create_invalid_token():
    '''
    Condition : when the given token is not valid.
    Exp result : Access Error.
    '''
    clear()
    register_3_users()
    with pytest.raises(AccessError):
        assert channels_create('123', "normal name", True)

# Input error :
# 1. Given name is more than 20 characters long (o)

def test_channels_create_invalid_name_size_exception():
    '''
    Condition : try creating channel with name longer than 20 chars.
    Exp result : Proper InputError
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        assert channels_create(u_1['token'], "Very Very long name over 20 chars", True)

# Edge cases :
# 1. When someone wants to make a channel with a name existing.

def test_channels_create_same_name_again():
    '''
    Condition : try creating channel with same name.
    Exp result : create new channel with same name
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    first_channel = channels_create(u_1['token'], "Same name", True)
    second_channel = channels_create(u_1['token'], "Same name", True)
    assert first_channel['channel_id'] == 1
    assert second_channel['channel_id'] == 2
