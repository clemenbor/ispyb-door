from pydesydoor.desydoorauth import DesyDoorAuth
from pydesydoor.desydoorapi import DesyDoorAPI

authclient = DesyDoorAuth()

auth = authclient.login("username", "password")
# If user is authenticated
print(auth)
if auth:
    user_id = auth[1]
    # To get the roles we need an instance of DesyDoorAPI (api using a door service account)
    apiclient = DesyDoorAPI()
    # Request the user roles
    roles = apiclient.get_user_roles(user_id)
    print(roles)
