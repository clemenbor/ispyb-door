import json
from datetime import datetime
from pydesydoor.desydoorapi import DesyDoorAPI


class DoorISPyB(DesyDoorAPI):
    """
    RESTful Web-service API client to generate the data format required to import
    data into ISPyB.
    """
    def get_full_proposal_to_ispyb(self, door_proposal_id, with_leader=True, with_cowriters=True, with_sessions=True):
        """
           Get the full proposal data (sessions, etc) from DOOR in format for py-ispyb

           :param str door_proposal_id: The DOOR proposal id
           :param boolean with_leader: True/False depending if the proposal leader data is needed
           :param boolean with_cowriters: True/False depending if the proposal cowriters data is needed
           :param boolean with_sessions: True/False depending if the proposal sessions data is needed
        """
        ispyb_proposal = {}
        # Getting the proposal data without leader and cowriters
        proposal_data = self.get_proposal_to_ispyb(door_proposal_id, with_leader, with_cowriters)
        ispyb_proposal["proposal"] = proposal_data
        sessions_data = self.get_sessions_to_ispyb(door_proposal_id, with_sessions)
        ispyb_proposal["sessions"] = sessions_data
        return json.dumps(ispyb_proposal, indent=4, sort_keys=True, default=str)

    def get_proposal_to_ispyb(self, door_proposal_id, with_leader=True, with_cowriters=True):
        """
           Get the proposal data from DOOR in format for py-ispyb

           :param str door_proposal_id: The DOOR proposal id
           :param boolean with_leader: True/False depending if the leader data is needed
           :param boolean with_cowriters: True/False depending if the cowriters data is needed
        """
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
        if with_leader:
            # Set the Leader
            if door_proposal["proposalLeader"]:
                leader = self.get_user_to_ispyb(door_proposal["proposalLeader"])
                leader["type"] = "leader"
                participants.append(leader)
        if with_cowriters:
            # Set the co-writers
            if door_proposal["proposalCowriters"]:
                if not isinstance(door_proposal["proposalCowriters"], int):
                    # There is more than one co-writer
                    cowriter_ids = self.split_multiple_by_comma(door_proposal["proposalCowriters"])
                    for cowriter_id in cowriter_ids:
                        cowriter = self.get_user_to_ispyb(cowriter_id)
                        cowriter["type"] = "cowriter"
                        participants.append(cowriter)
                else:
                    # There is only one co-writer
                    cowriter = self.get_user_to_ispyb(door_proposal["proposalCowriters"])
                    cowriter["type"] = "cowriter"
                    participants.append(cowriter)
        # Add participants
        data["participants"] = participants
        # Add proposal data
        return data

    def get_user_to_ispyb(self, door_user_id, with_laboratory=True):
        """
           Get the user data from DOOR in format for py-ispyb

           :param str door_user_id: The DOOR user id
           :param boolean with_laboratory: True/False depending if the Laboratory/Institute data is needed
        """
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

    def get_sessions_to_ispyb(self, door_proposal_id, with_participants=True):
        """
           Get the proposal sessions data from DOOR in format for py-ispyb

           :param str door_proposal_id: The DOOR proposal id
           :param boolean with_participants: True/False depending if the session participants data is needed
        """
        sessions = self.get_proposal_sessions(door_proposal_id)
        if sessions:
            for session in sessions:
                datetime_start = datetime.strptime(sessions[session]["startDate"], '%Y-%m-%d %H:%M:%S')
                sessions[session]["startDate"] = datetime_start.isoformat()
                datetime_end = datetime.strptime(sessions[session]["endDate"], '%Y-%m-%d %H:%M:%S')
                sessions[session]["endDate"] = datetime_end.isoformat()
                if sessions[session]["beamlineOperator"]:
                    operator = self.get_user_to_ispyb(sessions[session]["beamlineOperator"], False)
                    sessions[session]["beamlineOperator"] = operator
                if with_participants:
                    participants = []
                    remotes = self.get_participants(sessions[session]["participants"], "remote")
                    if remotes:
                        participants += remotes
                    on_sites = self.get_participants(sessions[session]["participants"], "on-site")
                    if on_sites:
                        participants += on_sites
                    data_onlys = self.get_participants(sessions[session]["participants"], "data-only")
                    if data_onlys:
                        participants += data_onlys
                    # Add session participants
                    sessions[session]["participants"] = participants
            return sessions
        return None

    def get_participants(self, participants, participant_type):
        """
           Helper function to setup the session participants data
        """
        users = []
        array_participants = None
        if participants[participant_type]:
            array_participants = self.split_multiple_by_comma(str(participants[participant_type]))
        if array_participants:
            for participant in array_participants:
                if participant:
                    participant = self.get_user_to_ispyb(participant, False)
                    participant["type"] = participant_type
                    users.append(participant)
            return users
