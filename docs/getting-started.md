# Getting Started with OpenHealthKit

This guide will walk you through setting up **OpenHealthKit** locally for development and testing.

---

## Prerequisites

- **Python**: 3.11 or 3.12
- **Node.js**: 18+ (for dashboard frontend)
- **Docker & Docker Compose** (Optional for containerized run)

---

## Local Setup

### 1. Clone Repository
```bash
git clone https://github.com/anannyamahajan/openhealthkit.git
cd openhealthkit
```

### 2. Set Up Virtual Environment & Install Package
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e "./packages/openhealthkit[postgres,dev]"
```

### 3. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 4. Run Seed Script
Populate synthetic demo data:
```bash
python scripts/seed_data.py
```

### 5. Start API Server
```bash
openhealthkit
```
The FastAPI interactive documentation will be available at:
`http://localhost:8000/docs`

---

## Running Dashboard

```bash
cd apps/dashboard
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.
