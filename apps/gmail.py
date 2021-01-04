from flask import request, jsonify ,Flask
import os
from flask_restful import reqparse, abort, Resource, reqparse
from bs4 import BeautifulSoup
import base64
from db.mongo import inputs
import os.path
from googleapiclient.discovery import build
# from scripts.action_brain import Brain
import requests
import google.oauth2.credentials
import json
from datetime import datetime,timedelta
import re
from utils import name_mapper
from scripts.nlp import check_if_cta,set_due_dates
import urllib
# from db import inputsDB,actions2DB

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']



base_url = r"https://accounts.google.com/o/oauth2/"

def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def get_to(str1,str2):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    regex2 = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}[.]\w{2,3}$'
    contacts = str1.split(",")
    emails = []
    for contact in contacts:
        contact = contact.replace("<","").replace(">","")
        for part in contact.split(" "):
            if(re.search(regex,part)):
                emails.append(part)
            else:
                if(re.search(regex2,part)):
                    emails.append(part)
    print(emails)
    return emails
    # print(str1)


class GmailWorker(Resource):
    def get_userinfo(code):
        CLIENT_ID = os.environ['CLIENT_ID']
        CLIENT_SECRET = os.environ['CLIENT_SECRET']
        access_token = GmailWorker.gmail_refresh_token(CLIENT_ID,CLIENT_SECRET,code["refresh_token"])
        authorization_header = {"Authorization": "OAuth %s" % access_token}
        r = requests.get("https://www.googleapis.com/oauth2/v2/userinfo",
                         headers=authorization_header)
        print(r)
        answer = r.json()
        print(answer)
        answer["code"] = code
        return answer

    def gmail_refresh_token(client_id, client_secret, refresh_token):
            params = {
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token
            }

            authorization_url = "https://www.googleapis.com/oauth2/v4/token"
            r = requests.post(authorization_url, data=params)

            if r.ok:
                return r.json()['access_token']
            else:
                return None

    def get_all_emails(token,user):
        print("start run over emails")
        emails = []
        black_listed = []
        CLIENT_ID = os.environ['CLIENT_ID']
        CLIENT_SECRET = os.environ['CLIENT_SECRET']
        access_token = GmailWorker.gmail_refresh_token(CLIENT_ID, CLIENT_SECRET, token)
        credentials = google.oauth2.credentials.Credentials(access_token)
        service = build('gmail', 'v1', credentials=credentials)
        # request a list of all the messages
        result = service.users().messages().list(userId='me', q='newer_than:3d').execute()
        messages = result.get('messages')
        threads = []
        messageIds = []

        print(len(messages))

        for msg in messages:
            obj = {
                "action_id": msg["id"],
                "key": None,
                "project_id": None,  # mail["conversationId"]
                "issue_status_id": '',
                "summary": '',
                "created_at": '',
                "updated": '',
                "description": None,
                "parentFolderId": '',
                "due_date": '',
                "resolution": None,
                "resolution_date": None,
                "priority": None,
                "issue_type": None,
                "assignee": [],
                "watches": None,
                "labels": [],
                "url": '',
                "fix_version": None,
                "origin_type": "google_email",
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
                "creator": '',
                "client": None,
                "server": None,
                "board_last_activity": None,
                "is_waiting": False
            }
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            print(txt["labelIds"])
            if ('INBOX' in txt["labelIds"] or "CHAT" in txt["labelIds"]) and 'CATEGORY_PROMOTIONS' not in txt['labelIds'] and 'CATEGORY_SOCIAL' not in \
                    txt['labelIds'] and 'CATEGORY_UPDATES' not in txt['labelIds']:
                if "payload" in txt:
                    payload = txt['payload']
                    headers = payload['headers']
                    # print(msg['id'])

                    headersObj = {}
                    print(headers)
                    # create an headers mapper object
                    for header in headers:
                        headersObj[header['name']] = header['value']

                    creator = get_to(headersObj["From"], '')
                    if len(creator) > 0:
                        obj["creator"] = creator[0]

                    assignees = []
                    if "Cc" in headersObj and "To" in headersObj:
                        assignees = get_to(headersObj["To"], headersObj["Cc"])
                    else:
                        if "To" in headersObj:
                            assignees = get_to(headersObj["To"], '')
                        else:
                            if "Cc" in headersObj:
                                assignees = get_to(headersObj["Cc"], '')
                    assignees = assignees + creator


                    if "data" in payload['body']:
                        # print("with data")
                        data = payload['body']['data']
                        data = data.replace("-", "+").replace("_", "/")
                        decoded_data = base64.b64decode(data)
                        soup = BeautifulSoup(decoded_data, "lxml")
                        body = ''
                        if soup is not None:
                            try:
                                body = soup.body()
                            except:
                                body = ''
                        if isinstance(body, list):
                            obj['description'] = striphtml(str(body[0]))
                        else:
                            obj['description'] = striphtml(body)
                        # print(striphtml(body))
                    else:
                        if "parts" in payload:
                            parts = payload['parts']
                            the_body = ''
                            description = ''
                            for part in parts:
                                # print(part)
                                if "data" in part["body"]:
                                    data = part['body']['data']
                                    data = data.replace("-", "+").replace("_", "/")
                                    decoded_data = base64.b64decode(data)
                                    soup = BeautifulSoup(decoded_data, "lxml")
                                    body = ' '
                                    if soup is not None:
                                        print("soup",soup)
                                        try:
                                            body = soup.body()
                                            body = str(body[0])
                                        except:
                                            body = ''
                                    the_body = striphtml(body)
                                    description =  body
                                else:
                                    if "parts" in part:
                                        for subPart in part['parts']:
                                            if "data" in subPart["body"]:
                                                data = subPart['body']['data']
                                                data = data.replace("-", "+").replace("_", "/")
                                                decoded_data = base64.b64decode(data)
                                                soup = BeautifulSoup(decoded_data, "lxml")
                                                if soup is not None:
                                                    print("soup", soup)
                                                    try:
                                                        body = soup.body()
                                                        body = str(body[0])
                                                    except:
                                                        body = ''
                                                body = str(body)
                                                the_body = the_body + striphtml(body)
                                                description = description + body
                            obj['description'] = description
                            obj["due_date"] = set_due_dates(the_body)
                            name_opt = {"eng":"","heb":""}
                            for n in name_mapper:
                                if n["eng"] == user["given_name"].lower() or n["heb"] == user["given_name"]:
                                    name_opt=n
                            obj["is_waiting"],obj["reason"] = check_if_cta(the_body,name_opt,assignees,user["email"])

                    newThread = True
                    print(headersObj)
                    if 'Subject' in headersObj:
                        print(msg['id'], headersObj['Subject'])
                        obj["summary"] = headersObj['Subject'].replace('Re:', '').replace("RE:","").replace("Fwd:","").replace("FW:","")

                    obj["project_id"] = msg["threadId"]
                    # if "Message-ID" in headersObj:
                    #     obj["project_id"] = headersObj['Message-ID']
                    # if "Message-Id" in headersObj:
                    #     obj["project_id"] = headersObj["Message-Id"]

                    # date = datetime.strptime(headersObj['Date'], '%a, %d %b %Y %H:%M:%S %z')
                    # obj["created_at"] = date.strftime('%Y/%m:%d %H:%M:%S')
                    # obj["updated"] = date.strftime('%Y/%m:%d %H:%M:%S')
                    if 'Date' in headersObj:
                        obj["created_at"] = datetime.strptime(headersObj['Date'], '%a, %d %b %Y %H:%M:%S %z')+timedelta(hours=2)
                        obj["updated"] = datetime.strptime(headersObj['Date'], '%a, %d %b %Y %H:%M:%S %z')+timedelta(hours=2)
                    obj["url"] = 'https://mail.google.com/mail/u/0/#inbox/' + msg['threadId']

                    obj["assignee"] = assignees
                    obj["labels"] = txt["labelIds"]

                    # print(datetime.strptime(headersObj['Date'],'%a, %d %b %Y %H:%M:%S %z'))
                    # irrelevant
                    # if headersObj['Message-ID'] not in messageIds:
                    #     messageIds.append(headersObj['Message-ID'])
                    #     newThread = True
                    # else:
                    #     newThread = False
                    # if newThread:
                    #     if 'Thread-Topic' in headersObj:
                    #         threads.append(headersObj['Thread-Topic'])
                    #     else:
                    #         threads.append(headersObj['Subject'])
                    inputs.find_one_and_update({"action_id":msg["id"],"user_email":user["email"]},{"$set":obj},upsert=True)
        print("done run over emails")
        return True


