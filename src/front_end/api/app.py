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

from ...knowledge_retrieval.knowledge_retriever import KnowledgeRetriever, topics
from .APIModel import APIModel
import time

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
knowledge_retriever = KnowledgeRetriever()
test_model = APIModel(knowledge_retriever.selected_knowledge, progress_update_queue=progress_queue)


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

    s1 = time.time()
    reply = test_model.reply(_message)
    print("\n\n--- %s seconds ---" % (time.time() - s1))

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


@app.route('/source', methods=['GET'])
def get_source():
    response = {"response": knowledge_retriever.selected_knowledge}
    return jsonify(response), 200


# End of route

@app.route('/topics', methods=['GET'])
def get_topics():
    print(
        f"GET TOPICS, (topic selected is {knowledge_retriever.selected_id}, {knowledge_retriever.getSelectedTopic()})")
    response = {"topics": topics, "current_topic": knowledge_retriever.getSelectedTopic()}
    return jsonify(response), 200


# End of route

@app.route('/topics/select', methods=['POST'])
def select_topics():
    _json = request.json
    _topic = _json['topic']
    print(_topic)

    # Update Knowledge Retriever's state
    knowledge_retriever.selectTopicKnowledge(_topic)

    # Update the current model's state
    test_model.updateKnowledge(knowledge_retriever.selected_knowledge)

    return jsonify({"response": "OK"}), 200
# End of route
