'''
This file wraps functions with the flask.
'''
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from error import InputError
from auth import auth_register, auth_login, auth_logout,\
                 auth_passwordreset_request, auth_passwordreset_reset
from channel import channel_invite, channel_details, channel_messages, channel_leave,\
                    channel_join, channel_addowner, channel_removeowner
from channels import channels_list, channels_listall, channels_create
from message import message_send, message_edit, message_remove, message_sendlater, \
                    message_react, message_unreact, message_pin, message_unpin
from user import user_profile, user_profile_setname, user_profile_setemail,\
                               user_profile_sethandle, user_profile_uploadphoto
from other import clear, users_all, admin_userpermission_change, search
from standup import standup_start, standup_active, standup_send
from global_vars import data

def default_handler(err):
    '''
    handle with the default cases
    '''
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, default_handler)

# Auth.py functions
@APP.route("/auth/register", methods=['POST'])
def register():
    '''Wrapping auth_register()'''
    info = request.get_json()
    return dumps(auth_register(info['email'], info['password'], \
                               info['name_first'], info['name_last']))

@APP.route("/auth/login", methods=['POST'])
def login():
    '''Wrapping auth_login'''
    info = request.get_json()
    return dumps(auth_login(info['email'], info['password']))

@APP.route("/auth/logout", methods=['POST'])
def logout():
    '''Wrapping auth_logout'''
    info = request.get_json()
    return dumps(auth_logout(info['token']))

@APP.route("/auth/passwordreset/request", methods=['POST'])
def passwordreset_request():
    '''Wrapping auth_passwordreset_request'''
    info = request.get_json()
    return dumps(auth_passwordreset_request(info['email']))

@APP.route("/auth/passwordreset/reset", methods=['POST'])
def passwordreset_reset():
    '''Wrapping auth_passwordreset_reset'''
    info = request.get_json()
    return dumps(auth_passwordreset_reset(info['reset_code'], info['new_password']))

# channels_list
@APP.route("/channels/list", methods=['GET'])
def channels_list_flask():
    '''
    Wrapping up the channels_list with flask
    '''
    return dumps(channels_list(request.args.get('token')))

# channels_listall
@APP.route("/channels/listall", methods=['GET'])
def channels_list_all_flask():
    '''
    Wrapping up the channels_list_all with flask
    '''
    return dumps(channels_listall(request.args.get('token')))

# channels_create
@APP.route("/channels/create", methods=['POST'])
def channels_create_flask():
    '''
    Wrapping up the channels_create with flask
    '''
    input_val = request.get_json()
    return dumps(channels_create(input_val['token'],\
                                 input_val['name'], input_val['is_public']))
# Channel.py functions
@APP.route("/channel/invite", methods=['POST'])
def invite():
    info = request.get_json()
    return dumps(channel_invite(info['token'], int(info['channel_id']),\
                                int(info['u_id'])))

@APP.route("/channel/details", methods=['GET'])
def details():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(channel_details(token, channel_id))

@APP.route("/view", methods=['POST'])
def view():
    return dumps(data)

@APP.route("/channel/messages", methods=['GET'])
def messages():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    return dumps(channel_messages(token, channel_id, start))

@APP.route("/channel/leave", methods=['POST'])
def leave():
    info = request.get_json()
    return dumps(channel_leave(info['token'], int(info['channel_id'])))

@APP.route("/channel/join", methods=['POST'])
def join():
    '''Wrapping channel_join'''
    payload = request.get_json()
    return dumps(channel_join(payload['token'], int(payload['channel_id'])))

@APP.route("/channel/addowner", methods=['POST'])
def addowner():
    '''Wrapping channel_addowner'''
    payload = request.get_json()
    return dumps(channel_addowner(payload['token'], int(payload['channel_id']),\
                 int(payload['u_id'])))

@APP.route("/channel/removeowner", methods=['POST'])
def removeowner():
    '''Wrapping channel_removeowner'''
    payload = request.get_json()
    return dumps(channel_removeowner(payload['token'], int(payload['channel_id']),\
                 int(payload['u_id'])))

# Message functions
@APP.route("/message/send", methods=['POST'])
def send():
    info = request.get_json()
    return dumps(message_send(info['token'], int(info['channel_id']),\
                              info['message']))

@APP.route("/message/remove", methods=['DELETE'])
def remove():
    info = request.get_json()
    return dumps(message_remove(info['token'], int(info['message_id'])))

@APP.route("/message/edit", methods=['PUT'])
def edit():
    info = request.get_json()
    return dumps(message_edit(info['token'], int(info['message_id']),\
                              info['message']))

@APP.route("/message/sendlater", methods=['POST'])
def sendlater():
    info = request.get_json()
    return dumps(message_sendlater(info['token'], int(info['channel_id']),\
                                   info['message'], int(info['time_sent'])))

@APP.route("/message/react", methods=['POST'])
def react():
    info = request.get_json()
    return dumps(message_react(info['token'], int(info['message_id']), \
                               int(info['react_id'])))

@APP.route("/message/unreact", methods=['POST'])
def unreact():
    info = request.get_json()
    return dumps(message_unreact(info['token'], int(info['message_id']), \
                               int(info['react_id'])))

@APP.route("/message/pin", methods=['POST'])
def pin():
    info = request.get_json()
    return dumps(message_pin(info['token'], int(info['message_id'])))

@APP.route("/message/unpin", methods=['POST'])
def unpin():
    info = request.get_json()
    return dumps(message_unpin(info['token'], int(info['message_id'])))

# user_profile
@APP.route("/user/profile", methods=['GET'])
def user_profile_flask():
    '''
    Wrapping up the user_profile with flask
    '''
    return dumps(user_profile(request.args.get('token'), int(request.args.get('u_id'))))

# user_profile_setname
@APP.route("/user/profile/setname", methods=['PUT'])
def user_profile_setname_flask():
    '''
    Wrapping up the user_profile_setname with flask
    '''
    input_val = request.get_json()
    return dumps(user_profile_setname(input_val['token'],\
                                      input_val['name_first'], input_val['name_last']))

# user_profile_setemail
@APP.route("/user/profile/setemail", methods=['PUT'])
def user_profile_setemail_flask():
    '''
    Wrapping up the user_profile_setemail with flask
    '''
    input_val = request.get_json()
    return dumps(user_profile_setemail(input_val['token'], input_val['email']))

# user_profile_sethandle
@APP.route("/user/profile/sethandle", methods=['PUT'])
def user_profile_sethandle_flask():
    '''
    Wrapping up the user_profile_sethandle with flask
    '''
    input_val = request.get_json()
    return dumps(user_profile_sethandle(input_val['token'], input_val['handle_str']))

# user_profile_uploadphoto
@APP.route("/user/profile/uploadphoto", methods=['POST'])
def user_profile_uplaodphoto_flask():
    '''
    Wrapping up the user_profile_uploadphoto with flask
    '''
    input_val = request.get_json()
    coordinates = {'x_start':input_val['x_start'], 'y_start':input_val['y_start'],\
                   'x_end':input_val['x_end'], 'y_end':input_val['y_end']}
    host = request.host
    return dumps(user_profile_uploadphoto(host, input_val['token'], input_val['img_url'],\
                 coordinates))

# Brings the cropped image.
@APP.route('/imgurl/<path:path>')
def bring_the_image(path):
    '''
    Bring the copy of profile image stored in the url.
    '''
    return send_from_directory('../imgurl/', path)

# other functions
@APP.route("/clear", methods=['DELETE'])
def reset():
    '''Wrapping clear()'''
    return dumps(clear())

@APP.route("/users/all", methods=['GET'])
def users_all_flask():
    '''Wrapping users_all()'''
    return dumps(users_all(request.args.get('token')))

@APP.route("/admin/userpermission/change", methods=['POST'])
def admin_userpermission_change_flask():
    '''Wrapping admin_userpermission_change()'''
    payload = request.get_json()
    return dumps(admin_userpermission_change(payload['token'], int(payload['u_id']),\
                 int(payload['permission_id'])))

@APP.route("/search", methods=['GET'])
def search_flask():
    '''Wrapping search()'''
    return dumps(search(request.args.get('token'), request.args.get('query_str')))

# standup functions
@APP.route("/standup/start", methods=['POST'])
def standup_start_flask():
    '''Wrapping standup_start()'''
    payload = request.get_json()
    return dumps(standup_start(payload['token'], int(payload['channel_id']),\
                 int(payload['length'])))

@APP.route("/standup/active", methods=['GET'])
def standup_active_flask():
    '''Wrapping standup_active()'''
    return dumps(standup_active(request.args.get('token'), int(request.args.get('channel_id'))))

@APP.route("/standup/send", methods=['POST'])
def standup_active_send():
    '''Wrapping standup_send()'''
    payload = request.get_json()
    return dumps(standup_send(payload['token'], int(payload['channel_id']), payload['message']))

if __name__ == "__main__":
    APP.run(port=0) # Do not edit this portimport sys

