# 🚀 AI Accounting Platform - Backend

AI-powered B2B SaaS platform for automated accounts receivable follow-up with QuickBooks integration and VAPI voice calling.

## 📋 Project Overview

This platform automates invoice follow-ups by:
1. **Syncing invoices** from QuickBooks in real-time
2. **Analyzing overdue payments** using intelligent scoring algorithms
3. **Making AI phone calls** to customers via VAPI
4. **Tracking results** and scheduling follow-ups automatically

---

## 🏗️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Alembic** - Database migrations
- **Celery + Redis** - Background task queue

### Integrations
- **QuickBooks API** - Invoice and customer data
- **VAPI** - AI voice calling
- **N8n** - Workflow automation
- **Bubble** - No-code frontend

### Security
- **JWT** - User authentication
- **OAuth 2.0** - QuickBooks integration
- **Bcrypt** - Password hashing
- **Fernet** - Token encryption

---

## 🚦 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Redis (for Celery)
- QuickBooks Developer Account
- VAPI Account

### 1. Clone & Setup

```bash
# Clone repository
git clone <your-repo-url>
cd workspace

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Install PostgreSQL (if not already installed)
# macOS: brew install postgresql@14
# Ubuntu: sudo apt install postgresql-14

# Create database
createdb accounting_platform

# Or using Docker:
docker run --name postgres-dev \
  -e POSTGRES_PASSWORD=devpassword \
  -e POSTGRES_DB=accounting_platform \
  -p 5432:5432 \
  -d postgres:14
```

### 3. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
nano .env
```

**Required environment variables:**

```bash
# Generate SECRET_KEY:
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 4. Run Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Run migrations
alembic upgrade head
```

### 5. Start the Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python app/main.py
```

**API will be available at:**
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

---

## 📚 API Documentation

### Authentication Endpoints

#### 1. Sign Up
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### 2. Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

#### 3. Get Current User
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "is_active": true,
  "email_verified": false,
  "created_at": "2025-11-24T10:00:00",
  "last_login_at": "2025-11-24T10:30:00"
}
```

---

## 🔐 Authentication Flow

### User Authentication (JWT)

```
1. User signs up/logs in
   ↓
2. Backend generates JWT token
   ↓
3. Client stores token (localStorage or cookie)
   ↓
4. Client sends token in Authorization header:
   Authorization: Bearer <token>
   ↓
5. Backend verifies token and grants access
```

### QuickBooks OAuth

```
1. User clicks "Connect QuickBooks"
   ↓
2. Redirect to: GET /api/quickbooks/connect
   ↓
3. User approves on QuickBooks site
   ↓
4. Callback to: GET /api/quickbooks/callback?code=xxx
   ↓
5. Exchange code for tokens
   ↓
6. Store encrypted tokens in database
   ↓
7. Start syncing invoices automatically
```

---

## 🗄️ Database Schema

### Key Tables

**users** - Platform users
```sql
id, email, password_hash, full_name, role, is_active
```

**companies** - Multi-tenant companies
```sql
id, name, quickbooks_realm_id, quickbooks_access_token (encrypted)
```

**customers** - QuickBooks customers
```sql
id, company_id, quickbooks_customer_id, display_name, email, phone
```

**invoices** - QuickBooks invoices
```sql
id, company_id, customer_id, doc_number, total_amount, balance, 
due_date, status, priority_score
```

**calls** - VAPI call records
```sql
id, invoice_id, customer_id, vapi_call_id, status, outcome, 
transcript, recording_url
```

See `AUTH_AND_DB_GUIDE.md` for complete schema.

---

## 🔒 Security Best Practices

### 1. **Never Commit Secrets**
```bash
# .env is in .gitignore
# Never commit API keys, passwords, or tokens
```

### 2. **Password Requirements**
- Minimum 8 characters
- Must contain: 1 digit, 1 uppercase letter
- Hashed with bcrypt (cost factor 12)

### 3. **Token Encryption**
- QuickBooks OAuth tokens encrypted with Fernet
- Stored encrypted in database
- Decrypted only when needed

### 4. **JWT Tokens**
- Access token: 15 minutes (short-lived)
- Refresh token: 30 days (long-lived)
- Includes user_id and role in payload

### 5. **API Key Authentication**
```python
# For Bubble, N8n, VAPI webhooks
Authorization: Bearer sk_live_xxxxx...
```

---

## 📦 Project Structure

```
workspace/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Environment config
│   ├── database.py          # DB connection
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── customer.py
│   │   ├── invoice.py
│   │   ├── call.py
│   │   └── api_key.py
│   ├── schemas/             # Pydantic schemas
│   │   └── auth.py
│   ├── api/                 # API endpoints (TO BE ADDED)
│   │   ├── auth.py
│   │   ├── quickbooks.py
│   │   ├── invoices.py
│   │   └── calls.py
│   ├── services/            # Business logic (TO BE ADDED)
│   │   ├── quickbooks_service.py
│   │   ├── vapi_service.py
│   │   └── call_scheduler.py
│   └── utils/
│       └── security.py      # Auth & encryption
├── tests/                   # Unit tests (TO BE ADDED)
├── alembic/                 # DB migrations
├── requirements.txt
├── .env.example
├── .env                     # Your local config (not committed)
├── README.md
├── PROJECT_PLAN.md          # Full development plan
└── AUTH_AND_DB_GUIDE.md     # Auth & DB detailed guide
```

---

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

### Manual Testing with cURL

**Sign Up:**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234",
    "full_name": "Test User"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234"
  }'
```

**Get User Info:**
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <your-token>"
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Set `APP_ENV=production` in `.env`
- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Use managed PostgreSQL (AWS RDS, Supabase, etc.)
- [ ] Set up Redis for Celery
- [ ] Configure CORS with specific frontend domains
- [ ] Enable HTTPS
- [ ] Set up error monitoring (Sentry)
- [ ] Configure backup strategy
- [ ] Set up logging and monitoring

### Deploy to Render (Example)

```bash
# 1. Create new Web Service on Render
# 2. Connect GitHub repository
# 3. Build command:
pip install -r requirements.txt

# 4. Start command:
uvicorn app.main:app --host 0.0.0.0 --port $PORT

# 5. Add environment variables in Render dashboard
# 6. Create PostgreSQL database (Render provides add-on)
```

---

## 📖 Next Steps

### Phase 2: QuickBooks Integration (Week 2-3)
- [ ] Implement OAuth 2.0 flow
- [ ] Create QuickBooks API wrapper
- [ ] Build invoice sync service
- [ ] Add webhook handlers

### Phase 3: Backend API (Week 3-4)
- [ ] Invoice management endpoints
- [ ] Company management
- [ ] User permissions
- [ ] Call scheduling logic

### Phase 4: N8n Workflows (Week 4-5)
- [ ] Invoice monitoring workflow
- [ ] Payment detection workflow
- [ ] Call trigger workflow

### Phase 5: VAPI Integration (Week 5-6)
- [ ] Configure VAPI assistants
- [ ] Dynamic call script generation
- [ ] Call webhook handlers
- [ ] Recording storage

---

## 🤝 Contributing

### Development Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test
3. Commit: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Create pull request

### Code Style

- Follow PEP 8 (Python)
- Use type hints
- Write docstrings for functions
- Keep functions small and focused

---

## 📞 Support

For questions or issues:
1. Check `PROJECT_PLAN.md` for project overview
2. Check `AUTH_AND_DB_GUIDE.md` for auth details
3. Review API docs at `/api/docs`
4. Open an issue on GitHub

---

## 📄 License

[Add your license here]

---

## 🎯 Summary

This backend provides:
✅ **User authentication** with JWT  
✅ **QuickBooks OAuth** ready to implement  
✅ **Database models** for invoices, customers, calls  
✅ **Security utilities** for encryption and hashing  
✅ **FastAPI app** with auto-generated docs  
✅ **Multi-tenant** architecture  
✅ **Production-ready** structure  

**Ready to build Phase 2: QuickBooks Integration!** 🚀
