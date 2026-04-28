# Store Monitoring System

## Overview

This project is a **Store Uptime Monitoring System** built with **Django**.  
It loads store-related data from a provided ZIP file into the database and provides APIs to:

- **Trigger a report calculation** (`/trigger_report`)
- **Check report status or download the generated CSV** (`/get_report`)

The report contains **uptime and downtime** stats for each store for:
- **Last hour**
- **Last day**
- **Last week**

---

## Features
- Import **store info**, **business hours**, and **status logs** from CSV files in a ZIP.
- Calculate **uptime/downtime** based on business hours and activity logs.
- Two main endpoints:
    - `/trigger_report` → Initiates report generation, returns `report_id`.
    - `/get_report` → Check report status or download the CSV.      
- **CSV Output Format:**
    - store_id, uptime_last_hour, downtime_last_hour, uptime_last_day, downtime_last_day, uptime_last_week, downtime_last_week
---

## Tech Stack
- **Framework:** Django
- **Database:** SQLite 
- **Language:** Python 3.10+

---

## Project Structure
```bash
loop_store_monitor/
├── manage.py
├── loop_store_monitor/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── monitor/
    ├── __init__.py
    ├── apps.py
    ├── models.py
    ├── admin.py
    ├── tasks.py
    ├── utils.py
    ├── views.py
    ├── urls.py
    ├── management/
    │   └── commands/
    │       └── load_store_data.py
    └── migrations/
        └── 0001_initial.py
```
---

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/amansingh1528/Store_Monitoring_System.git
cd Store_Monitoring_System
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Apply Migrations
```bash
python manage.py migrate
```

### 4. Load Initial Data
```bash
python manage.py load_store_data --zip /path/to/store-monitoring-data.zip
```

### 5. Running the Server
```bash
python manage.py runserver
```
## API Endpoints Documentation

### 1. Trigger Report

- **POST /trigger_report** 
  - Response:  
```bash
{
  "report_id": "abc123"
}
```

### 2. Get Report

- **GET /get_report?report_id=abc123**
  - If still running:
```bash
{
  "status": "Running"
}
```

   - If complete:
   - Returns CSV file with schema:
```bash
store_id, uptime_last_hour, downtime_last_hour, uptime_last_day, downtime_last_day, uptime_last_week, downtime_last_week
```

## Future Enhancements
- Support JWT Authentication for APIs.
- Replace SQLite with PostgreSQL for scalability.

## CSV Output
- [CSV](https://drive.google.com/file/d/1jF19nm6M1d2JKXn0b2Dl-1iRikDxMlC7/view?usp=sharing)

## Author

- AMAN SINGH CHAUHAN



