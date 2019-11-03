import os
import sys

import requests
from flask import Flask, redirect
import pymongo

# Env vars init
fldn_code = os.environ["KEY_CODE"]
fldn_target = os.environ["KEY_TARGET"]
not_found_url = os.environ["NOT_FOUND_URL"]
if requests.get(not_found_url).status_code != 200:
    print("URL to go when not found did not return 200.")
    sys.exit(1)

# Flask init
app = Flask(__name__)

# Mongo init
mongo_client = pymongo.MongoClient(os.environ["MONGO_URL"])
try:
    mongo_shorturl_col = mongo_client.get_database("surl").get_collection("data")
except Exception as e:
    print("Error occurred when trying to find Mongo Short URL collection. Terminating the app.")
    print(e)
    sys.exit(1)

if not mongo_shorturl_col:
    print("Short URL collection not found. Terminating the app.")
    sys.exit(1)


@app.route('/<str:url_code>/')
def short_url(url_code):
    data = mongo_shorturl_col.find_one({fldn_code: url_code})
    if not data:
        return redirect(not_found_url, code=404)

    return redirect(data[fldn_target], code=302)


if __name__ == '__main__':
    app.run(port=os.environ['PORT'], host='0.0.0.0')
