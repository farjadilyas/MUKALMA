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

# To register clean-up actions when exiting the Flask App
import atexit

# For thread-safe progress updates
from queue import Queue, Empty

# Defining the Flask APP and Setting up the
# Cross-Origin Resource Policy for the web-based front_end
app = Flask(__name__)
CORS(app)

# Queue and variables used for progress updates
progress_queue = Queue(maxsize=4)
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

@app.route('/reply', methods=['POST'])
def get_reply():
    _json = request.json
    _message = _json['message']
    reply = test_model.reply(_message)
    print(f"Returning the response: {jsonify(reply)}")
    return jsonify(reply), 200


# End of route

@app.route('/get_update', methods=['GET'])
def get_update():
    print("Received Request for Update")
    update = {}
    status = 404
    try:
        update = progress_queue.get(block=True, timeout=40)
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
        status = 200
        return jsonify({"status": "Success"}), status
    except Empty:
        status = 404
    finally:
        return jsonify({"status": "Error"}), status
