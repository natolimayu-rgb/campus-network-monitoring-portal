# Campus Network Monitoring Portal

## 1. Project Overview

The Campus Network Monitoring Portal is a containerized network monitoring application built with Python, FastAPI, Redis, and Docker.

The project demonstrates network segmentation, routing, firewall rules, HTTPS communication, network-flow data collection, health checks, and network performance testing.

## 2. Features

- REST API for creating, viewing, and updating network monitoring records.
- Redis database for storing monitoring records and imported network flows.
- Three separate Docker networks for client, application, and database traffic.
- Linux router using IP forwarding, iptables, and NAT.
- HTTPS communication using a self-signed TLS certificate.
- CIC-IDS2017 network-flow dataset import.
- Health-check script for detecting container and API availability.
- Network performance testing using Linux traffic control (tc/netem).

## 3. Technologies Used

- Python 3.12
- FastAPI
- Redis 7
- Docker and Docker Compose
- Linux
- iptables
- iproute2
- tcpdump
- CIC-IDS2017 dataset

## 4. Project Structure

```text
campus-network-portal/
├── app/
│   ├── Dockerfile
│   ├── main.py
│   ├── import_flows.py
│   └── requirements.txt
├── data/
│   └── DATASET_INSTRUCTIONS.md
├── router/
│   ├── Dockerfile
│   └── start-router.sh
├── scripts/
│   └── health-check.sh
├── docker-compose.yml
└── README.md
```

The dataset CSV and TLS certificates are not included in this repository. Follow the setup instructions below.

## 5. Network Architecture

The project uses three Docker bridge networks:

| Network | Subnet | Purpose |
|---|---|---|
| campus-client | 10.10.1.0/24 | Client network |
| campus-app | 10.10.2.0/24 | Application network |
| campus-database | 10.10.3.0/24 | Database network |

### Container IP Addresses

| Component | IP Address |
|---|---|
| Router - Client interface | 10.10.1.254 |
| Router - Application interface | 10.10.2.254 |
| Router - Database interface | 10.10.3.254 |
| API - Application interface | 10.10.2.10 |
| API - Database interface | 10.10.3.10 |
| Redis | 10.10.3.20 |

The router uses iptables rules to control forwarding between network segments. Direct client access to the Redis database port is blocked, while application-to-database communication is allowed.

## 6. Requirements

Install the following before starting:

- Docker Engine
- Docker Compose v2
- OpenSSL
- curl

## 7. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd campus-network-portal
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with the actual repository URL.

### Step 2: Create the Docker Networks

Run these commands once on a new Docker host:

```bash
sudo docker network create --driver bridge --subnet 10.10.1.0/24 --gateway 10.10.1.1 campus-client

sudo docker network create --driver bridge --subnet 10.10.2.0/24 --gateway 10.10.2.1 campus-app

sudo docker network create --driver bridge --subnet 10.10.3.0/24 --gateway 10.10.3.1 campus-database
```

These networks are declared as external in the Docker Compose configuration, so they must exist before starting the services.

### Step 3: Create HTTPS Certificates

The certificates are excluded from GitHub for security.

Create a certificate directory:

```bash
mkdir -p certs
```

Generate a self-signed certificate and private key:

```bash
openssl req -x509 -newkey rsa:2048 \
-keyout certs/server.key \
-out certs/server.crt \
-sha256 -days 365 -nodes \
-subj "/CN=localhost" \
-addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:10.10.2.10"
```

The certificate is intended for local project testing. Browsers and curl may warn that it is self-signed.

### Step 4: Obtain the Dataset

This project uses the CIC-IDS2017 dataset.

Download the required file from the official Canadian Institute for Cybersecurity website:

https://www.unb.ca/cic/datasets/ids-2017.html

Required file:

`Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv`

Place it in:

`data/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv`

See `data/DATASET_INSTRUCTIONS.md` for more information.

### Step 5: Start the Docker Services

```bash
sudo docker compose up -d --build
```

Check the running containers:

```bash
sudo docker ps
```

### Step 6: Import Network-Flow Records

After the services are running and the dataset is in the correct location:

```bash
sudo docker compose exec api python import_flows.py
```

The import script selects BENIGN and PortScan records and imports up to 2,500 records per category into Redis.

### Step 7: Verify the Application

Check the API health endpoint:

```bash
curl -k https://localhost:8000/health
```

Expected response:

```json
{
  "api": "healthy",
  "database": "connected"
}
```

Check the flow summary:

```bash
curl -k https://localhost:8000/flows/summary
```

Open the interactive API documentation:

https://localhost:8000/docs

Because the certificate is self-signed, your browser may display a security warning during local testing.

## 8. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Application status |
| GET | /health | API and Redis health |
| POST | /records | Create a monitoring record |
| GET | /records | Retrieve monitoring records |
| PUT | /records/{record_id} | Update a monitoring record |
| GET | /flows | Retrieve imported network flows |
| GET | /flows/summary | Display flow label counts |

### Example: Create a Monitoring Record

```bash
curl -k -X POST https://localhost:8000/records \
-H "Content-Type: application/json" \
-d '{"device":"Campus-Router-1","status":"online","latency_ms":8.7}'
```

### Example: Retrieve Monitoring Records

```bash
curl -k https://localhost:8000/records
```

### Example: Retrieve Network-Flow Summary

```bash
curl -k https://localhost:8000/flows/summary
```

## 9. Health Monitoring

The project includes a health-check script that checks whether the API, Redis, and router containers are running and whether the API health endpoint responds.

Run:

```bash
chmod +x scripts/health-check.sh
./scripts/health-check.sh
```

The script detects failures but does not automatically restart services.

## 10. Network Performance Testing

Linux traffic control (`tc`) and the netem queueing discipline can be used to introduce controlled network conditions, such as:

- Network delay
- Packet loss
- Rate limits

Application requests can then be measured under baseline and degraded conditions.

Performance results should be interpreted according to the actual network path traversed by the test traffic. Traffic shaped on a router interface will not necessarily affect requests that bypass that router.

## 11. Stopping the Services

Stop the containers:

```bash
sudo docker compose down
```

To also remove the Redis data volume:

```bash
sudo docker compose down -v
```

Warning: The second command deletes the persistent Redis volume and its stored records.

## 12. Security Notes

- Private TLS keys and certificates are not included in the repository.
- Packet captures are excluded because they may contain network metadata or sensitive traffic.
- Redis is not published as a host port.
- Router firewall rules restrict forwarding between network segments.
- The included self-signed certificate is for development and testing, not production deployment.

## 13. Dataset Attribution

This project uses the CIC-IDS2017 dataset provided by the Canadian Institute for Cybersecurity at the University of New Brunswick.

Dataset information:

https://www.unb.ca/cic/datasets/ids-2017.html

Refer to the official dataset page and associated research publication for citation information.
