import os
import sys
import time
from datetime import datetime, timezone
from threading import Thread

import requests
from flask import Flask, redirect, abort
import pymongo

# Env vars init
from pymongo import ReturnDocument

fldn_code = os.environ["KEY_CODE"]
fldn_target = os.environ["KEY_TARGET"]
fldn_ts = os.environ["KEY_TS"]
host_url = os.environ["HOST_URL"]
landing_url = os.environ["LANDING_URL"]

# Flask init
app = Flask(__name__)

# Mongo init
mongo_client = pymongo.MongoClient(os.environ["MONGO_URL"])
try:
    mongo_shorturl_col = mongo_client.get_database(os.environ["MONGO_DB"]).get_collection(os.environ["MONGO_COL"])
except Exception as e:
    print("Error occurred when trying to find Mongo Short URL collection. Terminating the app.")
    print(e)
    sys.exit(1)

if not mongo_shorturl_col:
    print("Short URL collection not found. Terminating the app.")
    sys.exit(1)


@app.route('/')
def home():
    return redirect(landing_url)


@app.route('/test')
def test():
    return "Jelly Bot Short URL Service"


@app.route('/<string:url_code>')
@app.route('/<string:url_code>/')
def short_url(url_code):
    data = mongo_shorturl_col.find_one_and_update(
        {fldn_code: url_code},
        {"$addToSet": {fldn_ts: datetime.utcnow().replace(tzinfo=timezone.utc)}},
        upsert=False, return_document=ReturnDocument.AFTER)
    if not data:
        return abort(404)

    return redirect(data[fldn_target], code=301)


def spam_ping(cd_sec: int, retry_sec: int = 60):
    # Prevent from sleep
    while True:
        try:
            requests.get(host_url)
            print(f"Ping spammed to {host_url}.")
            time.sleep(cd_sec)
        except (requests.exceptions.ConnectionError, ConnectionRefusedError):
            print(f"Ping failed to spam on {host_url}. ConnectionError. Retry in {retry_sec} seconds.")
            time.sleep(retry_sec)


if __name__ == '__main__':
    Thread(target=spam_ping, args=(300, 60)).start()
    app.run(port=os.environ['PORT'], host='0.0.0.0')
