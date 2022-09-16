"""
Imported the functions from auth to test
Imported pytest and errors for testing
Imported jwt to decode the token
Imported clear function to clear data dictionary after every test
"""
import string
import pytest
from hypothesis import given, strategies
from global_vars import data, code
from helper import encrypted, generate_token
from error import InputError, AccessError
from auth import auth_login, auth_logout, auth_register,\
                 auth_passwordreset_reset, auth_passwordreset_request
from other import clear
from user import user_profile
from fixtures import register_3_users

# Valid cases:
def test_auth_login_valid():
    """Tests for valid logins"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    u_3 = registers[2]
    auth_logout(u_1['token'])
    auth_logout(u_2['token'])
    auth_logout(u_3['token'])
    assert auth_login("good_email1@gmail.com", "111111") == u_1
    assert auth_login("good_email2@hotMAIL.com", "123456") == u_2
    assert auth_login("good_email3@outlook.com", "abc123") == u_3

# Error cases:
def test_auth_login_bad_email_exception1():
    """Bad email: No @ sign"""
    clear()
    with pytest.raises(InputError):
        assert auth_login("bad_email.com", "123456")
def test_auth_login_bad_email_exception2():
    """Bad email: No full stops after @"""
    clear()
    with pytest.raises(InputError):
        assert auth_login("bad_email@nofullstops", "123456")
def test_auth_login_bad_email_exception3():
    """Bad email: Capital letters before @"""
    clear()
    with pytest.raises(InputError):
        assert auth_login("BAD_EMAIL@gmail.com", "123456")
def test_auth_login_non_existing_email_exception():
    """Non existing account with the given email"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    auth_logout(u_1['token'])
    with pytest.raises(InputError):
        assert auth_login("non_existant@gmail.com", "123456")
def test_auth_login_password_exception():
    """Existing account/email but wrong password"""
    clear()
    register_3_users()
    with pytest.raises(InputError):
        assert auth_login("good_email1@gmail.com", "wrongpass")

# Valid cases:
def test_auth_logout_valid():
    """Valid logouts"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    assert auth_logout(u_1['token']) == {'is_success': True}

# Error cases:
def test_auth_logout_exception():
    """Invalid token/logout"""
    clear()
    register_3_users()
    with pytest.raises(AccessError):
        assert auth_logout('invalid')

# Valid cases:
def test_auth_register_valid():
    """Valid registers"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    u_2 = registers[1]
    assert u_1['u_id'] == 1
    assert generate_token(1) == u_1['token']
    assert u_2['u_id'] == 2
    assert generate_token(2) == u_2['token']

# Error cases:
def test_auth_register_email_exception1():
    """Bad email: No @ sign"""
    clear()
    with pytest.raises(InputError):
        assert auth_register("bad_email.com", "123456", "Bob", "Ross")
def test_auth_register_email_exception2():
    """Bad email: No full stops after @"""
    clear()
    with pytest.raises(InputError):
        assert auth_register("bad_email@nofullstops", "123456", "Bob", "Ross")
def test_auth_register_email_exception3():
    """Bad email: Capital letters before @"""
    clear()
    with pytest.raises(InputError):
        assert auth_register("BAD_EMAIL@gmail.com", "123456", "Bob", "Ross")
def test_auth_register_existing_email_exception():
    """Trying to register with an email that already exists in the database"""
    clear()
    register_3_users()
    with pytest.raises(InputError):
        assert auth_register("good_email1@gmail.com", "111111", "Bob", "Ross")
def test_auth_register_password_len_exception():
    """Password too short"""
    clear()
    with pytest.raises(InputError):
        assert auth_register("good_email6@gmail.com", "sh0rt", "Bob", "Ross")
def test_auth_register_first_name_exception1():
    """First name too short"""
    clear()
    with pytest.raises(InputError):
        assert auth_register("good_email@gmail.com", "goodsize", "", "Ross")
def test_auth_register_first_name_exception2():
    """First name too long"""
    clear()
    with pytest.raises(InputError):
        assert auth_register("good_email@gmail.com", "goodsize", \
                             "Abcdefghijklmnopqrstuvwxyz1234567891234567891231231", "Ross")
def test_auth_register_last_name_exception1():
    """Last name too short"""
    clear()
    with pytest.raises(InputError):
        assert auth_register("good_email@gmail.com", "goodsize", \
                             "Bob", "")
def test_auth_register_last_name_exception2():
    """First name too long"""
    clear()
    with pytest.raises(InputError):
        assert auth_register("good_email@gmail.com", "goodsize", \
                             "Bob", "Abcdefghijklmnopqrstuvwxyz1223334444555556666661111")

# Additional property based intensive tests
# Email registering
@given(strategies.text(alphabet=string.ascii_lowercase + string.digits))
def test_auth_register_email_intensive(input_string):
    """Property based testing for email registers"""
    clear()
    if not input_string:
        # Skipping case when it is an empty string since frontend blocks this
        return
    if len(input_string) <= 1:
        with pytest.raises(InputError):
            assert auth_register("h@gmail.com", "goodpassword", "Bob", "Ross")
    else:
        u_1 = auth_register(input_string + "@gmail.com", "111111", "Bob", "Ross")
        assert u_1['u_id'] == 1
        assert generate_token(1) == u_1['token']

# Password registering
@given(strategies.text(alphabet=string.printable, min_size=6))
def test_auth_register_valid_password_intensive(input_string):
    """Property based testing for valid password registers"""
    clear()
    u_1 = auth_register("good_email1@gmail.com", input_string, "Bob", "Ross")
    assert u_1['u_id'] == 1
    assert generate_token(1) == u_1['token']

@given(strategies.text(alphabet=string.printable, max_size=5))
def test_auth_register_invalid_password_intensive(input_string):
    """Property based testing for invalid password registers"""
    clear()
    with pytest.raises(InputError):
        assert auth_register("good_email6@gmail.com", input_string, "Bob", "Ross")

# First name registering
@given(strategies.text(alphabet=string.printable, min_size=1, max_size=50))
def test_auth_register_valid_first_name_intensive(input_string):
    """Property based testing for valid first name registers"""
    clear()
    u_1 = auth_register("good_email1@gmail.com", "111111", input_string, "Simon")
    assert u_1['u_id'] == 1
    assert generate_token(1) == u_1['token']

# Last name registering
@given(strategies.text(alphabet=string.printable, min_size=1, max_size=50))
def test_auth_register_valid_last_name_intensive(input_string):
    """Property based testing for valid last name registers"""
    clear()
    u_1 = auth_register("good_email1@gmail.com", "111111", "Bob", input_string)
    assert u_1['u_id'] == 1
    assert generate_token(1) == u_1['token']

# Valid cases:
def test_auth_passwordreset_request_valid():
    """Valid password reset request"""
    clear()
    registers = register_3_users()
    u_1 = registers[0]
    profile = user_profile(u_1['token'], u_1['u_id'])
    assert auth_passwordreset_request('noone@gmail.com') == {}
    assert auth_passwordreset_request(profile['user']['email']) == {}
    assert code[0]['u_id'] == 1

# Valid cases:
def test_auth_passwordreset_reset_valid_code():
    '''Valid password reset'''
    clear()
    register_3_users()
    auth_passwordreset_request('good_email1@gmail.com')
    assert auth_passwordreset_reset(code[0]['code'], 'goodpassword') == {}
    assert data['users'][0]['password'] == encrypted('goodpassword')

# Error cases:
def test_auth_passwordreset_reset_wrong_code():
    """Given invalid reset code"""
    clear()
    with pytest.raises(InputError):
        assert auth_passwordreset_reset('invalid code', 'goodpassword')

def test_auth_passwordreset_reset_invalid_password():
    """Given invalid password"""
    clear()
    register_3_users()
    auth_passwordreset_request('good_email1@gmail.com')
    with pytest.raises(InputError):
        assert auth_passwordreset_reset(code[0]['code'], 'bad')
