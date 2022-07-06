import os
import sys
import time
from datetime import datetime
from argparse import ArgumentParser
from requests import post
from pydesydoor.doorpyispyb import DoorPyISPyB
from dotenv import load_dotenv


def create_arg_parser():
    # Creates and returns the ArgumentParser object
    parser = ArgumentParser(
        description="Command line tool to syncronize a DOOR proposal"
        "into an ISPyB."
    )
    parser.add_argument("-p", "--proposal_id", help="Door proposal ID.", required=True)
    parser.add_argument("-s", "--start", help="Session start date in format YYYY-MM-DD", required=False)
    parser.add_argument("-e", "--end", help="Session end date in format YYYY-MM-DD", required=False)
    parser.add_argument("-d", "--door", help="It will only get and show the proposal from DOOR",
                        required=False, action="store_true")
    return parser


def sync_proposal(proposal_id, door=False, start_date=None, end_date=None):
    client = DoorPyISPyB()
    try:
        start_time = time.time()
        proposal = client.get_full_proposal_to_pyispyb(proposal_id, True, True, True, True, start_date, end_date)
        if door:
            '''
            If --door option is passed only get the proposal from DOOR
            and exit (do not sync with py-ispyb)
            '''
            print(proposal)
            exit(1)
        took = round(time.time() - start_time, 3)
        print(f"Retrieving proposal {proposal_id} from the DOOR API took {took}")
    except Exception as e:
        print(f"There was an error retrieving proposal {proposal_id} from the DOOR API.")
        print("Probably the proposal Id does not exist within the DOOR API environment.")
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


if __name__ == "__main__":
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    if parsed_args.proposal_id:
        if parsed_args.proposal_id == "20010001":
            '''
            If it is the commissioning proposal force to sync using a date range
            Otherwise it will retrieve too many sessions from the past
            '''
            if parsed_args.start and parsed_args.end:
                try:
                    datetime_start = datetime.strptime(parsed_args.start, '%Y-%m-%d')
                    datetime_end = datetime.strptime(parsed_args.end, '%Y-%m-%d')
                    sync_proposal(parsed_args.proposal_id, parsed_args.door, parsed_args.start, parsed_args.end)
                except ValueError as e:
                    print(e)
                    exit(1)
            else:
                print("You must use a date range when syncronizing the commissioning proposal 20010001.")
                exit(1)
        else:
            sync_proposal(parsed_args.proposal_id, parsed_args.door)
