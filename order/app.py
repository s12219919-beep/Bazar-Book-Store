from flask import Flask, jsonify
import requests
import os
import logging

from database import initialize_database, save_order

app = Flask(__name__)

# Catalog service URL
CATALOG_URL = os.getenv(
    "CATALOG_URL", "http://localhost:5001"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrderService")

# Initialize database
initialize_database()


# Health check
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "Order Service",
        "status": "running"
    }), 200


# Purchase a book
@app.route("/purchase/<int:item_id>", methods=["POST"])
def purchase(item_id):

    # Update stock using Catalog's atomic transaction
    try:
        response = requests.put(
            f"{CATALOG_URL}/update/{item_id}",
            json={"quantity_change": -1},
            timeout=5
        )

    except requests.RequestException:
        logger.error("Could not connect to Catalog Service")

        return jsonify({
            "error": "Catalog Service is unavailable"
        }), 503

    # Book does not exist
    if response.status_code == 404:
        return jsonify({
            "error": "Book not found"
        }), 404

    # Not enough stock
    if response.status_code == 409:
        logger.warning(
            "Purchase failed: book %d is out of stock",
            item_id
        )

        return jsonify({
            "message": "Purchase failed",
            "error": "Book is out of stock"
        }), 409

    # Other Catalog errors
    if response.status_code != 200:
        return jsonify({
            "error": "Failed to update book stock"
        }), 502

    # Get actual book information after the update
    book = response.json()["book"]

    # Save successful order
    try:
        order_id = save_order(
            book["id"],
            book["title"],
            book["price"]
        )

    except Exception:
        logger.exception("Failed to save order record")

        return jsonify({
            "error": "Stock was updated, but saving the order failed"
        }), 500

    logger.info(
        "Purchase successful: order_id=%d, book_id=%d",
        order_id,
        item_id
    )

    return jsonify({
        "message": "Purchase successful",
        "order_id": order_id,
        "book": book["title"],
        "price": book["price"],
        "remaining_quantity": book["quantity"]
    }), 200


if __name__ == "__main__":
    logger.info("Order Service is starting...")
    app.run(host="0.0.0.0", port=5002, threaded=True)
