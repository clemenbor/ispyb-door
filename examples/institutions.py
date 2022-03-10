from desydoorauth import DesyDoorAuth
import sys
sys.path.insert(0, '..')


client = DesyDoorAuth()

institute_json = client.get_institute("1")
print(institute_json)

json_institutes = client.get_institute_list()
for institute_id in json_institutes:
    print(json_institutes[institute_id])
