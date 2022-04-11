import json
from unittest import TestCase
from pydesydoor.doorispybjava import DoorISPyBJava


class TestDoorISPyBJava(TestCase):

    def setUp(self) -> None:
        self.client = DoorISPyBJava()
        self.proposal_id = "20210009"

    def test_get_proposers(self):
        site_id = None
        proposers = self.client.get_proposers(self.proposal_id)
        json_object = json.loads(proposers)
        for proposer in json_object:
            site_id = proposer["siteId"]
        self.assertTrue(site_id, 2)

    def test_get_labcontacts(self):
        lab_contacts = self.client.get_labcontacts(self.proposal_id)
        json_object = json.loads(lab_contacts)
        self.assertTrue(len(json_object), 3)

    def test_get_sessions(self):
        proposal_pk = None
        sessions = self.client.get_sessions(self.proposal_id)
        json_object = json.loads(sessions)
        for session in json_object:
            proposal_pk = session["proposalPk"]
        # Test we get a session
        self.assertTrue(proposal_pk, self.proposal_id)
        # Test the local contact is retrieved
        self.assertTrue(session["firstLocalContact"]["siteId"], 1)
