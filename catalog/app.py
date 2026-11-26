from flask import Flask, request, jsonify
from database import get_connection, initialize_database
import logging

app = Flask(__name__)

# Display service logs in the terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CatalogService")


# Initialize the database
initialize_database()


# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "Catalog Service",
        "status": "running"
    }), 200


# Search books by topic
@app.route("/search/<string:topic>", methods=["GET"])
def search_books(topic):
    conn = get_connection()

    books = conn.execute(
        """
        SELECT id, title
        FROM books
        WHERE LOWER(topic) = LOWER(?)
        ORDER BY id
        """,
        (topic,)
    ).fetchall()

    conn.close()

    results = [
        {"id": book["id"], "title": book["title"]}
        for book in books
    ]

    logger.info("Search request: topic=%s, results=%d",
                topic, len(results))

    return jsonify(results), 200


# Get complete information about one book
@app.route("/info/<int:item_id>", methods=["GET"])
def book_info(item_id):
    conn = get_connection()

    book = conn.execute(
        """
        SELECT id, title, topic, quantity, price
        FROM books
        WHERE id = ?
        """,
        (item_id,)
    ).fetchone()

    conn.close()

    if book is None:
        return jsonify({"error": "Book not found"}), 404

    result = {
        "id": book["id"],
        "title": book["title"],
        "topic": book["topic"],
        "quantity": book["quantity"],
        "price": book["price"]
    }

    logger.info("Info request: item_id=%d", item_id)

    return jsonify(result), 200


# Query catalog by topic or item
@app.route("/query", methods=["GET"])
def query_catalog():
    topic = request.args.get("topic")
    item_id = request.args.get("item")

    if topic and item_id:
        return jsonify({
            "error": "Provide topic or item, not both"
        }), 400

    if topic:
        conn = get_connection()

        books = conn.execute(
            """
            SELECT id, title, topic, quantity, price
            FROM books
            WHERE LOWER(topic) = LOWER(?)
            ORDER BY id
            """,
            (topic,)
        ).fetchall()

        conn.close()

        return jsonify([dict(book) for book in books]), 200

    if item_id:
        try:
            item_id = int(item_id)
        except ValueError:
            return jsonify({
                "error": "Invalid item number"
            }), 400

        conn = get_connection()

        book = conn.execute(
            "SELECT * FROM books WHERE id = ?",
            (item_id,)
        ).fetchone()

        conn.close()

        if book is None:
            return jsonify({
                "error": "Book not found"
            }), 404

        return jsonify(dict(book)), 200

    return jsonify({
        "error": "Provide a topic or item parameter"
    }), 400


# Update price or stock safely
@app.route("/update/<int:item_id>", methods=["PUT"])
def update_book(item_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A JSON object is required"
        }), 400

    conn = get_connection()

    try:
        # Start transaction before reading stock
        conn.execute("BEGIN IMMEDIATE")

        book = conn.execute(
            "SELECT * FROM books WHERE id = ?",
            (item_id,)
        ).fetchone()

        if book is None:
            return jsonify({
                "error": "Book not found"
            }), 404

        if "price" in data and "quantity_change" in data:
            return jsonify({
                "error": "Update price or quantity, one operation at a time"
            }), 400

        if "price" in data:
            try:
                new_price = float(data["price"])
            except (ValueError, TypeError):
                return jsonify({
                    "error": "Price must be a number"
                }), 400

            if new_price < 0:
                return jsonify({
                    "error": "Price cannot be negative"
                }), 400

            conn.execute(
                "UPDATE books SET price = ? WHERE id = ?",
                (new_price, item_id)
            )

        elif "quantity_change" in data:
            try:
                change = int(data["quantity_change"])
            except (ValueError, TypeError):
                return jsonify({
                    "error": "Quantity change must be an integer"
                }), 400

            new_quantity = book["quantity"] + change

            if new_quantity < 0:
                return jsonify({
                    "error": "Book is out of stock",
                    "message": "Purchase failed"
                }), 409

            conn.execute(
                "UPDATE books SET quantity = ? WHERE id = ?",
                (new_quantity, item_id)
            )

        else:
            return jsonify({
                "error": "Provide price or quantity_change"
            }), 400

        # Read updated information before releasing the lock
        updated_book = conn.execute(
            "SELECT * FROM books WHERE id = ?",
            (item_id,)
        ).fetchone()

        result = dict(updated_book)

        # Commit the transaction
        conn.commit()

        logger.info("Book updated: item_id=%d", item_id)

        return jsonify({
            "message": "Book updated successfully",
            "book": result
        }), 200

    except Exception:
        conn.rollback()

        logger.exception("Failed to update book")

        return jsonify({
            "error": "Database update failed"
        }), 500

    finally:
        conn.close()


if __name__ == "__main__":
    logger.info("Catalog Service is starting...")
    app.run(host="0.0.0.0", port=5001, threaded=True)
