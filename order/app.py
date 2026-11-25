from flask import Flask, jsonify
import requests
import os
import logging

from database import initialize_database, save_order

app = Flask(__name__)

# Catalog service URL
CATALOG_URL = os.getenv("CATALOG_URL", "http://localhost:5001")

# Configure service logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrderService")

# Initialize the orders database
initialize_database()


# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "Order Service",
        "status": "running"
    }), 200


# Purchase a book
@app.route("/purchase/<int:item_id>", methods=["POST"])
def purchase(item_id):

    # Step 1: Get book information from Catalog
    try:
        response = requests.get(
            f"{CATALOG_URL}/info/{item_id}",
            timeout=5
        )
    except requests.RequestException:
        logger.error("Could not connect to Catalog Service")
        return jsonify({
            "error": "Catalog Service is unavailable"
        }), 503

    if response.status_code == 404:
        return jsonify({"error": "Book not found"}), 404

    if response.status_code != 200:
        return jsonify({
            "error": "Failed to retrieve book information"
        }), 502

    book = response.json()

    # Step 2: Check available stock
    if book["quantity"] <= 0:
        logger.warning("Purchase failed: book %d is out of stock", item_id)

        return jsonify({
            "message": "Purchase failed",
            "error": "Book is out of stock"
        }), 409

    # Step 3: Decrease stock by one in Catalog
    try:
        update_response = requests.put(
            f"{CATALOG_URL}/update/{item_id}",
            json={"quantity_change": -1},
            timeout=5
        )
    except requests.RequestException:
        logger.error("Could not update Catalog stock")
        return jsonify({
            "error": "Could not complete purchase"
        }), 503

    if update_response.status_code != 200:
        return jsonify({
            "error": "Failed to update book stock"
        }), 502

    # Step 4: Save the successful order
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
        "remaining_quantity": book["quantity"] - 1
    }), 200


if __name__ == "__main__":
    logger.info("Order Service is starting...")
    app.run(host="0.0.0.0", port=5002, threaded=True)
