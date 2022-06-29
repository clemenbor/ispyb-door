import os
import sys
import time
from argparse import ArgumentParser
from requests import post
from pydesydoor.doorpyispyb import DoorPyISPyB
from dotenv import load_dotenv

parser = ArgumentParser()
parser.add_argument("-p", "--proposal", dest="proposal_id",
                    help="Door Proposal ID. Ex: 20210002")


def sync_proposal(proposal_id):
    client = DoorPyISPyB()

    try:
        start = time.time()
        proposal = client.get_full_proposal_to_pyispyb(proposal_id, True, True, True, True)
        took = round(time.time() - start, 3)
        print(f"Retrieving proposal {proposal_id} from the DOOR API took {took}")
    except Exception as e:
        print(f"There was an error retrieving proposal {proposal_id} from the DOOR API.")
        print(f"Probably the proposal Id does not exist within the DOOR API environment.")
        print(e)
        sys.exit(1)

    # Login to FastAPI and get the token
    login = dict()
    load_dotenv()
    # Get the environment variables from the .env file
    api_root = os.environ["PYISPYB_API_ROOT"] or None
    login["plugin"] = os.environ["PYISPYB_AUTH_PLUGIN"] or None
    login["username"] = os.environ["PYISPYB_SERVICE_ACCOUNT"] or None
    login["password"] = os.environ["PYISPYB_SERVICE_PASSWORD"] or None

    r = post(api_root + "/ispyb/api/v1/auth/login", json=login, verify=False)

    token = None
    if r.status_code == 201:
        token = r.json()['token']
    else:
        print(
            f"Could not login to py-ispyb with {login['username']}. "
            f"Please check the credentials or the connection to py-ispyb.")
        sys.exit(1)

    if token:
        headers = {"Authorization": "Bearer " + token, "accept": "application/json", "Content-Type": "application/json"}
        r = post(api_root + "/ispyb/api/v1/userportalsync/sync_proposal", headers=headers, data=proposal, verify=False)
        if r.status_code == 200:
            print(r.text)
        else:
            print(f"There was an error synchronizing proposal {proposal_id} with py-ispyb")
            print(r.text)
            sys.exit(1)


def main(args):
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = vars(parser.parse_args())

    if args["proposal_id"]:
        sync_proposal(args["proposal_id"])


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
