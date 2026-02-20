# Universal Data Connector

A production-quality FastAPI service that provides a **unified interface** for an LLM to access CRM, support ticket, and analytics data through **function calling**. Responses are automatically filtered, prioritized, and optimized for **voice conversations**.

---

## Setup Instructions

### Local

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/universal-data-connector.git
cd universal-data-connector

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env file
cp .env.example .env

# 4. Run the server
uvicorn app.main:app --reload

# 5. Open Swagger UI
# Visit: http://localhost:8000/docs
```

### Docker

```bash
docker-compose up --build
# Visit: http://localhost:8000/docs
```

---

## Sample .env File

```
APP_NAME=Universal Data Connector
MAX_RESULTS=10
OPENAI_API_KEY=your_openai_api_key_here  # optional
```

---

## Data Flow Architecture

```
User / LLM Query
      ↓
FastAPI Server (main.py)
      ↓
Router (/data/{source})
      ↓
Connector Layer
├── CRMConnector        → data/customers.json
├── SupportConnector    → data/support_tickets.json
└── AnalyticsConnector  → data/analytics.json
      ↓
Services Pipeline
├── BusinessRules       → prioritize, filter, limit to 10
├── DataIdentifier      → detect time_series / tabular_crm / tabular_support
└── VoiceOptimizer      → summarize + build voice_summary sentence
      ↓
DataResponse (Pydantic)
├── data[]              → filtered records
└── metadata
    ├── total_results
    ├── returned_results
    ├── data_type
    ├── data_freshness
    ├── voice_summary    ← one sentence, ready to speak aloud
    └── context_hint
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/data/crm` | Query CRM customers |
| GET | `/data/support` | Query support tickets |
| GET | `/data/analytics` | Query analytics metrics |
| POST | `/data/chat` | Natural language query routing |
| GET | `/data/schema/functions` | OpenAI-compatible LLM function schemas |
| GET | `/docs` | Swagger UI |

---

## Example Queries

### 1. Active enterprise customers
```
GET /data/crm?status=active&plan=enterprise
```

### 2. Open high-priority support tickets
```
GET /data/support?status=open&priority=high
```

### 3. Daily active users (last week)
```
GET /data/analytics?metric=daily_active_users&date_from=2026-02-10&date_to=2026-02-16
```

### 4. Natural language chat
```bash
POST /data/chat
{"query": "show me open high priority tickets"}
```

### 5. LLM function calling schemas
```
GET /data/schema/functions
```

---

## Voice Optimization Rules

| Rule | Detail |
|------|--------|
| Limit results | Default max 10 records per response |
| Prioritization | Open + high-priority tickets first; active customers by MRR |
| Summarization | Datasets > 10 items condensed to one readable sentence |
| Freshness | Every response includes a `data_freshness` timestamp |
| Voice summary | `voice_summary` field is a one-sentence spoken-ready answer |

---

## Scalability (10,000 Users)

Current implementation uses flat JSON files. To scale to 10,000 users:

1. **Database** — Replace JSON with PostgreSQL + async SQLAlchemy
2. **Caching** — Add Redis layer (TTL = 60s) for frequent queries
3. **Workers** — Run multiple Uvicorn workers behind Nginx
4. **Rate limiting** — Per-API-key limits via `slowapi`
5. **Horizontal scaling** — Docker containers behind AWS ALB with auto-scaling
6. **Observability** — Prometheus metrics + structured JSON logging

---

## Project Structure

```
universal-data-connector/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # Settings management
│   ├── connectors/
│   │   ├── base.py              # Abstract base connector
│   │   ├── crm_connector.py
│   │   ├── support_connector.py
│   │   └── analytics_connector.py
│   ├── models/
│   │   └── common.py            # Pydantic models
│   ├── routers/
│   │   ├── health.py
│   │   └── data.py              # All data endpoints + LLM schemas
│   ├── services/
│   │   ├── business_rules.py    # Filtering + prioritization
│   │   ├── data_identifier.py   # Data type detection
│   │   └── voice_optimizer.py   # Summarization
│   └── utils/
│       └── logging.py
├── data/
│   ├── customers.json
│   ├── support_tickets.json
│   └── analytics.json
├── tests/
│   └── test_api.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
