from desydoorauth import DesyDoorAuth
import sys
sys.path.insert(0, '..')

client = DesyDoorAuth()

auth = client.login("username", "password")
# If user is authenticated
if auth:
    user_id = auth[1]
    # Request the user roles
    roles = client.get_user_roles(user_id)
    print(roles)
