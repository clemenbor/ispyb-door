import sys
sys.path.insert(0, '..')
from desydoorauth import DesyDoorAuth

client = DesyDoorAuth()

auth = client.login("borgescl", "H6xuhx6k")
# If user is authenticated
print(auth)
if auth:
    user_id = auth[1]
    # Request the user roles
    roles = client.get_user_roles(user_id)
    print(roles)
