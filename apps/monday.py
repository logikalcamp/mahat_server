from graphqlclient import GraphQLClient
import requests
import os
import json
import sys
from urllib.error import HTTPError
from db.mongo import full_actions2DB
import datetime

class Monday():
    def __init__(self,token):
        self.token = token

    def load_data(token,board_id,db,user):
        array = []
        client = GraphQLClient("https://api.monday.com/v2/")
        client.inject_token(token)
        params = {
            'board_id':int(board_id)
        }
        query = '''
            query($board_id:[Int]){
              boards(ids:$board_id,limit:1000){
                id
                name
                items{
                  name
                  id
                  created_at
                  updated_at
                    creator {
                      id
                    name
                    email
                    }
                  group{
                    id
                    title
                  }
                  column_values(ids:["status","person","date","status1","person1","date1","status2","person2","date2","status3","person3","date3","status4","person4","date4"]){
                    value
                    title
                    id
                    text
                  }
                }
              }
            }
        '''
        result = client.execute(query,params)
        data = json.loads(result)
        board_id = data["data"]["boards"][0]["id"]
        board_name = data["data"]["boards"][0]["name"]
        for item in data["data"]["boards"][0]["items"]:
            due_date = None
            status=""
            status_id=""
            person = None
            for column in item["column_values"]:
                print(column)
                print(item["column_values"][0]["value"])
                print(column["value"])
                if "status" in column["id"]:
                    status = column["text"]
                    status_id = column["id"]
                if "person" in column["id"]:
                    if column["value"]:
                        temp = json.loads(column["value"])
                        print(temp)
                        if "personsAndTeams" in temp:
                            person = Monday.get_user(token, temp["personsAndTeams"][0]["id"])
                if "date" in column["id"]:
                    if column["value"]:
                        due_dateTemp = json.loads(column["value"])
                        due_date = due_dateTemp["date"]
            creator = None
            if item["creator"]:
                creator = item["creator"]["email"]

            updated = datetime.datetime.strptime(item["updated_at"],"%Y-%m-%d %H:%M:%S UTC")
            if due_date:
                if "-" in due_date:
                    due_date = datetime.datetime.strptime(due_date,"%Y-%m-%d")
                else:
                    if "/" in due_date:
                        due_date = datetime.datetime.strptime(due_date, "%m/%d/%Y")
            isWaiting = False
            if person == user["email"]:
                isWaiting = True
            obj = {
                "action_id": item["id"],
                "key": None,
                "project_id": board_id,
                "issue_status_id": status_id,
                "summary": item["name"],
                "created_at":item["created_at"],
                "updated": updated,
                "description": None,
                "due_date": due_date,
                "resolution": None,
                "resolution_date": None,
                "priority": None,
                "issue_type": None,
                "assignee": [person],
                "watches": None,
                "labels": [item["group"]["title"]],
                "url": None,
                "fix_version": None,
                "origin_type": "monday",
                "user_id": user["_id"],
                "user_email":user["email"],
                "project_name": board_name,
                "closed": None,
                "project_closed": None,
                "issue_status_name": status,
                "issue_status_closed": None,
                "topic": None,
                "start_date": None,
                "time_estimate": None,
                "due_complete": None,
                "id_labels": None,
                "creator":creator,
                "client": None,
                "server": None,
                "board_last_activity": None,
                "is_waiting":isWaiting
            }
            array.append(obj)
            db.find_one_and_update({"action_id": item["id"], "user_email": user["email"]}, {"$set": obj}, upsert=True)
        print(len(array))
        # db.insert_many(array)

    def get_user(token,user_id):
        client = GraphQLClient("https://api.monday.com/v2/")
        client.inject_token(token)
        params = {
            'user_id': user_id
        }
        query = '''
            query($user_id:[Int]){
              users(ids:$user_id){
               email
              }
            }
        '''
        result = client.execute(query, params)
        # print(result)
        data = json.loads(result)
        if "data" in data:
            return data["data"]["users"][0]["email"]
        else:
            return ""

    def get_boards(token):
        array = []
        client = GraphQLClient("https://api.monday.com/v2/")
        client.inject_token(token)
        query = '''
            query{
                boards{
                    id
                    name
                }
            }
        '''
        try:
            result = client.execute(query)
            data = json.loads(result)
            # print("data: ",data)
            return data["data"]["boards"]
        except HTTPError as e:
            return {"code":e.code}
