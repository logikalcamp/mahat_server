import requests
import os

# from db.queries.actions import create_action
# from db.mongo import full_actions2DB
os.environ['ASANA_CLIENT_ID'] = '1199241566672646'
os.environ['ASANA_CLIENT_SECRET'] = 'b98bec947b481e7303f7c8eb01c52948'

base_url = 'https://app.asana.com/-/'
base_app_url = 'https://app.asana.com/api/1.0/'

# {
#   "grant_type": "authorization_code",
#   "client_id": "",
#   "client_secret": "",
#   "redirect_uri": "http://localhost:3000",
#   "code": "325797325",
#   "code_verifier": "671608a33392cee13585063953a86d396dffd15222d83ef958f43a2804ac7fb2"
# }
class Asana:
    def get_refresh_token(token):
        url = base_url+'oauth_token'
        data = {
              "grant_type": "authorization_code",
              "client_id": os.environ['ASANA_CLIENT_ID'],
              "client_secret": os.environ['ASANA_CLIENT_SECRET'],
              "redirect_uri": "https://app.mahat.ai/asana",
              "code": token,
              # "code_verifier": "671608a33392cee13585063953a86d396dffd15222d83ef958f43a2804ac7fb2"
        }
        r = requests.post(url,data=data)
        return r.json()["refresh_token"]

    def get_access_token(refresh_token):
        url = base_url+'oauth_token'
        data = {
            "grant_type": "refresh_token",
            "client_id": os.environ['ASANA_CLIENT_ID'],
            "client_secret": os.environ['ASANA_CLIENT_SECRET'],
            "redirect_uri": "https://app.mahat.ai/asana",
            "refresh_token":refresh_token
        }
        r = requests.post(url,data=data)
        return r.json()["access_token"]

    def get_boards(token):
        url = base_app_url + 'projects'
        headers = {"Authorization": 'Bearer '+token}
        r = requests.get(url,headers=headers)
        print(r.json())
        return r.json()["data"]
        # client = asana.Client.access_token('PERSONAL_ACCESS_TOKEN')
        #
        # result = client.projects.get_projects({'param': 'value', 'param': 'value'}, opt_pretty=True)