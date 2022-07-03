"""
  MUKALMA - A Knowledge-Powered Conversational Agent
  Project Id: F21-20-R-KBCAgent

  app.py  - A Flask Application
    - Creates a pipeline model that provides interface functions to be routed from the API
    - Provides a flask API Application that is hosted locally to be connected from the front_end
"""

# Imports
from flask import Flask
from flask_cors import CORS
from flask import request
from flask import jsonify

from .APIModel import APIModel
from ..mukalma import mukalma

# To register clean-up actions when exiting the Flask App
import atexit

# For thread-safe progress updates
from queue import Queue, Empty

# Defining the Flask APP and Setting up the
# Cross-Origin Resource Policy for the web-based front_end
app = Flask(__name__)
CORS(app)

# Queue and variables used for progress updates
progress_queue = Queue()
__PROGRESS_UPDATE_TIMEOUT = 40  # Timeout in seconds

# Creating Models to be used by the API
test_model = APIModel(progress_update_queue=progress_queue)


# defining function to run on shutdown
def cleanup():
    test_model.exit()


# Register the function to be called on exit
atexit.register(cleanup)


# ---------------------------------------------------------------------------
# Routes of the API
# ---------------------------------------------------------------------------

def get_update_safe(block=True, timeout=None):
    try:
        update = progress_queue.get(block=block, timeout=timeout)
        print(f"Update id {update['id']} available")
        return update
    except Empty:
        return None


@app.route('/reply', methods=['POST'])
def get_reply():
    progress_queue.empty()
    _json = request.json
    _message = _json['message']
    m_id = _json['m_id']
    reply = test_model.reply(_message)

    # If async updates are not requested, then fetch the updates from the progress queue here in a blocking manner
    if not _json['async']:
        while True:
            update = get_update_safe(True, __PROGRESS_UPDATE_TIMEOUT)
            if update['id'] == mukalma.MUKALMA.FINAL_UPDATE:
                break
        if update is not None:
            reply = update
            reply["status"] = 200
        else:
            reply["status"] = 404
    else:
        reply["status"] = 200

    reply['m_id'] = m_id

    print(f"Returning the response: {jsonify(reply)}")
    return jsonify(reply), reply["status"]


# End of route

@app.route('/get_update', methods=['GET'])
def get_update():
    print("Received Request for Update")
    update = {}
    status = 404
    try:
        update = progress_queue.get(block=True, timeout=__PROGRESS_UPDATE_TIMEOUT)
        print("Update available, sending..")
        status = 200
    except Empty:
        status = 404
    finally:
        update["status"] = status
        return jsonify(update), status

# End of route


@app.route('/clear_context', methods=['GET'])
def clear_context():
    print ("Received Request for Clearing context")
    status = 404
    try:
        test_model.clear_context()
        progress_queue.empty()
        status = 200
        return jsonify({"status": "Success"}), status
    except Empty:
        status = 404
    finally:
        return jsonify({"status": "Error"}), status


@app.route('/set_parent_topic', methods=['POST'])
def set_parent_topic():
    _json = request.json
    topic = _json['topic']
    test_model.set_topic(topic)
    return jsonify({"status": "Success"}), 200


@app.route('/connect', methods=['GET'])
def connect():
    return jsonify({"status": 200}), 200
