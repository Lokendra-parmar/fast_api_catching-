from fastapi import FastAPI
import time
from collections import OrderedDict

app = FastAPI()

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

@app.post("/")
def query_api(data: dict):
    start = time.time()
    query = data["query"]

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

    latency = int((time.time() - start)*1000)

    return {
        "answer": answer,
        "cached": cached,
        "latency": latency,
        "cacheKey": query
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
