import secrets
from collections import defaultdict

from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

API_KEY = "ak_4kbj3jnpqnnqw9trm8ttnst4"
EMAIL = "23f1001027@ds.study.iitm.ac.in"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/analytics")
async def analytics(request: Request, x_api_key: str = Header(default=None)):
    # 1) auth before anything else
    if x_api_key is None or not secrets.compare_digest(x_api_key, API_KEY):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    # 2) parse body
    try:
        body = await request.json()
        events = body["events"]
    except Exception:
        return JSONResponse({"error": "body must be {\"events\": [...]}"}, status_code=400)

    users = set()
    positive_by_user = defaultdict(float)
    revenue = 0.0
    for e in events:
        user = e.get("user")
        amount = float(e.get("amount", 0))
        users.add(user)
        if amount > 0:
            revenue += amount
            positive_by_user[user] += amount

    top_user = max(positive_by_user, key=positive_by_user.get) if positive_by_user else None

    return {
        "email": EMAIL,
        "total_events": len(events),
        "unique_users": len(users),
        "revenue": round(revenue, 6),
        "top_user": top_user,
    }
