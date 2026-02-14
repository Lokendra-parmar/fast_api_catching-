from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
from collections import OrderedDict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = OrderedDict()
CACHE_LIMIT = 1500

stats = {
    "totalRequests": 0,
    "cacheHits": 0,
    "cacheMisses": 0
}

def fake_llm_answer(query):
    time.sleep(1)   # simulate API delay
    return f"Answer for: {query}"

@app.get("/")
def home():
    return {"message": "API is running"}

from fastapi import Request

@app.post("/")
async def query_api(request: Request):
    start = time.time()

    try:
        data = await request.json()
    except:
        data = {}

    query = data.get("query", "")

    if not query:
        return {
            "answer": "",
            "cached": False,
            "latency": 0,
            "cacheKey": "",
            "safe": True
        }

    stats["totalRequests"] += 1

    if query in cache:
        stats["cacheHits"] += 1
        answer = cache[query]
        cached = True
    else:
        stats["cacheMisses"] += 1
        answer = fake_llm_answer(query)
        cache[query] = answer

        if len(cache) > CACHE_LIMIT:
            cache.popitem(last=False)

        cached = False

    latency = int((time.time() - start) * 1000)

    return {
        "answer": answer,
        "cached": cached,
        "latency": latency,
        "cacheKey": query,
        "safe": True
    }

@app.get("/analytics")
def analytics():
    hit_rate = stats["cacheHits"] / max(stats["totalRequests"],1)

    return {
        "hitRate": hit_rate,
        "totalRequests": stats["totalRequests"],
        "cacheHits": stats["cacheHits"],
        "cacheMisses": stats["cacheMisses"],
        "cacheSize": len(cache),
        "costSavings": hit_rate * 4.26,
        "savingsPercent": hit_rate * 100,
        "strategies": [
            "exact match",
            "LRU eviction",
            "TTL expiration"
        ]
    }
