'''
This file contains testing for the u_1 functions
'''
import string
from hypothesis import given, strategies
import pytest
from other import clear
from error import InputError, AccessError
from user import user_profile, user_profile_setname, user_profile_setemail, \
                 user_profile_sethandle, user_profile_uploadphoto
from channels import channels_create
from global_vars import data
from channel import channel_invite, channel_addowner
from fixtures import register_3_users

LION_IMAGE_URL = 'https://images.unsplash.com/photo-1533450718592-\
                  29d45635f0a9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=\
                  format&fit=crop&w=1950&q=80'
# user_profile

def test_userprofile_valid_self_profile():
    '''
    case : u_1 is accessing own profile.
    return : return u_1's profile
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    assert user_profile(u_1['token'], u_1['u_id']) ==\
    {'user': {'email': 'good_email1@gmail.com',
              'handle_str': 'bobross00',
              'name_first': 'Bob',
              'name_last': 'Ross',
              'u_id': 1,
              'profile_img_url': ''}}


def test_userprofile_valid_others_profile():
    '''
    case : u_1 is accessing other's profile.
    return : return other's profile
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    assert user_profile(u_1['token'], u_2['u_id']) ==\
    {'user': {'email': 'good_email2@hotMAIL.com',
              'handle_str': 'lobmoss00',
              'name_first': 'Lob',
              'name_last': 'Moss',
              'u_id': 2,
              'profile_img_url': ''}}

def test_userprofile_invalid_u_id():
    '''
    case : u_1 is accessing no one's profile.
    return : Input Error raised
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        assert user_profile(u_1['token'], 4)

def test_userprofile_invalid_token():
    '''
    case : u_1 is accessing other's profile with invalid token.
    return : Access Error raised
    '''
    clear()
    register_3_users()
    with pytest.raises(AccessError):
        assert user_profile('Invalid Token', 1)

# user_profile_setname

def test_userprofilesetname_valid_name_change():
    '''
    case : u_1 is changing name.
    return : empty dics.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    user_profile_setname(u_1['token'], 'New', 'Name')
    profile = user_profile(u_2['token'], u_1['u_id'])
    assert profile['user']['name_first'] == 'New'
    assert profile['user']['name_last'] == 'Name'

@given(strategies.text(alphabet=string.printable, min_size=1, max_size=50))
def test_userprofilesetname_valid_name_change_intensive(input_string):
    '''Extra property based tests for valid name changes'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    user_profile_setname(u_1['token'], input_string, input_string)
    profile = user_profile(u_2['token'], u_1['u_id'])
    assert profile['user']['name_first'] == input_string
    assert profile['user']['name_last'] == input_string

def test_userprofilesetname_valid_name_change_channel_info():
    '''
    case : u_1 is changing name. Also u_1 is included in a channel.
           Need to change info stored in channels as well.
    return : empty disc.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    profile = user_profile(u_2['token'], u_1['u_id'])
    assert profile['user']['name_first'] == 'Bob'
    assert profile['user']['name_last'] == 'Ross'

    channel = channels_create(u_1['token'], 'First channel', True)
    channels_create(u_2['token'], 'Second channel', True)
    channel_id = channel['channel_id']
    channel_invite(u_1['token'], channel_id, u_2['u_id'])
    channel_addowner(u_1['token'], channel_id, u_2['u_id'])
    assert data['channels'][channel_id - 1]['owner_members'][0]['name_first'] == 'Bob'
    assert data['channels'][channel_id - 1]['owner_members'][0]['name_last'] == 'Ross'
    assert data['channels'][channel_id - 1]['all_members'][0]['name_first'] == 'Bob'
    assert data['channels'][channel_id - 1]['all_members'][0]['name_last'] == 'Ross'

    user_profile_setname(u_1['token'], 'New', 'Name')

    assert data['channels'][channel_id - 1]['owner_members'][0]['name_first'] == 'New'
    assert data['channels'][channel_id - 1]['owner_members'][0]['name_last'] == 'Name'
    assert data['channels'][channel_id - 1]['all_members'][0]['name_first'] == 'New'
    assert data['channels'][channel_id - 1]['all_members'][0]['name_last'] == 'Name'

def test_userprofilesetname_valid_name_change_multi_channel_info():
    '''
    case : u_1 is changing name. Also u_1 is included in multiple channels.
           Need to change info stored in channels as well.
    return : empty disc.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    profile = user_profile(u_2['token'], u_1['u_id'])
    assert profile['user']['name_first'] == 'Bob'
    assert profile['user']['name_last'] == 'Ross'

    channels_create(u_2['token'], 'channel', True)
    channel_1 = channels_create(u_1['token'], 'First channel', True)
    channel_id_1 = channel_1['channel_id']
    channel_2 = channels_create(u_1['token'], 'Second channel', True)
    channel_id_2 = channel_2['channel_id']
    channel_invite(u_1['token'], channel_id_1, u_2['u_id'])
    channel_addowner(u_1['token'], channel_id_1, u_2['u_id'])
    channel_invite(u_1['token'], channel_id_2, u_2['u_id'])
    channel_addowner(u_1['token'], channel_id_2, u_2['u_id'])
    assert data['channels'][channel_id_1 - 1]['owner_members'][0]['name_first'] == 'Bob'
    assert data['channels'][channel_id_1 - 1]['owner_members'][0]['name_last'] == 'Ross'
    assert data['channels'][channel_id_1 - 1]['all_members'][0]['name_first'] == 'Bob'
    assert data['channels'][channel_id_1 - 1]['all_members'][0]['name_last'] == 'Ross'
    assert data['channels'][channel_id_2 - 1]['owner_members'][0]['name_first'] == 'Bob'
    assert data['channels'][channel_id_2 - 1]['owner_members'][0]['name_last'] == 'Ross'
    assert data['channels'][channel_id_2 - 1]['all_members'][0]['name_first'] == 'Bob'
    assert data['channels'][channel_id_2 - 1]['all_members'][0]['name_last'] == 'Ross'

    user_profile_setname(u_1['token'], 'New', 'Name')

    assert data['channels'][channel_id_1 - 1]['owner_members'][0]['name_first'] == 'New'
    assert data['channels'][channel_id_1 - 1]['owner_members'][0]['name_last'] == 'Name'
    assert data['channels'][channel_id_1 - 1]['all_members'][0]['name_first'] == 'New'
    assert data['channels'][channel_id_1 - 1]['all_members'][0]['name_last'] == 'Name'
    assert data['channels'][channel_id_2 - 1]['owner_members'][0]['name_first'] == 'New'
    assert data['channels'][channel_id_2 - 1]['owner_members'][0]['name_last'] == 'Name'
    assert data['channels'][channel_id_2 - 1]['all_members'][0]['name_first'] == 'New'
    assert data['channels'][channel_id_2 - 1]['all_members'][0]['name_last'] == 'Name'

def test_userprofilesetname_invalid_first_name_over_50():
    '''
    case : given first name is longer than 50 chars.
    return : Input Error raised.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        assert user_profile_setname(u_1['token'],\
            'really really really really really really really long new', 'Name')


def test_userprofilesetname_invalid_first_name_empty():
    '''
    case : given first name is empty.
    return : Input Error raised.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        assert user_profile_setname(u_1['token'], '', 'Name')

def test_userprofilesetname_invalid_last_name_over_50():
    '''
    case : given last name is longer than 50 chars.
    return : Input Error raised.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        assert user_profile_setname(u_1['token'], 'New',\
            'really really really really really really long name')

def test_userprofilesetname_invalid_last_name_empty():
    '''
    case : given last name is empty.
    return : Input Error raised.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        assert user_profile_setname(u_1['token'], 'New', '')

def test_userprofilesetname_invalid_token():
    '''
    case : u_1 is accessing with invalid token.
    return : Access Error raised
    '''
    clear()
    register_3_users()
    with pytest.raises(AccessError):
        assert user_profile_setname('Invalid Token', 'New', 'Name')

# user_profile_setemail

def test_useprofilesetemail_valid_email_change():
    '''
    case : u_1 is changing email.
    return : empty dictionary
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    profile = user_profile(u_1['token'], u_1['u_id'])
    assert profile['user']['email'] == 'good_email1@gmail.com'

    user_profile_setemail(u_1['token'], "good_email4@hotMAIL.com")
    profile = user_profile(u_2['token'], u_1['u_id'])
    assert profile['user']['email'] == 'good_email4@hotMAIL.com'

@given(strategies.text(alphabet=string.ascii_lowercase + string.digits, min_size=2))
def test_useprofilesetemail_valid_email_change_intensive(input_string):
    '''Extra property based testing for valid emails'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    profile = user_profile(u_1['token'], u_1['u_id'])
    assert profile['user']['email'] == 'good_email1@gmail.com'

    user_profile_setemail(u_1['token'], input_string + '@gmail.com')
    profile = user_profile(u_2['token'], u_1['u_id'])
    assert profile['user']['email'] == input_string + '@gmail.com'

def test_userprofilesetemail_invalid_email():
    '''
    case : u_1 is trying to change email with invalid one
    return : Input Error raised.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        assert user_profile_setemail(u_1['token'], "bad_email@nofullstops")

def test_userprofilesetemail_invalid_used_email():
    '''
    case : u_1 is trying to change email with the one already used
    return : Input Error raised.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        assert user_profile_setemail(u_1['token'], "good_email2@hotMAIL.com")

def test_userprofilesetemail_invalid_token():
    '''
    case : u_1 is accessing with invalid token.
    return : Access Error raised
    '''
    clear()
    register_3_users()
    with pytest.raises(AccessError):
        assert user_profile_setemail('Invalid Token', 'good_email2@hotMAIL.com')

# user_profile_sethandle

def test_userprofilesethandle_valid_handle_change():
    '''
    case : u_1 is changing handle.
    return : empty dictionary
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    profile = user_profile(u_1['token'], u_1['u_id'])
    assert profile['user']['handle_str'] == 'bobross00'

    user_profile_sethandle(u_1['token'], 'potterjang00')
    profile = user_profile(u_2['token'], u_1['u_id'])
    assert profile['user']['handle_str'] == 'potterjang00'

@given(strategies.text(alphabet=string.printable, min_size=3, max_size=20))
def test_userprofilesethandle_valid_handle_change_intensive(input_string):
    '''Extra property based tests for valid handle strings'''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    profile = user_profile(u_1['token'], u_1['u_id'])
    assert profile['user']['handle_str'] == 'bobross00'

    user_profile_sethandle(u_1['token'], input_string)
    profile = user_profile(u_2['token'], u_1['u_id'])
    assert profile['user']['handle_str'] == input_string

def test_userprofilesethandle_invalid_handle_less_3():
    '''
    case : u_1 is trying to change handle less than 3 chars.
    return : Input Error raised.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        assert user_profile_sethandle(u_1['token'], 'ds')

def test_userprofilesethandle_invalid_handle_greater_20():
    '''
    case : u_1 is trying to change handle greater than 20 chars.
    return : Input Error raised.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        assert user_profile_sethandle(u_1['token'], 'longlonglonglonglonghandle')

def test_userprofilesethandle_invalid_handle_used():
    '''
    case : u_1 is trying to change handle already taken.
    return : Input Error raised.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    with pytest.raises(InputError):
        assert user_profile_sethandle(u_1['token'], 'lobmoss00')

def test_userprofilesethandle_invalid_token():
    '''
    case : u_1 is accessing with invalid token.
    return : Access Error raised
    '''
    clear()
    register_3_users()
    with pytest.raises(AccessError):
        assert user_profile_sethandle('Invalid Token', 'potterjang00')

# user_profile_uploadphoto

def test_userprofile_valid_uploadphoto():
    '''
    case : u_1 is changing profile image.
    return : empty dictionary.
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    channels_create(u_1['token'], 'First channel', True)
    channel_invite(u_1['token'], u_1['u_id'], u_2['u_id'])
    channel_addowner(u_1['token'], u_1['u_id'], u_2['u_id'])
    coordinates = {'x_start':0, 'y_start':0, 'x_end':1950, 'y_end':1300}
    assert user_profile_uploadphoto('localhost:8080', u_1['token'], 'https://images.unsplash.com/\
photo-1533450718592-29d45635f0a9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=forma\
t&fit=crop&w=1950&q=80', coordinates) == {}
    assert user_profile_uploadphoto('localhost:8080', u_2['token'], \
    'https://images.unsplash.com/photo-1533450718592-29d45635f0a9?ixlib=rb-1.2.1\
    &ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1950&q=80', coordinates) == {}

    # Check if the u_1 info has updated correctly
    profile = user_profile(u_1['token'], u_1['u_id'])
    assert profile['user']['profile_img_url'] == 'http://localhost:8080/imgurl/1.jpg'

    # Chcek if the u_1 info has updated correctly in the channels that u_1 is part of
    assert data['channels'][0]['owner_members'][0]['profile_img_url'] ==\
         'http://localhost:8080/imgurl/1.jpg'

    assert data['channels'][0]['all_members'][0]['profile_img_url'] == \
        'http://localhost:8080/imgurl/1.jpg'

def test_userprofile_uploadphoto_invalid_token():
    '''
    case : u_1 is accessing with invalid token.
    return : Access Error raised
    '''
    clear()
    register_3_users()
    coordinates = {'x_start':0, 'y_start':0, 'x_end':1950, 'y_end':1300}
    with pytest.raises(AccessError):
        assert user_profile_uploadphoto('localhost:8080', 'Invalid Token',\
                                        LION_IMAGE_URL, coordinates)

def test_userprofile_invalid_url():
    '''
    case : u_1 is trying to access invalid url.
    return : Input Error raised
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    coordinates = {'x_start':0, 'y_start':0, 'x_end':1950, 'y_end':1300}
    with pytest.raises(InputError):
        assert user_profile_uploadphoto('localhost:8080', u_1['token'],\
                                        'https://images.unsplash.com\
/photo-718592-29d45635f0a9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=f\
ormat&fit=crop&w=1950&q=80', coordinates)

def test_userprofile_invalid_coordinates_x_start_lower():
    '''
    case : u_1 is trying to crop an image with invalid coordinates.
    return : Input Error raised
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    coordinates = {'x_start':-1, 'y_start':0, 'x_end':1950, 'y_end':1300}
    with pytest.raises(InputError):
        assert user_profile_uploadphoto('localhost:8080', u_1['token'],\
                                        LION_IMAGE_URL, coordinates)

def test_userprofile_invalid_coordinates_y_start_lower():
    '''
    case : u_1 is trying to crop an image with invalid coordinates.
    return : Input Error raised
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    coordinates = {'x_start':0, 'y_start':-1, 'x_end':1950, 'y_end':1300}
    with pytest.raises(InputError):
        assert user_profile_uploadphoto('localhost:8080', u_1['token'],\
                                        LION_IMAGE_URL, coordinates)

def test_userprofile_invalid_coordinates_x_start_over():
    '''
    case : u_1 is trying to crop an image with invalid coordinates.
    return : Input Error raised
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    coordinates = {'x_start':2000, 'y_start':0, 'x_end':1950, 'y_end':1300}
    with pytest.raises(InputError):
        assert user_profile_uploadphoto('localhost:8080', u_1['token'],\
                                        LION_IMAGE_URL, coordinates)

def test_userprofile_invalid_coordinates_y_start_over():
    '''
    case : u_1 is trying to crop an image with invalid coordinates.
    return : Input Error raised
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    coordinates = {'x_start':0, 'y_start':1400, 'x_end':1950, 'y_end':1300}
    with pytest.raises(InputError):
        assert user_profile_uploadphoto('localhost:8080', u_1['token'],\
                                        LION_IMAGE_URL, coordinates)

def test_userprofile_invalid_coordinates_x_end_lower():
    '''
    case : u_1 is trying to crop an image with invalid coordinates.
    return : Input Error raised
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    coordinates = {'x_start':0, 'y_start':0, 'x_end':-1, 'y_end':1300}
    with pytest.raises(InputError):
        assert user_profile_uploadphoto('localhost:8080', u_1['token'],\
                                        LION_IMAGE_URL, coordinates)

def test_userprofile_invalid_coordinates_y_end_lower():
    '''
    case : u_1 is trying to crop an image with invalid coordinates.
    return : Input Error raised
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    coordinates = {'x_start':0, 'y_start':0, 'x_end':1950, 'y_end':-1}
    with pytest.raises(InputError):
        assert user_profile_uploadphoto('localhost:8080', u_1['token'],\
                                        LION_IMAGE_URL, coordinates)

def test_userprofile_invalid_coordinates_x_end_over():
    '''
    case : u_1 is trying to crop an image with invalid coordinates.
    return : Input Error raised
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    coordinates = {'x_start':0, 'y_start':0, 'x_end':2000, 'y_end':1300}
    with pytest.raises(InputError):
        assert user_profile_uploadphoto('localhost:8080', u_1['token'],\
                                        LION_IMAGE_URL, coordinates)

def test_userprofile_invalid_coordinates_y_end_over():
    '''
    case : u_1 is trying to crop an image with invalid coordinates.
    return : Input Error raised
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    coordinates = {'x_start':0, 'y_start':0, 'x_end':1950, 'y_end':1400}
    with pytest.raises(InputError):
        assert user_profile_uploadphoto('localhost:8080', u_1['token'],\
                                        LION_IMAGE_URL, coordinates)

def test_userprofile_image_not_jpg():
    '''
    case : given image is not in a form of jpg.
    return : Input Error raised
    '''
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    coordinates = {'x_start':0, 'y_start':0, 'x_end':450, 'y_end':520}
    with pytest.raises(InputError):
        assert user_profile_uploadphoto('localhost:8080', u_1['token'],\
                                        'https://upload.wikimedia.org/wi\
kipedia/commons/e/e9/Felis_silvestris_silvestris_small_gradual_decrease_of_quality.png',\
                                    coordinates)
