
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
from apps.outlook import OutlookWorker
from db.mongo import users,events,logs
from threading import Thread
from datetime import datetime
import sys
# from db.queries.users import find_user,create_user


black_listed = ['vgpnewsletter@gmail.com',
                'wshops@wallashopsmail.co.il',
                'info@big-shot-trade.com',
                'calendar-notification@google.com',
                'noreply@mail.pinnacle.com',
                'info@truefire.com',
                'sandy.mcneel@mcneel.com']




class Auth_Outlook(Resource):
    def get(self):
        #     fetch login info
        print()


    def post(self):
        data = request.get_json()
        doc = OutlookWorker.get_userinfo(data)
        user = users.find_one({"email":doc["email"]})
        if(user):
            print("return access token")
            if "apps" in user:
                del user["apps"]
            user["_id"] = str(user["_id"])
            access_token = create_access_token(identity=user, expires_delta=False)
            print(jsonify(access_token=access_token))
            print(jsonify(access_token=access_token, user=user))
            user["access_token"] = access_token
            return user, 200
        else:

            doc["platform"] = "microsoft"
            # created_id = users.insert(doc)
            created_id = "123"
            doc["_id"] = str(created_id)
            acc_data = doc

            code = doc["code"]
            print(doc["code"]["refresh_token"])
            OutlookWorker.get_all_emails(doc["code"]["refresh_token"], doc)
            del acc_data["code"]
            print(acc_data)
            access_token = create_access_token(identity=acc_data, expires_delta=False)
            # print("code: ",doc["code"])
            print("doc: ", doc)
            doc["access_token"] = access_token
            # should run the first time
            # print(doc)
            return doc, 200

    def put(self):

        def do_work(refresh_token,doc):
            # do something that takes a long time
            # doc = data
            print("the document ",refresh_token)
            logs.insert({"event":"started_long_session","user":doc["email"],"timedata":datetime.now()})
            if refresh_token:
                print("all good")
                OutlookWorker.get_all_emails(refresh_token, doc)
                logs.insert({"event":"finished_long_session","user":doc["email"],"timedata":datetime.now()})
            else:
                print("error")
                logs.insert({"error":True,"event": "there is not code in doc", "user": doc["email"], "timedata": datetime.now()})
            print("finish long time ")



        data = request.get_json()
        url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

        # urli = 'https://api.meetee.ai/v2/login/outlook'
        payload = 'client_id=e658bc45-5e57-4236-9751-b328f0d658d2&scope=user.read&code='+data["code"]+'&redirect_uri='+data["url"]+'&grant_type=authorization_code&client_secret=3pr.PyD~NoDSJJQ4R7.~6RF9Vv34.6.cwm'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'stsservicecookie=ests; x-ms-gateway-slice=estsfd; fpc=Aq_r_Zr_UjZNrByxiZB5Pd8hZSJGAgAAAKLWetcOAAAA'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.json())
        # return response.json(),200

        data = response.json()
        doc = OutlookWorker.get_userinfo(data)
        print("there it is ",doc)
        user = users.find_one({"email":doc["email"]})
        if (user):
            print("return access token")
            if "apps" in user:
                del user["apps"]
            user["_id"] = str(user["_id"])
            access_token = create_access_token(identity=user, expires_delta=False)
            user["access_token"] = access_token
            return user, 200
        else:
            doc["platform"] = "microsoft"
            created_id = users.insert(doc)
            # created_id = "123"
            doc["_id"] = str(created_id)
            acc_data = doc
            if "code" not in doc:
                doc["code"] = data
            code = doc["code"]

            print(type(doc))
            print("doooooo",doc)
            thread = Thread(target=do_work,kwargs={"refresh_token":doc["code"]["refresh_token"],"doc":doc})
            thread.start()



            del acc_data["code"]
            print(acc_data)
            access_token = create_access_token(identity=acc_data, expires_delta=False)
            # print("code: ",doc["code"])
            doc["access_token"] = access_token
            doc["waiting"] = True
            # should run the first time
            return doc, 200



class Api_Outlook(Resource):
    def get(self):
        email = request.args.get('email')
        token = request.args.get('token')
        res = OutlookWorker.get_all_emails(email,token,black_listed)
        return res

    def post(self):
        data = request.get_json()
        return ""
        # return Functions.analyze_email(data)