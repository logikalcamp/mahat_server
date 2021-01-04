import requests
import os

os.environ['CLICKUP_CLIENT_ID'] = '5O4PX5262QFET1M55RFSEEQCTXX15RDH'
os.environ['CLICKUP_CLIENT_SECRET'] = 'BD5Q4XRYQ3RWH85TNON6R1D3QTY4I976ZNF14VI49YREMX27TK9S3Q3EN808M1D5'

base_url = 'https://api.clickup.com/api/v2/'


class Clickup:
    def get_access_token(token):
        client_id = os.environ['CLICKUP_CLIENT_ID']
        client_secret = os.environ['CLICKUP_CLIENT_SECRET']
        url = base_url + 'oauth/token?client_id='+client_id+'&client_secret='+client_secret+'&code='+token
        r = requests.post(url=url)
        print(r.json())
        if "err" in r.json():
            return False
        else:
            return r.json()["access_token"]

    def get_teams(access_token):
        url = base_url + 'team'
        headers = {"Authorization": access_token}
        boards_arr = []
        r = requests.get(url=url,headers=headers)
        for team in r.json()["teams"]:
            print("----------------------")
            print("team: ",team["name"])
            arr = Clickup.get_spaces(access_token,team["id"])
            boards_arr = boards_arr+arr
        return boards_arr

    def get_spaces(token,team_id):
        url = base_url+'team/'+team_id+'/space?archived=false'
        headers = {"Authorization": token}

        r = requests.get(url=url, headers=headers)
        # print(r.json())
        arr = []
        for space in r.json()["spaces"]:
            print(space["name"])
            arr.append({"id":space["id"],"name":space["name"]})
        return arr

    def get_boards(token):
        # access_token = Clickup.get_access_token(token)
        if token:
            boards = Clickup.get_teams(token)
            print("im here - ",token)
            print(boards)
            return boards

        else:
            return {"code":401}
        # params = {
        #         "key":key,
        #         "token":token
        #     }
        # url = "/1/members/me/boards"
        # r = requests.get(base_url + url, data=params)
        # print(r.status_code)
        # try:
        #     data = r.json()
        #     return data
        # except:
        #     return {"code":r.status_code}
        #   # break

