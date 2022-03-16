from pydesydoor.desydoorapi import DesyDoorAPI

client = DesyDoorAPI()

# Get the sessions for a given proposal ID
proposal_sessions = client.get_proposal_sessions("20210046")
# Get all the sessions for a beamline
beamline_sessions = client.get_beamline_sessions("p11")
# Get the session given a session id
session = client.get_session("11001335")
