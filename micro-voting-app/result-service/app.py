from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import os
import logging

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/results")
def get_results():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT vote, COUNT(voter_id) FROM votes GROUP BY vote")
        rows = cur.fetchall()
        
        results = {row[0]: row[1] for row in rows}
        # Ensure both categories exist
        results.setdefault("A", 0)
        results.setdefault("B", 0)
        
        cur.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        app.logger.error(f"Database Error: {e}")
        return jsonify({"error": "Could not fetch results"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
