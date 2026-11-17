import csv
import json
import redis
import hashlib

CSV_FILE = "data/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv"

db = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)

LIMIT_PER_LABEL = 2500

counts = {
    "BENIGN": 0,
    "PortScan": 0
}

db.ping()
print("Connected to Redis")

with open(CSV_FILE, newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)

    for row in reader:
        row = {key.strip(): value.strip() for key, value in row.items() if key}

        label = row.get("Label", "")

        if label not in counts:
            continue

        if counts[label] >= LIMIT_PER_LABEL:
            continue

        flow_id = hashlib.sha256(
            f"CIC-IDS2017:{label}:{counts[label]}".encode()
        ).hexdigest()[:16]

        flow = {
            "dataset": "CIC-IDS2017",
            "source_file": CSV_FILE.split("/")[-1],
            "label": label,
            "destination_port": row.get("Destination Port"),
            "flow_duration": row.get("Flow Duration"),
            "total_fwd_packets": row.get("Total Fwd Packets"),
            "total_backward_packets": row.get("Total Backward Packets"),
            "flow_bytes_per_second": row.get("Flow Bytes/s"),
            "flow_packets_per_second": row.get("Flow Packets/s"),
            "syn_flag_count": row.get("SYN Flag Count")
        }

        db.set(f"flow:{flow_id}", json.dumps(flow))
        counts[label] += 1

        if all(count >= LIMIT_PER_LABEL for count in counts.values()):
            break

print("\nImport complete")
print("BENIGN records:", counts["BENIGN"])
print("PortScan records:", counts["PortScan"])
print("Total imported:", sum(counts.values()))
