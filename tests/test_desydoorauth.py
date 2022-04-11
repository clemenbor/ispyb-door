import os
from unittest import TestCase
from pydesydoor.desydoorauth import DesyDoorAuth
from dotenv import load_dotenv


class TestDesyDoorAuth(TestCase):

    def setUp(self) -> None:
        load_dotenv()
        self.client = DesyDoorAuth()
        self.test_username = os.environ["DOOR_TESTUSER_USERNAME"] or None
        self.test_password = os.environ["DOOR_TESTUSER_PASSWORD"] or None

    def test_login(self):
        auth = self.client.login(self.test_username, self.test_password)
        self.assertTrue(auth[0], True)
