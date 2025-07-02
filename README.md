# 📦 webhook-repo

This repository contains the **Flask backend** that receives GitHub webhook events (Push, Pull Request, and Merge), parses them, and stores the clean data into **MongoDB**. It is part of a two-repository setup for tracking GitHub activity.

---

## 📌 Features

- Receives GitHub webhook events via `/webhook` endpoint
- Handles:
  - ✅ Push events
  - ✅ Pull Requests (opened)
  - ✅ Merges (closed and merged PRs)
- Stores formatted data in MongoDB in the following schema:
  ```json
  {
    "author": "Travis",
    "action": "PUSH",
    "from_branch": null,
    "to_branch": "staging",
    "timestamp": "1 April 2021 - 9:30 PM UTC",
    "message": "Travis pushed to staging on 1 April 2021 - 9:30 PM UTC",
    "request_id": "abc123def456"
  }

PREREQUISITES:
Make sure you have the following installed:

Python 3.8+

MongoDB running locally (mongodb://localhost:27017)

pip package manager

Ngrok (for exposing local server to GitHub)

🚀 Setup Instructions:
1. Clone the Repository
2. Create Virtual Environment
3. Install Dependencies
4. Run the Flask App
The server will start at: http://127.0.0.1:5000

Expose Flask App via Ngrok (for GitHub Webhooks)

Related Repositories
action-repo — the GitHub repo that triggers the webhook
