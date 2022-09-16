"""
Importing the functions send, remove, and edit from message.py to test
Importing the function register from auth.py to create users
Importing the function create from channels.py to create channels
Importing the function invite from channel.py to invite users
Importing pytest, errors from error.py to test the raise of exceptions
Importing the clear function from helper.py to clear data after each test.
Importing functions from datetime for function sendlater
"""
from datetime import datetime, timedelta
import string
from hypothesis import given, strategies
import pytest
from message import message_send, message_remove, message_edit, message_sendlater, \
                    message_react, message_unreact, message_pin, message_unpin
from auth import auth_logout
from channels import channels_create
from channel import channel_invite, channel_messages, channel_addowner, channel_join
from error import InputError, AccessError
from other import clear
from fixtures import register_3_users

from helper import LONG_MESSAGE

# Tests for send
def test_send_valid():
    """Testing sending valid messages"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    # User 1 sending messages to channel 1
    channels_create(u_1['token'], 'BobAppreciation', True)
    assert message_send(u_1['token'], 1, 'message1') == {'message_id': 1}
    assert message_send(u_1['token'], 1, 'message2') == {'message_id': 2}
    # User 2 sending messages to channel 1
    channel_invite(u_1['token'], 1, 2)
    assert message_send(u_2['token'], 1, 'message3') == {'message_id': 3}
    # User 2 sending message to channel 2
    channels_create(u_2['token'], 'RossAppreciation', True)
    assert message_send(u_2['token'], 2, 'message4') == {'message_id': 4}
    # User 2 sending another message to channel 1
    assert message_send(u_2['token'], 1, 'message5') == {'message_id': 5}

    # Use channel_messages to check whether the messages are correct
    msgs = channel_messages(u_1['token'], 1, 0)['messages']
    assert msgs[0]['message'] == 'message5'
    assert msgs[1]['message'] == 'message3'
    assert msgs[2]['message'] == 'message2'
    assert msgs[3]['message'] == 'message1'
    msgs2 = channel_messages(u_2['token'], 2, 0)['messages']
    assert msgs2[0]['message'] == 'message4'

@given(strategies.text(alphabet=string.printable))
def test_send_intensive(string_msg):
    """Testing sending valid messages using property based tests"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'BobAppreciation', True)
    assert message_send(u_1['token'], 1, string_msg) == {'message_id': 1}
    msgs = channel_messages(u_1['token'], 1, 0)['messages']
    assert msgs[0]['message'] == string_msg

def test_send_invalid_token_exception():
    """Exception: Invalid token"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'BobAppreciation', True)
    auth_logout(u_2['token'])
    with pytest.raises(AccessError):
        assert message_send(u_2['token'], 1, 'Invalid token')

def test_send_len_exception():
    """Exception: Message more than 1000 characters in length"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'BobAppreciation', True)
    channel_invite(u_1['token'], 1, 2)
    with pytest.raises(InputError):
        assert message_send(u_2['token'], 1, LONG_MESSAGE)

def test_send_non_member_exception():
    """Exception: Authorised user is not a member of given channel"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'BobAppreciation', True)
    with pytest.raises(AccessError):
        assert message_send(u_2['token'], 1, 'Okay length message')

# Tests for remove
def test_remove_by_flockr_owner():
    """Testing removal by flockr owner (not channel owner)"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_2['token'], 'BobAppreciation', True)
    message_send(u_2['token'], 1, 'message1')
    assert message_remove(u_1['token'], 1) == {}
    assert len(channel_messages(u_2['token'], 1, 0)['messages']) == 0

def test_remove_by_channel_owner():
    """
    Testing removal by owner of the channel that has the message (not flockr
    owner)
    """
    clear()
    registers = register_3_users()
    u_2 = registers[1]
    u_3 = registers[2]
    channels_create(u_2['token'], 'BobAppreciation', True)
    channel_invite(u_2['token'], 1, 3)
    message_send(u_3['token'], 1, 'message1')
    assert message_remove(u_2['token'], 1) == {}
    assert len(channel_messages(u_2['token'], 1, 0)['messages']) == 0

def test_remove_by_sender():
    """Testing removal by message sender"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'BobAppreciation', True)
    channel_invite(u_1['token'], 1, 2)
    message_send(u_2['token'], 1, 'message1')
    assert message_remove(u_2['token'], 1) == {}
    assert len(channel_messages(u_1['token'], 1, 0)['messages']) == 0

def test_remove_invalid_token_exception():
    """Exception: Invalid token"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'BobAppreciation', True)
    message_send(u_1['token'], 1, 'message1')
    auth_logout(u_2['token'])
    with pytest.raises(AccessError):
        assert message_remove(u_2['token'], 1)

def test_remove_nonexistant_exception():
    """Exception: Message based on given id no longer exists"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'BobAppreciation', True)
    message_send(u_1['token'], 1, 'message1')
    message_remove(u_1['token'], 1)
    with pytest.raises(InputError):
        assert message_remove(u_1['token'], 1)

def test_remove_no_authority_member_exception():
    """
    Exception: Message with given id is not sent by the authorised user
    making the request and the authorised user is not an owner of this channel
    or the flockr
    """
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'BobAppreciation', True)
    message_send(u_1['token'], 1, 'message1')
    channel_invite(u_1['token'], 1, 2)
    with pytest.raises(AccessError):
        assert message_remove(u_2['token'], 1)

def test_remove_no_authority_nonmember_exception():
    """
    Exception: Message with given id is not sent by the authorised user
    making the request and the authorised user is not an owner of this channel
    or the flockr
    """
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'BobAppreciation', True)
    message_send(u_1['token'], 1, 'message1')
    with pytest.raises(AccessError):
        assert message_remove(u_2['token'], 1)

# Tests for message_edit
# Valid cases
def test_edit_single_message_valid():
    """Testing editing messages"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'NERV', True)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there')
    assert message_edit(u_1['token'], 1, 'Peter') == {}
    messages = channel_messages(u_1['token'], 1, 0)['messages']
    assert messages[0]['message'] == 'Peter' # checking 1st message in channel 1

def test_edit_multiple_message_valid():
    """Testing editing multiple messages"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'NERV', True)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there')
    message_send(u_1['token'], 1, 'I gotta go')
    assert message_edit(u_1['token'], 1, 'Peter') == {}
    assert message_edit(u_1['token'], 2, 'Parker') == {}
    messages = channel_messages(u_1['token'], 1, 0)['messages']
    assert messages[0]['message'] == 'Parker' # checking 1st message in channel 1
    assert messages[1]['message'] == 'Peter' # checking 2nd message in channel 1

@given(strategies.text(alphabet=string.printable))
def test_edit_intensive(string_msg):
    """
    Testing editing valid messages using property based tests.
    """
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'BobAppreciation', True)
    message_send(u_1['token'], 1, 'Change me!')
    assert message_edit(u_1['token'], 1, string_msg) == {}
    msgs = channel_messages(u_1['token'], 1, 0)['messages']
    if not string_msg:
        assert msgs == []
    else:
        assert msgs[0]['message'] == string_msg

def test_edit_delete_message_valid():
    """Testing deleting messages"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'NERV', True)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there')
    # User 1 deleting their message
    assert message_edit(u_1['token'], 1, '') == {}
    messages = channel_messages(u_1['token'], 1, 0)['messages']
    assert messages == []

def test_edit_message_channel_owner():
    """Testing editing messages as channel owner"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    u_3 = registers[2]
    channels_create(u_1['token'], 'NERV', True)
    channel_invite(u_1['token'], 1, 2)
    channel_addowner(u_1['token'], 1, 2)
    channel_invite(u_1['token'], 1, 3)
    # Now, Bob Ross is a flockr owner and Jeremy is a channel owner
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there')
    message_send(u_2['token'], 1, 'I gotta go')
    message_send(u_3['token'], 1, 'Okay, bye')
    assert message_edit(u_2['token'], 1, 'Peter') == {}
    assert message_edit(u_2['token'], 2, 'Benjamin') == {}
    assert message_edit(u_2['token'], 3, 'Parker') == {}
    messages = channel_messages(u_1['token'], 1, 0)['messages']
    assert messages[0]['message'] == 'Parker' # checking 1st message in channel 1
    assert messages[1]['message'] == 'Benjamin' # checking 2nd message in channel 1
    assert messages[2]['message'] == 'Peter' # checking 3rd message in channel 1

def test_edit_message_flockr_owner():
    """Testing editing messages as flockr owner"""
    clear()
    # Bob Ross is the flockr owner
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    u_3 = registers[2]
    channels_create(u_2['token'], 'channel1', True) # Jeremy is an owner of channel1
    channels_create(u_3['token'], 'channel2', True) # Gabe is an owner of channel2
    # Bob Ross joins channel2. Since he is a flockr owner, he should
    # have channel owner privileges and be able to edit messages
    channel_join(u_1['token'], 1)
    channel_join(u_1['token'], 2)
    message_send(u_2['token'], 1, 'I gotta go')
    message_send(u_3['token'], 2, 'Okay, bye')

    assert message_edit(u_1['token'], 1, 'Peter') == {}
    assert message_edit(u_1['token'], 2, 'Parker') == {}

    messages_1 = channel_messages(u_1['token'], 1, 0)['messages']
    messages_2 = channel_messages(u_1['token'], 2, 0)['messages']
    assert messages_1[0]['message'] == 'Peter' # checking 1st message in channel 1
    assert messages_2[0]['message'] == 'Parker' # checking 1st message in channel 2

# Error cases
def test_edit_more_than_1000():
    '''Test if someone tries to edit a message past 1000 characters'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'NERV', True) # channel_id = 1
    message_send(u_1['token'], 1, 'Hello there') # message_id = 1
    with pytest.raises(InputError):
        assert message_edit(u_1['token'], 1, LONG_MESSAGE)

# AccessErrors
def test_edit_exception():
    """Exception: Authorised user did not send the message being edited and
       Exception: Authorised user is not an channel or flockr owner"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    u_3 = registers[2]
    channels_create(u_1['token'], 'NERV', True) # channel_id = 1
    channel_invite(u_1['token'], 1, 2)
    channel_invite(u_1['token'], 1, 3)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there') # message_id = 1
    # User 2 sending messages to channel 1
    message_send(u_2['token'], 1, 'Delta') # message_id = 2
    with pytest.raises(AccessError):
        assert message_edit(u_3['token'], 2, 'Changing')

def test_sendlater_valid():
    """Valid case of sending a message later in time"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'BobRoss', True)
    result = message_sendlater(u_1['token'], 1, "goodmessage1", \
                               (datetime.now() + timedelta(seconds=1)).timestamp())
    assert result == {'message_id': 1}
    channel_invite(u_1['token'], 1, 2)
    result = message_sendlater(u_2['token'], 1, "goodmessage2", \
                               (datetime.now() + timedelta(seconds=1)).timestamp())
    assert result == {'message_id': 2}

def test_sendlater_invalid_token():
    """Exception: Given token is invalid"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'BobRoss', True)
    with pytest.raises(AccessError):
        assert message_sendlater("invalidtoken", 1, "goodmessage", \
                                 (datetime.now() + timedelta(seconds=1)).timestamp())

def test_sendlater_exception_invalid_channel():
    """Exception: Given channel id is invalid"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'BobRoss', True)
    with pytest.raises(InputError):
        assert message_sendlater(u_1['token'], 2, "goodmessage", \
                                 (datetime.now() + timedelta(seconds=1)).timestamp())

def test_sendlater_exception_message_too_long():
    """Exception: Message is too long"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'BobRoss', True)
    with pytest.raises(InputError):
        assert message_sendlater(u_1['token'], 1, LONG_MESSAGE, \
                                 (datetime.now() + timedelta(seconds=1)).timestamp())

def test_sendlater_exception_time_in_past():
    """Exception: Specified send time is a time in the past"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'BobRoss', True)
    with pytest.raises(InputError):
        assert message_sendlater(u_1['token'], 1, "goodmessage", \
                                 (datetime.now() + timedelta(seconds=-1)).timestamp())

def test_sendlater_exception_non_member():
    """Exception: Authorised user is not a member of the channel"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'BobRoss', True)
    with pytest.raises(AccessError):
        assert message_sendlater(u_2['token'], 1, "goodmessage", \
                                 (datetime.now() + timedelta(seconds=1)).timestamp())

def test_react_valid():
    """Testing valid reacts"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'BobRoss', True)
    message_send(u_1['token'], 1, 'hehe')
    assert message_react(u_1['token'], 1, 1) == {}
    messages = channel_messages(u_1['token'], 1, 0)['messages']
    assert messages[0]['reacts'][0]['u_ids'] == [1]
    assert messages[0]['reacts'][0]['is_this_user_reacted']
    channel_invite(u_1['token'], 1, 2)
    assert message_react(u_2['token'], 1, 1) == {}
    messages = channel_messages(u_1['token'], 1, 0)['messages']
    assert messages[0]['reacts'][0]['u_ids'] == [1, 2]
    assert messages[0]['reacts'][0]['is_this_user_reacted']

def test_react_exception_invalid_message_id():
    """
    Exception: Given message id is not a valid message within a channel that
    the authorised user has joined
    """
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'BobRoss', True)
    message_send(u_1['token'], 1, 'hehe') # id 1
    with pytest.raises(InputError):
        assert message_react(u_1['token'], 2, 1)

def test_react_exception_invalid_react_id():
    """Exception: Given react id is invalid"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'BobRoss', True)
    message_send(u_1['token'], 1, 'hehe')
    with pytest.raises(InputError):
        assert message_react(u_1['token'], 1, 0)

def test_react_exception_already_reacted():
    """Exception: Authorised user has already reacted to the message"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'BobRoss', True)
    message_send(u_1['token'], 1, 'hehe')
    message_react(u_1['token'], 1, 1)
    with pytest.raises(InputError):
        assert message_react(u_1['token'], 1, 1)

def test_unreact_valid():
    """Testing successful unreacts"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'BobRoss', True)
    message_send(u_1['token'], 1, 'hehe')
    message_react(u_1['token'], 1, 1)
    assert message_unreact(u_1['token'], 1, 1) == {}
    messages = channel_messages(u_1['token'], 1, 0)['messages']
    assert not messages[0]['reacts'][0]['is_this_user_reacted']
    assert messages[0]['reacts'][0]['u_ids'] == []

def test_unreact_exception_invalid_message_id():
    """
    Exception: Given message id is not a valid message within a channel that
    the authorised user has joined
    """
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'BobRoss', True)
    message_send(u_1['token'], 1, 'hehe') # id 1
    with pytest.raises(InputError):
        assert message_unreact(u_1['token'], 2, 1)

def test_unreact_exception_invalid_react_id():
    """Exception: Given react id is invalid"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'BobRoss', True)
    message_send(u_1['token'], 1, 'hehe')
    with pytest.raises(InputError):
        assert message_unreact(u_1['token'], 1, 0)

def test_unreact_exception_not_reacted():
    """Exception: Authorised user has not yet reacted to the message"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'BobRoss', True)
    message_send(u_1['token'], 1, 'hehe')
    with pytest.raises(InputError):
        assert message_unreact(u_1['token'], 1, 1)

# Tests for message_pin
# Valid cases
def test_pin_message_valid():
    """Valid test case for pinning messages"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'NERV', True)
    channel_invite(u_1['token'], 1, 2)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there')
    assert message_pin(u_1['token'], 1) == {}
    messages = channel_messages(u_1['token'], 1, 0)['messages']
    # Checking 1st message in channel 1 is pinned
    assert messages[0]['is_pinned'] is True
    # User 2 sending messages to channel 1
    message_send(u_2['token'], 1, 'Greetings')
    assert message_pin(u_1['token'], 2) == {}
    # Checking 2nd message in channel 1 is pinned
    messages = channel_messages(u_1['token'], 1, 0)['messages']
    assert messages[1]['is_pinned'] is True

def test_pin_promoted_to_owner_members():
    """Checking the case where a newly promoted user can pin messages"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'NERV', True)
    channel_invite(u_1['token'], 1, 2)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there')
    channel_addowner(u_1['token'], 1, 2)
    assert message_pin(u_2['token'], 1) == {}
    messages = channel_messages(u_1['token'], 1, 0)['messages']
    # Checking 1st message in channel 1 is pinned
    assert messages[0]['is_pinned'] is True

def test_pin_flockr_owner():
    """Checking the case where a flockr owner can pin messages"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_2['token'], 'channel1', True)
    # User 1 is a flockr owner and should become a channel owner when they join
    channel_invite(u_2['token'], 1, 1)
    # User 2 sending messages to channel 1
    message_send(u_2['token'], 1, 'Hello there')
    assert message_pin(u_1['token'], 1) == {}
    messages = channel_messages(u_2['token'], 1, 0)['messages']
    # Checking 1st message in channel 1 is pinned
    assert messages[0]['is_pinned'] is True

# Error cases

def test_pin_invalid_token_exception():
    """Invalid token exception"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'NERV', True)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there') # Message id 1
    with pytest.raises(AccessError):
        assert message_pin('INVALIDTOKEN', 1)

# Input Errors
def test_pin_invalid_message_exception():
    """Message id is not a valid message"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'NERV', True)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there') # Message id 1
    with pytest.raises(InputError):
        assert message_pin(u_1['token'], 2)

def test_pin_message_already_pinned_exception():
    """Given message of message_id is already pinned"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'NERV', True)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there') # Message id 1
    assert message_pin(u_1['token'], 1) == {}
    with pytest.raises(InputError):
        assert message_pin(u_1['token'], 1)

# Access Errors
def test_pin_not_part_of_channel_exception():
    """Authorised user is not a member of the channel that the message is in"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'NERV', True)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there') # Message id 1
    with pytest.raises(AccessError):
        assert message_pin(u_2['token'], 1)

def test_pin_not_owner_of_channel():
    """Authorised user is not an owner of the channel"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'NERV', True)
    # Adding User to channel 1
    channel_invite(u_1['token'], 1, 2)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there') # Message id 1
    with pytest.raises(AccessError):
        assert message_pin(u_2['token'], 1)

# Tests for message_unpin
# Valid cases
def test_unpin_message_valid():
    """Valid test case for unpinning messages"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'NERV', True)
    channel_invite(u_1['token'], 1, 2)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there')
    message_pin(u_1['token'], 1)
    # User 2 sending messages to channel 1
    message_send(u_2['token'], 1, 'Greetings')
    message_pin(u_1['token'], 2)
    # User 1 unpins both messages
    assert message_unpin(u_1['token'], 1) == {}
    assert message_unpin(u_1['token'], 2) == {}
    messages = channel_messages(u_1['token'], 1, 0)['messages']
    assert not messages[0]['is_pinned']
    assert not messages[1]['is_pinned']

def test_unpin_promoted_to_owner_members():
    """Checking the case where a newly promoted user can unpin messages"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'NERV', True)
    channel_invite(u_1['token'], 1, 2)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there')
    channel_addowner(u_1['token'], 1, 2)
    message_pin(u_1['token'], 1)
    assert message_unpin(u_2['token'], 1) == {}
    messages = channel_messages(u_1['token'], 1, 0)['messages']
    # Checking 1st message in channel 1 is pinned
    assert messages[0]['is_pinned'] is False

def test_unpin_flockr_owner():
    """Checking the case where a flockr owner can unpin messages"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_2['token'], 'channel1', True)
    # User 1 is a flockr owner and should become a channel owner when they join
    channel_invite(u_2['token'], 1, 1)
    # User 2 sending messages to channel 1
    message_send(u_2['token'], 1, 'Hello there')
    message_pin(u_2['token'], 1)
    assert message_unpin(u_1['token'], 1) == {}
    messages = channel_messages(u_2['token'], 1, 0)['messages']
    # Checking 1st message in channel 1 is pinned
    assert messages[0]['is_pinned'] is False

# Error cases

def test_unpin_invalid_token_exception():
    """Invalid token exception"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'NERV', True)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there') # Message id 1
    message_pin(u_1['token'], 1)
    with pytest.raises(AccessError):
        assert message_unpin('INVALIDTOKEN', 1)

# Input Errors
def test_unpin_invalid_message_exception():
    """Message id is not a valid message"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'NERV', True)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there') # Message id 1
    with pytest.raises(InputError):
        assert message_unpin(u_1['token'], 2)

def test_unpin_message_already_pinned_exception():
    """Given message of message_id is already unpinned"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'NERV', True)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there') # Message id 1
    message_pin(u_1['token'], 1)
    assert message_unpin(u_1['token'], 1) == {}
    with pytest.raises(InputError):
        assert message_unpin(u_1['token'], 1)

# Access Errors
def test_unpin_not_part_of_channel_exception():
    """Authorised user is not a member of the channel that the message is in"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'NERV', True)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there') # Message id 1
    message_pin(u_1['token'], 1)
    with pytest.raises(AccessError):
        assert message_unpin(u_2['token'], 1)

def test_unpin_not_owner_of_channel():
    """Authorised user is not an owner of the channel"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'NERV', True)
    # Adding User to channel 1
    channel_invite(u_1['token'], 1, 2)
    # User 1 sending messages to channel 1
    message_send(u_1['token'], 1, 'Hello there') # Message id 1
    message_pin(u_1['token'], 1)
    with pytest.raises(AccessError):
        assert message_unpin(u_2['token'], 1)
