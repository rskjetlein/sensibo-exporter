<!-- Badges -->
[![CI](https://github.com/rskjetlein/sensibo-exporter/actions/workflows/ci.yml/badge.svg)](https://github.com/rskjetlein/sensibo-exporter/actions/workflows/ci.yml)
[![Docker](https://github.com/rskjetlein/sensibo-exporter/actions/workflows/docker.yml/badge.svg)](https://github.com/rskjetlein/sensibo-exporter/actions/workflows/docker.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/OWNER/REPO.svg)](https://github.com/OWNER/REPO/commits/main)


# Sensibo Prometheus Exporter

A lightweight Python/Flask web service that exposes **Sensibo temperature and humidity** as Prometheus-compatible metrics.

Useful for collecting and visualizing indoor climate data using Prometheus + Grafana.

---

## Features

* Exposes Sensibo measurements at `/metrics`  
* Outputs Prometheus-formatted gauge metrics  
* Temperature (°C)  
* Relative humidity (%)  
* Configurable via environment variables  
* Docker + Docker Compose support  
* Simple, dependency-minimal  

---

## Requirements

- Python 3.10+
- A valid Sensibo API key
- Sensibo Device ID

---

## Environment Variables

| Name       | Required | Description |
|------------|----------|-------------|
| `API_KEY`  | x       | Sensibo API key |
| `DEVICE_ID`| x       | Sensibo device ID |

You can provide them via shell, `.env`, Docker, or Docker Compose.

---

## Running Locally

```bash
export API_KEY="your_api_key_here"
export DEVICE_ID="your_device_id_here"
python app.py
```

Endpoint accesible at
http://localhost:8000/metrics

### Example metrics output
```prometheusexporter
# HELP sensibo_temperature_celsius Current temperature in Celsius
# TYPE sensibo_temperature_celsius gauge
sensibo_temperature_celsius{device="DEVICE_ID"} 22.3

# HELP sensibo_humidity_relative Relative humidity in percent
# TYPE sensibo_humidity_relative gauge
sensibo_humidity_relative{device="DEVICE_ID"} 40.1
```

## Docker

### Build image
```dockerfile
docker build -t sensibo-metrics:latest .
```

### Run
```bash
docker run -p 8000:8000 \
  -e API_KEY="your_api_key_here" \
  -e DEVICE_ID="your_device_id_here" \
  sensibo-metrics:latest
```

## Docker Compose
```dockercompose
version: "3.9"

services:
  sensibo-exporter:
    image: sensibo-metrics:latest
    container_name: sensibo-exporter
    ports:
      - "8000:8000"
    environment:
      API_KEY: "${API_KEY}"
      DEVICE_ID: "${DEVICE_ID}"
    restart: unless-stopped
```

## Prometheus scrape example
```
scrape_configs:
  - job_name: "sensibo"
    static_configs:
      - targets: ["sensibo-exporter:8000"]
```

## Development

Install dependencies:
```
pip install -r requirements.txt
```

Run locally:
```
API_KEY=xxx DEVICE_ID=yyy python app.py
```

## Project structure
```
.
├── app.py
├── Dockerfile
├── requirements.txt
├── docker-compose.yml   (optional)
└── README.md
```

## Future Enhancements (Planned)

* Multi-device support
* More metrics: power state, fan mode, target temperature
* Optional labels (room, location)
* Prometheus Python client version

**PRs welcome!**




