import pymongo

client = pymongo.MongoClient('mongodb://root:A260196r.@logikal-shard-00-00-iilvr.gcp.mongodb.net:27017,logikal-shard-00-01-iilvr.gcp.mongodb.net:27017,logikal-shard-00-02-iilvr.gcp.mongodb.net:27017/meeteebeta2?ssl=true&replicaSet=logikal-shard-0&authSource=admin&retryWrites=true&w=majority')

mydb = client["meeteebeta3"]

ActionsDB = mydb["actions"]
MeetingsDB = mydb["meetings"]
BodyDB = mydb["body"]
JobsDB = mydb["jobs"]
AutomationsDB = mydb["automations"]
ThirdAppsDB = mydb["thirdApps"]
UsersDB = mydb["users"]
NamesDB = mydb["names"]
Apps = mydb["apps"]
Logs = mydb["logs"]

# for statistics needs
AttendeesDB = mydb["attendees"]
Training = mydb["train"]


# ------------------------- second - Generation -------------------------
mydb2 = client["second_generation"]
inputsDB = mydb2["inputes"]
actions2DB = mydb2["actions"]
votes2DB = mydb2["votes"]
contact2DB = mydb2["contact"]
comments2DB = mydb2["comments"]
Users2DB = mydb2["users"]
Apps2DB = mydb2["apps"]

mydb3 = client["pi_beta"]
full_actions2DB = mydb3["imported_tasks"]
zofim_tomer = mydb3["imported_tasks_zofim"]
zofim_after = mydb3["processed_tasks_zofim"]

zofim_pairs = mydb3["pairs_zofim"]
zofim_edges = mydb3["zofim_edges"]
zofim_nodes = mydb3["zofim_nodes"]

mydevdb = client["mahat_dev"]
users = mydevdb["users"]
integrations = mydevdb["integrations"]
inputs = mydevdb["inputs"]
events = mydevdb["events"]
premium = mydevdb["premium"]
logs = mydevdb["logs"]
