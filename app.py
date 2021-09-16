from ActionNetwork import ActionNetworkMap
import json
import os
from dotenv import load_dotenv

import yaml

load_dotenv()

with open("./orgs.json") as orgs_file:
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
print(yaml.dump(events))
with open("./events.json", "w+") as events_json:
    events_json.write(json.dumps(events))
