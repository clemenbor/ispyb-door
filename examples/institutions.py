from pydesydoor.desydoorapi import DesyDoorAPI

client = DesyDoorAPI()

institute_json = client.get_institute("1")
print(institute_json)
