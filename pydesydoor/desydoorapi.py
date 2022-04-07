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
        r = get(self.__door_rest_root + url, headers=self.__door_service_headers)
        r.raise_for_status()
        return r

    def post_door_request(self, url):
        r = post(self.__door_rest_root + url, headers=self.__door_service_headers)
        r.raise_for_status()
        return r

    def get_beamline_proposals(self, beamline):
        r = self.get_door_request("/proposals/beamline/{}".format(beamline))
        if r.status_code == 200:
            try:
                return r.json()['proposals']
            except KeyError:
                logging.warning(r.json()['message'])
        return None

    def get_proposal(self, proposal_id):
        r = self.get_door_request("/proposals/propid/{}".format(proposal_id))
        if r.status_code == 200:
            try:
                return r.json()['proposals'][proposal_id]
            except KeyError:
                logging.warning(r.json()['message'])
        return None

    def get_proposal_sessions(self, proposal_id):
        r = self.get_door_request("/experiments/propid/{}".format(proposal_id))
        if r.status_code == 200:
            try:
                return r.json()['experiment metadata']
            except KeyError:
                logging.warning(r.json()['message'])
        return None

    def get_beamline_sessions(self, beamline):
        r = self.get_door_request("/experiments/beamline/{}".format(beamline))
        if r.status_code == 200:
            try:
                return r.json()['experiment metadata']
            except KeyError:
                logging.warning(r.json()['message'])
        return None

    def get_session(self, session_id):
        r = self.get_door_request("/experiments/expid/{}".format(session_id))
        if r.status_code == 200:
            try:
                return r.json()['experiment metadata'][session_id]
            except KeyError:
                logging.warning(r.json()['message'])
        return None

    def get_user(self, user_id):
        r = self.get_door_request("/users/id/{}".format(user_id))
        if r.status_code == 200:
            try:
                return r.json()['user metadata'][str(user_id)]
            except KeyError:
                logging.warning(r.json()['message'])
        return None

    def get_user_roles(self, user_id):
        r = self.get_door_request("/roles/userid/{}".format(user_id))
        if r.status_code == 200:
            try:
                roles = r.json()['roles']
                return roles
            except KeyError:
                logging.warning('No roles assigned to userid: %s', user_id)
                return False
        else:
            logging.warning('Roles could not be checked for userid: %s', user_id)
        return False

    def get_institute(self, institute_id):
        r = self.get_door_request("/institutes/id/{}".format(institute_id))
        if r.status_code == 200:
            try:
                return r.json()['institute metadata'][str(institute_id)]
            except KeyError:
                logging.warning(r.json()['message'])
        return None

    def split_multiple_by_comma(self, multiple_values):
        data = [x.strip() for x in multiple_values.split(',')]
        return data
