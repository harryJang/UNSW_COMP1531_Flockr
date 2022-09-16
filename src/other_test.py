'''
Importing pytest for testing
Importing fucntion users_all, admin_userpermission_change and search for testing
Importing data to find messages to assert search output
Importing clear function to clear data before each test
Importing auth_register to add users to data
Importing channels_create to create channels
Importing message_send to send message to test search
Import AccessError and InputError to check exceptions
'''
import pytest
from other import users_all, admin_userpermission_change, search, clear
from auth import auth_login, auth_logout
from channels import channels_create
from channel import channel_join
from message import message_send
from error import InputError, AccessError
from fixtures import register_3_users

# Tests for users_all

def test_users_all():
    '''Test users_all for correct output'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    assert users_all(u_1['token']) == \
    {'users': [{'u_id': 1, 'email': 'good_email1@gmail.com', 'name_first': 'Bob',
                'name_last': 'Ross', 'handle_str': 'bobross00'},\
               {'u_id': 2, 'email': 'good_email2@hotMAIL.com', 'name_first': 'Lob',
                'name_last': 'Moss', 'handle_str': 'lobmoss00'}, \
               {'u_id': 3, 'email': 'good_email3@outlook.com', 'name_first': 'Bob',
                'name_last': 'Ross', 'handle_str': 'bobross01'}]}

def test_users_all_invalid_token():
    '''Test for empty output when users_all() is given an invalid token'''
    clear()
    with pytest.raises(AccessError):
        assert users_all('Invalid')

# Tests for admin_userpermission_change

# Valid cases
def test_admin_userpermission_change():
    '''Test admin_userpermission_change for correct output'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    auth_logout(u_2['token'])
    # Give u_id = 2 owner permission
    assert admin_userpermission_change(u_1['token'], 2, 1) == {}
    # Remove u_id = 1 owner permission
    u_2 = auth_login('good_email2@hotMAIL.com', '123456')
    assert admin_userpermission_change(u_2['token'], 1, 2) == {}

# Input errors
def test_admin_userpermission_change_invalid_uid():
    '''Test if admin_userpermission_change correctly raises InputError given
    invalid u_id'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        assert admin_userpermission_change(u_1['token'], 4, 1)

def test_admin_userpermission_change_invalid_permission():
    '''Test if admin_userpermission_change correctly raises InputError given
    invalid permission_id'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        assert admin_userpermission_change(u_1['token'], 2, 3)

# Access errors
def test_admin_userpermission_change_auth_not_owner():
    '''Test if admin_userpermission_change correctly raises AccessError if authorised
    user is not an owner'''
    clear()
    registers = register_3_users()
    u_2 = registers[1]
    with pytest.raises(AccessError):
        assert admin_userpermission_change(u_2['token'], 1, 2)

# Tests for search

def test_search_one_message():
    '''Test if search returns correct output for one message'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', True)
    message_send(u_1['token'], 1, 'Hello world!')
    # assert message with the ouput from search()
    assert search(u_1['token'], 'Hello')['messages'][0]['message'] == 'Hello world!'

def test_search_different_channels():
    '''Test if search returns correct output for messages in different channels'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    message_send(u_1['token'], 1, 'Hello world!')
    channels_create(u_1['token'], 'Channel 2', True) # channel_id = 2
    message_send(u_1['token'], 2, 'Hello!!')
    assert search(u_1['token'], 'Hello')['messages'][0]['message'] == 'Hello world!'
    assert search(u_1['token'], 'Hello')['messages'][1]['message'] == 'Hello!!'

def test_search_same_message_diff_users():
    '''Test if search returns correct output if different users send the same message'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    channel_join(u_2['token'], 1)
    message_send(u_1['token'], 1, 'Hello world!')
    message_send(u_2['token'], 1, 'Hello world!')
    assert search(u_1['token'], 'Hello')['messages'][0]['message'] == 'Hello world!'
    assert search(u_1['token'], 'Hello')['messages'][1]['message'] == 'Hello world!'

def test_search_multiple_messages():
    '''Test if search returns correct output for multiple messages'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    message_send(u_1['token'], 1, 'Hello world!') # message_id = 1
    message_send(u_1['token'], 1, 'Hello!!')
    message_send(u_1['token'], 1, 'HELLO???????')
    assert search(u_1['token'], 'Hello')['messages'][0]['message'] == 'HELLO???????'
    assert search(u_1['token'], 'Hello')['messages'][1]['message'] == 'Hello!!'
    assert search(u_1['token'], 'Hello')['messages'][2]['message'] == 'Hello world!'

def test_search_same_message():
    '''Test if search returns correct output if user sends the same message'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    message_send(u_1['token'], 1, 'Hello world!')
    message_send(u_1['token'], 1, 'Hello world!')
    assert search(u_1['token'], 'Hello')['messages'][0]['message'] == 'Hello world!'
    assert search(u_1['token'], 'Hello')['messages'][1]['message'] == 'Hello world!'

def test_search_private():
    '''Test if search returns correct output for messages sent in private channels'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', False) # channel_id = 1
    message_send(u_1['token'], 1, 'Hello world!')
    assert search(u_1['token'], 'Hello')['messages'][0]['message'] == 'Hello world!'

def test_search_different_case():
    '''Test if search returns correct output when query string is different case
    to matching messages'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    message_send(u_1['token'], 1, 'hello!')
    message_send(u_1['token'], 1, 'HELLO!')
    message_send(u_1['token'], 1, 'hELLo!')
    assert search(u_1['token'], 'Hello')['messages'][0]['message'] == 'hELLo!'
    assert search(u_1['token'], 'Hello')['messages'][1]['message'] == 'HELLO!'
    assert search(u_1['token'], 'Hello')['messages'][2]['message'] == 'hello!'

def test_search_no_match():
    '''Test if search returns correct output when query string does not match any messages'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    message_send(u_1['token'], 1, 'Hello world!') # message_id = 1
    assert search(u_1['token'], 'YOYO') == {'messages': []}

def test_seach_match_not_in_joined_channel():
    '''Test if search returns correct output when query string matches message
    but user is not in that channel'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'Channel 1', False) # channel_id = 1
    message_send(u_1['token'], 1, 'Hello world!') # message_id = 1
    # Find message dictionary to assert with the ouput from search()
    assert search(u_2['token'], 'Hello') == {'messages': [],}
