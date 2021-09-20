# A module to create a Folium map from the action network api
import requests
import os
import yaml
import json
import folium
import folium.plugins
import branca

class ActionNetworkMap:
    def __init__(self, event_campaign_id=None,ACTION_NETWORK_API_KEY=None,public_data=None):
        if public_data:
            self.public_data = public_data
        else:
            self.api_url = 'https://actionnetwork.org/api/v2'
            if not ACTION_NETWORK_API_KEY:
                raise Exception("No API key provided")
            self.headers = {
                "OSDI-API-Token": ACTION_NETWORK_API_KEY,
                "Content-Type": "application/json"
            }
            self.event_campaign_id = event_campaign_id
            if event_campaign_id:
                self.events_campaign_url = f'{self.api_url}/event_campaigns/{event_campaign_id}'
                # test campaign exists
                ec_response = requests.get(self.events_campaign_url,headers=self.headers)
                if ec_response.status_code == 404:
                    raise Exception("Event Campaign does not exist")
                elif ec_response.status_code == 403:
                    raise Exception("Unauthorised. Event Campaign not available")
                self.events_url = f'{self.api_url}/event_campaigns/{event_campaign_id}/events'
            else:
                # If no event campaign, use all groups events
                self.events_url = f'{self.api_url}/events'
            self.get_events()
            self.public_data()
    def get_events(self):
        # TODO deal with multi[le requests]
        events_data = requests.get(self.events_url,headers=self.headers)
        self.events = events_data.json()["_embedded"]["osdi:events"]
        # Loop through and get
        for e in self.events:
            embed_url = e["_links"]["action_network:embed"]["href"]
            embed_data = requests.get(embed_url,headers=self.headers)
            e["embed"] = embed_data.json()
        return self.events
    def public_data(self):
        keys = {"title","description","location","browser_url","start_date","featured_image_url","end_date","embed"}
        events=[]
        for e in self.events:
            event = { key:value for key,value in e.items() if key in keys}
            if e["visibility"] == "public":
                events.append(event)
        self.public_data = events
    def json(self,file="events.json"):
        json_data = json.dumps({"events":self.public_data})
        with open(file, "w+") as json_file:
            json_file.write(json_data)
        return json_data

    def map(self,output_file="map.html"):
        m = folium.Map(tiles="Stamen Watercolor")
        marker_cluster = folium.plugins.MarkerCluster().add_to(m)
        lats = []
        lons = []
        for e in self.public_data:
            lat_lon = [
                e["location"]["location"]["latitude"],
                e["location"]["location"]["longitude"]
                ]
            lats.append(lat_lon[0])
            lons.append(lat_lon[1])
            popup_text=f"""
            <p><b>{e["title"]}</b></p>
            <p><date>{e["start_date"]}</date></p>
            <a target="_blank" href={e["browser_url"]}><button>RSVP</button></a>
            """
            iframe = branca.element.IFrame(html=popup_text, width=200, height=200)
            popup = folium.Popup(iframe,max_width=2650)
            marker = folium.Marker(lat_lon, popup=popup)
            marker.add_to(marker_cluster)
        # Get edges
        m.fit_bounds([
            [min(lats),min(lons)],
            [max(lats),max(lons)]
        ])
        # output to file
        m.save(output_file)
        # use folium to create event map
        return

if __name__ == "__main__":
    pass
