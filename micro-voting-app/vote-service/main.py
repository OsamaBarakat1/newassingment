from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voting Service")

# Configuration from Environment Variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")

class Vote(BaseModel):
    voter_id: str
    vote: str

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/vote")
async def cast_vote(vote: Vote):
    if vote.vote not in ["A", "B"]:
        raise HTTPException(status_code=400, detail="Invalid vote. Must be 'A' or 'B'.")
    
    data = json.dumps({"voter_id": vote.voter_id, "vote": vote.vote})
    
    try:
        r.lpush("votes", data)
        logger.info(f"Vote cast by {vote.voter_id} for {vote.vote}")
        return {"status": "Vote registered", "voter_id": vote.voter_id}
    except Exception as e:
        logger.error(f"Redis Error: {e}")
        raise HTTPException(status_code=500, detail="Could not record vote")
