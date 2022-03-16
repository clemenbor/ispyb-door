from pydesydoor.desydoorapi import DesyDoorAPI

client = DesyDoorAPI()

# Get all proposals for beamline P11
proposals = client.get_beamline_proposals("p11")
# Get a proposal data given a proposal ID
proposal = client.get_proposal("20210046")
