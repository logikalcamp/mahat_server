
import requests
from flask_restful import reqparse, abort, Resource, reqparse
from flask import request, jsonify ,Flask
from flask_jwt_extended import (JWTManager, jwt_required,
                                jwt_refresh_token_required,
                                jwt_optional, fresh_jwt_required,
                                get_raw_jwt, get_jwt_identity,
                                create_access_token, create_refresh_token,
                                set_access_cookies, set_refresh_cookies,
                                unset_jwt_cookies,unset_access_cookies)
# from apps.functions import Functions
from apps.gmail import GmailWorker
from db.mongo import users,inputs,events
import datetime

# from db.queries.users import find_user,create_user

class Queries(Resource):
    decorators = [jwt_required]
    def get(self,quest):
        # user = {
        #     "_id":"5ff19939af9933b84a9d782f",
        #     "email":"noam.kashtan@vision.bi"
        # }
        # user = {
        #     "_id":"5fe822a29b5c47e2b874a61c",
        #     "email":"chenm@vision.bi"
        # }
        user = get_jwt_identity()
        # user["_id"] = str(user["_id"])
        # user = {"_id":"5fe8e66fd34dda85b9a19658"}
        print(user)
        arr = []
        if quest == "waiting":
            # is_waiting = true
            data = inputs.aggregate([
                {
                    "$match":{
                        "user_id":user["_id"],
                        "is_waiting":True,
                        "due_date": '',
                        "closed": {"$ne": True},
                        "resolution": {"$ne": "closed"}
                        # "resolution": {"$ne": "Closed"}
                    }
                },
                {
                    "$group":{
                        "_id":"$project_id",
                        "action_id": {"$last": "$action_id"},
                        "key": {"$last": "$key"},
                        "project_id": {"$last": "$project_id"},
                        "issue_status_id": {"$last": "$issue_status_id"},
                        "summary": {"$last": "$summary"},
                        "created_at": {"$last": "$created_at"},
                        "updated": {"$last": "$updated"},
                        "description": {"$last": "$description"},
                        "parentFolderId": {"$last": "$parentFolderId"},
                        "due_date": {"$last": "$due_date"},
                        "resolution": {"$last": "$resolution"},
                        "resolution_date": {"$last": "$resolution_date"},
                        "priority": {"$last": "$priority"},
                        "issue_type": {"$last": "$issue_type"},
                        "assignee": {"$last": "$assignee"},
                        "watches": {"$last": "$watches"},
                        "labels": {"$last": "$labels"},
                        "url": {"$last": "$url"},
                        "fix_version": {"$last": "$fix_version"},
                        "origin_type": {"$last": "$origin_type"},
                        "user_id": {"$last": "$user_id"},
                        "user_email": {"$last": "$user_email"},
                        "project_name": {"$last": "$project_name"},
                        "closed": {"$last": "$closed"},
                        "project_closed": {"$last": "$project_closed"},
                        "issue_status_name": {"$last": "$issue_status_name"},
                        "issue_status_closed": {"$last": "$issue_status_closed"},
                        "topic": {"$last": "$topic"},
                        "start_date": {"$last": "$start_date"},
                        "time_estimate": {"$last": "$time_estimate"},
                        "due_complete": {"$last": "$due_complete"},
                        "id_labels": {"$last": "$id_labels"},
                        "creator": {"$last": "$creator"},
                        "client": {"$last": "$client"},
                        "server": {"$last": "$server"},
                        "board_last_activity": {"$last": "$board_last_activity"},
                        "is_waiting": {"$last": "$is_waiting"},
                    }
                },
                {
                    "$sort": {"updated": 1}
                }
            ])
            # data = inputs.find({"user_id":user["_id"],"is_waiting":True})
            for l in data:
                l["_id"] = str(l["_id"])
                if l["created_at"]:
                    if isinstance(l["created_at"], str):
                        l["created_at"] = l["created_at"]
                    else:
                        l["created_at"] = l["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                if l["updated"]:
                    if isinstance(l["updated"], str):
                        l["updated"] = l["updated"]
                    else:
                        l["updated"] = l["updated"].strftime("%Y-%m-%d %H:%M:%S")
                if l["due_date"]:
                    if isinstance(l["due_date"], str):
                        l["due_date"] = l["due_date"]
                    else:
                        l["due_date"] = l["due_date"].strftime("%Y-%m-%d %H:%M:%S")
                arr.append(l)
        if quest == "updates":
            # to add condition for updates in last 3 days
            data = inputs.aggregate([
                {
                    "$match":{
                        "user_id":user["_id"],
                        "is_waiting":False,
                        "due_date":'',
                        "updated": {"$gt": datetime.datetime.now() - datetime.timedelta(days=3)},
                        "closed":{"$ne":True},
                        "resolution": {"$ne": "closed"}
                        # "resolution": {"$ne": "Closed"}
                    }
                },
                {
                    "$group": {
                        "_id": "$project_id",
                        "action_id": {"$last": "$action_id"},
                        "key": {"$last": "$key"},
                        "project_id": {"$last": "$project_id"},
                        "issue_status_id": {"$last": "$issue_status_id"},
                        "summary": {"$last": "$summary"},
                        "created_at": {"$last": "$created_at"},
                        "updated": {"$last": "$updated"},
                        "description": {"$last": "$description"},
                        "parentFolderId": {"$last": "$parentFolderId"},
                        "due_date": {"$last": "$due_date"},
                        "resolution": {"$last": "$resolution"},
                        "resolution_date": {"$last": "$resolution_date"},
                        "priority": {"$last": "$priority"},
                        "issue_type": {"$last": "$issue_type"},
                        "assignee": {"$last": "$assignee"},
                        "watches": {"$last": "$watches"},
                        "labels": {"$last": "$labels"},
                        "url": {"$last": "$url"},
                        "fix_version": {"$last": "$fix_version"},
                        "origin_type": {"$last": "$origin_type"},
                        "user_id": {"$last": "$user_id"},
                        "user_email": {"$last": "$user_email"},
                        "project_name": {"$last": "$project_name"},
                        "closed": {"$last": "$closed"},
                        "project_closed": {"$last": "$project_closed"},
                        "issue_status_name": {"$last": "$issue_status_name"},
                        "issue_status_closed": {"$last": "$issue_status_closed"},
                        "topic": {"$last": "$topic"},
                        "start_date": {"$last": "$start_date"},
                        "time_estimate": {"$last": "$time_estimate"},
                        "due_complete": {"$last": "$due_coסכmplete"},
                        "id_labels": {"$last": "$id_labels"},
                        "creator": {"$last": "$creator"},
                        "client": {"$last": "$client"},
                        "server": {"$last": "$server"},
                        "board_last_activity": {"$last": "$board_last_activity"},
                        "is_waiting": {"$last": "$is_waiting"},
                    }
                },
                {
                    "$sort":{"updated":-1}
                }
            ])
            # data = inputs.find({"user_id":user["_id"],"is_waiting":False,"due_date":'',"updated":{ "$gt": datetime.datetime.now() - datetime.timedelta(days=3) }})
            for l in data:
                l["_id"] = str(l["_id"])
                if l["created_at"]:
                    if isinstance(l["created_at"], str):
                        l["created_at"] = l["created_at"]
                    else:
                        l["created_at"] = l["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                if l["updated"]:
                    if isinstance(l["updated"], str):
                        l["updated"] = l["updated"]
                    else:
                        l["updated"] = l["updated"].strftime("%Y-%m-%d %H:%M:%S")
                if l["due_date"]:
                    if isinstance(l["due_date"], str):
                        l["due_date"] = l["due_date"]
                    else:
                        l["due_date"] = l["due_date"].strftime("%Y-%m-%d %H:%M:%S")
                arr.append(l)
        if quest == "deadline":
            # to add order by priority
            data = inputs.aggregate([
                {
                    "$match":{
                        "user_id":user["_id"],
                        "due_date":{"$ne":''},
                        "closed": {"$ne": True},
                        "resolution":{"$ne":"closed"}
                        # "resolution" : {"$ne":"Closed"}
                    }
                },
                {
                    "$group": {
                        "_id": "$project_id",
                        "action_id": {"$last": "$action_id"},
                        "key": {"$last": "$key"},
                        "project_id": {"$last": "$project_id"},
                        "issue_status_id": {"$last": "$issue_status_id"},
                        "summary": {"$last": "$summary"},
                        "created_at": {"$last": "$created_at"},
                        "updated": {"$last": "$updated"},
                        "description": {"$last": "$description"},
                        "parentFolderId": {"$last": "$parentFolderId"},
                        "due_date": {"$last": "$due_date"},
                        "resolution": {"$last": "$resolution"},
                        "resolution_date": {"$last": "$resolution_date"},
                        "priority": {"$last": "$priority"},
                        "issue_type": {"$last": "$issue_type"},
                        "assignee": {"$last": "$assignee"},
                        "watches": {"$last": "$watches"},
                        "labels": {"$last": "$labels"},
                        "url": {"$last": "$url"},
                        "fix_version": {"$last": "$fix_version"},
                        "origin_type": {"$last": "$origin_type"},
                        "user_id": {"$last": "$user_id"},
                        "user_email": {"$last": "$user_email"},
                        "project_name": {"$last": "$project_name"},
                        "closed": {"$last": "$closed"},
                        "project_closed": {"$last": "$project_closed"},
                        "issue_status_name": {"$last": "$issue_status_name"},
                        "issue_status_closed": {"$last": "$issue_status_closed"},
                        "topic": {"$last": "$topic"},
                        "start_date": {"$last": "$start_date"},
                        "time_estimate": {"$last": "$time_estimate"},
                        "due_complete": {"$last": "$due_complete"},
                        "id_labels": {"$last": "$id_labels"},
                        "creator": {"$last": "$creator"},
                        "client": {"$last": "$client"},
                        "server": {"$last": "$server"},
                        "board_last_activity": {"$last": "$board_last_activity"},
                        "is_waiting": {"$last": "$is_waiting"},
                    }
                }
            ])
            # data = inputs.find({"user_id":user["_id"], "due_date": {"$ne":''}})
            for l in data:
                l["_id"] = str(l["_id"])
                if l["created_at"]:
                    if isinstance(l["created_at"], str):
                        l["created_at"] = l["created_at"]
                    else:
                        l["created_at"] = l["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                if l["updated"]:
                    if isinstance(l["updated"], str):
                        l["updated"] = l["updated"]
                    else:
                        l["updated"] = l["updated"].strftime("%Y-%m-%d %H:%M:%S")
                if l["due_date"]:
                    if isinstance(l["due_date"], str):
                        l["due_date"] = l["due_date"]
                    else:
                        l["due_date"] = l["due_date"].strftime("%Y-%m-%d %H:%M:%S")
                arr.append(l)
        if quest == "refresh":
            data = events.find({"email":user["email"],"event":"last_data_refresh"})
            for l in data:
                l["_id"] = str(l["_id"])
                l["time"] = l["time"].strftime('%Y/%m/%d %H:%M:%S')
                arr.append(l)
        print(len(arr))
        return arr,200


# { "$gt": datetime.datetime.now() - datetime.timedelta(days=2) }}