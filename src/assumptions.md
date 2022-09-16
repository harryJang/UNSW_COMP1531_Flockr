General Assumptions:
1. u_id will increment by 1 for each new user, starting at u_id = 1
2. channel_id will increment by 1 for each new channel, starting at channel_id = 1
3. There won't be empty function arguments
4. Whoever registers first is the flockr owner 
5. There is only 1 owner of the flockr for iteration 1, since the testing/implementation of much of the iteration 1 functions does not depend/require multiple flockr owners. This can be changed easily if subsequent iterations require multiple flockr owners (could make a helper function in other.py)
6. For functions that require an authorised user/token (E.g. auth_logout, channel_join, channels_create etc.), there is at least 1 user in the flockr, since these functions require an existing user to call them

auth_login:
1. There are existing users i.e. data['users'] isn't an empty list

auth_register:
1. There will not be more than 100 users whose handle_str will be the same from the function handle_string
2. User will be automatically logged in after registering

auth_passwordreset_request:
1. Reset code will be a random 8 characters string.

channel_invite:
1. You cannot try to add someone who is already part of a channel. Frontend will stop this

channel_messages:
1. If number of messages in channel is 0, then return a dictionary containing an empty list of messages, the start of messages at 0 (Regardless of what the user assigned since it does not matter) and end = -1

channels_create:
1. Whoever creates the channel automatically joins it as an owner of the channel

channel_join:
1. A user can only join a private channel through the channel owner's invitation.

channel_add_owner:
1. If a user is a member and an owner of a channel, they will be in the channel's list of owner members and all members.
2. A user can only be made an owner of a channel if they are a member of that channel.

channel_remove_owner:
1. If an owner user has their owner privileges removed, they will still remain in all_members as a regular member with no owner permissions but will be removed from owner_members

message:
1. A user cannot try to edit or remove a message if they are not part of the channel. The frontend will prevent this from being an option
