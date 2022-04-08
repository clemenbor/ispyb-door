import json
from pydesydoor.desydoorapi import DesyDoorAPI
from datetime import datetime


class DoorISPyBJava(DesyDoorAPI):

    def get_ispyb_user(self, door_user_id, user_type, door_proposal):
        """
           Generates the proposers/lab contacts json structure

           :param int door_user_id: The DOOR user id
           :param str user_type: The user type Ex: "proposalPI, proposalLeader or proposalCowriters"
           :param array door_proposal: The user type Ex: "proposalPI"
        """
        data = dict()
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
        data["scientistTitle"] = door_user["title"]
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

    def get_sessions(self, door_proposal_id):
        sessions = []
        door_proposal = self.get_proposal(door_proposal_id)
        door_sessions = self.get_proposal_sessions(door_proposal_id)
        if door_sessions:
            for session in door_sessions:
                ispyb_session = self.get_ispyb_session(door_sessions[session], door_proposal)
                if ispyb_session:
                    sessions.append(ispyb_session)
        return json.dumps(sessions, indent=4, sort_keys=True, default=str)

    def get_ispyb_session(self, door_session, door_proposal):
        session = dict()
        # Session data
        session["pk"] = door_session["expSessionPk"]
        session["experimentPk"] = door_session["expSessionPk"]
        session["shifts"] = door_session["nbShifts"]
        # startShift is needed by default set to 1
        session["startShift"] = 1
        # The Java API will import only sessions which are not cancelled
        session["cancelled"] = False
        # Start date
        start_datetime = self.convert_date(door_session["startDate"])
        start_date = self.get_ispyb_date(start_datetime)
        session["startDate"] = start_date
        # End date
        end_datetime = self.convert_date(door_session["endDate"])
        end_date = self.get_ispyb_date(end_datetime)
        session["endDate"] = end_date
        # Proposal data
        session["proposalType"] = 3
        session["proposalGroup"] = 103
        session["proposalTitle"] = door_proposal["title"]
        session["proposalPk"] = door_proposal["proposalNumber"]
        session["categCode"] = door_proposal["proposalCode"]
        session["categCounter"] = door_proposal["proposalNumber"]
        session["proposalGroupCode"] = "Crystallography"
        session["name"] = self.get_session_name(door_proposal, door_session["beamlineName"],
                                                start_datetime, end_datetime)
        # Beamline data
        session["beamlineName"] = door_session["beamlineName"]
        session["physicalBeamlineName"] = door_session["beamlineName"]
        # Main proposer and Local contact/s
        if door_proposal["proposalPI"]:
            session["mainProposer"] = self.get_session_user(door_proposal["proposalPI"])

        # Pending to see where to get the local contact
        session["firstLocalContact"] = self.get_session_user(1)
        return session

    @staticmethod
    def get_session_name(door_proposal, beamline_name, start, end):
        name = ""
        proposal = door_proposal["proposalCode"]+"-"+str(door_proposal["proposalNumber"])+" "+beamline_name
        daterange = start.strftime("%d.%m.%Y")+"/"+end.strftime("%d.%m.%Y")
        name = proposal + " " + daterange
        return name

    def get_session_user(self, door_user_id):
        user = dict()
        door_user = self.get_user(door_user_id)
        user["name"] = door_user["familyName"]
        user["realName"] = door_user["familyName"]
        user["firstName"] = door_user["givenName"]
        user["email"] = door_user["emailAddress"]
        user["phone"] = door_user["phoneNumber"]
        user["scientistPk"] = door_user_id
        user["siteId"] = door_user_id
        return user

    @staticmethod
    def get_ispyb_date(datetime_object: datetime) -> dict:
        date_dict = dict()
        date_dict["year"] = datetime_object.year
        date_dict["month"] = datetime_object.month
        date_dict["dayOfMonth"] = datetime_object.day
        date_dict["hourOfDay"] = datetime_object.hour
        date_dict["minute"] = datetime_object.minute
        date_dict["second"] = datetime_object.second
        return date_dict

    @staticmethod
    def convert_date(date: str) -> datetime:
        try:
            # https://stackoverflow.com/questions/466345/converting-string-into-datetime
            datetime_object = datetime.strptime(date, '%Y-%m-%d  %H:%M:%S')
            return datetime_object
        except ValueError as e:
            print(e)
        return None
