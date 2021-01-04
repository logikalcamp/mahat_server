import os
import requests
# from db.queries.actions import create_action

os.environ['JIRA_CLIENT_ID'] = '1s6gbhSYYOcdCqXDSArpNRSAIqN2ykNk'
os.environ['JIRA_CLIENT_SECRET'] = 'jyUL8Jdi455Ey41jGKM6z8EAvBpPPXuHm9h3w0OV_maUH_C-MANaxOexypBBvXfA'
client_id = os.environ['JIRA_CLIENT_ID']
client_secret = os.environ['JIRA_CLIENT_SECRET']

base_url = '.atlassian.net/rest/api/3'
from datetime import datetime
from db.mongo import inputs

class Jira:

    def refresh_token(refresh_token):
            params = {
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token
            }

            authorization_url = "https://auth.atlassian.com/oauth/token"
            r = requests.post(authorization_url, data=params)
            if r.ok:
                return r.json()['access_token']
            else:
                return None
    def get_all_projects(refresh_token,org_domain):
        token = Jira.refresh_token(refresh_token)
        headers = {
            "Authorization": "Basic " + token
        }
        url = 'https://' + org_domain + base_url + '/project/search'
        r = requests.get(url, headers=headers)
        print(r.json())


        # rest / api / 3 / project / search
    def load_data(self,token,org_domain,user):
        headers = {
            "Authorization": "Basic " + token
        }
        url = 'https://' + org_domain + base_url
        array = []
        counter = 1
        self.get_all_issue(headers,url,array,counter,user)

        # print("-------------------------done reading-------------------------")
        # # print(array)
        # count = 1
        # for i in array:
        #     i["id"] = count
        #     print(count,i)
        #     create_action(i)
        #     count = count + 1

    def get_all_issue(headers,basic_url,array,counter,user):
        startAt = 0
        print("started")
        url = basic_url+'/search?jql=created >= startOfMonth(-2) &maxResults=100&startAt='
        r = requests.get(url+str(startAt),headers=headers)
        data = r.json()
        arr = []
        # print(data["total"])
        for action in data["issues"]:
            print(action)
            resolution =  None
            if (action["fields"]["resolution"]):
                resolution = action["fields"]["resolution"]["name"]
            priority = None
            if (action["fields"]["priority"]):
                priority = action["fields"]["priority"]["name"]
            issue_type = None
            if (action["fields"]["issuetype"]):
                issue_type = action["fields"]["issuetype"]["name"]
            emailAddress = []
            if (action["fields"]["assignee"]):
                if "emailAddress" in action["fields"]["assignee"]:
                    emailAddress = action["fields"]["assignee"]["emailAddress"]
                else:
                    emailAddress = action["fields"]["assignee"]["displayName"]
            fixVersions = []
            if(len(action["fields"]["fixVersions"])>1):
                fixVersions = action["fields"]["fixVersions"][0]["name"]

            due = ''
            if  action["fields"]["duedate"]:
                print( action["fields"]["duedate"])
                due =datetime.strptime(action["fields"]["duedate"],"%Y-%m-%d")

            updated = datetime.strptime(action["fields"]["updated"],"%Y-%m-%dT%H:%M:%S.%f%z")
            is_waiting = False
            if user["email"] in emailAddress:
                is_waiting= True
            actionurl = basic_url + '/browse/' + action["key"]
            obj = {
                "action_id": action["id"],
                "key": action["key"],
                "project_id": action["fields"]["project"]["id"],
                "issue_status_id": action["fields"]["status"]["id"],
                "summary": action["fields"]["summary"],
                "updated": updated,
                "description": str(action["fields"]["description"]),
                "due_date": due,
                "resolution": resolution,
                "resolution_date": action["fields"]["resolutiondate"],
                "priority": priority,
                "issue_type": issue_type,
                "assignee": emailAddress,
                "watches": action["fields"]["watches"]["watchCount"],
                "labels": action["fields"]["labels"],
                "url": actionurl,
                "fix_version": fixVersions,
                "origin_type": 'jira',
                "user_id": user["_id"],
                "user_email":user["email"],
                "project_name": action["fields"]["project"]["name"],
                "closed": None,
                "project_closed": action["fields"]["project"]["key"],
                "issue_status_name": action["fields"]["status"]["name"],
                "issue_status_closed": None,
                "topic": None,
                "start_date": None,
                "time_estimate": None,
                "due_complete": None,
                "id_labels": None,
                "creator": None,
                "client": None,
                "server": None,
                "board_last_activity": action["fields"]["lastViewed"],
                "is_waiting":is_waiting
            }
            # print(obj)
            try:
                # arr.append(obj)
                inputs.find_one_and_update({"user_email":user["email"],"action_id":action["id"]},{"$set":obj},upsert=True)
                # create_action(obj)
            except:
                print("missed: ", obj["key"])

        amount = data["total"]-startAt
        while(amount > 0):
            startAt += data["maxResults"]
            newUrl = url +str(startAt)
            # print(newUrl)
            print("newUrl",newUrl)
            print("headers",headers)
            r = requests.get(newUrl, headers=headers)
            print(r)
            try:
                data = r.json()
                amount = amount - data["maxResults"]
                for action in data["issues"]:
                    resolution = None
                    if(action["fields"]["resolution"]):
                        resolution = action["fields"]["resolution"]["name"]
                    priority = None
                    if(action["fields"]["priority"]):
                        priority = action["fields"]["priority"]["name"]
                    issue_type = None
                    if(action["fields"]["issuetype"]):
                       issue_type = action["fields"]["issuetype"]["name"]
                    emailAddress = []
                    if(action["fields"]["assignee"]):
                        if "emailAddress" in action["fields"]["assignee"]:
                            emailAddress = action["fields"]["assignee"]["emailAddress"]
                        else:
                            emailAddress = action["fields"]["assignee"]["displayName"]
                    fixVersions = []
                    if (len(action["fields"]["fixVersions"]) > 1):
                        fixVersions = action["fields"]["fixVersions"][0]["name"]
                    # print(action)
                    due = ''
                    if action["fields"]["duedate"]:
                        print(action["fields"]["duedate"])
                        due = datetime.strptime(action["fields"]["duedate"], "%Y-%m-%d")
                    updated = datetime.strptime(action["fields"]["updated"], "%Y-%m-%dT%H:%M:%S.%f%z")
                    is_waiting = False
                    if user["email"] in emailAddress:
                        is_waiting = True
                    actionurl = basic_url + '/browse/' + action["key"]
                    obj = {
                        "action_id":action["id"],
                        "key": action["key"],
                        "project_id": action["fields"]["project"]["id"],
                        "issue_status_id": action["fields"]["status"]["id"],
                        "summary": action["fields"]["summary"],
                        "updated": updated,
                        "description": str(action["fields"]["description"]),
                        "due_date": due,
                        "resolution": resolution,
                        "resolution_date": action["fields"]["resolutiondate"],
                        "priority": priority,
                        "issue_type": issue_type,
                        "assignee": emailAddress,
                        "watches": action["fields"]["watches"]["watchCount"],
                        "labels": action["fields"]["labels"],
                        "url": actionurl,
                        "fix_version": fixVersions,
                        "origin_type":'jira',
                        "user_id": user["_id"],
                        "user_email":user["email"],
                        "project_name": action["fields"]["project"]["name"],
                        "closed": None,
                        "project_closed": action["fields"]["project"]["key"],
                        "issue_status_name": action["fields"]["status"]["name"],
                        "issue_status_closed":None,
                        "topic":None,
                        "start_date":None,
                        "time_estimate":None,
                        "due_complete":None,
                        "id_labels":None,
                        "creator":None,
                        "client":None,
                        "server":None,
                        "board_last_activity": action["fields"]["lastViewed"],
                        "is_waiting":is_waiting
                    }
                    # print(obj)
                    try:
                        # arr.append(obj)
                        inputs.find_one_and_update({"user_email": user["email"], "action_id": action["id"]}, {"$set": obj},upsert=True)
                        # create_action(obj)
                    except:
                        print("missed: ",obj["key"])
            except:
                print("missed")
        print(len(arr))


            # integer
        print(len(data["issues"]))

        print('')

    def get_all_actions(self):
        print()

    def get_all_boards(self):
        print()