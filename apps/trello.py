import requests
import os
from datetime import datetime
# from db.queries.actions import create_action
# from db.mongo import full_actions2DB

os.environ['TRELLO_API_KEY'] = '376998bf9b552e830d5f418d4ca58271'

base_url = 'https://api.trello.com'
key = os.environ['TRELLO_API_KEY']


class Trello:
    # def load_data(self,token):
    #     params = {
    #         "key":key,
    #         "token":token
    #     }
    #     array = []
    #     counter = 1
    #     self.get_all_boards(params,array,counter)
    #     print("-------------------------done reading-------------------------")
    #     # print(array)
    #     count = 1
    #     # for i in array:
    #     #     i["id"] = count
    #     #     print(count)
    #     #     create_action(i)
    #     #     count = count + 1
    #
    #     full_actions2DB.insert_many(array)
    #     # create_actions(array)
    # def get_all_actions(self):
    #     print('')

    def load_data(token,board_id,db,user):

        boardObj = Trello.get_board(token,board_id)
        params = {
                "key":key,
                "token":token
            }
        url = "/1/boards/" + board_id + "/lists"
        r = requests.get(base_url + url, data=params)
        data = r.json()
        for list in data:
            # print("---------list")
            # print(list["name"]," ",list["id"]," ",list["closed"])
            listObj = {
                "issue_status_id": list["id"],
                "issue_status_name": list["name"],
                "issue_status_closed": list["closed"]
            }

        Trello.get_all_cards(list["id"], params, boardObj, listObj, db,user)
        return True

    def get_board(token,id):
        params = {
            "key": key,
            "token": token
        }
        url = "/1/board/" + id
        r = requests.get(base_url + url, data=params)
        print(r.status_code)
        data = r.json()
        print(data)
        obj = {
            "project_name": data["name"],
            "board_last_activity": None,
            "project_id": data["id"],
            "project_closed": data["closed"]
        }
        return obj

    def get_boards(token):
        params = {
                "key":key,
                "token":token
            }
        url = "/1/members/me/boards"
        r = requests.get(base_url + url, data=params)
        print(r.status_code)
        try:
            data = r.json()
            return data
        except:
            return {"code":r.status_code}

    def get_all_boardss(params,array,counter):
        url = "/1/members/me/boards"
        r = requests.get(base_url+url, data=params)
        data = r.json()
        for board in data:
            print("------------board")
            if(board["name"] == "tasks- quilliup"):
                print(board["name"]," ",board["dateLastActivity"]," - ",board["id"])
                obj = {
                    "project_name":board["name"],
                    "board_last_activity":board["dateLastActivity"],
                    "project_id":board["id"],
                    "project_closed":board["closed"]
                }
                Trello.get_all_lists(board["id"],params,obj,array,counter)
                # break


    def get_all_lists(id,params,boardObj,array,counter):
        url = "/1/boards/"+id+"/lists"
        r = requests.get(base_url + url, data=params)
        data = r.json()
        for list in data:
            # print("---------list")
            # print(list["name"]," ",list["id"]," ",list["closed"])
            listObj = {
                "issue_status_id":list["id"],
                "issue_status_name":list["name"],
                "issue_status_closed":list["closed"]
            }

            Trello.get_all_cards(list["id"],params,boardObj,listObj,array,counter)
            # break

    def get_all_cards(id,params,boardObj,listObj,db,user):
        url = "/1/lists/" + id + "/cards"
        r = requests.get(base_url + url, data=params)
        data = r.json()
        for card in data:
            print("---card")

            assignee = []
            print(card)
            for user_id in card["idMembers"]:
                print(user_id)
                another_url = "/1/members/" + user_id
                r = requests.get(base_url+another_url,data=params)
                user_data = r.json()
                print(user_data)
                if user_data["email"]:
                    assignee.append(user_data["email"])
                else:
                    assignee.append(user_data["username"])
            labels = []

            for label in card["labels"]:
                labels.append(label["name"])
            # print(card["id"])
            is_waiting = False
            if user["email"] in assignee:
                is_waiting = True

            updated = None
            due = ''
            if card["dateLastActivity"]:
                updated =  datetime.strptime(card["dateLastActivity"],"%Y-%m-%dT%H:%M:%S.%f%z")
            if card["due"]:
                due = datetime.strptime(card["due"],"%Y-%m-%dT%H:%M:%S.%f%z")
            obj = {
                "action_id": card["id"],
                "key": None,
                "project_id": boardObj["project_id"],
                "issue_status_id": listObj["issue_status_id"],
                "summary": card["name"],
                "updated":updated,
                "description": card["desc"],
                "due_date": due,
                "resolution": None,
                "resolution_date": None,
                "priority": 0,
                "issue_type": None,
                "assignee": assignee,
                "watches": card["idMembersVoted"],
                "labels": labels,
                "url":card["url"],
                "fix_version": None,
                "origin_type": 'trello',
                "user_id": user["_id"],
                "user_email": user["email"],
                "project_name": boardObj["project_name"],
                "closed": card["closed"],
                "project_closed": boardObj["project_closed"],
                "issue_status_name": listObj["issue_status_name"],
                "issue_status_closed": listObj["issue_status_closed"],
                "topic": None,
                "start_date": None,
                "time_estimate": None,
                "due_complete": card["dueComplete"],
                "id_labels": card["idLabels"],
                "creator": None,
                "client": None,
                "server": None,
                "board_last_activity": boardObj["board_last_activity"],
                "is_waiting":is_waiting
            }
            db.find_one_and_update({"action_id":card["id"],"user_email":user["email"]},{"$set":obj},upsert=True)
            # counter += 1
        return True
            #
            # array.append(obj)

            # print(list["name"], " ", list["id"], " ", list["closed"])

