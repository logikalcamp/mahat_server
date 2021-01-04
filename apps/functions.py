# import requests
# from bs4 import BeautifulSoup
# import os
# from googleapiclient.discovery import build
# import google.oauth2.credentials
# import base64
# import re
# from scripts.action_brain import Brain
#
# class Functions:
#     def analyze_email(i):
#         exp = str(i["body"])
#         exp = re.sub('<[^>]+>', '', exp)
#         exp = exp.split('--')
#         emailBody = exp[0]
#
#         data = {
#             "message": emailBody
#         }
#         ans = Brain.manual(data)
#         # try:
#         actions = []
#         for n in ans:
#             if "action" in n:
#                 if(n["dueDate"] != '' and n["dueDate"] != None):
#                     print(n["dueDate"])
#                     date = n["dueDate"].strftime('%d/%m/%Y')
#                 else:
#                     date = ''
#                 act2insert = {
#                     "details": {
#                         "user": i["email"],
#                         "platform": "gmail",
#                         "link": i["link"],
#                         "from": i["from_email"]
#                     },
#                     "body": {
#                         "action":n["action"],
#                         "assignedTo":n["assignedTo"],
#                         "dueDate":date,
#                         "remove":n["remove"]
#                     },
#                     "status": 0
#                 }
#                 actions.append(act2insert)
#                 # actions2DB.insert_one(act2insert)
#         # """
#         print(actions)
#         for i in actions:
#             if "_id" in i:
#                 i["_id"] = str(i["_id"])
#         return actions
#
#
#     def extract_topics_formal(self):
#         print("extract")
#
