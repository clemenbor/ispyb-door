from pydesydoor.doorpyispyb import DoorPyISPyB

client = DoorPyISPyB()

proposal = client.get_full_proposal_to_pyispyb("20010001", True, True, True, True, "2022-06-01", "2022-07-01")
print(proposal)
