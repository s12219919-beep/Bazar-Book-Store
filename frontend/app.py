from flask import Flask, jsonify
import requests
import os
import logging

app = Flask(__name__)

# Backend services URLs
CATALOG_URL = os.getenv(
    "CATALOG_URL", "http://localhost:5001"
)

ORDER_URL = os.getenv(
    "ORDER_URL", "http://localhost:5002"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FrontendService")


# Health check
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "Frontend Service",
        "status": "running"
    }), 200


# Search books by topic
@app.route("/search/<topic>", methods=["GET"])
def search(topic):
    try:
        response = requests.get(
            f"{CATALOG_URL}/search/{topic}",
            timeout=5
        )

        return jsonify(response.json()), response.status_code

    except requests.RequestException:
        return jsonify({
            "error": "Catalog Service is unavailable"
        }), 503


# Get book information
@app.route("/info/<int:item_id>", methods=["GET"])
def info(item_id):
    try:
        response = requests.get(
            f"{CATALOG_URL}/info/{item_id}",
            timeout=5
        )

        return jsonify(response.json()), response.status_code

    except requests.RequestException:
        return jsonify({
            "error": "Catalog Service is unavailable"
        }), 503


# Purchase a book
@app.route("/purchase/<int:item_id>", methods=["POST"])
def purchase(item_id):
    try:
        response = requests.post(
            f"{ORDER_URL}/purchase/{item_id}",
            timeout=10
        )

        result = response.json()

        if response.status_code == 200:
            logger.info("bought book %s", result["book"])

        return jsonify(result), response.status_code

    except requests.RequestException:
        return jsonify({
            "error": "Order Service is unavailable"
        }), 503


if __name__ == "__main__":
    logger.info("Frontend Service is starting...")
    app.run(host="0.0.0.0", port=5000, threaded=True)
