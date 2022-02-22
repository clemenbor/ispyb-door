from desydoorclient import DesyDoorClient

client = DesyDoorClient()

auth = client.login("username", "password")
# If user is authenticated
if auth:
    user_id = auth[1]
    # Request the user roles
    roles = client.get_user_roles(user_id)
    print(roles)
