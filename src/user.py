'''
This file contains user_profile, user_profile_setname
                   user_profile_setemail, user_profile_sethandle, user_profile_uploadphoto
'''
import os
from io import BytesIO
from PIL import Image
import requests
from global_vars import data
from channels import channels_list
from helper import find_user, find_user_in_all, find_user_in_owners
from error_checks import check_valid_email, check_existing_email, check_first_name, \
                         check_last_name
from error import InputError

def user_profile(token, u_id):
    '''
    This function returns the info of the user with a given u_id
    '''
    # Check if token is valid or not.
    find_user(token)

    # Check if u_id is valid ot not.
    # If u_id is valid, return the user info.
    for user in data['users']:
        if user['u_id'] == u_id:
            user_info = {'u_id': user['u_id'], 'email': user['email'],
                         'name_first': user['name_first'],
                         'name_last': user['name_last'], 'handle_str': user['handle_str'],
                         'profile_img_url': user['profile_img_url'],}
            return {'user' : user_info}
    raise InputError(description='Invalid u_id')

def user_profile_setname(token, name_first, name_last):
    '''
    This function set a new name for the user.
    '''
    # Check if token is valid or not.
    user = find_user(token)

    # Error checking:
    check_first_name(name_first)
    check_last_name(name_last)

    # Look for the user and modify with the new name
    data['users'][user['u_id'] - 1]['name_first'] = name_first
    data['users'][user['u_id'] - 1]['name_last'] = name_last

    # Look for the channels that user is part of and change the name info
    for channel in data['channels']:
        if find_user_in_owners(user['u_id'], channel['channel_id']):
            for users in channel['owner_members']:
                if users['u_id'] == user["u_id"]:
                    users['name_first'] = name_first
                    users['name_last'] = name_last
        if find_user_in_all(user['u_id'], channel['channel_id']):
            for users in channel['all_members']:
                if users['u_id'] == user["u_id"]:
                    users['name_first'] = name_first
                    users['name_last'] = name_last

    return {}

def user_profile_setemail(token, email):
    '''
    This function set a new email for the user.
    '''
    # Check if token is valid or not.
    # If token is valid, record user dictionary.
    auth_user = find_user(token)

    check_valid_email(email)
    check_existing_email(email)

    # Look for the user and modify with given the email
    data['users'][auth_user['u_id'] - 1]['email'] = email

    return {
    }

def user_profile_sethandle(token, handle_str):
    '''
    This function set a new handle for the user.
    '''
    # Check if token is valid or not.
    auth_user = find_user(token)

    # Check if handle is valid or not.
    # If handle is invalid, raise Inpur Error
    if len(handle_str) < 3:
        raise InputError(description="Too short handle")
    if len(handle_str) > 20:
        raise InputError(description="Too long handle")

    # Check if handle is already taken.
    # If it's taken, raise Input Error.
    for user in data['users']:
        if user['handle_str'] == handle_str:
            raise InputError(description='handle already taken')

    # Look for the user and modify with the given handle
    data['users'][auth_user['u_id'] - 1]['handle_str'] = handle_str

    return {
    }

def user_profile_uploadphoto(host, token, img_url, coordinates):
    '''
    This function updates a profile photo with a given img url and coordinates.
    '''
    # Check if token is valid or not.
    user = find_user(token)

    response = requests.get(img_url)
    # Check if img_url is working fine.
    if response.status_code != 200:
        raise InputError(description='There is a problem with a given image url.')

    img = Image.open(BytesIO(response.content))
    _, _, width, height = list(img.getbbox())

    # Check if coordinates are in appropriate boundry.
    if coordinates['x_start'] < 0 or coordinates['x_start'] > width or\
       coordinates['x_end'] < 0 or coordinates['x_end'] > width:
        raise InputError(description='You can not crop an image with the size you have chosen.')
    if coordinates['y_start'] < 0 or coordinates['y_start'] > height or\
       coordinates['y_end'] < 0 or coordinates['y_end'] > height:
        raise InputError(description='You can not crop an image with the size you have chosen.')

    # Check if image file is in jpg form.
    if img.format != 'JPEG' and img.format != 'JPG':
        raise InputError(description='You need to bring a image in jpg/jpeg form.')

    profile_img_url = f"http://{host}/imgurl/{user['u_id']}.jpg"

    # Update new profile photo.
    # 1. update user.
    data['users'][user['u_id']-1]['profile_img_url'] = profile_img_url
    # 2. update channels which user is part of.
    for channel in channels_list(token)['channels']:
        for users in data['channels'][channel['channel_id']-1]['all_members']:
            if users['u_id'] == user['u_id']:
                users['profile_img_url'] = profile_img_url
        for users in data['channels'][channel['channel_id']-1]['owner_members']:
            if users['u_id'] == user['u_id']:
                users['profile_img_url'] = profile_img_url

    cropped_img = img.crop((coordinates['x_start'], coordinates['y_start'],\
                            coordinates['x_end'], coordinates['y_end']))
    # Make a directory called imgurl (if not exists)
    # Save copy of cropped imgaed in this dir.
    if not os.path.isdir(str(os.getcwd())+'/imgurl'):
        os.mkdir(str(os.getcwd())+'/imgurl')
    os.chdir(str(os.getcwd())+'/imgurl')
    file_pointer = open(f"{user['u_id']}.jpg", "w+")
    cropped_img = cropped_img.save(f"{user['u_id']}.jpg")
    file_pointer.close()
    os.chdir(str(os.getcwd())+'/..')

    return {}
