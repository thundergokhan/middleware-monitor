# Middleware Health & Integration Monitor (Enterprise Edition)

![Status](https://img.shields.io/badge/Status-Production%20Ready-success) ![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![Docker](https://img.shields.io/badge/Docker-Supported-blue)

A high-performance, containerized observability platform for banking and enterprise middleware environments. Designed to monitor REST, SOAP, and MQ services with SLA tracking and real-time visualization.

## 🚀 Features

### Core Capabilities
- **Multi-Protocol Monitoring**: Native support for **REST**, **SOAP**, and **Message Queues (MQ)**.
- **Parallel Execution**: Uses threaded architecture to check hundreds of services concurrently.
- **SLA Grading**: Automatically highlights services performing below defined latency thresholds (e.g., >1s).

### Observability & UI
- **Live OpsCenter Dashboard**: Auto-refreshing HTML5 interface with **Chart.js** latency trends.
- **System Topology Map**: Visual dependency graph generated automatically using **Mermaid.js**.
- **Prometheus Exporter**: Built-in `/metrics` endpoint for integration with Grafana/Cloud stacks.
- **Alerting**: Real-time logging alerts when services go DOWN.

### Architecture
- **Tech Stack**: Python 3.9, Flask (Web UI), SQLite (History), ThreadPoolExecutor (Concurrency).
- **Deployment**: Full Docker support with `docker-compose`.

## 🛠️ Installation & Usage

### Option 1: Docker (Recommended)
The easiest way to run the full stack:
```bash
docker compose up --build
```
Access the dashboard at [http://localhost:5000](http://localhost:5000).

### Option 2: Local Python
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python -m src.main --web
   ```

## ⚙️ Configuration

Edit `config/services.yaml` to define your landscape.

```yaml
services:
  - name: "Critical Payment API"
    type: "REST"
    url: "https://api.bank.com/payments"
    sla_threshold: 0.5  # Warn if latency > 500ms

  - name: "Legacy Mainframe"
    type: "SOAP"
    wsdl: "http://internal-soap/wsdl"
    simulation_mode: true
```

## 📊 API Endpoints

- **Dashboard**: `/` - The main visual interface.
- **Health JSON**: `/api/health` - Raw status data.
- **History**: `/api/history/<service_name>` - Time-series latency data.
- **Prometheus**: `/metrics` - Scrape target for monitoring systems.

## 📜 License

MIT License. Free for personal and commercial use.
