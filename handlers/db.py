import pymongo
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError
from configurebot import cfg

dburl = cfg.get('db_url')
db_name = cfg.get('db_name')

# Try to create a client at import time but fail safely if auth/connection fails.
client = None
profiles = None
try:
    client = pymongo.MongoClient(dburl, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)
    # quick check to force authentication/connection now
    client.admin.command('ping')
    _db = client[db_name]
    profiles = _db['profiles']
except Exception as e:
    print(f"[DB] MongoDB connection/auth failed: {e}")
    client = None
    profiles = None


def db_profile_exist(uid):
    if profiles is None:
        return False
    try:
        return profiles.find_one({"_id": uid}) is not None
    except PyMongoError as e:
        print(f"[DB] db_profile_exist error: {e}")
        return False

def db_profile_exist_usr(username):
    if profiles is None:
        return False
    try:
        return profiles.find_one({"username": username}) is not None
    except PyMongoError as e:
        print(f"[DB] db_profile_exist_usr error: {e}")
        return False

def db_profile_insertone(query):
    if profiles is None:
        print("[DB] insert skipped: no DB connection")
        return None
    try:
        return profiles.insert_one(query)
    except PyMongoError as e:
        print(f"[DB] db_profile_insertone error: {e}")
        return None

def db_profile_access(uid):
    if profiles is None:
        return 0
    try:
        doc = profiles.find_one({'_id': uid})
        return doc.get('access', 0) if doc else 0
    except PyMongoError as e:
        print(f"[DB] db_profile_access error: {e}")
        return 0

def db_profile_banned(uid):
    if profiles is None:
        return False
    try:
        doc = profiles.find_one({'_id': uid})
        return bool(doc and doc.get('ban', 0) == 1)
    except PyMongoError as e:
        print(f"[DB] db_profile_banned error: {e}")
        return False

def db_profile_updateone(query, query2):
    if profiles is None:
        print("[DB] update skipped: no DB connection")
        return None
    try:
        return profiles.update_one(query, query2)
    except PyMongoError as e:
        print(f"[DB] db_profile_updateone error: {e}")
        return None

def db_profile_get_usrname(username, get):
    if profiles is None:
        return None
    try:
        doc = profiles.find_one({'username': username})
        return doc.get(get) if doc else None
    except PyMongoError as e:
        print(f"[DB] db_profile_get_usrname error: {e}")
        return None