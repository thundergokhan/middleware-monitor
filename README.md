# Middleware Health Monitor Platform (v2.0)

![Status](https://img.shields.io/badge/Version-2.0%20SaaS-blueviolet) ![License](https://img.shields.io/badge/License-MIT-green)

A self-hosted, enterprise-grade observability platform. Monitor REST, SOAP, and MQ services with a built-in management interface.

## 🌟 v2.0 New Features
- **Admin Panel**: Manage services via Web UI (No more YAML editing!).
- **Authentication**: Secure Login/Logout system.
- **Database Engine**: Fully dynamic configuration using SQLite.

## 🚀 Quick Start

### Docker (Recommended)
```bash
docker compose up --build
```
- **Dashboard**: [http://localhost:5000](http://localhost:5000)
- **Admin Panel**: [http://localhost:5000/settings](http://localhost:5000/settings)
  - **User**: `admin`
  - **Pass**: `admin123`

### Local Python
```bash
pip install -r requirements.txt
python -m src.main --web
```

## 📸 Screenshots
![Dashboard Preview](assets/dashboard_preview.png)
*v3.0 Dashboard featuring Dark Mode and AI Anomaly Detection*

## 🛠️ Tech Stack
- **Backend**: Python 3.9, Flask
- **Database**: SQLite (Zero config required)
- **Frontend**: Bootstrap 5, Chart.js, Mermaid.js
- **Ops**: Docker, Threading

## 📜 License
MIT License.
