from pydesydoor.doorpyispyb import DoorPyISPyB

client = DoorPyISPyB()

proposal = client.get_full_proposal_to_pyispyb("20210004", True, True, True, True)
print(proposal)
