from ActionNetwork import ActionNetworkMap
import json
import os
# from dotenv import load_dotenv
import argparse

# import yaml

# load_dotenv()

# Set up paths
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-o","--orgs",help="Path to json of organisations")
arg_parser.add_argument("-a","--actions",help="Path to where actions json should be written")
args = arg_parser.parse_args()

with open(args.orgs) as orgs_file:
    orgs = json.loads(orgs_file.read())
    events = {
        "events":[],
        "orgs":orgs["orgs"]
    }
    for org in orgs["orgs"]:
        slug = org["slug"]
        if "event_campaign_id" in org.keys():
            new_map = ActionNetworkMap(
                event_campaign_id=org["event_campaign_id"],
                ACTION_NETWORK_API_KEY=os.environ.get(f"{slug}_AN_API_KEY")
            )
            events["events"] += new_map.public_data

total_map = ActionNetworkMap(public_data=events["events"])

with open(args.actions, "w+") as events_json:
    print(events)
    events_json.write(json.dumps(events))
