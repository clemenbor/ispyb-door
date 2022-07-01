import json
from datetime import datetime
from pydesydoor.desydoorapi import DesyDoorAPI


class DoorPyISPyB(DesyDoorAPI):
    """
    RESTful Web-service API client to generate the data format required to import
    data into py-ISPyB.
    """

    def get_full_proposal_to_pyispyb(self, door_proposal_id, with_leader=True, with_cowriters=True, with_sessions=True,
                                     with_session_participants=True, start_date=None, end_date=None):
        """
           Get the full proposal data (sessions, etc) from DOOR in format for py-ispyb

           :param str door_proposal_id: The DOOR proposal id
           :param boolean with_leader: True/False depending if the proposal leader data is needed
           :param boolean with_cowriters: True/False depending if the proposal cowriters data is needed
           :param boolean with_sessions: True/False depending if the proposal sessions data is needed
           :param boolean with_session_participants: True/False depending if the session participants data is needed
           :param string start_date (%Y-%m-%d): the start date range to find proposal sessions
           :param string end_date (%Y-%m-%d): the end date range to find proposal sessions
        """
        ispyb_proposal = {}
        # Getting the proposal data without leader and cowriters
        proposal_data = self.get_proposal_to_pyispyb(door_proposal_id, with_leader, with_cowriters)
        ispyb_proposal["proposal"] = proposal_data
        if with_sessions:
            sessions_data = self.get_sessions_to_pyispyb(door_proposal_id, "P11", with_session_participants, start_date,
                                                         end_date)
            ispyb_proposal["sessions"] = sessions_data
        return json.dumps(ispyb_proposal, indent=4, sort_keys=True, default=str)

    def get_proposal_to_pyispyb(self, door_proposal_id, with_leader=True, with_cowriters=True):
        """
           Get the proposal data from DOOR in format for py-ispyb

           :param str door_proposal_id: The DOOR proposal id
           :param boolean with_leader: True/False depending if the leader data is needed
           :param boolean with_cowriters: True/False depending if the cowriters data is needed
        """
        # Add proposal data
        data = {}
        door_proposal = self.get_proposal(door_proposal_id)
        data["title"] = door_proposal["title"]
        data["proposalNumber"] = str(door_proposal["proposalNumber"])
        data["proposalCode"] = door_proposal["proposalCode"]
        data["proposalType"] = "MX"
        '''
        ExternalId field is not compatible with the JAVA API, can be used later
        when full migration to py-ispyb is done and JAVA API is not used anymore.
        '''
        # data["externalId"] = int(door_proposal["proposalNumber"])
        data["bltimeStamp"] = None
        data["state"] = "Open"
        persons = []
        # Set the PI
        if door_proposal["proposalPI"]:
            # First one in the list will be the PI
            pi = self.get_user_to_pyispyb(door_proposal["proposalPI"])
            persons.append(pi)
        if with_leader:
            # Set the Leader
            if door_proposal["proposalLeader"]:
                leader = self.get_user_to_pyispyb(door_proposal["proposalLeader"])
                persons.append(leader)
        if with_cowriters:
            # Set the co-writers
            if door_proposal["proposalCowriters"]:
                if not isinstance(door_proposal["proposalCowriters"], int):
                    # There is more than one co-writer
                    cowriter_ids = self.split_multiple_by_comma(door_proposal["proposalCowriters"])
                    for cowriter_id in cowriter_ids:
                        cowriter = self.get_user_to_pyispyb(cowriter_id)
                        cowriter["type"] = "cowriter"
                        persons.append(cowriter)
                else:
                    # There is only one co-writer
                    cowriter = self.get_user_to_pyispyb(door_proposal["proposalCowriters"])
                    persons.append(cowriter)
        if not persons:
            # For commisioning proposal there are no persons. py-ispyb required at least one
            default_person = self.get_user_to_pyispyb("5714")
            persons.append(default_person)
        # Add proposal persons
        data["persons"] = persons
        # Add lab contacts
        data["labcontacts"] = self.get_labcontacts_to_pyispyb(persons)
        return data

    def get_user_to_pyispyb(self, door_user_id, with_laboratory=True):
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
            user["laboratory"] = self.get_laboratory_to_pyispyb(door_user["laboratoryId"])
        user["phoneNumber"] = str(door_user["phoneNumber"])
        '''
        ExternalId field is not compatible with the JAVA API, can be used later
        when full migration to py-ispyb is done and JAVA API is not used anymore.
        '''
        # user["externalId"] = int(door_user_id)
        return user

    def get_laboratory_to_pyispyb(self, laboratory_id):
        door_laboratory = self.get_institute(laboratory_id)
        return door_laboratory

    def get_sessions_to_pyispyb(self, door_proposal_id, beamline, with_persons=True, start_date=None, end_date=None):
        """
           Get the proposal sessions data from DOOR in format for py-ispyb

           :param str door_proposal_id: The DOOR proposal id
           :param str beamline: The beamline name (to filter sessions from commisioning proposals)
           :param boolean with_persons: True/False depending if the session participants data is needed
        """
        sessions = []
        door_sessions = self.get_proposal_sessions(door_proposal_id, beamline, start_date, end_date)
        if door_sessions:
            for session in door_sessions:
                add_session = dict()
                '''
                ExternalId field is not compatible with the JAVA API, can be used later
                when full migration to py-ispyb is done and JAVA API is not used anymore.
                '''
                # add_session["externalId"] = int(session["expSessionPk"])
                add_session["expSessionPk"] = int(session["expSessionPk"])
                datetime_start = datetime.strptime(session["startDate"], '%Y-%m-%d %H:%M:%S')
                add_session["startDate"] = datetime_start.isoformat()
                datetime_end = datetime.strptime(session["endDate"], '%Y-%m-%d %H:%M:%S')
                add_session["endDate"] = datetime_end.isoformat()
                add_session["beamLineName"] = session["beamlineName"]
                add_session["scheduled"] = session["scheduled"]
                add_session["nbShifts"] = session["nbShifts"]

                if session["beamlineOperator"]:
                    operator = self.get_user_to_pyispyb(session["beamlineOperator"], False)
                    add_session["beamlineOperator"] = " ".join([operator["givenName"], operator["familyName"]])
                if with_persons:
                    persons = []
                    remotes = self.get_participants(session["participants"], "remote")
                    if remotes:
                        persons += remotes
                    on_sites = self.get_participants(session["participants"], "on-site")
                    if on_sites:
                        persons += on_sites
                    data_onlys = self.get_participants(session["participants"], "data-only")
                    if data_onlys:
                        persons += data_onlys
                    # Add session participants
                    add_session["persons"] = persons
                sessions.append(add_session)
        return sessions

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
                    participant = self.get_user_to_pyispyb(participant, True)
                    # By now we consider only the remote option
                    # the remote field in ISPyB Session_has_Person table is a tinyint
                    # Door apparently is not storing the participant session role (Staff, Principal Investigator, etc)
                    if participant_type == "remote":
                        session_options = dict()
                        session_options["remote"] = 1
                        participant["session_options"] = session_options
                    users.append(participant)
            return users

    def get_labcontacts_to_pyispyb(self, persons):
        """
           The lab contact will be basically the same proposers (Pi, co-writers, etc).
           If needed, we could add later also the session participants.
        """
        lab_contacts = []
        for person in persons:
            labcontact = dict()
            cardname = person["login"] + "-" + person["laboratory"]["name"]
            if len(cardname) > 45:
                cardname = cardname[:45]
            labcontact["cardName"] = cardname
            labcontact["person"] = person
            lab_contacts.append(labcontact)
        return lab_contacts
