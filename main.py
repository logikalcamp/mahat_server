import os
from flask import Flask, redirect, make_response, render_template , request,jsonify
from flask_cors import CORS, cross_origin
from flask_restful import Api, Resource,abort
from flask_jwt_extended import (JWTManager, jwt_required,
                                jwt_refresh_token_required,
                                jwt_optional, fresh_jwt_required,
                                get_raw_jwt, get_jwt_identity,
                                create_access_token, create_refresh_token,
                                set_access_cookies, set_refresh_cookies,
                                unset_jwt_cookies,unset_access_cookies)
from datetime import datetime
import time
# # from flask_graphql import GraphQLView
#
os.environ['CLIENT_ID'] = '46648562-okl2uajj21c5jttab4i6k9877vcks43f.apps.googleusercontent.com'
os.environ['CLIENT_SECRET'] = 'qzv83s_hmmP3j5s45wFdBBBf'
os.environ['JIRA_CLIENT_ID'] = 'mOhVjuVJ1LqUwBz2T4DiTCLvmuOrjepv'
os.environ['JIRA_CLIENT_SECRET'] = 'OAMKwOipgOhswG5AMnw1JB0xW4QLd5D4G0dEtnbMZ6W5DfGaI8aaZxmqQQJkQRLv'
os.environ['TRELLO_API_KEY'] = '376998bf9b552e830d5f418d4ca58271'
os.environ['TRELLO_API_SECRET'] = '2af1b7b952256eee1121e49e3beaf536bf92010c9deae26157b19061ba8844f1'

from resources.apps import Third_Apps
from resources.gmail import Api_Gmail,Auth_Gmail
from resources.queries import Queries
from resources.outlook import Auth_Outlook

from db.mongo import premium,events,users,inputs
import time
from threading import Thread
#
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'MeeteeWillRaiseaviram'  # Change this!
jwt = JWTManager(app)
# app.config['BASE_URL'] = 'http://127.0.0.1:3000'  #Running on localhost
#
cors = CORS(app, resources={r"/*": {"origins": '*'}},allow_headers=[
    "Content-Type", "Authorization", "Access-Control-Allow-Credentials","Cookie"],
    supports_credentials=True)
#
# @jwt.unauthorized_loader
# def unauthorized_callback(callback):
#     # No auth header
#     data = 'need to login'
#     return data ,401
#
#
api = Api(app)
#
base_url_v1 = '/v1'
base_url_v2 = '/v2'

api.add_resource(Third_Apps,base_url_v2+'/apps/<string:app_name>/<string:method>',base_url_v2+'/apps')
api.add_resource(Auth_Gmail,base_url_v2+'/login/gmail')
api.add_resource(Auth_Outlook,base_url_v2+'/login/outlook')
api.add_resource(Queries,base_url_v2+'/query/<string:quest>')
# api.add_resource(Api_Gmail, base_url_v2+'/gmail')
# api.add_resource(Votes,base_url_v2+'/votes')
# api.add_resource(Query,base_url_v2+'/query')
# api.add_resource(Comments,base_url_v2+'/comments')
# api.add_resource(Third_Apps,base_url_v2+'/apps',base_url_v2+'/apps/<string:user_id>')
# app.add_url_rule('/graphql',view_func=GraphQLView.as_view("graphql",schema=schema,graphiql=True))

from apps.gmail import GmailWorker
from apps.outlook import OutlookWorker
from apps.jira import Jira
from apps.clickup import Clickup
from apps.trello import Trello
from apps.zendesk import Zendesk
from apps.monday import Monday

@app.route('/measure',methods=['POST'])
@jwt_required
def b():
    user = get_jwt_identity()
    data = request.get_json()
    if data["event"] == "add_new_component":
        premium.insert_one({"request":data["event"],"idea":data["idea"],"time":datetime.now(),"user":user["email"]})
    if data["event"] == "change_refresh_settings":
        premium.insert_one(
            {"request": data["event"], "rate": data["chosen"], "time": datetime.now(), "user": user["email"]})
    if data["event"] == "event":
        events.insert({"event":data["type"],"user":user["email"],"time": datetime.now()})
    return "True"
    # return create_app("a")

@app.route('/testing',methods=['POST'])
def a():
    data = request.get_json()
    print(data)
    res = users.aggregate([
        {
            "$match":{
                "email":data["email"]
            }
        },
        {
            "$lookup":{
                "from":"integrations",
                "localField":"email",
                "foreignField":"email",
                "as":"apps"
            }
        }
    ])

    def do_work(user):
        print(user)
        if user["platform"] == "google":
            GmailWorker.get_all_emails(user["code"]["refresh_token"],user)
        else:
            OutlookWorker.get_all_emails(user["code"]["refresh_token"], user)

        for app in user["apps"]:
            print (app)
            if app["app"] == "trello":
                for board in app["boards"]:
                    Trello.load_data(app["token"],board,inputs,user)
            if app["app"] == "zendesk":
                Zendesk.load_data(Zendesk,app["org_domain"],app["token"],user)
            if app["app"] == "jira":
                Jira.load_data(Jira,app["token"],app["org_domain"],user)
            if app["app"] == "monday":
                for board in app["boards"]:
                    Monday.load_data(app["token"],board,inputs,user)
            if app["app"] == "clickup":
                print()
            if app["app"] == "asana":
                print()
        print("finished")

    for user in res:
        print(user["apps"])
        user["_id"] = str(user["_id"])

        thread = Thread(target=do_work, kwargs={"user": user})
        thread.start()


    # refresh_code = "0.ATEA9trNmiSEHECO86QLE38MeEW8WOZXXjZCl1GzKPDWWNIxAIQ.AgABAAAAAABeStGSRwwnTq2vHplZ9KL4AQDs_wMA9P8tQ5TJoGDDGbZ0TD4Pp6ixU6iyYmicFhcIfM7PyME8V5K5nfOeiRE8gd7-IamhTzSD-p00duP7ykYh-oaUdD3EaHXtV3GX-I8QW6L2eCqEZGWcBP2RpQme0hRnOI3VpEngd-8KwmOJ-B9AjPnMv0bXJJyBjTDIK4mMhIS3YyPxSxMf4zevDkDzFwxgwk4vLygkRJ82KMp_H57S53rAD9iAQTBGWQG8NOmJPeIYgkeLrzfNCDe4KOLnNosZA4uKL6IBAhGkUIORDbRyqtTgZHPIRTsbtZ3AyeoyoQkzGslmNVOk6My3fdpIl3inaQaM1G1X6iqWCrtAtVN0gqtguX6ijeteEnCE5ITkW6jUfuK73pmSxZ96Wdm7JAE9BiYL_7fauy1GssxnMW8sFvt8efwCfahb2rz5NPL1YtdeqAX58zF53CFc7-2IQZCfngEHIldqQ4iIb_porYTH1fbLh2DSevIpx4SVDTBC4iTHS95dsxWHBB1wJ1xR0A7gvoSFdXJ-WfHJW1RtHZyoHbKxcO5OXyN7n-f3_jyTAuMOQHVzxgWDDjjiRs0giiifJqTM5-uJMOtqra96n54skHnZVgeiPBh3-oNqKlNbSu4xhqYleiGXrs6d8S0VGNpcBw0lGXqHbVXw6dwz5NT_kkkue0zueeAQ9KfV8t-sVr9C5cNMfZooFK2dnnROoQ8E7DKKTthqYK90tRh2iPMGYHdn9Z9h2kNoF-unRIyV0Md8h3XPbYB9xjRypAyI-VLr8j1KKYwE4tLFfZjwO_j0bjJ8ON8fxWjOfN91Jx7kfuzhGMXlXHx01IAbN2sUEsknHgk_m1L15ZtDLPP6RVzqQ1bFEg5tmZYwcmxEe1rCkOeLCC-YJ7kadcMpQKNO7FfW-QsNIJSO0GhOf9yxKF5aazoEKak7J3UUXpiD2a8-nEHPt2kjdUCr_1ZA6WKqvSs6PhUhfuNrXbAkX6fk3xn0OY0x9qTSdH5GFw"
    # user = {
    #     "_id":"5feb0b9c8c18295b41977110",
    #     "email":"digital@zofim.org.il",
    #     "given_name":"עמית"
    # }
    #
    #

    # GmailWorker.get_all_emails(refresh_code,user)
    # OutlookWorker.get_all_emails(refresh_code, user)
    # def load_data(self,org_domain,token,user):
    return "done"
    # return query_users()


@app.route('/threading')
def threadi():
    def do_work(value,data):
        # do something that takes a long time
        import time
        time.sleep(value)
        print("code" in data)
        print(data["code"])
        print("finish long time ")
    doc = {'id': 'dfb52366-2858-430d-ada2-d4de050be053', 'email': 'tomerd@zofim.org.il', 'verified_email': 'tomerd@zofim.org.il', 'name': 'תומר דגן', 'given_name': 'תומר', 'family_name': 'דגן', 'picture': '', 'locale': None, 'code': {'token_type': 'Bearer', 'scope': 'Calendars.ReadWrite email Files.ReadWrite Mail.Read openid profile User.Read', 'expires_in': 3599, 'ext_expires_in': 3599, 'access_token': 'eyJ0eXAiOiJKV1QiLCJub25jZSI6ImUyUUlGeGVvaXRHOHZvejQxdFJ4emFQREIzUnV5cG5pa3RrbWFGZGZuOGMiLCJhbGciOiJSUzI1NiIsIng1dCI6IjVPZjlQNUY5Z0NDd0NtRjJCT0hIeEREUS1EayIsImtpZCI6IjVPZjlQNUY5Z0NDd0NtRjJCT0hIeEREUS1EayJ9.eyJhdWQiOiIwMDAwMDAwMy0wMDAwLTAwMDAtYzAwMC0wMDAwMDAwMDAwMDAiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC85YWNkZGFmNi04NDI0LTQwMWMtOGVmMy1hNDBiMTM3ZjBjNzgvIiwiaWF0IjoxNjA5MjM4NzU4LCJuYmYiOjE2MDkyMzg3NTgsImV4cCI6MTYwOTI0MjY1OCwiYWNjdCI6MCwiYWNyIjoiMSIsImFjcnMiOlsidXJuOnVzZXI6cmVnaXN0ZXJzZWN1cml0eWluZm8iLCJ1cm46bWljcm9zb2Z0OnJlcTEiLCJ1cm46bWljcm9zb2Z0OnJlcTIiLCJ1cm46bWljcm9zb2Z0OnJlcTMiLCJjMSIsImMyIiwiYzMiLCJjNCIsImM1IiwiYzYiLCJjNyIsImM4IiwiYzkiLCJjMTAiLCJjMTEiLCJjMTIiLCJjMTMiLCJjMTQiLCJjMTUiLCJjMTYiLCJjMTciLCJjMTgiLCJjMTkiLCJjMjAiLCJjMjEiLCJjMjIiLCJjMjMiLCJjMjQiLCJjMjUiXSwiYWlvIjoiRTJKZ1lJZzdsSlN0dkN3ajg3RDJUamFaSUxhd3JOOGJOL3V0VytiMy8wRHZWOWZmUFlVQSIsImFtciI6WyJwd2QiXSwiYXBwX2Rpc3BsYXluYW1lIjoiTWVldGVlLmFpIiwiYXBwaWQiOiJlNjU4YmM0NS01ZTU3LTQyMzYtOTc1MS1iMzI4ZjBkNjU4ZDIiLCJhcHBpZGFjciI6IjEiLCJmYW1pbHlfbmFtZSI6IteT15LXnyIsImdpdmVuX25hbWUiOiLXqteV157XqCIsImlkdHlwIjoidXNlciIsImlwYWRkciI6IjQ2LjE5Ljg2LjEyMSIsIm5hbWUiOiLXqteV157XqCDXk9eS158iLCJvaWQiOiJkZmI1MjM2Ni0yODU4LTQzMGQtYWRhMi1kNGRlMDUwYmUwNTMiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtNDA2OTQyNjA5Mi0xMTYyMjczNTI0LTI0NDEzNzc3MzktMTQ1MSIsInBsYXRmIjoiNSIsInB1aWQiOiIxMDAzMjAwMDVGMkRDRDhEIiwicmgiOiIwLkFURUE5dHJObWlTRUhFQ084NlFMRTM4TWVFVzhXT1pYWGpaQ2wxR3pLUERXV05JeEFGWS4iLCJzY3AiOiJDYWxlbmRhcnMuUmVhZFdyaXRlIGVtYWlsIEZpbGVzLlJlYWRXcml0ZSBNYWlsLlJlYWQgb3BlbmlkIHByb2ZpbGUgVXNlci5SZWFkIiwic3ViIjoiR1g5eFgzQmVqZ2ZqRlNnajB2cHNRMFpGOVdXUnRuWUJZb0l0THl1VEQ1NCIsInRlbmFudF9yZWdpb25fc2NvcGUiOiJFVSIsInRpZCI6IjlhY2RkYWY2LTg0MjQtNDAxYy04ZWYzLWE0MGIxMzdmMGM3OCIsInVuaXF1ZV9uYW1lIjoidG9tZXJkQHpvZmltLm9yZy5pbCIsInVwbiI6InRvbWVyZEB6b2ZpbS5vcmcuaWwiLCJ1dGkiOiJDTG5DSkZ3UjAwZXFQTWI1LTdzTUFBIiwidmVyIjoiMS4wIiwid2lkcyI6WyJiNzlmYmY0ZC0zZWY5LTQ2ODktODE0My03NmIxOTRlODU1MDkiXSwieG1zX3N0Ijp7InN1YiI6IkxsMWdvMDk2Z1JlWHJzNVBHRVpieWxiYUtCNGZsbW95SjlEVVdIVDVLcDgifSwieG1zX3RjZHQiOjE1NDI4ODk3NTV9.lPPYGF7xTNBBK8tUkpw33OV8Sn5l1Yy5S8gz3pk2wBX2zAAIgt2FE2q25ICHMnWgw_rr_UVxKlmxPZUudcbf6z2erld2FnuLA5pjxGo1Xiw0tYVHz6MxFz9xpWBcT269FTz2no5uUw3EXfjQ1v12TK2uX3R06xBG56aEXbmKvtQjMCZiPoC-CN8MWGuJUfr9s0MvLZ3H3PmLxZR7O5XmynjY738LOjpTFojN2WZOPlGne69OIJPbfS0sZ46DUlKSG3Es_SXCXcv4RimGBUmxMVlvCQZUge7mT32N3oc4pH9PEA-tRsKdwLAR_AcX0F2mhknai4N_8UHtHLHL5j4bLQ', 'refresh_token': '0.ATEA9trNmiSEHECO86QLE38MeEW8WOZXXjZCl1GzKPDWWNIxAFY.AgABAAAAAABeStGSRwwnTq2vHplZ9KL4AQDs_wMA9P-jWfOixxFJXrZBbxINTPO7wftYgBm-Ds8caCnM2YIkicCwr67Jc7MHCTC7JohyWbGlSAe7GsVLyg7aTCzQg2X1MeCpsIX3vzVvi75UMZTTt8SETnsXe-iT8fP27peSN14m4PmJkSZwfxQtir_8HM6kxO8Wh3sZ2iDEsSMyK6393mz4odEKZhPlMhcF_kABI3PaD90XamSl-0QB60s2osfJnmkiESvBkm2rw4EdNip1hrGmMBVZFbKGI1A6fLtb-5Ydv75ufzCV_ltxwuufKpx1TKZWuasfIn8HFID40O8AQmuMrSVXGE3IP7MTp9Isu8kmhhHpZHSFAZOHmuAfBO15eEPRr7a5nK3j7jwqAygCQVxTfh5IYdQ1mWI7Z-gkPBE_8QWSlqj2mf89mvbPU8PC9VlR8UYV-oLvsYcbA5lPD5-wu-sJn0rw_WYERBkQxCNoL_fSroxBUnH1b9bzFn3a2AJfdD-1hRojEhz4fg7k6G_WKp2JMXokcPRd_pSLJSZyFot7aZ-ozsTcqT1mbcafQnwE0wCyq_Y19ByVszgARtR9iO9bNpDv87zJvxM9LponixzK0tbTGHSdPHFmfal4WeDa-SWYUcGpFhiNhI0M8qgVLcJqAnjRml3K_QH--RTBkmitoyz8bk9-Mr6dqD3pke_rfkaNjfou_7AQhthpOenvuRufljwsLg1SQ0QKlid8H0uq4HveOVFT4mNKmgoQ7nwvfSXT3R9egmeK1jldi__kJqClr3l6QFuvq2YAWiue_-Cfm5p8GE_EUC1NHi-fAYKUUIvvgBm2W2QJXuNmw77yNegnxhCBLaJZwWt4Yb8rxkCWjWBYF8LB3v0RWrk65t9HppteZnN5Yi4AkN7knCMk-OR_JpfJbyRM4tI21mjiPGRgk1Kti3LoH_qXMD3fO1LMTxMjc8F4bVr_If6T-T1v2GUIXXHy_g'}, 'platform': 'microsoft', '_id': '5feb0a176d0ed9ae422f99bc'}
    thread = Thread(target=do_work, kwargs={'value':10,'data':doc})
    thread.start()
    return 'started'

@app.route('/')
def main():
    return 'Hello, World!! it`s mahat on board '





def foo():
    print(datetime.now())
    events.insert_one({"event":"new new new","time":datetime.now()})
    res = users.aggregate([
        {
            "$match":{
                "to_refresh":True
            }
        },
        {
            "$lookup":{
                "from":"integrations",
                "localField":"email",
                "foreignField":"email",
                "as":"apps"
            }
        }
    ])

    for user in res:
        print(user["email"])
        # user["_id"] = str(user["_id"])
        # print(user)
        if user["platform"] == "google":
            GmailWorker.get_all_emails(user["code"]["refresh_token"],user)
        else:
            OutlookWorker.get_all_emails(user["code"]["refresh_token"], user)

        for app in user["apps"]:
            # print (app)
            if app["app"] == "trello":
                for board in app["boards"]:
                    Trello.load_data(app["token"],board,inputs,user)
            if app["app"] == "zendesk":
                Zendesk.load_data(Zendesk,app["org_domain"],app["token"],user)
            if app["app"] == "jira":
                Jira.load_data(Jira,app["token"],app["org_domain"],user)
            if app["app"] == "monday":
                for board in app["boards"]:
                    Monday.load_data(app["token"],board,inputs,user)
            if app["app"] == "clickup":
                print()
            if app["app"] == "asana":
                print()
        events.find_one_and_update({"email":user["email"],"event":"last_data_refresh"},{"$set":{"email":user["email"],"event":"last_data_refresh","time":datetime.now()}},upsert=True)
        print(user["email"]," --- finished")
        # thread = Thread(target=do_work, kwargs={"user": user})
        # thread.start()


while True:
    foo()
    time.sleep(120)

if __name__ == '__main__':
    # every(30, foo)
    app.run(debug=True)
