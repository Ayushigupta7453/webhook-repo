from flask import Flask, request
from pymongo import MongoClient
from datetime import datetime
from flask_cors import CORS


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["github_events"]             # Database: github_events
collection = db["events"]                # Collection: events

@app.route("/webhook", methods=["POST"])
def github_webhook():
    """
    Endpoint to handle GitHub webhook events:
    - PUSH
    - PULL_REQUEST (opened)
    - MERGE (pull_request closed and merged)
    Extracts relevant info and stores it in MongoDB.
    """
    payload = request.json

    if not payload:
        return {"status": "no data"}, 400

    # -----------------------------------
    # Handle Pull Request Events (opened/closed)
    # -----------------------------------
    if "pull_request" in payload:
        pr = payload["pull_request"]
        author = pr["user"]["login"]              # PR author
        from_branch = pr["head"]["ref"]
        to_branch = pr["base"]["ref"]
        pr_id = str(pr["id"])                     # Use PR ID as request_id
        timestamp = datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")

        # PR opened → treat as PULL_REQUEST
        if payload["action"] == "opened":
            action = "PULL_REQUEST"
            message = f"{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"
            request_id = pr_id

        # PR closed and merged → treat as MERGE
        elif payload["action"] == "closed" and pr.get("merged"):
            action = "MERGE"
            message = f"{author} merged branch {from_branch} to {to_branch} on {timestamp}"
            request_id = pr_id

        # Ignore other pull_request actions
        else:
            return {"status": "ignored"}, 200

    # -----------------------------------
    # Handle Push Events
    # -----------------------------------
    elif "head_commit" in payload:
        author = payload["head_commit"]["author"]["name"]
        to_branch = payload["ref"].split("/")[-1]   # Extract branch name from "refs/heads/main"
        from_branch = None
        commit_hash = payload["head_commit"]["id"]  # Use commit hash as request_id
        timestamp = datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        action = "PUSH"
        message = f"{author} pushed to {to_branch} on {timestamp}"
        request_id = str(commit_hash)

    # -----------------------------------
    # Unsupported event type
    # -----------------------------------
    else:
        return {"status": "unsupported event"}, 200

    # -----------------------------------
    # Store the cleaned event data in MongoDB
    # -----------------------------------
    event_data = {
        "author": author,
        "action": action,
        "from_branch": from_branch if action != "PUSH" else None,
        "to_branch": to_branch,
        "timestamp": timestamp,
        "message": message,
        "request_id": request_id
    }

    collection.insert_one(event_data)
    return {"status": "success"}, 200

from flask import jsonify

@app.route("/events", methods=["GET"])
def get_events():
    """
    Returns all stored GitHub events from MongoDB in reverse chronological order.
    """
    events = list(collection.find().sort("timestamp", -1))
    
    # Convert ObjectId and timestamp for JSON serialization
    for event in events:
        event["_id"] = str(event["_id"])

    return jsonify(events), 200


# -----------------------------------
# Run the Flask app
# -----------------------------------
if __name__ == "__main__":
    app.run(port=5000)
