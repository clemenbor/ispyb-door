import os
import logging
import logging.handlers
from requests import post, get, exceptions
from functools import wraps
from dotenv import load_dotenv


logging.basicConfig(filename='desydoorapi.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

"""
    Decorator for requests exception handling.
"""


def requests_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        """A wrapper function"""
        try:
            func(*args, **kwargs)
        except exceptions.HTTPError as e:
            logging.warning(e)

    return wrapper


class DesyDoorAPI(object):
    """
    RESTful Web-service API client for DESY Door user portal.
    """

    def __init__(self):
        load_dotenv()
        self.__door_rest_root = os.environ["DOOR_REST_ROOT"] or None
        self.__door_rest_token = os.environ["DOOR_REST_TOKEN"] or None
        self.__door_rest_service_account = os.environ["DOOR_SERVICE_ACCOUNT"] or None
        self.__door_rest_service_password = os.environ["DOOR_SERVICE_PASSWORD"] or None
        # Set required door token header for any HTTP call
        self.__door_header_token = {"x-door-token": self.__door_rest_token}
        # Set door service account headers
        self.__door_service_headers = {"x-door-token": self.__door_rest_token,
                                       "x-door-service-account": self.__door_rest_service_account,
                                       "x-door-service-auth": self.__door_rest_service_password}

    def get_door_rest_root(self):
        return self.__door_rest_root

    def get_door_header_token(self):
        return self.__door_header_token

    def get_door_request(self, url):
        r = get(url, headers=self.__door_service_headers)
        r.raise_for_status()
        return r

    def post_door_request(self, url):
        r = post(url, headers=self.__door_service_headers)
        r.raise_for_status()
        return r

    @requests_exceptions
    def get_proposals(self, beamline):
        r = self.get_door_request(self.__door_rest_root + "/proposals/beamline/" + beamline)
        if r.status_code == 200:
            try:
                return r.json()['proposals']
            except KeyError:
                logging.warning(r.json()['message'])
        return None

    @requests_exceptions
    def get_proposal(self, proposal_id):
        r = self.get_door_request(self.__door_rest_root + "/proposals/propid/" + proposal_id)
        if r.status_code == 200:
            try:
                return r.json()['proposals'][proposal_id]
            except KeyError:
                logging.warning(r.json()['message'])
        return None

    @requests_exceptions
    def get_proposal_sessions(self, proposal_id):
        r = self.get_door_request(self.__door_rest_root + "/experiments/propid/" + proposal_id)
        if r.status_code == 200:
            try:
                print(r.json()['experiment metadata'])
                return r.json()['experiment metadata']
            except KeyError:
                logging.warning(r.json()['message'])
        return None

    @requests_exceptions
    def get_sessions(self, beamline):
        r = self.get_door_request(self.__door_rest_root + "/experiments/beamline/" + beamline)
        if r.status_code == 200:
            try:
                return r.json()['experiment metadata']
            except KeyError:
                logging.warning(r.json()['message'])
        return None

    @requests_exceptions
    def get_session(self, session_id):
        r = self.get_door_request(self.__door_rest_root + "/experiments/expid/" + session_id)
        if r.status_code == 200:
            try:
                return r.json()['experiment metadata'][session_id]
            except KeyError:
                logging.warning(r.json()['message'])
        return None
