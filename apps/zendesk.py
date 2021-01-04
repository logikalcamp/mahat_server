import requests
import os
# from db.queries.actions import create_action
from db.mongo import full_actions2DB
from db.mongo import inputs
base_url = '.zendesk.com/api/v2/'

from datetime import datetime
class Zendesk:
    def load_data(self,org_domain,token,user):
        print("token",token)
        # url = 'https://quilliup'+base_url+'tickets.json'
        page = 1
        done = False

        array = []
        while(not done):
            url = "https://"+org_domain+base_url+"search.json?page=" + str(page)+'&query=created>2020-11-30  type:ticket '
            params = {
                "Authorization": "Basic " + token
            }
            r = requests.get(url, headers=params)
            data = r.json()

            for action in data["results"]:
                resolution_date = None
                if(action["status"] == "closed" or action["status"] == "solved"):
                    resolution_date = action["updated_at"]
                priority = None
                issue_type = None
                client = None
                server = None
                for pr in action["custom_fields"]:
                    if pr["id"] == 24917485:
                        priority = pr["value"]
                    if pr["id"] == 44906789:
                        issue_type = pr["value"]
                    if pr["id"] == 24862879:
                        client = pr["value"]
                    if pr["id"] == 44524909:
                        server = pr["value"]
                assignee = Zendesk.get_user(params,"https://quilliup"+base_url,action["assignee_id"])
                creator_id = Zendesk.get_user(params,"https://quilliup"+base_url,action["requester_id"])
                follower_ids = []
                for fl in action["follower_ids"]:
                    d = Zendesk.get_user(params,"https://quilliup"+base_url,fl)
                    follower_ids = follower_ids +d
                print(action["updated_at"])
                updated = datetime.strptime(action["updated_at"],"%Y-%m-%dT%H:%M:%S%z")
                is_waiting = False
                if user["email"] in assignee:
                    is_waiting = True

                actionurl = action["url"]
                actionurl = actionurl.replace("api/v2/","agent/").replace(".json","")
                obj = {
                    "action_id": None,
                    "key": action["id"],
                    "project_id": None,
                    "issue_status_id": None,
                    "summary": action["subject"],
                    "updated": updated,
                    "description": action["description"],
                    "due_date": "",
                    "resolution": action["status"],
                    "resolution_date": resolution_date,
                    "priority": priority,
                    "issue_type": issue_type,
                    "assignee": assignee,
                    "watches": follower_ids,
                    "labels": None,
                    "url": actionurl,
                    "fix_version":None,
                    "origin_type": "zendesk",
                    "user_id": user["_id"],
                    "user_email": user["email"],
                    "project_name": None,
                    "closed": None,
                    "project_closed": None,
                    "issue_status_name": None,
                    "issue_status_closed": None,
                    "topic": None,
                    "start_date": None,
                    "time_estimate": None,
                    "due_complete": None,
                    "id_labels": None,
                    "creator": creator_id,
                    "client":client,
                    "server":server,
                    "board_last_activity": None,
                    "is_waiting":is_waiting
                }
                inputs.find_one_and_update({"email":user["email"],"key":action["id"]},{"$set":obj},upsert=True)
                # array.append(obj)
            if data["next_page"]:
                page += 1
                print("data:", data["next_page"])
            else:
                done = True

        # full_actions2DB.insert_many(array)

        # del data["tickets"]
        # print(data)

    def get_user(headers,base_url,user_id):
        print("user",user_id)
        if(user_id == None):
            return []
        else:
            r = requests.get(base_url+'users/'+str(user_id)+'.json',headers=headers)
            data = r.json()
            return [data["user"]["email"]]
