import json
from pydesydoor.desydoorapi import DesyDoorAPI


class DoorISPyB(DesyDoorAPI):
    """
    RESTful Web-service API client to generate the data format required to import
    data into ISPyB.
    """

    def get_proposal_to_ispyb(self, door_proposal_id, with_leader=True, with_cowriters=True):
        ispyb_proposal = {}
        data = {}
        door_proposal = self.get_proposal(door_proposal_id)
        data["title"] = door_proposal["title"]
        data["proposalNumber"] = door_proposal["proposalNumber"]
        data["proposalCode"] = door_proposal["proposalCode"]
        data["proposalType"] = "MX"
        data["bltimeStamp"] = None
        data["state"] = "Open"
        participants = []
        # Set the PI
        if door_proposal["proposalPI"]:
            pi = self.get_user_to_ispyb(door_proposal["proposalPI"])
            pi["type"] = "pi"
            participants.append(pi)
        else:
            # If proposal has no pi return None (pi is needed)
            return None
        if with_leader:
            # Set the Leader
            if door_proposal["proposalLeader"]:
                leader = self.get_user_to_ispyb(door_proposal["proposalLeader"])
                leader["type"] = "leader"
                participants.append(leader)
        if with_cowriters:
            # Set the co-writers
            if door_proposal["proposalCowriters"]:
                cowriter_ids = [x.strip() for x in door_proposal["proposalCowriters"].split(',')]
                for cowriter_id in cowriter_ids:
                    cowriter = self.get_user_to_ispyb(cowriter_id)
                    cowriter["type"] = "cowriter"
                    participants.append(cowriter)
        # Add participants
        data["participants"] = participants
        # Add proposal data
        ispyb_proposal["proposal"] = data
        print(json.dumps(ispyb_proposal))
        return json.dumps(ispyb_proposal)

    def get_user_to_ispyb(self, door_user_id, with_laboratory=True):
        user = {}
        door_user = self.get_user(door_user_id)
        user["givenName"] = door_user["givenName"]
        user["familyName"] = door_user["familyName"]
        user["emailAddress"] = door_user["emailAddress"]
        user["login"] = door_user["login"]
        if with_laboratory:
            user["laboratory"] = self.get_laboratory_to_ispyb(door_user["laboratoryId"])
        user["phoneNumber"] = door_user["phoneNumber"]
        user["siteId"] = door_user_id
        user["personUUID"] = None
        user["recordTimeStamp"] = None
        return user

    def get_laboratory_to_ispyb(self, laboratory_id):
        door_laboratory = self.get_institute(laboratory_id)
        return door_laboratory
