import json
from pydesydoor.desydoorapi import DesyDoorAPI


class DoorISPyBJava(DesyDoorAPI):

    def get_ispyb_user(self, door_user_id, user_type, door_proposal):
        """
           Generates the proposers/lab contacts json structure

           :param int door_user_id: The DOOR user id
           :param str user_type: The user type Ex: "proposalPI, proposalLeader or proposalCowriters"
           :param array door_proposal: The user type Ex: "proposalPI"
        """
        data = {}
        # Set main proposal data
        data["categoryCode"] = door_proposal["proposalCode"]
        data["categoryCounter"] = door_proposal["proposalNumber"]
        # Get Door user
        door_user = self.get_user(door_user_id)
        # Get Door Laboratory associated to user
        door_laboratory = self.get_institute(door_user["laboratoryId"])
        # Set the lab / user data
        data["labAddress"] = [None, door_laboratory["address"], None, None, None]
        data["labAddress1"] = door_laboratory["address"]
        data["labAddress2"] = None
        data["labCity"] = door_laboratory["city"].upper()
        data["labCountryCode"] = door_laboratory["country"]
        data["labName"] = door_laboratory["name"]
        data["labPostalCode"] = None
        data["laboratoryPk"] = door_user["laboratoryId"]
        data["scientistEmail"] = door_user["emailAddress"]
        data["scientistFirstName"] = door_user["givenName"]
        data["scientistName"] = door_user["familyName"]
        data["scientistPk"] = door_user_id
        data["siteId"] = door_user_id
        data["bllogin"] = door_user["login"]
        data["userName"] = door_user["login"]
        # Set extra proposal data
        data["proposalTitle"] = door_proposal["title"]
        data["proposalType"] = 3
        data["proposalGroup"] = 103
        if user_type == "proposalPI":
            data["mainProposer"] = True
            data["user"] = True
            data["proposer"] = True
        if user_type == "proposalLeader" or user_type == "proposalCowriters":
            data["mainProposer"] = False
            data["user"] = True
            data["proposer"] = True
        return data

    def get_proposers(self, door_proposal_id):
        door_proposal = self.get_proposal(door_proposal_id)
        if door_proposal["proposalPI"]:
            pi_entry = self.get_ispyb_user(door_proposal["proposalPI"], "proposalPI", door_proposal)
            if pi_entry:
                return json.dumps([pi_entry], indent=4, sort_keys=True, default=str)
        return None

    def get_labcontacts(self, door_proposal_id):
        labcontacts = []
        door_proposal = self.get_proposal(door_proposal_id)
        pi_entry = self.get_ispyb_user(door_proposal["proposalPI"], "proposalPI", door_proposal)
        if pi_entry:
            labcontacts.append(pi_entry)
        leader_entry = self.get_ispyb_user(door_proposal["proposalLeader"], "proposalLeader", door_proposal)
        if leader_entry:
            labcontacts.append(leader_entry)
        # Check for co-writer
        if door_proposal["proposalCowriters"]:
            if isinstance(door_proposal["proposalCowriters"], int):
                # Single co-writer
                cowriter_entry = self.get_ispyb_user(door_proposal["proposalCowriters"],
                                                     "proposalCowriters", door_proposal)
                if cowriter_entry:
                    labcontacts.append(cowriter_entry)
            else:
                # Multiple co-writers
                cowriters = self.split_multiple_by_comma(door_proposal["proposalCowriters"])
                for cowriter in cowriters:
                    cowriter_entry = self.get_ispyb_user(cowriter,
                                                         "proposalCowriters", door_proposal)
                    if cowriter_entry:
                        labcontacts.append(cowriter_entry)
        if labcontacts:
            return json.dumps(labcontacts, indent=4, sort_keys=True, default=str)
        return None
