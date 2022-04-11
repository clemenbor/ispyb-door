from unittest import TestCase
from pydesydoor.desydoorapi import DesyDoorAPI


class TestDesyDoorAPI(TestCase):

    def setUp(self) -> None:
        self.client = DesyDoorAPI()
        self.proposal_id = "20210009"
        self.session_id = "11000938"
        # User with id 1 has super user role
        self.user_id = 1
        self.institute_id = 1

    def test_get_proposal(self):
        door_proposal = self.client.get_proposal(self.proposal_id)
        self.assertTrue(door_proposal["proposalNumber"], self.proposal_id)

    def test_get_proposal_sessions(self):
        door_sessions = self.client.get_proposal_sessions(self.proposal_id)
        for session in door_sessions:
            self.assertTrue(door_sessions[session]["proposalId"], self.proposal_id)

    def test_get_session(self):
        session = self.client.get_session(self.session_id)
        self.assertTrue(session["expSessionPk"], self.session_id)

    def test_get_user(self):
        user = self.client.get_user(self.user_id)
        self.assertTrue(user["externalId"], self.user_id)

    def test_get_user_roles(self):
        has_super_user_role = False
        roles = self.client.get_user_roles(self.user_id)
        for role in roles:
            if role["name"] == "Super User":
                has_super_user_role = True
        self.assertTrue(has_super_user_role, True)

    def test_get_institute(self):
        institute = self.client.get_institute(self.institute_id)
        self.assertTrue(institute["laboratoryExtPk"], self.institute_id)
