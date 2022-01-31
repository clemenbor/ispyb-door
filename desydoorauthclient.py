import json
import base64
import os
import logging
import logging.handlers
from requests import post, get
from dotenv import load_dotenv
from urllib.parse import urljoin


logging.basicConfig(filename='desydoorauthclient.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)


class DesyDoorAuthClient(object):
    """
    RESTful Web-service authentication client for DESY Door user portal.
    """

    def __init__(self):
        load_dotenv()
        self.__door_rest_root = os.environ["DOOR_REST_ROOT"] or None
        self.__door_rest_token = os.environ["DOOR_REST_TOKEN"] or None

    def login(self, username, password, retry=True, fields=None):
        # First encode the password in base64
        message_bytes = password.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_password = base64_bytes.decode('ascii')
        # Add a required token header
        headers_dict = {"x-door-token": self.__door_rest_token}
        # Make a HTTO post request with usernmae and encoded password
        r = post(urljoin(self.__door_rest_root, "api/v1.0/doorauth/auth"), data={'user': username, 'pass': base64_password}, headers=headers_dict)
        if r.status_code == 200:
             # status 200 means user authenticated
             logging.info('Username has been succesfully authenticated: %s', username)
             return (True, username)
        elif r.status_code == 401:
             # status 401 means unauthorized for different reasons: wrong password, wrong token, server not allowed to connect
            try:
                json_response = json.loads(r.text)
                logging.warning('%s - %s', json_response["message"], username)
            except json.decoder.JSONDecodeError:
                logging.warning("Error decoding JSON response %s", r.status_code)
                logging.warning(r.text)
        elif r.status_code == 404:
            # status 404 means username does not exist
            logging.warning('Username does not exist: %s', username)
        return False


client = DesyDoorAuthClient()
client.login("testuser", "testpass")
