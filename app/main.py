from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import json
import time

app = FastAPI(title="Campus Network Monitoring Portal")

db = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)

class NetworkRecord(BaseModel):
    device: str
    status: str
    latency_ms: float

@app.get("/")
def home():
    return {"message": "Campus Network Monitoring Portal is running"}

@app.get("/health")
def health():
    try:
        db.ping()
        return {"api": "healthy", "database": "connected"}
    except Exception as e:
        return {"api": "running", "database": "disconnected", "error": str(e)}

@app.post("/records")
def add_record(record: NetworkRecord):
    record_id = str(time.time_ns())
    db.set(record_id, json.dumps(record.model_dump()))
    return {"message": "Record saved", "id": record_id}
@app.get("/records")
def get_records():
    records = []

    for key in db.scan_iter(match="*"):
        if key.startswith("flow:"):
            continue

        record_data = db.get(key)

        if record_data:
            records.append({
                "id": key,
                **json.loads(record_data)
            })

    return {"total": len(records), "records": records}
@app.put("/records/{record_id}")
def update_record(record_id: str, record: NetworkRecord):
    existing_record = db.get(record_id)

    if existing_record is None:
        raise HTTPException(
            status_code=404,
            detail="Network record not found"
        )

    db.set(record_id, json.dumps(record.model_dump()))

    return {
        "message": "Record updated",
        "id": record_id,
        "record": record.model_dump()
    }
@app.get("/flows")
def get_flows(limit: int = 100):
    limit = max(1, min(limit, 1000))

    flows = []

    for key in db.scan_iter(match="flow:*"):
        flow_data = db.get(key)

        if flow_data:
            flows.append({
                "id": key,
                **json.loads(flow_data)
            })

        if len(flows) >= limit:
            break

    return {
        "total_returned": len(flows),
        "flows": flows
    }


@app.get("/flows/summary")
def get_flows_summary():
    counts = {
        "BENIGN": 0,
        "PortScan": 0
    }

    total = 0

    for key in db.scan_iter(match="flow:*"):
        flow_data = db.get(key)

        if flow_data:
            flow = json.loads(flow_data)
            label = flow.get("label")

            if label in counts:
                counts[label] += 1
                total += 1

    return {
        "dataset": "CIC-IDS2017",
        "total_flows": total,
        "labels": counts
    }
