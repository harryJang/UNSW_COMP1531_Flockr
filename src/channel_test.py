'''
Importing channel functions to test them
Importing channels and auth functions to help with making tests
Importing data structure for users, channels etc.
Importing helper functions from helper.py to streamline user finding process
'''
import pytest
from channel import channel_invite, channel_details, channel_messages,\
channel_leave, channel_join, channel_addowner, channel_removeowner
from channels import channels_create, channels_list
from message import message_send
from other import clear
from error import InputError, AccessError
from helper import find_user_in_owners
from fixtures import register_3_users

# Since only a simple version of token is required for iteration 1,
# token will simply be a string of the u_id
# Note that is_public = True and is_private = False

# Tests for channel_invite

# Valid cases
def test_channel_invite_valid_input():
    '''Testing valid case for channel_invite'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    assert channel_invite(u_1['token'], 1, 2) == {}

def test_channel_invite_flockr_owner():
    '''Testing case for inviting a flockr owner'''
    clear()
    # Registering two users, and making Bob Ross the flockr owner
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    channels_create(u_2['token'], "Channel2", True) # channel_id = 2
    assert channel_invite(u_2['token'], 2, 1) == {} # Adding Bob Ross to this channel

    # Check that there are now two owners in this channel, since
    # when a flockr owner joins a channel, they will be given channel owner permissions
    assert find_user_in_owners(1, 2)
    assert find_user_in_owners(2, 2)

# Error cases
def test_channel_invite_self():
    '''Testing inviting yourself'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    with pytest.raises(InputError):
        # Add asserts for cases where it would raise an exception
        assert channel_invite(u_1['token'], 1, 1)

def test_channel_invite_user_already_in_channel():
    '''Testing inviting people already in the channel'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    # Adding James May to this channel
    assert channel_invite(u_1['token'], 1, 2) == {}
    # Re-inviting James May.
    with pytest.raises(InputError):
        # Add asserts for cases where it would raise an exception
        assert channel_invite(u_1['token'], 1, 2)

# Input errors
def test_channel_invite_invalid_channel_exception():
    '''Testing invalid channel exception case'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    with pytest.raises(InputError):
        # Add asserts for cases where it would raise an exception
        assert channel_invite(u_1['token'], 3, 1)

def test_channel_invite_invalid_uid_exception():
    '''Testing invalid u_id exception case'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    with pytest.raises(InputError):
        # Add asserts for cases where it would raise an exception
        assert channel_invite(u_1['token'], 1, 4)

# Access errors
def test_channel_invite_authorised_exception():
    '''Testing authorised user exception case'''
    # Checking if the authorised user is part of the channel
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1

    with pytest.raises(AccessError):
        # Add asserts for cases where it would raise an exception
        assert channel_invite(u_2['token'], 1, 3)

def test_channel_invite_invalid_token_exception():
    '''Testing authorised user exception case'''
    # Checking if the authorised user is part of the channel
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    with pytest.raises(AccessError):
        # Add asserts for cases where it would raise an exception
        assert channel_invite("invalidtoken", 1, 2)

# Tests for channel_details

# Valid cases
def test_channel_details_valid_input():
    '''Testing valid input case'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    channel_invite(u_1['token'], 1, 2)

    assert channel_details(u_1['token'], 1) == \
    {'name':"BobRoss", 'owner_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''}], 'all_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''},\
    {'u_id':2, 'name_first':"Lob", 'name_last':"Moss", "profile_img_url":''}]}

def test_channel_details_updating_1():
    '''Testing if channel details updates'''
    # Test that details are updated when an all_member is removed
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    channel_invite(u_1['token'], 1, 2)

    assert channel_details(u_1['token'], 1) == \
    {'name':"BobRoss", 'owner_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''}], 'all_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''}, \
    {'u_id':2, 'name_first':"Lob", 'name_last':"Moss", "profile_img_url":''}]}

    channel_leave(u_2['token'], 1)

    assert channel_details(u_1['token'], 1) == \
    {'name':"BobRoss", 'owner_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''}], 'all_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''}]}

def test_channel_details_updating_2():
    '''Testing if channel details updates'''
    # Test that details are updated when an owner_member is removed
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    channel_invite(u_1['token'], 1, 2)

    assert channel_details(u_1['token'], 1) == \
    {'name':"BobRoss", 'owner_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''}], 'all_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''},\
    {'u_id':2, 'name_first':"Lob", 'name_last':"Moss", "profile_img_url":''}]}

    channel_leave(u_1['token'], 1)

    assert channel_details(u_2['token'], 1) == \
    {'name':"BobRoss", 'owner_members':[],
     'all_members':[{'u_id':2, 'name_first':"Lob", 'name_last':"Moss", "profile_img_url":''}]}

def test_channel_details_no_owners():
    '''Testing what happens if there are no owners'''
    # Test if a user's owner permissions are removed but they are not removed
    # from the channel itself
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    channel_invite(u_1['token'], 1, 2)
    channel_removeowner(u_1['token'], 1, 1)

    assert channel_details(u_1['token'], 1) == \
    {'name':"BobRoss", 'owner_members':[], 'all_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''},\
    {'u_id':2, 'name_first':"Lob", 'name_last':"Moss", "profile_img_url":''}]}

# Error cases
# Input errors
def test_channel_details_invalid_channel_exception():
    '''Testing invalid channel exception'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    with pytest.raises(InputError):
        # Add asserts for cases where it would raise an exception
        assert channel_details(u_1['token'], 2)

# Access errors
def test_channel_details_not_member_exception():
    '''Testing invalid member exception'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    with pytest.raises(AccessError):
        # Add asserts for cases where it would raise an exception
        assert channel_details(u_2['token'], 1)

def test_channel_details_invalid_token_exception():
    '''Testing authorised user exception case'''
    # Checking if the authorised user is part of the channel
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1

    with pytest.raises(AccessError):
        # Add asserts for cases where it would raise an exception
        assert channel_details("invalidtoken", 1)

# Tests for channel_messages

# Valid cases
def test_channel_messages_empty():
    '''Testing empty messages'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    assert channel_messages(u_1['token'], 1, 0) == {'messages':[], 'start': 0, 'end': -1}

def test_channel_messages_standard():
    '''Testing a standard message case'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    channel_invite(u_1['token'], 1, 2)
    message_send(u_1['token'], 1, "Hello there")
    message_send(u_2['token'], 1, "What's up")

    messages_data = channel_messages(u_1['token'], 1, 0)

    assert messages_data['messages'][0]['message'] == "What's up"
    assert messages_data['messages'][1]['message'] == "Hello there"
    assert messages_data['start'] == 0
    assert messages_data['end'] == -1

def test_channel_messages_lots_of_messages():
    '''Testing many messages and if it only returns first 50'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "Channel1", True) # channel_id = 1
    for increment in range(100):
        message_send(u_1['token'], 1, "I AM SPAMMING")

    messages_data = channel_messages(u_1['token'], 1, 0)
    for increment in range(50):
        assert messages_data['messages'][increment]['message'] == "I AM SPAMMING"

    assert messages_data['start'] == 0
    assert messages_data['end'] == 50


# Error cases
# Input errors
def test_channel_messages_invalid_channel_exception():
    '''Testing invalid channel exception'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    with pytest.raises(InputError):
        # Add asserts for all cases where it would raise an exception
        assert channel_messages(u_1['token'], 2, 0)

def test_channel_messages_start_greater_than_total_exception():
    '''This is supposed to raise an exception. I have already tested before
    and it does. But given the nature of this iteration (lack of way to
    add messages), we currently cannot differentiate between the empty message
    case and the invalid start index case'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    message_send(u_1['token'], 1, "Hello there")

    with pytest.raises(InputError):
        # Add asserts for all cases where it would raise an exception
        assert channel_messages(u_1['token'], 1, 5)

# Access errors
def test_channel_messages_not_member_exception():
    '''Testing invalid member exception'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1
    with pytest.raises(AccessError):
        # Add asserts for all cases where it would raise an exception
        assert channel_messages(u_2['token'], 1, 0)

def test_channel_messages_invalid_token_exception():
    '''Testing authorised user exception case'''
    # Checking if the authorised user is part of the channel
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], "BobRoss", True) # channel_id = 1

    with pytest.raises(AccessError):
        # Add asserts for cases where it would raise an exception
        assert channel_messages("invalidtoken", 1, 0)

# Tests for channel_leave

# Valid cases
def test_channel_leave_valid():
    '''Test channel_leave for correct return'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'valid_channel', True) # channel_id = 1
    channel_invite(u_1['token'], 1, 2)
    assert channel_leave(u_2['token'], 1) == {}

    # Check that user now is part of no channels
    channels = channels_list(u_2['token'])
    assert channels['channels'] == []

def test_channel_leave_owner():
    '''Test channel_leave for correct return when owner leaves channel'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'valid_channel', True) # channel_id = 1
    assert channel_leave(u_1['token'], 1) == {}
    # Check that user now is part of no channels
    channels = channels_list(u_1['token'])
    assert channels['channels'] == []

# Input error
def test_channel_leave_input_error():
    '''Check that channel_leave raises InputError when given invalid channel_id'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        assert channel_leave(u_1['token'], 1)

# Access error
def test_channel_leave_access_error():
    '''Check that channel_leave raises AccessError when user is not a member'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'valid_channel', True)
    with pytest.raises(AccessError):
        # User with token u_2['token'] is not a member of channel
        assert channel_leave(u_2['token'], 1)

# Tests for channel_join

# Valid cases
def test_channel_join():
    '''Test that channel_join returns correct output'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'valid_channel', True) # channel_id = 1
    assert channel_join(u_2['token'], 1) == {}

    # Test if user has successfully joined channel_id = 1 by using channels_list
    channels = channels_list(u_2['token'])
    assert channels['channels'][0]['channel_id'] == 1

def test_channel_join_owner_private():
    '''Test flockr owner joining private channel'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_2['token'], 'valid_channel', False) # channel_id = 1
    assert channel_join(u_1['token'], 1) == {}

# Input error
def test_channel_join_input_error():
    '''Check that channel_join raises InputError channel_id is invalid'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        # Channel with id = 1 has not be created
        assert channel_join(u_1['token'], 1)

# Access error
def test_channel_join_access_error():
    '''Check that channel_join raises AccessError when joining private channel'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    # Make only token u_1['token'] an owner
    channels_create(u_1['token'], 'valid_channel', False) # Private channel

    # User that is not owner tries to join private channel
    with pytest.raises(AccessError):
        assert channel_join(u_2['token'], 1)

# Tests for channel_addowner

# Valid case
def test_channel_addowner():
    '''Check that channel_addowner returns correct output'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'valid_channel', True) # channel_id = 1
    channel_invite(u_1['token'], 1, 2)
    assert channel_addowner(u_1['token'], 1, 2) == {}

# Input errors
def test_channel_addowner_invalid_channel():
    '''Check that channel_addowner raises InputError when given invalid channel_id'''
    clear()
    # Create users to make sure error is caused by channel_addowner()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        # Invalid channel id
        assert channel_addowner(u_1['token'], 10, 2)

def test_channel_addowner_repeat():
    '''Check that channel_addowner raises InputError if u_id is already an owner'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'valid_channel', True)
    channel_invite(u_1['token'], 1, 2)
    channel_addowner(u_1['token'], 1, 2)

    with pytest.raises(InputError):
        # User is already an owner in this channel
        assert channel_addowner(u_1['token'], 1, 2)

# Access error
def test_channel_addowner_not_owner():
    '''Check that channel_addowner raises AccessError if authorised user does not
    have permission to add owner'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_3 = registers[2]
    channels_create(u_1['token'], 'valid_channel', True)
    channel_invite(u_1['token'], 1, 2)
    channel_invite(u_1['token'], 1, 3)

    with pytest.raises(AccessError):
        # User with token 'invalid' is not a owner of channel or owner of flockr
        assert channel_addowner(u_3['token'], 1, 2)

# Tests for channel_removeowner

# Valid cases
def test_channel_removeowner():
    '''Test channel_removeowner for correct output'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'valid_channel', True)
    channel_invite(u_1['token'], 1, 2)
    channel_addowner(u_1['token'], 1, 2)
    assert channel_removeowner(u_1['token'], 1, 2) == {}

# Input errors
def test_channel_removeowner_invalid_channel():
    '''Check that channel_removeowner raises InputError when given invalid channel_id'''
    clear()
    # Create user to make sure error is caused by channel_removeowner()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        # Invalid channel id
        assert channel_removeowner(u_1['token'], 1, 2)

def test_channel_removeowner_not_owner():
    '''Check that channel_removeowner raises InputError if u_id is not an owner
    of the channel'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'valid_channel', True)

    with pytest.raises(InputError):
        # User is not an owner of this channel
        assert channel_removeowner(u_1['token'], 1, 2)

# Access error
def test_channel_no_auth_removeowner():
    '''Check that channel_removeowner raises AccessError if authorised user does
    not have permission to remove owner'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'valid_channel', True)
    channel_invite(u_1['token'], 1, 2)

    with pytest.raises(AccessError):
        # User with token u_2['token'] is not a owner of channel or owner of flockr
        assert channel_removeowner(u_2['token'], 1, 1)
