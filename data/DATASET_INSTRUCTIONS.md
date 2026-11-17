# Dataset Instructions

This project uses the CIC-IDS2017 network intrusion detection dataset.

## Required file

Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv

## Download

Download the dataset from the official Canadian Institute for Cybersecurity website:

https://www.unb.ca/cic/datasets/ids-2017.html

Place the required CSV file inside this project's `data/` directory.

The expected path is:

data/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv

## Import the data

After downloading the file and starting the Docker services, run:

sudo docker compose exec api python import_flows.py

The import script selects BENIGN and PortScan records and imports up to 2,500 records per category into Redis.

## Attribution

Please refer to the official CIC-IDS2017 dataset page for dataset details and the associated research citation.
arch citation.
