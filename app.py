from flask import Flask, request, jsonify, render_template, send_from_directory
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Use environment variables for database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Abhishek@1259')
DB_NAME = os.getenv('DB_NAME', 'practice')


def connect():
    """Connect to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error occurred during connection: {e}")
        return None


def initialize_db():
    """Ensure the `books` table exists."""
    connection = connect()
    if connection:
        try:
            cur = connection.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    bookid INT AUTO_INCREMENT PRIMARY KEY,
                    available VARCHAR(225) NOT NULL,
                    booktitle VARCHAR(255) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    timestamp VARCHAR(255) NOT NULL
                );
            """)
            connection.commit()
            print("Database initialized successfully.")
        except Error as e:
            print(f"Error initializing database: {e}")
        finally:
            connection.close()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index():
    """Render the admin HTML page."""
    return render_template('index.html')


@app.route('/admine.html')
def admine():
    return render_template('admine.html')


@app.route('/student.html')
def student():
    return render_template('student.html')


@app.route('/api/books', methods=['GET'])
def get_books():
    """Retrieve all books from the database."""
    connection = connect()
    if not connection:
        return jsonify({"error": "Failed to connect to the database"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM books')
        books = cursor.fetchall()
        return jsonify({"books": books}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()


@app.route('/api/addBook', methods=['POST'])
def add_book():
    """Add a new book to the database."""
    data = request.json
    bookid = data.get('bookid')
    available = data.get('available')
    booktitle = data.get('booktitle')
    author = data.get('author')
    timestamp = data.get('timestamp')

    if not all([bookid, available, booktitle, author, timestamp]):
        return jsonify({"error": "Missing required fields"}), 400

    connection = connect()
    if not connection:
        return jsonify({"error": "Failed to connect to the database"}), 500

    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO books (bookid, available, booktitle, author, timestamp) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (bookid, available, booktitle, author, timestamp))
        connection.commit()
        return jsonify({"message": "Book added successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()


@app.route('/api/updatepa', methods=['POST'])
def update_book():
    """Update a book's availability in the database."""
    data = request.json
    bookid = data.get('bookid')
    available = data.get('available')

    if not bookid or not available:
        return jsonify({"error": "Missing bookid or available field"}), 400

    connection = connect()
    if not connection:
        return jsonify({"error": "Failed to connect to the database"}), 500

    try:
        cursor = connection.cursor()
        query = "UPDATE books SET available = %s WHERE bookid = %s;"
        cursor.execute(query, (available, bookid))
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "No book found with the given bookid"}), 404
        return jsonify({"message": "Book updated successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()


@app.route('/api/book', methods=['GET'])
def show_book():
    """Retrieve book details by title."""
    booktitle = request.args.get('booktitle')
    if not booktitle:
        return jsonify({"error": "Book title cannot be empty"}), 400

    connection = connect()
    if not connection:
        return jsonify({"error": "Failed to connect to the database"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM books WHERE booktitle=%s;"
        cursor.execute(query, (booktitle,))
        book = cursor.fetchone()
        if not book:
            return jsonify({"error": "No book found with the given title"}), 404
        return jsonify({"booknameis": book}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()


@app.route('/api/deletElement', methods=['DELETE'])
def delete_book():
    """Delete a book from the database."""
    data = request.get_json()
    bookname = data.get('booknamehere')

    if not bookname:
        return jsonify({"error": "Book name cannot be empty"}), 400

    connection = connect()
    if not connection:
        return jsonify({"error": "Failed to connect to the database"}), 500

    try:
        cursor = connection.cursor()
        check_query = "SELECT * FROM books WHERE booktitle = %s"
        cursor.execute(check_query, (bookname,))
        book = cursor.fetchone()

        if not book:
            return jsonify({"error": "No book found with the given name"}), 404

        delete_query = "DELETE FROM books WHERE booktitle = %s"
        cursor.execute(delete_query, (bookname,))
        connection.commit()
        return jsonify({"message": "Book deleted successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()


if __name__ == "__main__":
    # Initialize the database
    initialize_db()

    # Use environment variables for host/port if available
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
