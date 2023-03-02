import datetime
import logging
import threading

import threading
from flask import Flask, request
from flask_cors import CORS
from flask_jsonpify import jsonify
from flask_restful import Api, Resource
from flask_bootstrap import Bootstrap

from baoshu8 import Baoshu8

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(name)s: %(levelname)s: %(message)s")

autopost_msg = {
    "leo007": [],
    "catherine005": [],
    "phoebe005": [],
    "yan005": []
}
autopost_thread = {
    "leo007": None,
    "catherine005": None,
    "phoebe005": None,
    "yan005": None
}

def get_system_state():
    state = []
    state.append(f"thread count: [{threading.active_count()}]")
    state.append(f"")
    return state

class User(Resource):
    def get(self):
        res = [{
            "id": "leo007",
            "password": "leo007",
            "email": "leo007@random.com",
            "posts": 951,
            "coins": 782,
            "contributions": 642
        },{
            "id": 'catherine005',
            "password": "catherine005",
            "email": "catherine005@random.com",
            "posts": 955,
            "coins": 767,
            "contributions": 32
        },{
            "id": 'phoebe005',
            "password": "phoebe005",
            "email": "phoebe005@random.com",
            "posts": 234,
            "coins": 23452,
            "contributions": 234
        }]
        return res, 200
class Autopost(Resource):
    def post(self):
        query = request.json
        user_name = query["userId"]
        param = query.copy()
        param["password"] = "liucan007"
        print(param)

        if not autopost_thread[user_name] or not autopost_thread[user_name].is_alive():
            autopost_msg[user_name].clear()
            autopost_thread[user_name] = Baoshu8(param, autopost_msg[user_name])
            logger.info("created a thread for autoposting")
            autopost_thread[user_name].start()
            logger.info("autoposting ... ")
        else:
            logger.warn("already has a thread for {user_name}")

        return "hello", 200
        
    def get(self):
        user_name = str(request.args["userId"])
        current_id = int(request.args["currentId"])

        res = {}
        if current_id >= len(autopost_msg[user_name]):
            res = { "progress": 0, "posts": [] }
        else: 
            if autopost_thread[user_name] and autopost_thread[user_name].is_alive():
                res["progress"] = autopost_thread[user_name].get_progress()
            res["posts"] = autopost_msg[user_name][current_id+1:]
        return res, 200

if __name__ == '__main__':
    app = Flask(__name__)
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    app.config['SEND_FILE_MAX_AGE_DEFALUT'] = datetime.timedelta(0)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    Bootstrap(app)

    CORS(app, resources={r"/*": {"origins": "*"}})
    api = Api(app)
    api.add_resource(User, '/user')  # Route_1
    api.add_resource(Autopost, '/autopost')  # Route_1

    app.run(port=6001, debug=True)
