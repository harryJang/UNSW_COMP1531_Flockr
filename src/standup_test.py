'''
Import functions and libraries used to test standup functions
'''
from datetime import datetime, timedelta
import time
import pytest
from standup import standup_start, standup_send, standup_active
from message import message_send
from global_vars import data
from other import clear
from channels import channels_create
from error import InputError, AccessError
from helper import LONG_MESSAGE
from fixtures import register_3_users

# Tests for standup_start()
def test_standup_start():
    '''Test if standup_start() returns the correct output when given valid input'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    # Calculate finish time rounded to nearest 10
    finish_time = round((datetime.now() + timedelta(seconds=1)).timestamp() / 10) * 10
    result = standup_start(u_1['token'], 1, 1)
    # Compare function time_finish to correct time_finish rounded to nearest 10
    assert round(result['time_finish'] / 10) * 10 == finish_time
    time.sleep(1)

def test_standup_start_messages():
    '''Test if standup_start() packages message correctly and sends after standup is finished'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    message_send(u_1['token'], 1, 'HI')
    # Start standup and send messages
    standup_start(u_1['token'], 1, 15)
    standup_send(u_1['token'], 1, 'YOYO')
    standup_send(u_1['token'], 1, 'EVERYBODY')
    time.sleep(15)
    # Check if startup_start correctly packages and send messages
    assert data['channels'][0]['messages'][0]['message'] ==\
                                        'bobross00: YOYO\nbobross00: EVERYBODY'

def test_standup_start_invalid_channel_id():
    '''Test if standup_start() returns the correct output when given invalid channel_id'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        # channel_id = 1 does not exist
        assert standup_start(u_1['token'], 1, 1)

def test_standup_start_standup_already_running():
    '''Test if standup_start() returns the correct output when there is a standup
    already running'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    standup_start(u_1['token'], 1, 8)
    with pytest.raises(InputError):
        # A standup has already been started
        assert standup_start(u_1['token'], 1, 1)
    time.sleep(8)

# Tests for standup_active()
def test_standup_active():
    '''Test if standup_active() returns the correct output when a standup
    is already active'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    finish_time = standup_start(u_1['token'], 1, 15)['time_finish']
    # Check standup_active for correct output
    assert standup_active(u_1['token'], 1) == {'is_active': True,
                                               'time_finish': finish_time}
    time.sleep(15)

def test_standup_active_no_active():
    '''Test if standup_active() returns the correct output when there is no
    standup active'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    assert standup_active(u_1['token'], 1) == {'is_active': False,
                                               'time_finish': None}

def test_standup_active_invalid_channel():
    '''Test if standup_active() returns the correct output when given invalid channel_id'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        # channel_id = 1 does not exist
        assert standup_active(u_1['token'], 1)

# Tests for standup_send
def test_standup_send_valid():
    '''Test standup_send for correct output'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    standup_start(u_1['token'], 1, 15)
    assert standup_send(u_1['token'], 1, 'YOYO') == {}
    time.sleep(15)

def test_standup_send_invalid_channel():
    '''Test if standup_send() returns the correct output when given invalid channel_id'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        # channel_id = 1 does not exist
        assert standup_send(u_1['token'], 1, 'YOYO')

def test_standup_send_message_too_long():
    '''Test if standup_send() returns the correct output when message is over 1000
    characters'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    standup_start(u_1['token'], 1, 15)
    with pytest.raises(InputError):
        assert standup_send(u_1['token'], 1, LONG_MESSAGE)
    time.sleep(15)

def test_standup_send_no_standup():
    '''Test if standup_send() returns the correct output when there is no active standup'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    with pytest.raises(InputError):
        standup_send(u_1['token'], 1, 'YOYO')

def test_standup_send_not_member():
    '''Test if standup_send() returns the correct output when authorised user is
    not a member of the channel that standup is in'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'Channel 1', True) # channel_id = 1
    standup_start(u_1['token'], 1, 15)
    with pytest.raises(AccessError):
        standup_send(u_2['token'], 1, 'YOYO')
    time.sleep(15)
