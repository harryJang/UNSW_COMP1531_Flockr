"""
Imported hashlib to encrypt user passwords
Imported jwt to generate tokens
Imported data dictionary that stores user information
Imported errors to deal with exceptions
Imported re module to determine validity of emails
"""
import smtplib
import ssl
from helper import generate_handle_string, encrypted, get_reset_code, generate_token
from error_checks import check_valid_email, check_existing_email, check_password_len, \
                         check_first_name, check_last_name
from global_vars import data, code
from error import InputError, AccessError

def auth_login(email, password):
    """Login with the given email and password"""
    check_valid_email(email)
    for user in data['users']:
        if user['email'] == email:
            if user['password'] == encrypted(password):
                token = generate_token(user['u_id'])
                return {
                    'u_id': user['u_id'],
                    'token': token,
                }
            raise InputError(description='Incorrect password')
    raise InputError(description='Email does not belong to a user')

def auth_logout(token):
    """Logout the user if token is valid"""
    if token in data['online']:
        data['online'].remove(token)
        return {'is_success': True}
    raise AccessError(description='Invalid token')

def auth_register(email, password, name_first, name_last):
    """Make a new user from the given information"""

    # Error checking:
    check_valid_email(email)
    check_existing_email(email)
    check_password_len(password)
    check_first_name(name_first)
    check_last_name(name_last)

    # Creating new user dictionary
    num_of_users = len(data['users'])
    u_id = num_of_users + 1
    new_user = {'u_id': u_id, 'email': email, 'password': encrypted(password),
                'name_first': name_first, 'name_last': name_last,
                'profile_img_url': '', }

    # Generating unique handle string
    new_user['handle_str'] = generate_handle_string(name_first, name_last)

    # Setting default permission id
    if u_id == 1:
        new_user['permission_id'] = 1
    else:
        new_user['permission_id'] = 2
    data['users'].append(new_user)

    token = generate_token(u_id)

    return {
        'u_id': u_id,
        'token': token,
    }

def auth_passwordreset_request(receiver_email):
    """receive a password reset request and send a reset code to the user"""
    found = 0
    for user in data['users']:
        if user['email'] == receiver_email:
            u_id = user['u_id']
            found = 1
    # User with a given email exists.
    if found == 1:
        port = 465
        smtp_server = "smtp.gmail.com"
        sender_email = "itisfortesting112@gmail.com"
        password = "testing12345!!"
        message = get_reset_code()
        user_reset_code = {'u_id': u_id, 'code': message}
        code.append(user_reset_code)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
    return {}

def auth_passwordreset_reset(reset_code, new_password):
    """With a given code and password, reset password."""
    # Check if code is valid
    # If it's found, copy u_id and remove it from the list.
    u_id = None
    for users in code:
        if users['code'] == reset_code:
            u_id = users['u_id']
            code.remove(users)

    if u_id is None:
        raise InputError(description='Your have entered wrong code.')

    check_password_len(new_password)
    data['users'][u_id-1]['password'] = encrypted(new_password)

    return {}
