"""
Imported modules to get URL of server
"""
from datetime import datetime, timedelta
import time
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import pytest
import requests
import jwt
from helper import encrypted, find_user_in_owners, LONG_MESSAGE
from global_vars import SECRET

# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture
def url():
    """
    Get the URL of the server
    """
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

good_reg_1 = {"email": "good_email1@gmail.com", "password":"a1!@#~", \
              "name_first": "Bob", "name_last":"Ross"}
good_reg_2 = {"email": "good_email2@gmail.com", "password":"aaaaaa", \
              "name_first": "Bob", "name_last":"Ross"}
good_reg_3 = {"email": "good_email3@gmail.com", "password":"abc123", \
              "name_first": "Bob", "name_last":"Ross"}

# auth tests
def test_login_valid(url):
    """Tests for valid logins"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_3)
    u_3 = response.json()
    requests.post(url + 'auth/logout', json={'token': u_1['token']})
    requests.post(url + 'auth/logout', json={'token': u_2['token']})
    requests.post(url + 'auth/logout', json={'token': u_3['token']})
    response = requests.post(url + 'auth/login', json={'email': 'good_email1@gmail.com',
                                                         'password': 'a1!@#~'})
    assert response.json() == u_1
    response = requests.post(url + 'auth/login', json={'email': 'good_email2@gmail.com',
                                                         'password': 'aaaaaa'})
    assert response.json() == u_2
    response = requests.post(url + 'auth/login', json={'email': 'good_email3@gmail.com',
                                                         'password': 'abc123'})
    assert response.json() == u_3

def test_login_email_exception1(url):
    """Bad email: No @ sign"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/login', json={'email': 'bad_email.com',
                                                         'password': '111111'})
    assert response.json()['code'] == 400

def test_login_email_exception2(url):
    """Bad email: No full stops after @"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/login', json={'email': 'bad_email@nofullstops',
                                                         'password': '111111'})
    assert response.json()['code'] == 400

def test_login_email_exception3(url):
    """Bad email: Capital letters before @"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/login', json={'email': 'BAD_EMAIL@gmail.com',
                                                         'password': '111111'})
    assert response.json()['code'] == 400

def test_login_non_existing_email_exception(url):
    """Non existing account with the given email"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'auth/logout', params={'token': u_1['token']})
    response = requests.post(url + 'auth/login', json={'email': 'good_email1@gmail.com',
                                                         'password': 'wrongpass'})
    assert response.json()['code'] == 400

def test_login_password_exception(url):
    """Existing account/email but wrong password"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'auth/logout', params={'token': u_1['token']})
    response = requests.post(url + 'auth/login', json={'email': 'non_existant@gmail.com',
                                                         'password': '111111'})
    assert response.json()['code'] == 400

def test_logout_valid(url):
    """Tests for valid logouts"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/logout', json={'token': u_1['token']})
    payload = response.json()
    assert payload['is_success'] is True

def test_auth_logout_exception(url):
    """Invalid token/logout"""
    requests.delete(url + 'clear')
    requests.post(url + 'auth/register', json=good_reg_1)
    response = requests.post(url + 'auth/logout', json={'token': 'invalid'})
    assert response.json()['code'] == 400

def test_register_valid(url):
    """Testing valid registers"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    assert u_1['u_id'] == 1
    assert jwt.encode({'u_id': 1}, SECRET, algorithm='HS256').decode('utf-8') == u_1['token']
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    assert u_2['u_id'] == 2
    assert jwt.encode({'u_id': 2}, SECRET, algorithm='HS256').decode('utf-8') == u_2['token']

def test_register_email_exception1(url):
    """Bad email: No @ sign"""
    requests.delete(url + 'clear')
    info = {"email": "bad_email.com", "password":"a1!@#~", \
            "name_first": "Bob", "name_last":"Ross"}
    response = requests.post(url + 'auth/register', json=info)
    assert response.json()['code'] == 400

def test_register_email_exception2(url):
    """Bad email: No full stops after @"""
    requests.delete(url + 'clear')
    info = {"email": "bad_email@nofullstops", "password":"a1!@#~", \
            "name_first": "Bob", "name_last":"Ross"}
    response = requests.post(url + 'auth/register', json=info)
    assert response.json()['code'] == 400

def test_register_email_exception3(url):
    """Bad email: Capital letters before @"""
    requests.delete(url + 'clear')
    info = {"email": "BAD_EMAIL@gmail.com", "password":"a1!@#~", \
            "name_first": "Bob", "name_last":"Ross"}
    response = requests.post(url + 'auth/register', json=info)
    assert response.json()['code'] == 400

def test_register_existing_email_exception(url):
    """Trying to register with an email that already exists in the database"""
    requests.delete(url + 'clear')
    requests.post(url + 'auth/register', json=good_reg_1)
    response = requests.post(url + 'auth/register', json=good_reg_1)
    assert response.json()['code'] == 400

def test_auth_register_password_len_exception(url):
    """Password too short"""
    requests.delete(url + 'clear')
    info = {"email": "good_email1@gmail.com", "password":"short", \
            "name_first": "Bob", "name_last":"Ross"}
    response = requests.post(url + 'auth/register', json=info)
    assert response.json()['code'] == 400

def test_auth_register_first_name_exception1(url):
    """First name too short"""
    requests.delete(url + 'clear')
    info = {"email": "good_email1@gmail.com", "password":"aaaaaa", \
            "name_first": "", "name_last":"Ross"}
    response = requests.post(url + 'auth/register', json=info)
    assert response.json()['code'] == 400

def test_auth_register_first_name_exception2(url):
    """First name too long"""
    requests.delete(url + 'clear')
    info = {"email": "good_email1@gmail.com", "password":"aaaaaa", \
            "name_first": "Abcdefghijklmnopqrstuvwxyz1234567891234567891231231", \
            "name_last":"Ross"}
    response = requests.post(url + 'auth/register', json=info)
    assert response.json()['code'] == 400

def test_auth_register_last_name_exception1(url):
    """Last name too short"""
    requests.delete(url + 'clear')
    info = {"email": "good_email1@gmail.com", "password":"aaaaaa", \
            "name_first": "Bob", "name_last":""}
    response = requests.post(url + 'auth/register', json=info)
    assert response.json()['code'] == 400

def test_auth_register_last_name_exception2(url):
    """First name too long"""
    requests.delete(url + 'clear')
    info = {"email": "good_email1@gmail.com", "password":"aaaaaa", \
            "name_first": "Bob", \
            "name_last":"Abcdefghijklmnopqrstuvwxyz1223334444555556666661111"}
    response = requests.post(url + 'auth/register', json=info)
    assert response.json()['code'] == 400

def test_auth_passwordreset_request_valid(url):
    """Valid password reset request"""
    requests.delete(url + 'clear')
    requests.post(url + 'auth/register', json=good_reg_1)
    responese = requests.post(url + 'auth/passwordreset/request', json={'email':good_reg_1['email']})
    assert responese.json() == {}

# channels_list
def test_channels_list(url):
    '''
    A simple test to check channels/list
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()

    response = requests.post(url + 'channels/create', json={'token':u_1['token'],
                                                            'name':'First channel',
                                                            'is_public':True})
    channels_id_1 = response.json()

    response = requests.post(url + 'channels/create', json={'token':u_2['token'],
                                                            'name':'Second channel',
                                                            'is_public':True})
    channels_id_2 = response.json()

    response = requests.post(url + 'channels/create', json={'token':u_1['token'],
                                                            'name':'Third channel',
                                                            'is_public':True})
    channels_id_3 = response.json()

    response = requests.get(f'{url}channels/list', params={'token':u_1['token']})
    channels = response.json()

    response = requests.get(url + 'channels/list', params={'token':u_2['token']})
    channels_1 = response.json()

    assert len(channels['channels']) == 2
    assert len(channels_1['channels']) == 1
    assert channels['channels'][0]['channel_id'] == channels_id_1['channel_id']
    assert channels['channels'][1]['channel_id'] == channels_id_3['channel_id']
    assert channels['channels'][0]['name'] == "First channel"
    assert channels['channels'][1]['name'] == "Third channel"
    assert channels_1['channels'][0]['channel_id'] == channels_id_2['channel_id']
    assert channels_1['channels'][0]['name'] == "Second channel"

def test_channels_list_exception_invalid_token(url):
    '''
    A simple test to check exception case of channels_list
    '''
    requests.delete(url + 'clear')

    response = requests.get(f'{url}channels/list', json={'token':'invalid_token'})
    assert response.json()['code'] == 400

# channels_listall
def test_channels_listall(url):
    '''
    A simple test to check channels/listall
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()

    response = requests.post(url + 'channels/create', json={'token':u_1['token'],
                                                            'name':'First channel',
                                                            'is_public':True})
    channels_id_1 = response.json()

    response = requests.post(url + 'channels/create', json={'token':u_2['token'],
                                                            'name':'Second channel',
                                                            'is_public':True})
    channels_id_2 = response.json()

    response = requests.post(url + 'channels/create', json={'token':u_1['token'],
                                                            'name':'Third channel',
                                                            'is_public':True})
    channels_id_3 = response.json()

    response = requests.get(url + 'channels/listall', params={'token':u_1['token']})
    channels = response.json()

    assert len(channels['channels']) == 3
    assert channels['channels'][0]['channel_id'] == channels_id_1['channel_id']
    assert channels['channels'][1]['channel_id'] == channels_id_2['channel_id']
    assert channels['channels'][2]['channel_id'] == channels_id_3['channel_id']
    assert channels['channels'][0]['name'] == "First channel"
    assert channels['channels'][1]['name'] == "Second channel"
    assert channels['channels'][2]['name'] == "Third channel"

def test_channels_listall_exception_invalid_token(url):
    '''
    A simple test to check exception case of channels_listall
    '''
    requests.delete(url + 'clear')

    response = requests.get(f'{url}channels/listall', json={'token':'invalid_token'})
    assert response.json()['code'] == 400

# channels_create
def test_channels_create(url):
    '''
    A simple test to check channels/create
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    requests.post(url + 'channels/create', json={'token':u_1['token'],
                                                 'name':'First channel',
                                                 'is_public':True})
    response = requests.get(url + 'channels/listall', params={'token':u_1['token']})
    channels = response.json()

    assert len(channels['channels']) == 1
    assert channels['channels'][0]['channel_id'] == 1
    assert channels['channels'][0]['name'] == "First channel"

def test_channels_create_exception_invalid_token(url):
    '''
    A simple test to check exception case (invalid token) of channels_create
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'channels/create', json={'token':'invalid_token',
                                                            'name':'First channel',
                                                            'is_public':True})
    assert response.json()['code'] == 400

def test_channels_create_exception_long_name(url):
    '''
    A simple test to check exception case (long name) of channels_create
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'channels/create',\
                             json={'token':u_1['token'],
                                   'name':'long long long long long long name',
                                   'is_public':True})
    assert response.json()['code'] == 400


# Channel functions tests
def test_channel_invite_valid(url):
    """Test for valid invite"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})                
    response = requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                  'channel_id': 1,\
                                                  'u_id': u_2['u_id']})
    assert response.json() == {}

def test_channel_invite_flockr_owner(url):
    """Test for valid invite of flockr owner"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': True
                                                })
    requests.post(url + 'channels/create', json={'token': u_2['token'],\
                                                 'name': 'MobBoss',\
                                                 'is_public': True
                                                })                  
    response = requests.post(url + 'channel/invite', json={'token': u_2['token'],\
                                                           'channel_id': 2,\
                                                           'u_id': u_1['u_id']
                                                          })
    assert response.json() == {}

def test_channel_invite_self(url):
    """Testing for inviting yourself"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': True
                                                })

    response = requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                           'channel_id': 1,\
                                                           'u_id': u_1['u_id']
                                                          })
    assert response.json()['code'] == 400

def test_channel_invite_already_in_channel(url):
    """Testing inviting somebody already in the channel"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': True
                                                })

    response = requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                           'channel_id': 1,\
                                                           'u_id': u_2['u_id']
                                                          })
    assert response.json() == {}

    # Reinviting the user
    response = requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                           'channel_id': 1,\
                                                           'u_id': u_2['u_id']
                                                          })
    assert response.json()['code'] == 400

def test_channel_invite_exception_invalid_channel(url):
    """Testing for invalid channel id exception"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': True
                                                })

    response = requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                           'channel_id': 2,\
                                                           'u_id': u_2['u_id']
                                                          })
    assert response.json()['code'] == 400

def test_channel_invite_exception_invalid_uid(url):
    """Testing for invalid u_id exception"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': True
                                                })

    response = requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                           'channel_id': 1,\
                                                           'u_id': 4
                                                          })
    assert response.json()['code'] == 400

def test_channel_invite_exception_authorised_user(url):
    """Testing for authorised user not in channel exception"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_3)
    u_3 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': True
                                                })

    response = requests.post(url + 'channel/invite', json={'token': u_2['token'],\
                                                           'channel_id': 1,\
                                                           'u_id': u_3['u_id']
                                                          })
    assert response.json()['code'] == 400

def test_channel_invite_exception_invalid_token(url):
    """Testing for authorised user not in channel exception"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': True
                                                })

    response = requests.post(url + 'channel/invite', json={'token': 'invalidtoken',\
                                                           'channel_id': 1,\
                                                           'u_id': u_2['u_id']
                                                          })
    assert response.json()['code'] == 400

# Tests for channel_details
def test_channel_details_valid(url):
    """Test for valid invite"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})                       
    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})

    response = requests.get(url + 'channel/details', params={'token': u_1['token'],\
                                                             'channel_id': 1})

    assert response.json() == \
    {'name':"BobRoss", 'owner_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''}], 'all_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''},\
    {'u_id':2, 'name_first':"Bob", 'name_last':"Ross", "profile_img_url":''}]}


def test_channel_details_update_1(url):
    """Test if channel details updates when a regular member leaves"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})                       
    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})

    response = requests.get(url + 'channel/details', params={'token': u_1['token'],\
                                                             'channel_id': 1})

    assert response.json() == \
    {'name':"BobRoss", 'owner_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''}], 'all_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''},\
    {'u_id':2, 'name_first':"Bob", 'name_last':"Ross", "profile_img_url":''}]}

    requests.post(url + 'channel/leave', json={'token': u_2['token'],'channel_id': 1})
    
    response = requests.get(url + 'channel/details', params={'token': u_1['token'],\
                                                             'channel_id': 1})
    assert response.json() == \
    {'name':"BobRoss",\
     'owner_members':[{'u_id':1, 'name_first':"Bob",'name_last':"Ross", "profile_img_url":''}],\
     'all_members':[{'u_id':1, 'name_first':"Bob", 'name_last':"Ross", "profile_img_url":''}]}

def test_channel_details_update_2(url):
    """Test if channel details updates when a channel owner leaves"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})                        
    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})

    response = requests.get(url + 'channel/details', params={'token': u_1['token'],\
                                                             'channel_id': 1})

    assert response.json() == \
    {'name':"BobRoss", 'owner_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''}], 'all_members':[{'u_id':1, 'name_first':"Bob",\
     'name_last':"Ross", "profile_img_url":''},\
    {'u_id':2, 'name_first':"Bob", 'name_last':"Ross", "profile_img_url":''}]}

    requests.post(url + 'channel/leave', json={'token': u_1['token'],'channel_id': 1})
    
    response = requests.get(url + 'channel/details', params={'token': u_2['token'],\
                                                             'channel_id': 1})

    assert response.json() == \
    {'name':"BobRoss", 'owner_members':[], 'all_members':[{'u_id':2, 'name_first':"Bob", 
                                                           'name_last':"Ross", 
                                                           "profile_img_url":''}]}

def test_channel_details_exception_invalid_channel(url):
    """Test for invalid channel exception"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})         
    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})

    response = requests.get(url + 'channel/details', params={'token': u_1['token'],\
                                                             'channel_id': 3})

    assert response.json()['code'] == 400

def test_channel_details_exception_authorised_user_not_member(url):
    """Test for invalid authorised user exception"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})             

    response = requests.get(url + 'channel/details', params={'token': u_2['token'],\
                                                             'channel_id': 1})

    assert response.json()['code'] == 400

def test_channel_details_exception_invalid_token(url):
    """Test for invalid authorised user exception"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})              

    response = requests.get(url + 'channel/details', params={'token': 'INVALIDTOKEN',\
                                                             'channel_id': 1})

    assert response.json()['code'] == 400


# Tests for channel_messages
def test_channel_messages_empty(url):
    """Test for channel with no messages"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})

    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    assert response.json() == {'messages':[], 'start': 0, 'end': -1}

def test_channel_messages_standard(url):
    """Standard test for channel_messages"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})

    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})

    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello there"})

    requests.post(url + 'message/send', json={'token': u_2['token'],\
                                              'channel_id': 1,\
                                              'message': "What's up"})

    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json()

    assert messages_data['messages'][0]['message'] == "What's up"
    assert messages_data['messages'][1]['message'] == "Hello there"
    assert messages_data['start'] == 0
    assert messages_data['end'] == -1

def test_channel_messages_alot(url):
    """Lots of messages tests for channel_messages"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})

    for increment in range(0, 100):
        requests.post(url + 'message/send', json={'token': u_1['token'],\
                                                  'channel_id': 1,\
                                                  'message': "I AM SPAMMING"})

    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json()

    for increment in range(0, 50):
        assert messages_data['messages'][increment]['message'] == "I AM SPAMMING"

    assert messages_data['start'] == 0
    assert messages_data['end'] == 50

def test_channel_messages_exception_invalid_channel(url):
    """Test for invalid channel exception"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})

    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 3,\
                                                              'start': 0})
    assert response.json()['code'] == 400

def test_channel_messages_exception_not_member(url):
    """Test when authorised user is not a member"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})

    response = requests.get(url + 'channel/messages', params={'token': u_2['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    assert response.json()['code'] == 400


def test_channel_messages_exception_invalid_token(url):
    """Test when invalid token is passed in"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})

    response = requests.get(url + 'channel/messages', params={'token': 'INVALIDTOKEN',\
                                                              'channel_id': 1,\
                                                              'start': 0})
    assert response.json()['code'] == 400

# channel/leave
def test_channel_leave(url):
    '''Test channel_leave for correct return'''
    requests.delete(url + "clear")
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    response = requests.post(url + 'channel/leave', json={'token': u_1['token'],
                                                          'channel_id': 1})
    assert response.json() == {}

def test_channel_leave_input_error(url):
    '''Check that channel_leave raises InputError when given invalid channel_id'''
    requests.delete(url + "clear")
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'channel/leave', json={'token': u_1['token'],
                                                          'channel_id': 1})
    assert response.json()['code'] == 400

def test_channel_leave_access_error(url):
    '''Check that channel_leave raises AccessError when user is not a member'''
    requests.delete(url + "clear")
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
     # User with token u_2['token'] is not a member of channel
    response = requests.post(url + 'channel/leave', json={'token': u_2['token'],
                                                          'channel_id': 1})
    assert response.json()['code'] == 400

# channel/join
def test_channel_join(url):
    '''Test that channel_join returns correct output'''
    requests.delete(url + "clear")
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    response = requests.post(url + '/channel/join', json={'token': u_2['token'],
                                                          'channel_id': 1})
    assert response.json() == {}

def test_channel_join_owner_private(url):
    '''Test flockr owner joining private channel'''
    requests.delete(url + "clear")
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_2['token'],
                                                 'name': 'First channel',
                                                 'is_public': False})
    response = requests.post(url + '/channel/join', json={'token': u_1['token'],
                                                          'channel_id': 1})
    assert response.json() == {}

def test_channel_join_input_error(url):
    '''Check that channel_join raises InputError channel_id is invalid'''
    requests.delete(url + "clear")
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    # Channel with id = 1 has not be created
    response = requests.post(url + '/channel/join', json={'token': u_1['token'],
                                                          'channel_id': 1})
    assert response.json()['code'] == 400

def test_channel_join_access_error(url):
    '''Check that channel_join raises AccessError when joining private channel'''
    requests.delete(url + "clear")
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': False})
    response = requests.post(url + '/channel/join', json={'token': u_2['token'],
                                                          'channel_id': 1})
    # u_2 is not owner of private channel or a flockr owner
    assert response.json()['code'] == 400

# channel/addowner
def test_channel_addowner(url):
    '''Check that channel_addowner returns correct output'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    response = requests.post(url + 'channel/join', json={'token': u_2['token'],
                                                         'channel_id': '1'})
    response = requests.post(url + 'channel/addowner', json={'token': u_1['token'],
                                                             'channel_id': 1,
                                                             'u_id': 2})
    assert response.json() == {}

def test_channel_addowner_invalid_channel(url):
    '''Check that channel_addowner raises InputError when given invalid channel_id'''
    requests.delete(url + 'clear')
    # Create users to make sure error is caused by channel_addowner()
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'auth/register', json=good_reg_2)
    response = requests.post(url + 'channel/addowner', json={'token': u_1['token'],
                                                             'channel_id': 10,
                                                             'u_id': 2})
    assert response.json()['code'] == 400

def test_channel_addowner_repeat(url):
    '''Check that channel_addowner raises InputError if u_id is already an owner'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    requests.post(url + '/channel/join', json={'token': u_2['token'],
                                               'channel_id': 1})
    requests.post(url + 'channel/addowner', json={'token': u_1['token'],
                                                  'channel_id': 1,
                                                  'u_id': 2})
    response = requests.post(url + 'channel/addowner', json={'token': u_1['token'],
                                                             'channel_id': 1,
                                                             'u_id': 2})
    assert response.json()['code'] == 400

def test_channel_addowner_not_owner(url):
    '''Check that channel_addowner raises AccessError if authorised user does not
    have permission to add owner'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_3)
    u_3 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    requests.post(url + '/channel/join', json={'token': u_2['token'],
                                               'channel_id': 1})
    requests.post(url + '/channel/join', json={'token': u_3['token'],
                                               'channel_id': 1})
    # u_3 is not a owner of channel or owner of flockr
    response = requests.post(url + 'channel/addowner', json={'token': u_3['token'],
                                                             'channel_id': 1,
                                                             'u_id': 2})
    assert response.json()['code'] == 400

# channel/removeowner
def test_channel_removeowner(url):
    '''Test channel_removeowner for correct output'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    response = requests.post(url + 'channel/join', json={'token': u_2['token'],
                                                         'channel_id': '1'})
    response = requests.post(url + 'channel/addowner', json={'token': u_1['token'],
                                                             'channel_id': '1',
                                                             'u_id': 2})

    response = requests.post(url + 'channel/removeowner', json={'token': u_1['token'],
                                                                'channel_id': 1,
                                                                'u_id': 2})
    assert response.json() == {}

def test_channel_removeowner_invalid_channel(url):
    '''Check that channel_removeowner raises InputError when given invalid channel_id'''
    requests.delete(url + 'clear')
    # Register users to make sure error is caused by channel_addowner()
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'auth/register', json=good_reg_2)
    # channel_id = 1 is not valid
    response = requests.post(url + 'channel/removeowner', json={'token': u_1['token'],
                                                                'channel_id': 1,
                                                                'u_id': 2})
    assert response.json()['code'] == 400

def test_channel_removeowner_not_owner(url):
    '''Check that channel_removeowner raises InputError if u_id is not an owner
    of the channel'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    # u_id = 2 is not an owner of the channel
    response = requests.post(url + 'channel/removeowner', json={'token': u_1['token'],
                                                                'channel_id': 1,
                                                                'u_id': 2})
    assert response.json()['code'] == 400

def test_channel_no_auth_removeowner(url):
    '''Check that channel_removeowner raises AccessError if authorised user does
    not have permission to remove owner'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    requests.post(url + 'channel/join', json={'token': u_2['token'],
                                              'channel_id': '1'})
    # u_2 is not an owner of channel or owner of flockr
    response = requests.post(url + 'channel/removeowner', json={'token': u_2['token'],
                                                                'channel_id': 1,
                                                                'u_id': 1})
    assert response.json()['code'] == 400

# Tests for message functions

def test_message_send_valid(url):
    """Testing sending valid message"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})

    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})
    # User 1 sending messages to channel 1
    response = requests.post(url + 'message/send', json={'token': u_1['token'],\
                                                         'channel_id': 1,\
                                                         'message': "MESSAGE1"})
    assert response.json() == {'message_id': 1}
    response = requests.post(url + 'message/send', json={'token': u_1['token'],\
                                                         'channel_id': 1,\
                                                         'message': "MESSAGE2"})
    assert response.json() == {'message_id': 2}
    # User 2 sending messages to channel 1
    response = requests.post(url + 'message/send', json={'token': u_1['token'],\
                                                         'channel_id': 1,\
                                                         'message': "MESSAGE3"})
    assert response.json() == {'message_id': 3}
    requests.post(url + 'channels/create', json={'token': u_2['token'],\
                                                 'name': 'Channel2',\
                                                 'is_public': "True"})
    # User 2 sending messages to channel 2
    response = requests.post(url + 'message/send', json={'token': u_2['token'],\
                                                         'channel_id': 2,\
                                                         'message': "MESSAGE4"})
    assert response.json() == {'message_id': 4}
    # User 2 sending another message to channel 1
    response = requests.post(url + 'message/send', json={'token': u_2['token'],\
                                                         'channel_id': 1,\
                                                         'message': "MESSAGE5"})
    assert response.json() == {'message_id': 5}
    
    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json()
    assert messages_data['messages'][0]['message'] == "MESSAGE5"
    assert messages_data['messages'][1]['message'] == "MESSAGE3"
    assert messages_data['messages'][2]['message'] == "MESSAGE2"
    assert messages_data['messages'][3]['message'] == "MESSAGE1"

    response = requests.get(url + 'channel/messages', params={'token': u_2['token'],\
                                                              'channel_id': 2,\
                                                              'start': 0})
    messages_data = response.json()
    assert messages_data['messages'][0]['message'] == "MESSAGE4"

def test_message_send_invalid_token_exception(url):
    """Exception: Invalid token"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})

    response = requests.post(url + 'message/send', json={'token': "INVALIDTOKEN",\
                                                         'channel_id': 1,\
                                                         'message': "MESSAGE5"})
    assert response.json()['code'] == 400

def test_message_send_length_exception(url):
    """Exception: Message more than 1000 characters in length"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})

    response = requests.post(url + 'message/send', json={'token': u_1['token'],\
                                                         'channel_id': 1,\
                                                         'message':\
    LONG_MESSAGE})
    
    assert response.json()['code'] == 400

def test_message_send_authorised_user_not_in_channel_exception(url):
    """Exception: Authorised user is not a member of given channel"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()   
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    response = requests.post(url + 'message/send', json={'token': u_2['token'],\
                                                         'channel_id': 1,\
                                                         'message': "Mefe"})
    assert response.json()['code'] == 400

def test_message_remove_by_flockr_owner(url):
    """Testing removal by flockr owner (not channel owner)"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_2['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_2['token'],\
                                              'channel_id': 1,\
                                              'message': "Mefe"})
    
    response = requests.delete(url + 'message/remove', json={'token': u_1['token'],\
                                                             'message_id': 1})
    assert response.json() == {}
    
    response = requests.get(url + 'channel/messages', params={'token': u_2['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json() 
    assert messages_data['messages'] == []

def test_message_remove_by_channel_owner(url):
    """Testing removal by channel owner (not flockr owner)"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_2['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'channel/invite', json={'token': u_2['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_1['u_id']})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Mefe"})
    
    response = requests.delete(url + 'message/remove', json={'token': u_2['token'],\
                                                             'message_id': 1})
    assert response.json() == {}
    
    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json() 
    assert messages_data['messages'] == []

def test_message_remove_by_sender(url):
    """Testing removal by message sender"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})
    requests.post(url + 'message/send', json={'token': u_2['token'],\
                                              'channel_id': 1,\
                                              'message': "Mefe"})
    response = requests.delete(url + 'message/remove', json={'token': u_2['token'],\
                                                             'message_id': 1})
    assert response.json() == {}

    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json() 
    assert messages_data['messages'] == []

def test_message_remove_invalid_token_exception(url):
    """Exception: Invalid token"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "yes"})
    response = requests.delete(url + 'message/remove', json={'token': "INVALIDTOKEN",\
                                                             'message_id': 1})
    assert response.json()['code'] == 400

def test_message_remove_nonexistent_exception(url):
    """Exception: Non existent message"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "yes"})
    response = requests.delete(url + 'message/remove', json={'token': u_1['token'],\
                                                             'message_id': 1})
    assert response.json() == {}
    response = requests.delete(url + 'message/remove', json={'token': u_1['token'],\
                                                             'message_id': 1})
    assert response.json()['code'] == 400

def test_message_remove_authorised_not_in_channel_exception_1(url):
    """
    Exception: Message with given id is not sent by the authorised user
    making the request and the authorised user is not an owner of this channel
    or the flockr
    """
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "yes"})
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})

    response = requests.delete(url + 'message/remove', json={'token': u_2['token'],\
                                                             'message_id': 1})
    assert response.json()['code'] == 400

def test_message_remove_authorised_not_in_channel_exception_2(url):
    """
    Exception: Message with given id is not sent by the authorised user
    making the request and the authorised user is not an owner of this channel
    or the flockr
    """
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "yes"})
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()

    response = requests.delete(url + 'message/remove', json={'token': u_2['token'],\
                                                             'message_id': 1})
    assert response.json()['code'] == 400

def test_message_edit_single_message_valid(url):
    """Testing editing single message"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})  

    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello there"})

    response = requests.put(url + 'message/edit', json={'token': u_1['token'],\
                                                        'message_id': 1,\
                                                        'message': "Peter"})

    assert response.json() == {}

    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json()
    
    assert messages_data['messages'][0]['message'] == "Peter"
    assert messages_data['start'] == 0
    assert messages_data['end'] == -1

def test_message_edit_multiple_message_valid(url):
    """Testing editing multiple messages"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})  

    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello there"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Goodbye"})
    response = requests.put(url + 'message/edit', json={'token': u_1['token'],\
                                                        'message_id': 1,\
                                                        'message': "Peter"})
    assert response.json() == {}
    response = requests.put(url + 'message/edit', json={'token': u_1['token'],\
                                                        'message_id': 2,\
                                                        'message': "Parker"})
    assert response.json() == {}

    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json()
    
    assert messages_data['messages'][0]['message'] == "Parker"
    assert messages_data['messages'][1]['message'] == "Peter"
    assert messages_data['start'] == 0
    assert messages_data['end'] == -1

def test_message_edit_delete_valid(url):
    """Testing removing message by editing with empty string"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})  
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello there"})
   
    response = requests.put(url + 'message/edit', json={'token': u_1['token'],\
                                                        'message_id': 1,\
                                                        'message': ""})
    assert response.json() == {}
    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json()
    
    assert messages_data['messages'] == []
    assert messages_data['start'] == 0
    assert messages_data['end'] == -1

def test_message_edit_as_channel_owner(url):
    """Testing editing message as channel owner"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()

    response = requests.post(url + 'auth/register', json=good_reg_3)
    u_3 = response.json()

    requests.post(url + 'channels/create', json={'token': u_2['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})  
    requests.post(url + 'channel/invite', json={'token': u_2['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_1['u_id']})
    requests.post(url + 'channel/invite', json={'token': u_2['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_3['u_id']})

    # User 1 is a flockr owner + channel owner and User 2 is just a channel owner

    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                             'channel_id': 1,\
                                             'message': "Hello"})
    requests.post(url + 'message/send', json={'token': u_2['token'],\
                                             'channel_id': 1,\
                                             'message': "Sup"})
    requests.post(url + 'message/send', json={'token': u_3['token'],\
                                             'channel_id': 1,\
                                             'message': "Yo"})
    
    # Since User 2 is a channel owner, he should be allowed to edit any message,
    # even if they didn't create them
    response = requests.put(url + 'message/edit', json={'token': u_2['token'],\
                                                        'message_id': 1,\
                                                        'message': "HA"})
    assert response.json() == {}
    response = requests.put(url + 'message/edit', json={'token': u_2['token'],\
                                                        'message_id': 2,\
                                                        'message': "HA"})
    assert response.json() == {}
    response = requests.put(url + 'message/edit', json={'token': u_2['token'],\
                                                        'message_id': 3,\
                                                        'message': "HA"})
    assert response.json() == {}
    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json()
    
    assert messages_data['messages'][0]['message'] == "HA"
    assert messages_data['messages'][1]['message'] == "HA"
    assert messages_data['messages'][2]['message'] == "HA"
    assert messages_data['start'] == 0
    assert messages_data['end'] == -1

def test_message_edit_as_flockr_owner(url):
    """Testing editing message as flockr owner"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()

    response = requests.post(url + 'auth/register', json=good_reg_3)
    u_3 = response.json()

    requests.post(url + 'channels/create', json={'token': u_2['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})  
    requests.post(url + 'channel/invite', json={'token': u_2['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_1['u_id']})
    requests.post(url + 'channel/invite', json={'token': u_2['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_3['u_id']})

    # User 1 is a flockr owner + channel owner and User 2 is just a channel owner

    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                             'channel_id': 1,\
                                             'message': "Hello"})
    requests.post(url + 'message/send', json={'token': u_2['token'],\
                                             'channel_id': 1,\
                                             'message': "Sup"})
    requests.post(url + 'message/send', json={'token': u_3['token'],\
                                             'channel_id': 1,\
                                             'message': "Yo"})
    
    # Since User 1 is a flockr owner, they should have channel owner permissions and thus
    # be allowed to edit any message, even if they didn't create them
    response = requests.put(url + 'message/edit', json={'token': u_1['token'],\
                                                        'message_id': 1,\
                                                        'message': "HA"})
    assert response.json() == {}
    response = requests.put(url + 'message/edit', json={'token': u_1['token'],\
                                                        'message_id': 2,\
                                                        'message': "HA"})
    assert response.json() == {}
    response = requests.put(url + 'message/edit', json={'token': u_1['token'],\
                                                        'message_id': 3,\
                                                        'message': "HA"})
    assert response.json() == {}

    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json()
    
    assert messages_data['messages'][0]['message'] == "HA"
    assert messages_data['messages'][1]['message'] == "HA"
    assert messages_data['messages'][2]['message'] == "HA"
    assert messages_data['start'] == 0
    assert messages_data['end'] == -1

def test_message_edit_more_than_1000(url):
    """Editing a message to more than 1000 characters in length"""
    requests.post(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})

    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                             'channel_id': 1,\
                                             'message': "Hello"})

    response = requests.put(url + 'message/edit', json={'token': u_1['token'],\
                                                         'message_id': 1,\
                                                         'message': \
    LONG_MESSAGE})
    
    assert response.json()['code'] == 400


def test_message_edit_exception(url):
    """Exception: Authorised user did not send the message being edited and
       Exception: Authorised user is not an channel or flockr owner"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_3)
    u_3 = response.json()

    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})  
    requests.post(url + 'channel/invite', json={'token': u_2['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})
    requests.post(url + 'channel/invite', json={'token': u_2['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_3['u_id']})

    # User 1 sending messages to channel 1
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    # User 2 sending messages to channel 1
    requests.post(url + 'message/send', json={'token': u_2['token'],\
                                              'channel_id': 1,\
                                              'message': "Boomer"})

    # User 3, neither a channel/flockr owner nor the person who created the messages,
    # tries to edit them, this will raise an error
    response = requests.put(url + 'message/edit', json={'token': u_3['token'],\
                                                        'message_id': 1,\
                                                        'message': "HA"})

    assert response.json()['code'] == 400 

def test_message_sendlater_valid(url):
    """Sending a message at a later time in the future"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    response = requests.post(url + 'message/sendlater', json= \
    {'token': u_1['token'], 'channel_id': 1, 'message': 'goodmessage1', \
     'time_sent': (datetime.now() + timedelta(seconds=1)).timestamp()})
    assert response.json() == {'message_id': 1}
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})
    response = requests.post(url + 'message/sendlater', json= \
    {'token': u_2['token'], 'channel_id': 1, 'message': 'goodmessage2', \
     'time_sent': (datetime.now() + timedelta(seconds=1)).timestamp()})
    assert response.json() == {'message_id': 2}

def test_message_sendlater_invalid_token(url):
    """Exception: Invalid token"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    response = requests.post(url + 'message/sendlater', json= \
    {'token': "invalidtoken", 'channel_id': 1, 'message': 'goodmessage1', \
     'time_sent': (datetime.now() + timedelta(seconds=1)).timestamp()})
    assert response.json()['code'] == 400

def test_message_sendlater_invalid_channel(url):
    """Exception: Invalid channel id"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    response = requests.post(url + 'message/sendlater', json= \
    {'token': u_1['token'], 'channel_id': 2, 'message': 'goodmessage1', \
     'time_sent': (datetime.now() + timedelta(seconds=1)).timestamp()})
    assert response.json()['code'] == 400

def test_message_sendlater_message_too_long(url):
    """Exception: Given message is too long (>1000 characters)"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    response = requests.post(url + 'message/sendlater', json= \
    {'token': u_1['token'], 'channel_id': 1, 'message': LONG_MESSAGE, \
     'time_sent': (datetime.now() + timedelta(seconds=1)).timestamp()})
    assert response.json()['code'] == 400

def test_message_sendlater_time_in_past(url):
    """Exception: Specified time is in the past instead of future"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    response = requests.post(url + 'message/sendlater', json= \
    {'token': u_1['token'], 'channel_id': 1, 'message': 'goodmessage1', \
     'time_sent': (datetime.now() + timedelta(seconds=-1)).timestamp()})
    assert response.json()['code'] == 400

def test_message_sendlater_non_member(url):
    """Exception: Authorised user isn't a member of the channel"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    response = requests.post(url + 'message/sendlater', json= \
    {'token': u_2['token'], 'channel_id': 1, 'message': 'goodmessage1', \
     'time_sent': (datetime.now() + timedelta(seconds=1)).timestamp()})
    assert response.json()['code'] == 400

def test_react_valid(url):
    """Testing valid reacts"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    response = requests.post(url + 'message/react', json={'token': u_1['token'], \
                                                          'message_id': 1, \
                                                          'react_id': 1})
    assert response.json() == {}
    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages = response.json()['messages']
    assert messages[0]['reacts'][0]['u_ids'] == [1]
    assert messages[0]['reacts'][0]['is_this_user_reacted']
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})
    response = requests.post(url + 'message/react', json={'token': u_2['token'], \
                                                          'message_id': 1, \
                                                          'react_id': 1})
    assert response.json() == {}
    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages = response.json()['messages']
    assert messages[0]['reacts'][0]['u_ids'] == [1, 2]
    assert messages[0]['reacts'][0]['is_this_user_reacted']

def test_react_exception_invalid_message_id(url):
    """Exception: Given message id is invalid"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    response = requests.post(url + 'message/react', json={'token': u_1['token'], \
                                                          'message_id': 2, \
                                                          'react_id': 1})
    assert response.json()['code'] == 400

def test_react_exception_invalid_react_id(url):
    """Exception: Given react id is invalid"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    response = requests.post(url + 'message/react', json={'token': u_1['token'], \
                                                          'message_id': 1, \
                                                          'react_id': 0})
    assert response.json()['code'] == 400

def test_react_exception_already_reacted(url):
    """Exception: Authorised user has already reacted to the message"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    requests.post(url + 'message/react', json={'token': u_1['token'], \
                                               'message_id': 1, 'react_id': 1})
    response = requests.post(url + 'message/react', json={'token': u_1['token'], \
                                                          'message_id': 1, \
                                                          'react_id': 1})
    assert response.json()['code'] == 400

def test_unreact_valid(url):
    """Testing valid unreacts"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    requests.post(url + 'message/react', json={'token': u_1['token'], \
                                               'message_id': 1, 'react_id': 1})
    response = requests.post(url + 'message/unreact', json={'token': u_1['token'], \
                                                            'message_id': 1, \
                                                            'react_id': 1})
    assert response.json() == {}
    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages = response.json()['messages']
    assert messages[0]['reacts'][0]['u_ids'] == []
    assert not messages[0]['reacts'][0]['is_this_user_reacted']

def test_unreact_exception_invalid_message_id(url):
    """Exception: Given message id is invalid"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    response = requests.post(url + 'message/unreact', json={'token': u_1['token'], \
                                                            'message_id': 2, \
                                                            'react_id': 1})
    assert response.json()['code'] == 400

def test_unreact_exception_invalid_react_id(url):
    """Exception: Given react id is invalid"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    response = requests.post(url + 'message/unreact', json={'token': u_1['token'], \
                                                            'message_id': 1, \
                                                            'react_id': 0})
    assert response.json()['code'] == 400

def test_unreact_exception_not_yet_reacted(url):
    """Exception: Authorised user has not yet reacted to the message"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    response = requests.post(url + 'message/unreact', json={'token': u_1['token'], \
                                                            'message_id': 1, \
                                                            'react_id': 1})
    assert response.json()['code'] == 400

# Message_pin
def test_pin_valid(url):
    """Valid test case for pinning messages"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})

    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})

    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})

    response = requests.post(url + 'message/pin', json={'token': u_1['token'],\
                                                        'message_id': 1})
    assert response.json() == {}
    
    requests.post(url + 'message/send', json={'token': u_2['token'],\
                                              'channel_id': 1,\
                                              'message': "Hi"})

    response = requests.post(url + 'message/pin', json={'token': u_1['token'],\
                                                        'message_id': 2})

    assert response.json() == {}
    
    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json()
    
    assert messages_data['messages'][0]['is_pinned'] == True
    assert messages_data['messages'][1]['is_pinned'] == True

def test_pin_promoted_to_owner_member(url):
    """Checking the case where a newly promoted user can pin messages"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})

    response = requests.post(url + 'channel/addowner', json={'token': u_1['token'],
                                                             'channel_id': 1,
                                                             'u_id': 2})
    response = requests.post(url + 'message/pin', json={'token': u_2['token'],\
                                                        'message_id': 1})
    assert response.json() == {}

    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json()
    assert messages_data['messages'][0]['is_pinned'] == True

def test_pin_flockr_owner(url):
    """Checking the case where a flockr owner can pin messages"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_2['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'channel/invite', json={'token': u_2['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_1['u_id']})
    requests.post(url + 'message/send', json={'token': u_2['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})

    response = requests.post(url + 'message/pin', json={'token': u_1['token'],\
                                                        'message_id': 1})
    assert response.json() == {}

    response = requests.get(url + 'channel/messages', params={'token': u_2['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json()
    assert messages_data['messages'][0]['is_pinned'] == True

def test_pin_invalid_token_exception(url):
    """Invalid token exception"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})

    response = requests.post(url + 'message/pin', json={'token': 'INVALIDTOKEN',\
                                                        'message_id': 1})
    assert response.json()['code'] == 400

def test_pin_invalid_message_exception(url):
    """Message id is not a valid message"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    response = requests.post(url + 'message/pin', json={'token': u_1['token'],\
                                                        'message_id': 2})
    assert response.json()['code'] == 400

def test_pin_message_already_pinned_exception(url):
    """Given message of message_id is already pinned"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})

    response = requests.post(url + 'message/pin', json={'token': u_1['token'],\
                                                        'message_id': 1})
    assert response.json() == {}

    response = requests.post(url + 'message/pin', json={'token': u_1['token'],\
                                                        'message_id': 1})
    assert response.json()['code'] == 400

def test_pin_not_part_of_channel_exception(url):
    """Authorised user is not a member of the channel that the message is in"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})

    response = requests.post(url + 'message/pin', json={'token': u_2['token'],\
                                                        'message_id': 1})
    assert response.json()['code'] == 400

def test_pin_not_owner_of_channel_exception(url):
    """Authorised user is not an owner of the channel"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})

    response = requests.post(url + 'message/pin', json={'token': u_2['token'],\
                                                        'message_id': 1})
    assert response.json()['code'] == 400

# Message_unpin
def test_unpin_valid(url):
    """Valid test case for unpinning messages"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})

    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    requests.post(url + 'message/pin', json={'token': u_1['token'],\
                                             'message_id': 1})
    requests.post(url + 'message/send', json={'token': u_2['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello1"})
    requests.post(url + 'message/pin', json={'token': u_1['token'],\
                                             'message_id': 2})

    response = requests.post(url + 'message/unpin', json={'token': u_1['token'],\
                                                          'message_id': 1})
    assert response.json() == {}
    response = requests.post(url + 'message/unpin', json={'token': u_1['token'],\
                                                          'message_id': 2})
    assert response.json() == {}
    
    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json()
    
    assert messages_data['messages'][0]['is_pinned'] == False
    assert messages_data['messages'][1]['is_pinned'] == False

def test_unpin_promoted_to_owner_member(url):
    """Checking the case where a newly promoted user can unpin messages"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})

    response = requests.post(url + 'channel/addowner', json={'token': u_1['token'],
                                                             'channel_id': 1,
                                                             'u_id': 2})
    requests.post(url + 'message/pin', json={'token': u_1['token'],\
                                             'message_id': 1})

    response = requests.post(url + 'message/unpin', json={'token': u_2['token'],\
                                                          'message_id': 1})
    assert response.json() == {}

    response = requests.get(url + 'channel/messages', params={'token': u_1['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json()
    assert messages_data['messages'][0]['is_pinned'] == False

def test_unpin_flockr_owner(url):
    """Checking the case where a flockr owner can unpin messages"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_2['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'channel/invite', json={'token': u_2['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_1['u_id']})
    requests.post(url + 'message/send', json={'token': u_2['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    requests.post(url + 'message/pin', json={'token': u_2['token'],\
                                             'message_id': 1})
    response = requests.post(url + 'message/unpin', json={'token': u_1['token'],\
                                                          'message_id': 1})
    assert response.json() == {}

    response = requests.get(url + 'channel/messages', params={'token': u_2['token'],\
                                                              'channel_id': 1,\
                                                              'start': 0})
    messages_data = response.json()
    assert messages_data['messages'][0]['is_pinned'] == False

def test_unpin_invalid_token_exception(url):
    """Invalid token exception"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    requests.post(url + 'message/pin', json={'token': u_1['token'],\
                                             'message_id': 1})
    response = requests.post(url + 'message/unpin', json={'token': 'INVALIDTOKEN',\
                                                          'message_id': 1})
    assert response.json()['code'] == 400

def test_unpin_invalid_message_exception(url):
    """Message id is not a valid message"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    response = requests.post(url + 'message/unpin', json={'token': u_1['token'],\
                                                          'message_id': 2})
    assert response.json()['code'] == 400

def test_unpin_message_already_pinned_exception(url):
    """Given message of message_id is already unpinned"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    requests.post(url + 'message/pin', json={'token': u_1['token'],\
                                             'message_id': 1})

    requests.post(url + 'message/unpin', json={'token': u_1['token'],\
                                               'message_id': 1})

    response = requests.post(url + 'message/unpin', json={'token': u_1['token'],\
                                                          'message_id': 1})
    assert response.json()['code'] == 400

def test_unpin_not_part_of_channel_exception(url):
    """Authorised user is not a member of the channel that the message is in"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})

    requests.post(url + 'message/pin', json={'token': u_1['token'],\
                                             'message_id': 1})

    response = requests.post(url + 'message/unpin', json={'token': u_2['token'],\
                                                          'message_id': 1})
    assert response.json()['code'] == 400

def test_unpin_not_owner_of_channel_exception(url):
    """Authorised user is not an owner of the channel"""
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'BobRoss',\
                                                 'is_public': "True"})
    requests.post(url + 'channel/invite', json={'token': u_1['token'],\
                                                'channel_id': 1,\
                                                'u_id': u_2['u_id']})
    requests.post(url + 'message/send', json={'token': u_1['token'],\
                                              'channel_id': 1,\
                                              'message': "Hello"})
    requests.post(url + 'message/pin', json={'token': u_1['token'],\
                                             'message_id': 1})
    response = requests.post(url + 'message/unpin', json={'token': u_2['token'],\
                                                          'message_id': 1})
    assert response.json()['code'] == 400

# user_profile
def test_user_profile(url):
    '''
    A simple test to check user/profile
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.get(url + 'user/profile', params={'token':u_1['token'],
                                                          'u_id':u_1['u_id']})
    profile = response.json()

    assert profile == {'user': {'email': 'good_email1@gmail.com',
                                'handle_str': 'bobross00',
                                'name_first': 'Bob',
                                'name_last': 'Ross',
                                'u_id': 1,
                                'profile_img_url': ''}}

def test_user_profile_exception_invalid_token(url):
    '''
    A simple test to check exception case (invalid token) of user_profile
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.get(url + 'user/profile', params={'token':'invalid token',
                                                        'u_id':u_1['u_id']})
    assert response.json()['code'] == 400

def test_user_profile_exception_invalid_id(url):
    '''
    A simple test to check exception case (invalid user id) of user_profile
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.get(url + 'user/profile', params={'token':u_1['token'],
                                                        'u_id':'2'})
    assert response.json()['code'] == 400

# user_profile_setname
def test_user_profile_setname(url):
    '''
    A simple test to check user/profile/setname
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()

    requests.put(url + 'user/profile/setname', json={'token':u_1['token'],
                                                     'name_first':'New',
                                                     'name_last':'Name'})

    response = requests.get(url + 'user/profile', params={'token':u_2['token'],
                                                        'u_id':u_1['u_id']})
    profile = response.json()
    assert profile['user']['name_first'] == 'New'
    assert profile['user']['name_last'] == 'Name'

def test_user_profile_setname_exception_invalid_token(url):
    '''
    A simple test to check exception case (invalid token) of user_profile_setname
    '''
    requests.delete(url + 'clear')

    requests.post(url + 'auth/register', json=good_reg_1)

    response = requests.put(url + 'user/profile/setname', json={'token':'invalid token',
                                                                'name_first':'New',
                                                                'name_last':'Name'})
    assert response.json()['code'] == 400

def test_user_profile_setname_exception_long_first_name(url):
    '''
    A simple test to check exception case (long first_name) of user_profile_setname
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.put(url + 'user/profile/setname',\
                            json={'token':u_1['token'],
                                  'name_first':'really really really really\
                                                really really long long new',
                                  'name_last':'Name'})
    assert response.json()['code'] == 400

def test_user_profile_setname_exception_long_last_name(url):
    '''
    A simple test to check exception case (long last_name) of user_profile_setname
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.put(url + 'user/profile/setname',\
                            json={'token':u_1['token'],
                                  'name_first':'New',
                                  'name_last':'really really really really really\
                                               really long long name'})

    assert response.json()['code'] == 400

def test_user_profile_setname_exception_empty_first_name(url):
    '''
    A simple test to check exception case (empty first_name) of user_profile_setname
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.put(url + 'user/profile/setname', json={'token':u_1['token'],
                                                                'name_first':'',
                                                                'name_last':'Name'})
    assert response.json()['code'] == 400

def test_user_profile_setname_exception_empty_last_name(url):
    '''
    A simple test to check exception case (empty last_name) of user_profile_setname
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.put(url + 'user/profile/setname', json={'token':u_1['token'],
                                                                'name_first':'New',
                                                                'name_last':''})

    assert response.json()['code'] == 400

# user_profile_setemail
def test_user_profile_setemail(url):
    '''
    A simple test to check user/profile/setemail
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()

    requests.put(url + 'user/profile/setemail', json={'token':u_1['token'],
                                                      'email':'good_email3@hotMAIL.com'})

    response = requests.get(url + 'user/profile', params={'token':u_2['token'],
                                                        'u_id':u_1['u_id']})
    profile = response.json()
    assert profile['user']['email'] == 'good_email3@hotMAIL.com'

def test_user_profile_setemail_exception_invalid_token(url):
    '''
    A simple test to check exception case (invalid token) of user_profile_setemail
    '''
    requests.delete(url + 'clear')

    requests.post(url + 'auth/register', json=good_reg_1)

    response = requests.put(url + 'user/profile/setemail', json={'token':'invalid token',
                                                                 'email':'good_email2@hotMAIL.com'})
    assert response.json()['code'] == 400

def test_user_profile_setemail_exception_invalid_email(url):
    '''
    A simple test to check exception case (invalid email) of user_profile_setemail
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.put(url + 'user/profile/setemail', json={'token':u_1['token'],
                                                                 'email':'good_email2hotMAIL.com'})
    assert response.json()['code'] == 400

def test_user_profile_setemail_exception_email_taken(url):
    '''
    A simple test to check exception case (taken email) of user_profile_setemail
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    requests.post(url + 'auth/register', json=good_reg_2)

    response = requests.put(url + 'user/profile/setemail', json={'token':u_1['token'],
                                                                 'email':'good_email2@gmail.com'})
    assert response.json()['code'] == 400

# user_profile_sethandle
def test_user_profile_sethandle(url):
    '''
    A simple test to check user/profile/sethandle
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()

    requests.put(url + 'user/profile/sethandle', json={'token':u_1['token'],
                                                       'handle_str':'hithere'})

    response = requests.get(url + 'user/profile', params={'token':u_2['token'],
                                                        'u_id':u_1['u_id']})
    profile = response.json()
    assert profile['user']['handle_str'] == 'hithere'

def test_user_profile_sethandle_exception_invalid_token(url):
    '''
    A simple test to check exception case (invalid token) of user_profile_sethandle
    '''
    requests.delete(url + 'clear')

    requests.post(url + 'auth/register', json=good_reg_1)

    response = requests.put(url + 'user/profile/sethandle', json={'token':'invalid token',
                                                                  'handle_str':'hithere'})
    assert response.json()['code'] == 400

def test_user_profile_sethandle_exception_long_handle(url):
    '''
    A simple test to check exception case (outsized handle) of user_profile_sethandle
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()


    response = requests.put(url + 'user/profile/sethandle',\
                            json={'token':u_1['token'],
                                  'handle_str':'long long long long\
                                                long long long handle'})
    assert response.json()['code'] == 400

def test_user_profile_sethandle_exception_short_handle(url):
    '''
    A simple test to check exception case (short handle) of user_profile_sethandle
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()


    response = requests.put(url + 'user/profile/sethandle', json={'token':u_1['token'],
                                                                  'handle_str':'h'})
    assert response.json()['code'] == 400

def test_user_profile_sethandle_exception_taken_handle(url):
    '''
    A simple test to check exception case (taken handle) of user_profile_sethandle
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'auth/register', json=good_reg_2)

    response = requests.put(url + 'user/profile/sethandle', json={'token':u_1['token'],
                                                                  'handle_str':'bobross01'})
    assert response.json()['code'] == 400

# user_profile_uploadphoto
def test_user_profile_uploadphoto_valid(url):
    '''
    A simple test to check user/profile/uploadphoto
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    requests.post(url + 'channels/create', json={'token': u_1['token'],\
                                                 'name': 'First channel',\
                                                 'is_public': "True"})
    
    response = requests.post(url + 'user/profile/uploadphoto', json={'token': u_1['token'],\
                                                          'img_url': 'https://images.unsplash.com/\
photo-1533450718592-29d45635f0a9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=forma\
t&fit=crop&w=1950&q=80', 'x_start':0, 'y_start':0, 'x_end':1950, 'y_end':1300})

    assert response.json() == {}

def test_user_profile_uploadphoto_exception_invalid_token(url):
    '''
    A simple test to check exception case (invalid token) of user_profile_uplaodphoto
    '''
    requests.delete(url + 'clear')

    requests.post(url + 'auth/register', json=good_reg_1)

    response = requests.post(url + 'user/profile/uploadphoto', json={'token': 'invalid token',\
                                                          'img_url': 'https://images.unsplash.com/\
photo-1533450718592-29d45635f0a9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=forma\
t&fit=crop&w=1950&q=80', 'x_start':0, 'y_start':0, 'x_end':1950, 'y_end':1300})
    assert response.json()['code'] == 400

def test_user_profile_uploadphoto_exception_invalid_url(url):
    '''
    A simple test to check exception case (invalid url) of user_profile_uploadphoto
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'user/profile/uploadphoto', json={'token': u_1['token'],\
                                                          'img_url': 'https://images.unsplash.com/\
photo-192-29d45635f0a9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=forma\
t&fit=crop&w=1950&q=80', 'x_start':0, 'y_start':0, 'x_end':1950, 'y_end':1300})
    assert response.json()['code'] == 400

def test_user_profile_uploadphoto_exception_invalid_coordinates_x_start_lower(url):
    '''
    A simple test to check exception case (invalid coordinates) of user_profile_uploadphoto
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'user/profile/uploadphoto', json={'token': u_1['token'],\
                                                          'img_url': 'https://images.unsplash.com/\
photo-1533450718592-29d45635f0a9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=forma\
t&fit=crop&w=1950&q=80', 'x_start':-1, 'y_start':0, 'x_end':1950, 'y_end':1300})
    assert response.json()['code'] == 400

def test_user_profile_uploadphoto_exception_invalid_coordinates_y_start_lower(url):
    '''
    A simple test to check exception case (invalid coordinates) of user_profile_uploadphoto
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'user/profile/uploadphoto', json={'token': u_1['token'],\
                                                          'img_url': 'https://images.unsplash.com/\
photo-1533450718592-29d45635f0a9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=forma\
t&fit=crop&w=1950&q=80', 'x_start':0, 'y_start':-1, 'x_end':1950, 'y_end':1300})
    assert response.json()['code'] == 400

def test_user_profile_uploadphoto_exception_invalid_coordinates_x_end_lower(url):
    '''
    A simple test to check exception case (invalid coordinates) of user_profile_uploadphoto
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'user/profile/uploadphoto', json={'token': u_1['token'],\
                                                          'img_url': 'https://images.unsplash.com/\
photo-1533450718592-29d45635f0a9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=forma\
t&fit=crop&w=1950&q=80', 'x_start':0, 'y_start':0, 'x_end':-1, 'y_end':1300})
    assert response.json()['code'] == 400

def test_user_profile_uploadphoto_exception_invalid_coordinates_y_end_lower(url):
    '''
    A simple test to check exception case (invalid coordinates) of user_profile_uploadphoto
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'user/profile/uploadphoto', json={'token': u_1['token'],\
                                                          'img_url': 'https://images.unsplash.com/\
photo-1533450718592-29d45635f0a9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=forma\
t&fit=crop&w=1950&q=80', 'x_start':0, 'y_start':0, 'x_end':1950, 'y_end':-1})
    assert response.json()['code'] == 400

def test_user_profile_uploadphoto_exception_invalid_coordinates_x_start_over(url):
    '''
    A simple test to check exception case (invalid coordinates) of user_profile_uploadphoto
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'user/profile/uploadphoto', json={'token': u_1['token'],\
                                                          'img_url': 'https://images.unsplash.com/\
photo-1533450718592-29d45635f0a9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=forma\
t&fit=crop&w=1950&q=80', 'x_start':2000, 'y_start':0, 'x_end':1950, 'y_end':1300})
    assert response.json()['code'] == 400

def test_user_profile_uploadphoto_exception_invalid_coordinates_y_start_over(url):
    '''
    A simple test to check exception case (invalid coordinates) of user_profile_uploadphoto
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'user/profile/uploadphoto', json={'token': u_1['token'],\
                                                          'img_url': 'https://images.unsplash.com/\
photo-1533450718592-29d45635f0a9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=forma\
t&fit=crop&w=1950&q=80', 'x_start':0, 'y_start':2000, 'x_end':1950, 'y_end':1300})
    assert response.json()['code'] == 400

def test_user_profile_uploadphoto_exception_invalid_coordinates_x_end_over(url):
    '''
    A simple test to check exception case (invalid coordinates) of user_profile_uploadphoto
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'user/profile/uploadphoto', json={'token': u_1['token'],\
                                                          'img_url': 'https://images.unsplash.com/\
photo-1533450718592-29d45635f0a9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=forma\
t&fit=crop&w=1950&q=80', 'x_start':0, 'y_start':0, 'x_end':2000, 'y_end':1300})
    assert response.json()['code'] == 400

def test_user_profile_uploadphoto_exception_invalid_coordinates_y_end_over(url):
    '''
    A simple test to check exception case (invalid coordinates) of user_profile_uploadphoto
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'user/profile/uploadphoto', json={'token': u_1['token'],\
                                                          'img_url': 'https://images.unsplash.com/\
photo-1533450718592-29d45635f0a9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=forma\
t&fit=crop&w=1950&q=80', 'x_start':0, 'y_start':0, 'x_end':1950, 'y_end':2000})
    assert response.json()['code'] == 400

def test_user_profile_uploadphoto_exception_invalid_tpye_image(url):
    '''
    A simple test to check exception case (invalid type of image) of user_profile_uplaodphoto
    '''
    requests.delete(url + 'clear')

    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()

    response = requests.post(url + 'user/profile/uploadphoto', json={'token': u_1['token'],\
                                                          'img_url': 'https://upload.wikimedia.org/wi\
kipedia/commons/e/e9/Felis_silvestris_silvestris_small_gradual_decrease_of_quality.png',\
     'x_start':0, 'y_start':0, 'x_end':1950, 'y_end':1300})
    assert response.json()['code'] == 400

# other tests
# users_all
def test_users_all(url):
    '''Test users_all for correct output'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'auth/register', json=good_reg_2)
    response = requests.get(url + 'users/all', params={'token': u_1['token']})
    assert response.json() == {'users': [{'u_id': 1, 'email': 'good_email1@gmail.com',
                                          'name_first': 'Bob', 'name_last': 'Ross',
                                          'handle_str': 'bobross00'},
                                         {'u_id': 2, 'email': 'good_email2@gmail.com',
                                          'name_first': 'Bob', 'name_last': 'Ross',
                                          'handle_str': 'bobross01'}]}

def test_users_all_invalid_token(url):
    '''Test for empty output when users_all() is given an invalid token'''
    requests.delete(url + 'clear')
    response = requests.get(url + 'users/all', params={'token': 'Invalid'})
    assert response.json()['code'] == 400

# admin_userpermission_change
def test_admin_userpermission_change(url):
    '''Test admin_userpermission_change for correct output'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'auth/register', json=good_reg_2)
    # Give u_id = 2 owner permission
    response = requests.post(url + 'admin/userpermission/change', json={'token': u_1['token'],
                                                                        'u_id': 2,
                                                                        'permission_id': 1})
    assert response.json() == {}

def test_admin_userpermission_change2(url):
    '''Test admin_userpermission_change for correct output'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'admin/userpermission/change', json={'token': u_1['token'],
                                                                        'u_id': 1,
                                                                        'permission_id': 2})
    assert response.json() == {}

def test_admin_userpermission_change_invalid_uid(url):
    '''Test if admin_userpermission_change correctly raises InputError given
    invalid u_id'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'admin/userpermission/change', json={'token': u_1['token'],
                                                                        'u_id': 2,
                                                                        'permission_id': 1})
    assert response.json()['code'] == 400

def test_admin_userpermission_change_invalid_permission(url):
    '''Test if admin_userpermission_change correctly raises InputError given
    invalid permission_id'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'auth/register', json=good_reg_2)
    response = requests.post(url + 'admin/userpermission/change', json={'token': u_1['token'],
                                                                        'u_id': 2,
                                                                        'permission_id': 3})
    assert response.json()['code'] == 400


# Access errors
def test_admin_userpermission_change_auth_not_owner(url):
    '''Test if admin_userpermission_change correctly raises AccessError if authorised
    user is not an owner'''
    requests.delete(url + 'clear')
    requests.post(url + 'auth/register', json=good_reg_1)
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    response = requests.post(url + 'admin/userpermission/change', json={'token': u_2['token'],
                                                                        'u_id': 1,
                                                                        'permission_id': 2})
    assert response.json()['code'] == 400

# search
def test_search_one_message(url):
    '''Test if search returns correct output for one message'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    requests.post(url + 'message/send', json={'token': u_1['token'],
                                              'channel_id': 1,
                                              'message': 'Hello world!'})
    response = requests.get(url + 'search', params={'token': u_1['token'],
                                                    'query_str': 'Hello'})
    # Check if message with query string is returned by search()
    assert response.json()['messages'][0]['message'] == 'Hello world!'

def test_search_same_message_diff_users(url):
    '''Test if search returns correct output if different users send the same message'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    requests.post(url + 'channel/join', json={'token': u_2['token'],
                                              'channel_id': 1})
    requests.post(url + 'message/send', json={'token': u_1['token'],
                                              'channel_id': 1,
                                              'message': 'Hello world!'})
    requests.post(url + 'message/send', json={'token': u_2['token'],
                                              'channel_id': 1,
                                              'message': 'Hello world!'})
    response = requests.get(url + 'search', params={'token': u_1['token'],
                                                    'query_str': 'Hello'})
    # Check if messages containing query string is returned by search()
    assert response.json()['messages'][0]['message'] == 'Hello world!'
    assert response.json()['messages'][1]['message'] == 'Hello world!'

def test_search_private(url):
    '''Test if search returns correct output for messages sent in private channels'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': False})
    requests.post(url + 'message/send', json={'token': u_1['token'],
                                              'channel_id': 1,
                                              'message': 'Hello world!'})
    response = requests.get(url + 'search', params={'token': u_1['token'],
                                                    'query_str': 'Hello'})
    # Check if messages containing query string is returned by search()
    assert response.json()['messages'][0]['message'] == 'Hello world!'

def test_search_different_case(url):
    '''Test if search returns correct output when query string is different case
    to matching messages'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    requests.post(url + 'message/send', json={'token': u_1['token'],
                                              'channel_id': 1,
                                              'message': 'hello!'})
    requests.post(url + 'message/send', json={'token': u_1['token'],
                                              'channel_id': 1,
                                              'message': 'HELLO!'})
    requests.post(url + 'message/send', json={'token': u_1['token'],
                                              'channel_id': 1,
                                              'message': 'hELLo!'})
    response = requests.get(url + 'search', params={'token': u_1['token'],
                                                    'query_str': 'Hello'})
    # Check if messages containing query string is returned by search()
    assert response.json()['messages'][0]['message'] == 'hELLo!'
    assert response.json()['messages'][1]['message'] == 'HELLO!'
    assert response.json()['messages'][2]['message'] == 'hello!'

def test_search_no_match(url):
    '''Test if search returns correct output when query string does not match any messages'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    requests.post(url + 'message/send', json={'token': u_1['token'],
                                              'channel_id': 1,
                                              'message': 'Hello world!'})
    response = requests.get(url + 'search', params={'token': u_1['token'],
                                                    'query_str': 'YOYO'})
    assert response.json()['messages'] == []

# standup tests   
def test_standup_start(url):
    '''Test if standup_start() returns the correct output when given valid input'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    # Calculate finish time rounded to nearest 10
    finish_time = round((datetime.now() + timedelta(seconds=1)).timestamp() / 10) * 10
    response = requests.post(url + 'standup/start', json={'token': u_1['token'],
                                                          'channel_id': 1,
                                                          'length': 1})
    
    # Compare function time_finish to correct time_finish rounded to nearest 10
    assert round(response.json()['time_finish'] / 10) * 10 == finish_time

def test_standup_start_invalid_channel_id(url):
    '''Test if standup_start() returns the correct output when given invalid channel_id'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'standup/start', json={'token': u_1['token'],
                                                         'channel_id': 1,
                                                         'length': 10})
    # channel_id = 1 does not exist
    assert response.json()['code'] == 400

def test_standup_start_standup_already_running(url):
    '''Test if standup_start() returns the correct output when there is a standup 
    already running'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    requests.post(url + 'standup/start', json={'token': u_1['token'],
                                               'channel_id': 1,
                                               'length': 8})
    response = requests.post(url + 'standup/start', json={'token': u_1['token'],
                                                          'channel_id': 1,
                                                          'length': 1})
    # channel_id = 1 does not exist
    assert response.json()['code'] == 400

def test_standup_active(url):
    '''Test if standup_active() returns the correct output when given valid input'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    response = requests.post(url + 'standup/start', json={'token': u_1['token'],
                                                          'channel_id': 1,
                                                          'length': 10})
    finish_time = response.json()['time_finish']
    response = requests.get(url + 'standup/active', params={'token': u_1['token'],
                                                            'channel_id': 1})
    assert response.json() == {'is_active': True, 'time_finish': finish_time}

def test_standup_active_no_active(url):
    '''Test if standup_active() returns the correct output when there is no
    standup active'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    response = requests.get(url + 'standup/active', params={'token': u_1['token'],
                                                    'channel_id': 1})
    assert response.json() == {'is_active': False, 'time_finish': None}

def test_standup_active_invalid_channel(url):
    '''Test if standup_active() returns the correct output when given invalid channel_id'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.get(url + 'standup/active', params={'token': u_1['token'],
                                                            'channel_id': 2})
    assert response.json()['code'] == 400

def test_standup_send_valid(url):
    '''Test standup_send for correct output'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    requests.post(url + 'standup/start', json={'token': u_1['token'],
                                               'channel_id': 1,
                                               'length': 10})
    response = requests.post(url + 'standup/send', json={'token': u_1['token'],
                                                         'channel_id': 1,
                                                         'message': 'YOYO'})
    assert response.json() == {}

def test_standup_send_invalid_channel(url):
    '''Test if standup_send() returns the correct output when given invalid channel_id'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'standup/send', json={'token': u_1['token'],
                                                         'channel_id': 1,
                                                         'message': 'YOYO'})
    # channel_id = 1 does not exist
    assert response.json()['code'] == 400

def test_standup_send_message_too_long(url):
    '''Test if standup_send() returns the correct output when message is over 1000
    characters'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    requests.post(url + 'standup/start', json={'token': u_1['token'],
                                               'channel_id': 1,
                                               'length': 10})
    response = requests.post(url + 'standup/send', json={'token': u_1['token'],
                                                         'channel_id': 1,
                                                         'message': LONG_MESSAGE})
    assert response.json()['code'] == 400

def test_standup_send_no_standup(url):
    '''Test if standup_send() returns the correct output when there is no active standup'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    response = requests.post(url + 'standup/send', json={'token': u_1['token'],
                                                         'channel_id': 1,
                                                         'message': 'YOYO'})
    assert response.json()['code'] == 400

def test_standup_send_not_member(url):
    '''Test if standup_send() returns the correct output when authorised user is
    not a member of the channel that standup is in'''
    requests.delete(url + 'clear')
    response = requests.post(url + 'auth/register', json=good_reg_1)
    u_1 = response.json()
    response = requests.post(url + 'auth/register', json=good_reg_2)
    u_2 = response.json()
    requests.post(url + 'channels/create', json={'token': u_1['token'],
                                                 'name': 'First channel',
                                                 'is_public': True})
    response = requests.post(url + 'standup/send', json={'token': u_2['token'],
                                                         'channel_id': 1,
                                                         'message': 'YOYO'})
    assert response.json()['code'] == 400
