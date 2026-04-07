# AI Document Intelligence Platform

A full-stack AI-powered platform for secure document ingestion, text extraction, and conversational querying using a custom RAG (Retrieval-Augmented Generation) pipeline with embeddings-based semantic search and LLM-powered responses.

---

## Tech Stack

### Backend
- **Django 5.0.6** + **Django REST Framework** — REST API layer
- **PostgreSQL** + **psycopg2** — relational database
- **Simple JWT** — authentication and token management
- **drf-spectacular** — auto-generated Swagger/OpenAPI documentation
- **django-ratelimit** — API rate limiting
- **django-cors-headers** — cross-origin request handling
- **Gunicorn** — production WSGI server

### AI & Document Processing
- **OpenAI API** — LLM-powered conversational querying
- **FAISS** + **NumPy** — vector indexing and embeddings-based semantic search
- **PyPDF2** — PDF text extraction
- **python-docx** — DOCX text extraction
- **openpyxl** — Excel file processing

### Storage & Cloud
- **Azure Blob Storage** — secure document and asset storage

### Frontend
- **React.js** — UI layer
- **Nginx** — production static file serving (via Docker)

### Testing
- **pytest** + **pytest-django** — backend unit and integration testing

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                     │
│              (Nginx — Docker Container)              │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP / REST
┌─────────────────────▼───────────────────────────────┐
│              Django REST Framework                   │
│         JWT Auth │ Rate Limiting │ Swagger           │
└──────┬──────────────────────────────────┬───────────┘
       │                                  │
┌──────▼──────┐                  ┌────────▼────────┐
│  PostgreSQL │                  │  Azure Blob     │
│  (Metadata) │                  │  Storage (Docs) │
└─────────────┘                  └─────────────────┘
       │
┌──────▼──────────────────────────────────────────────┐
│                  RAG Pipeline                        │
│   Extract Text → Generate Embeddings → FAISS Index  │
│   Semantic Search → OpenAI API → LLM Response       │
└─────────────────────────────────────────────────────┘
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker + Docker Compose
- PostgreSQL
- Azure Storage Account
- OpenAI API Key

---

### 1. Clone the Repository

```bash
git clone https://github.com/Archana544/user_management_django.git
```

---

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```env
# Django
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/docplatform

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=your-azure-connection-string
AZURE_CONTAINER_NAME=documents

# JWT
JWT_SECRET_KEY=your-jwt-secret
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7
```

Run migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

---

### 3. Frontend Setup

```bash
cd frontend/ui
npm install
npm start
```

Create a `.env` file in the `frontend/` directory:

```env
REACT_APP_API_BASE_URL=http://localhost:8000/api
```

---

### 4. Run with Docker Compose (Recommended for Production)

```bash
docker-compose up --build
```

This spins up:
- Django API (Gunicorn) on port `8000`
- React frontend (Nginx) on port `80`
- PostgreSQL on port `5432`

---

## API Documentation

Once the backend is running, Swagger UI is available at:

```
http://localhost:8000/api/docs/
```

ReDoc alternative:

```
http://localhost:8000/api/redoc/
```

---

## Key API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/login/` | Obtain JWT tokens | No |
| POST | `/api/auth/refresh/` | Refresh access token | No |
| POST | `/api/documents/upload/` | Upload PDF/DOCX/XLSX | Yes |
| GET | `/api/documents/` | List user documents | Yes |
| DELETE | `/api/documents/:id/` | Delete a document | Yes |
| POST | `/api/documents/query/` | Query document via RAG | Yes |

---

## RAG Pipeline Flow

```
1. User uploads document (PDF / DOCX / XLSX)
        ↓
2. Text extracted (PyPDF2 / python-docx / openpyxl)
        ↓
3. Text chunked into segments
        ↓
4. Embeddings generated via OpenAI Embeddings API
        ↓
5. Vectors stored in FAISS index
        ↓
6. Original file uploaded to Azure Blob Storage
        ↓
7. Metadata saved to PostgreSQL

--- On Query ---

8. User submits a question
        ↓
9. Question converted to embedding
        ↓
10. FAISS semantic search → top K relevant chunks retrieved
        ↓
11. Chunks + question sent to OpenAI Chat API
        ↓
12. LLM generates answer with source references
        ↓
13. Response returned to user
```

---

## Running Tests

```bash
cd backend
pytest
```

Run with coverage:

```bash
pytest --cov=. --cov-report=html
```

---

## Docker — Frontend Build

The frontend uses a multi-stage Docker build:

- **Stage 1 (Build):** Node.js 20 Alpine — installs dependencies and builds the React app
- **Stage 2 (Serve):** Nginx Alpine — serves the static build files

```bash
# Build frontend image
docker build -t doc-platform-frontend ./frontend

# Run frontend container
docker run -p 80:80 doc-platform-frontend
```
---

## Environment Variables Reference

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Debug mode — always `False` in production |
| `DATABASE_URL` | PostgreSQL connection string |
| `OPENAI_API_KEY` | OpenAI API key for embeddings and chat |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Blob Storage connection |
| `AZURE_CONTAINER_NAME` | Azure container name for document storage |
| `JWT_SECRET_KEY` | Secret for signing JWT tokens |

---

## Security

- All endpoints (except auth) require a valid JWT Bearer token
- Role-based access control (RBAC) for upload and delete operations
- API rate limiting via `django-ratelimit` to prevent abuse
- CORS configured to allow only trusted frontend origins
- Files validated by type and size before upload
- All secrets managed via environment variables — never hardcoded

---
- GitHub: [github.com/Archana544](https://github.com/Archana544)
- LinkedIn: [linkedin.com/in/archana-chukkannagari-45aa951b9](https://linkedin.com/in/archana-chukkannagari-45aa951b9)
- Portfolio: [archanaportfolio-ruby.vercel.app](https://archanaportfolio-ruby.vercel.app)
