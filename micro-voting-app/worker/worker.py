import redis
import psycopg2
import os
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")

def init_db():
    while True:
        try:
            conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS votes (voter_id VARCHAR(255) PRIMARY KEY, vote VARCHAR(10))")
            conn.commit()
            cur.close()
            conn.close()
            logger.info("Database initialized")
            break
        except Exception as e:
            logger.error(f"Waiting for DB... {e}")
            time.sleep(2)

def process_votes():
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
    
    while True:
        try:
            # Block until an item is available in the 'votes' list
            _, data = r.brpop("votes")
            vote_data = json.loads(data)
            
            voter_id = vote_data["voter_id"]
            vote = vote_data["vote"]
            
            conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
            cur = conn.cursor()
            cur.execute("INSERT INTO votes (voter_id, vote) VALUES (%s, %s) ON CONFLICT (voter_id) DO UPDATE SET vote = EXCLUDED.vote", (voter_id, vote))
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"Processed vote: {voter_id} -> {vote}")
            
        except Exception as e:
            logger.error(f"Worker Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    init_db()
    process_votes()
