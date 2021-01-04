import requests
from flask_restful import reqparse, Resource, reqparse
from flask import request, jsonify ,Flask,abort
from apps.monday import Monday
from apps.trello import Trello
from apps.asana import Asana
from apps.clickup import Clickup
from apps.jira import Jira
from db.mongo import integrations,inputs
from flask_jwt_extended import jwt_required ,get_jwt_identity
from datetime import datetime

class Third_Apps(Resource):
    decorators = [jwt_required]

    def get(self,app_name=None,method=None):
        user = get_jwt_identity()
        if app_name:
            if app_name == "monday":
                if method == "get_boards":
                    print()
        else:
            data = integrations.find({"email":user["email"]})
            # return data
            obj = {}
            for app in data:
                print(app)
                if "isAutherized" in app:
                    obj[app["app"]] = True
            return obj

    def post(self,app_name,method):
        user = get_jwt_identity()
        print(user)
        if app_name == "monday":
            if method == "setup":
                data = request.get_json()
                result = Monday.get_boards(data["token"])
                if "code" in result:
                    abort(401, description="Invalid Token.")
                else:
                    # should run for the first time

                    # should setup the integration
                    obj = {
                        "token":data["token"],
                        "app":"monday",
                        "email":user["email"],
                        "time": datetime.now()
                    }
                    integrations.find_one_and_update({"email":user["email"],"app":"monday"}, {"$set":obj},upsert=True)
                    return result,200
            if method == "setup_boards":
                data = request.get_json()
                obj = {
                    "boards": data["boards"],
                    "isAutherized": True
                }
                integrations.find_one_and_update({"email": user["email"], "app": "monday"}, {"$set": obj}, upsert=True)
                return True, 200
            if method == "load_data":
                print("im here")
                doc = integrations.find_one({"email":user["email"],"app":"monday"})
                print(doc)
                for board in doc["boards"]:
                    Monday.load_data(doc["token"],board,inputs,user)
                return True,200
        if app_name == "trello":
            if method == "setup":
                data = request.get_json()
                result = Trello.get_boards(data["token"])
                if "code" in result:
                    abort(401, description="Invalid Token.")
                else:
                    # should setup the integration
                    obj = {
                        "token":data["token"],
                        "app":"trello",
                        "email":user["email"],
                        "time": datetime.now()
                    }
                    integrations.find_one_and_update({"email":user["email"],"app":"trello"},{"$set":obj},upsert=True)
                    return result,200
            if method == "setup_boards":
                data = request.get_json()
                obj = {
                    "boards":data["boards"],
                    "isAutherized":True
                }
                integrations.find_one_and_update({"email": user["email"], "app": "trello"}, {"$set":obj}, upsert=True)
                return True,200
            if method == "load_data":
                # print("im here")
                doc = integrations.find_one({"email":user["email"],"app":"trello"})
                print(doc)
                for board in doc["boards"]:
                    Trello.load_data(doc["token"],board,inputs,user)
                    print("add one board")
                return True,200
        if app_name == "clickup":
            if method == "setup":
                data = request.get_json()
                token = Clickup.get_access_token(data["token"])
                result = Clickup.get_boards(token)
                if "code" in result:
                    abort(401, description="Invalid Token.")
                else:
                    obj = {
                        "token": token,
                        "app": "clickup",
                        "email": user["email"],
                        "time": datetime.now()
                    }
                    integrations.find_one_and_update({"email": user["email"], "app": "clickup"}, {"$set": obj},upsert=True)
                    return result,200
            if method == "setup_boards":
                data = request.get_json()
                obj = {
                    "boards":data["boards"],
                    "isAutherized":True
                }
                integrations.find_one_and_update({"email": user["email"], "app": "clickup"}, {"$set":obj}, upsert=True)
                return True,200
        if app_name == "asana":
            if method == "setup":
                data = request.get_json()
                refresh_token = Asana.get_refresh_token(data["token"])
                accees_token = Asana.get_access_token(refresh_token)
                result = Asana.get_boards(accees_token)
                if "code" in refresh_token:
                    abort(401, description="Invalid Token.")
                else:
                    # should setup the integration
                    obj = {
                        "token":refresh_token,
                        "app":"asana",
                        "email":user["email"],
                        "time": datetime.now()
                    }
                    integrations.find_one_and_update({"email":user["email"],"app":"asana"}, {"$set":obj},upsert=True)
                    return result,200
            if method == "setup_boards":
                data = request.get_json()
                obj = {
                    "boards":data["boards"],
                    "isAutherized":True
                }
                integrations.find_one_and_update({"email": user["email"], "app": "asana"}, {"$set":obj}, upsert=True)
                return True,200
        if app_name == "jira":
            print("boom")
            body_data = request.get_json()
            if method == "setup":
                data = {
                    "grant_type":"authorization_code",
                    "client_id":"1s6gbhSYYOcdCqXDSArpNRSAIqN2ykNk",
                    "client_secret":"jyUL8Jdi455Ey41jGKM6z8EAvBpPPXuHm9h3w0OV_maUH_C-MANaxOexypBBvXfA",
                    "code":body_data["token"],
                    "redirect_uri":body_data["url"]
                }
                r = requests.post("https://auth.atlassian.com/oauth/token",data=data)
                print(r.json())
                refresh_token = r.json()["refresh_token"]
                accees_token = r.json()["access_token"]
                boards = Jira.get_all_projects(refresh_token,body_data["subdomain"])
                print("boards",boards)

                return True
            # let data = {
            #     "grant_type":"authorization_code",
            #     "client_id":"mOhVjuVJ1LqUwBz2T4DiTCLvmuOrjepv",
            #     "client_secret":"OAMKwOipgOhswG5AMnw1JB0xW4QLd5D4G0dEtnbMZ6W5DfGaI8aaZxmqQQJkQRLv",
            #     "code":router.query.code,
            #     "redirect_uri":APP_URL+'/jira'
            # }
            # axios.post('https://auth.atlassian.com/oauth/token',data).then((res)=>{
            #     // res.data
            #     console.log(res.data)
            #     let newApp = {
            #         name:"jira",
            #         tokens:res.data,
            #         user_id:account.id
            #     }
            #
            #
            # })