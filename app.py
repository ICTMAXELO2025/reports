from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import os  # Add this import
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Needed for flash messages

# --- Database connection ---
def get_db_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        DATABASE_URL = "postgresql://postgres:Maxelo%402023@localhost:5432/messagedb"
    return psycopg2.connect(DATABASE_URL)

# Create messages table if it doesn't exist
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            message TEXT NOT NULL,
            priority VARCHAR(10) NOT NULL,
            type VARCHAR(20) NOT NULL,
            terms BOOLEAN NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    if request.method == "POST":
        try:
            # Get form data
            name = request.form["name"]
            email = request.form["email"]
            message = request.form["message"]
            priority = request.form["priority"]
            message_type = request.form["type"]
            terms = True if request.form.get("terms") == "on" else False
            
            # Validate required fields
            if not all([name, email, message, priority, message_type]):
                flash("Please fill in all required fields", "error")
                return redirect(url_for("index"))
            
            # Insert into database
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO messages (name, email, message, priority, type, terms) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, email, message, priority, message_type, terms)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            flash("Your message has been sent successfully!", "success")
            return redirect(url_for("index"))
            
        except Exception as e:
            print("Error:", e)
            flash("An error occurred while submitting your message. Please try again.", "error")
            return redirect(url_for("index"))

@app.route("/messages")
def view_messages():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM messages ORDER BY submitted_at DESC")
        all_messages = cur.fetchall()
        cur.close()
        conn.close()
        
        return render_template("get_result.html", messages=all_messages)
    except Exception as e:
        print("Error:", e)
        flash("An error occurred while retrieving messages.", "error")
        return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()  # Initialize the database
    app.run(debug=True)