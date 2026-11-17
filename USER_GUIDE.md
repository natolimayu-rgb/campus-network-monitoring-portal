# Campus Network Monitoring Portal — User Guide

## 1. Introduction

This guide explains how to use the Campus Network Monitoring Portal.

The application provides REST API endpoints for managing network monitoring records and viewing network-flow information stored in Redis.

## 2. Starting the Application

Before starting, make sure you have completed the installation steps in README.md:

- Created the three Docker networks.
- Generated the HTTPS certificates.
- Downloaded the required CIC-IDS2017 dataset.
- Placed the dataset CSV file inside the data directory.

Start the application:

    sudo docker compose up -d --build

Check whether the containers are running:

    sudo docker ps

The application services are:

- campus-api: FastAPI application.
- campus-redis: Redis database.
- campus-router: Network router and firewall.

## 3. Accessing the Application

The API runs on port 8000 using HTTPS.

Base URL:

    https://localhost:8000

The interactive API documentation is available at:

    https://localhost:8000/docs

Because the project uses a self-signed certificate, use the -k option with curl during local testing.

## 4. Checking Application Health

To check whether the API and Redis database are responding, run:

    curl -k https://localhost:8000/health

Expected response when both are healthy:

    {
      "api": "healthy",
      "database": "connected"
    }

If Redis is unavailable, the response reports that the database is disconnected.

## 5. Managing Network Monitoring Records

### 5.1 Create a Record

Use POST /records to create a monitoring record.

Example:

    curl -k -X POST https://localhost:8000/records \
    -H "Content-Type: application/json" \
    -d '{"device":"Campus-Router-1","status":"online","latency_ms":8.7}'

Example response:

    {
      "message": "Record saved",
      "id": "GENERATED_RECORD_ID"
    }

The application generates a unique record ID and stores the record in Redis.

### 5.2 View Records

Use GET /records to retrieve stored monitoring records.

    curl -k https://localhost:8000/records

The response contains the total number of records and their details.

### 5.3 Update a Record

Use PUT /records/{record_id} to update an existing record.

Replace GENERATED_RECORD_ID with the ID returned when the record was created.

Example:

    curl -k -X PUT https://localhost:8000/records/GENERATED_RECORD_ID \
    -H "Content-Type: application/json" \
    -d '{"device":"Campus-Router-1","status":"maintenance","latency_ms":12.3}'

A successful response confirms that the record was updated.

If the record ID does not exist, the API returns a 404 error.

## 6. Viewing Network Flows

The application supports importing selected network-flow records from the CIC-IDS2017 dataset.

### 6.1 Import Network Flows

Make sure the dataset CSV is in the data directory.

Run:

    sudo docker compose exec api python import_flows.py

The script:

- Connects to Redis.
- Reads the CIC-IDS2017 CSV file.
- Selects BENIGN and PortScan records.
- Imports up to 2,500 records for each category.
- Stores the imported records in Redis.

A successful import reports the number of records imported for each category.

### 6.2 View Imported Flows

Use GET /flows to retrieve imported network flows.

    curl -k https://localhost:8000/flows

You can also specify a limit:

    curl -k "https://localhost:8000/flows?limit=20"

The API accepts limits from 1 to 1,000.

### 6.3 View Flow Summary

Use GET /flows/summary to view the number of imported records in each category.

    curl -k https://localhost:8000/flows/summary

Example response:

    {
      "dataset": "CIC-IDS2017",
      "total_flows": 5000,
      "labels": {
        "BENIGN": 2500,
        "PortScan": 2500
      }
    }

The numbers above represent the expected result when all 5,000 records have been imported successfully.

## 7. Running the Health-Check Script

The project includes a script that checks whether the API, Redis, and router containers are running and whether the API health endpoint responds.

Make the script executable:

    chmod +x scripts/health-check.sh

Run it:

    ./scripts/health-check.sh

The script displays PASS or FAIL messages for the container and API checks.

The script detects problems but does not automatically restart failed containers.

## 8. Stopping the Application

To stop the containers:

    sudo docker compose down

This stops and removes the Compose containers while preserving the Redis data volume.

To also delete the Redis data volume:

    sudo docker compose down -v

WARNING: Removing the volume permanently deletes the records stored in that volume.

## 9. Troubleshooting

### API is unavailable

Check the container status:

    sudo docker ps -a

View API logs:

    sudo docker compose logs api

### Redis is disconnected

Check Redis:

    sudo docker compose logs redis

Check whether the Redis container is running:

    sudo docker inspect campus-redis

### Dataset file is missing

Verify that the required CSV exists:

    ls -lh data/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv

If it is missing, follow the download instructions in data/DATASET_INSTRUCTIONS.md.

### HTTPS certificate error

Make sure these files exist:

    certs/server.crt
    certs/server.key

If they are missing, follow the certificate-generation instructions in README.md.

## 10. Important Notes

- Redis stores application records and imported network flows.
- The dataset import script imports up to 2,500 records per label.
- The health-check script detects failures but does not provide automatic recovery.
- The HTTPS certificate is self-signed and intended for local testing.
- The raw packet captures and private certificate keys are not included in the public repository.

