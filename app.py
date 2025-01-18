from flask import Flask, request, jsonify, render_template, send_from_directory
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def connect():
    """Connect to the MySQL database and ensure the `books` table exists."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Abhishek@1259',
            db='practice'
        )
        if connection.is_connected():
            print("Connected to the database!")
            cur = connection.cursor()
            cur.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'practice' AND table_name = 'books';
            """)
            result = cur.fetchone()
            if result[0] == 0:
                cur.execute("""
                    CREATE TABLE books (
                        bookid INT AUTO_INCREMENT PRIMARY KEY,
                        available VARCHAR(225) NOT NULL,
                        booktitle VARCHAR(255) NOT NULL,
                        author VARCHAR(255) NOT NULL,
                        timestamp VARCHAR(255) NOT NULL
                    );
                """)
                print("Books table created.")
            cur.close()
            return connection
    except Error as e:
        print(f"Error occurred during connection: {e}")
        return None

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
        if connection.is_connected():
            connection.close()

@app.route('/api/addBook', methods=['POST'])
def add_book():
    """Add a new book to the database."""
    try:
        data = request.json
        bookid = data.get('bookid')
        available = data.get('available')
        booktitle = data.get('booktitle')
        author = data.get('author')
        timestamp = data.get('timestamp')

        conn = connect()
        if not conn:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cur = conn.cursor()
        query = """
            INSERT INTO books (bookid, available, booktitle, author, timestamp) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query, (bookid, available, booktitle, author, timestamp))
        conn.commit()
        return jsonify({"message": "Book added successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/api/updatepa', methods=['POST'])
def update_book():
    """Update a book's availability in the database."""
    try:
        data = request.json
        bookid = data.get('bookid')  # Ensure key matches frontend
        available = data.get('available')  # Ensure key matches frontend

        if not bookid or not available:
            return jsonify({"error": "Missing bookid or available field"}), 400

        conn = connect()
        if not conn:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cur = conn.cursor()
        query = "UPDATE books SET available = %s WHERE bookid = %s;"
        cur.execute(query, (available, bookid))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "No book found with the given bookid"}), 404
        return jsonify({"message": "Book updated successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/api/book',methods = ['GET'])
def show_book():
    try:
        booktitle = request.args.get('booktitle')
        if not booktitle:
            return jsonify({"error" :"book title cannot be empty" }),200
        conn = connect()
        if not conn:
            return "failed connecting!!"
        cur = conn.cursor(dictionary=True)
        query = "SELECT * FROM books WHERE booktitle=%s;"
        cur.execute(query,(booktitle,))
        
        book = cur.fetchone()
        print("resived book is: ",book)
        if not book:
            return jsonify({"error":"no book found with given title"})
        return jsonify({"booknameis":book}),200
    except Error as e:
        return jsonify({"error":str(e)}),500
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/api/deletElement', methods=['DELETE'])
def delete_book():
    try:
        # Parse the JSON body of the request
        data = request.get_json()
        bookname = data.get('booknamehere')

        # Validate the book name
        if not bookname:
            return jsonify({"error": "Book name cannot be empty"}), 400

        # Connect to the database
        conn = connect()
        if not conn:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cur = conn.cursor()

        # Check if the book exists
        check_query = "SELECT * FROM books WHERE booktitle = %s"
        cur.execute(check_query, (bookname,))
        book = cur.fetchone()

        if not book:
            return jsonify({"error": "No book found with the given name"}), 404

        # Delete the book
        delete_query = "DELETE FROM books WHERE booktitle = %s"
        cur.execute(delete_query, (bookname,))
        conn.commit()

        return jsonify({"message": "Book deleted successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)
