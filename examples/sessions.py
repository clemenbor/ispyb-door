from pydesydoor.desydoorapi import DesyDoorAPI

client = DesyDoorAPI()

# Get the sessions for a given proposal ID and a date range
proposal_sessions = client.get_proposal_sessions("20010001", "P11", "2022-01-01", "2022-12-31")
# Get all the sessions for a beamline
beamline_sessions = client.get_beamline_sessions("p11")
# Get the session given a session id
session = client.get_session("11015610")