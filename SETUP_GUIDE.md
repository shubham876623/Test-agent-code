# 🎯 Complete Setup Guide

## Quick Answer to "How do we handle auth and DB?"

### **Authentication Strategy:**

We use **3 types of authentication**:

1. **JWT for Users** (Login to platform)
   - Users sign up → Get JWT token → Use token for API calls
   - Token expires in 15 minutes, refresh token lasts 30 days

2. **OAuth 2.0 for QuickBooks** (Connect to QuickBooks)
   - User clicks "Connect" → Redirects to QuickBooks → Gets back tokens
   - Tokens encrypted and stored in database
   - Auto-refreshes every hour

3. **API Keys for Integrations** (Bubble, N8n, VAPI)
   - Generate API key → Give to Bubble/N8n → They use it to call your backend
   - Format: `sk_live_abc123...`

### **Database Setup:**

We use **PostgreSQL** with these key tables:
- `users` - Platform users
- `companies` - Multi-tenant companies (each company = 1 QuickBooks account)
- `customers` - Synced from QuickBooks
- `invoices` - Synced from QuickBooks
- `calls` - AI call records from VAPI

**All sensitive data encrypted** (QuickBooks tokens, passwords hashed)

---

## 🚀 Step-by-Step Setup (30 minutes)

### Step 1: Install Python & PostgreSQL (5 min)

**macOS:**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.10+
brew install python@3.10

# Install PostgreSQL
brew install postgresql@14
brew services start postgresql@14
```

**Ubuntu/Linux:**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
sudo apt install postgresql-14
sudo systemctl start postgresql
```

**Windows:**
- Download Python: https://www.python.org/downloads/
- Download PostgreSQL: https://www.postgresql.org/download/windows/

### Step 2: Create Database (2 min)

```bash
# Create database
createdb accounting_platform

# Or connect to PostgreSQL and create:
psql postgres
CREATE DATABASE accounting_platform;
\q
```

**Or use Docker (easiest):**
```bash
docker run --name postgres-dev \
  -e POSTGRES_PASSWORD=devpassword \
  -e POSTGRES_DB=accounting_platform \
  -p 5432:5432 \
  -d postgres:14
```

### Step 3: Set Up Project (5 min)

```bash
# Navigate to project
cd /workspace

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment (5 min)

```bash
# Copy example env file
cp .env.example .env

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output to .env as SECRET_KEY=

# Generate ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy output to .env as ENCRYPTION_KEY=

# Edit .env file
nano .env
```

**Minimal .env for testing:**
```bash
DATABASE_URL=postgresql://postgres:devpassword@localhost:5432/accounting_platform
SECRET_KEY=<your-generated-secret-key>
ENCRYPTION_KEY=<your-generated-encryption-key>

# QuickBooks (get from developer.intuit.com)
QUICKBOOKS_CLIENT_ID=your-client-id
QUICKBOOKS_CLIENT_SECRET=your-client-secret
QUICKBOOKS_REDIRECT_URI=http://localhost:8000/api/quickbooks/callback
QUICKBOOKS_ENVIRONMENT=sandbox

# VAPI (get from vapi.ai)
VAPI_API_KEY=your-vapi-key
VAPI_API_URL=https://api.vapi.ai

# Optional
CORS_ORIGINS=["http://localhost:3000"]
```

### Step 5: Run Database Migrations (3 min)

```bash
# Initialize Alembic
alembic init alembic

# Edit alembic.ini - find this line:
# sqlalchemy.url = driver://user:pass@localhost/dbname

# Replace with:
# sqlalchemy.url = postgresql://postgres:devpassword@localhost:5432/accounting_platform

# Or use environment variable (better):
# Comment out the line and edit alembic/env.py

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### Step 6: Start the Server (2 min)

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**You should see:**
```
🚀 Starting AI Accounting Platform
📝 Environment: development
📚 API Docs: http://0.0.0.0:8000/api/docs
✅ Database initialized
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 7: Test the API (8 min)

**Open browser:** http://localhost:8000/api/docs

**Test Sign Up:**
1. Expand `POST /api/auth/signup`
2. Click "Try it out"
3. Enter:
```json
{
  "email": "test@example.com",
  "password": "Test1234",
  "full_name": "Test User"
}
```
4. Click "Execute"
5. Copy the `access_token` from response

**Test Get User:**
1. Expand `GET /api/auth/me`
2. Click "Try it out"
3. Click 🔒 Authorize button at top
4. Paste token: `Bearer <your-token>`
5. Click "Execute"

**Success!** You should see your user data returned.

---

## 🔐 Authentication in Detail

### How JWT Works

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  1. User Signs Up                               │
│     POST /api/auth/signup                       │
│     { email, password, full_name }              │
│                                                 │
│  2. Backend:                                    │
│     - Hashes password with bcrypt               │
│     - Stores user in database                   │
│     - Generates JWT token                       │
│                                                 │
│  3. JWT Token Contains:                         │
│     {                                           │
│       "user_id": "uuid",                        │
│       "role": "user",                           │
│       "exp": 1735689600  // Expires in 15 min  │
│     }                                           │
│                                                 │
│  4. Client Stores Token                         │
│     localStorage.setItem('token', token)        │
│                                                 │
│  5. Client Makes Request:                       │
│     Authorization: Bearer <token>               │
│                                                 │
│  6. Backend Verifies:                           │
│     - Decodes JWT                               │
│     - Checks expiration                         │
│     - Loads user from database                  │
│     - Grants access                             │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Code Example (Python/JavaScript)

**Backend (FastAPI):**
```python
from app.utils.security import create_access_token

# After successful login:
token = create_access_token({
    "user_id": str(user.id),
    "role": user.role
})

return {"access_token": token}
```

**Frontend (JavaScript):**
```javascript
// Login
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({ email, password })
});

const { access_token } = await response.json();
localStorage.setItem('token', access_token);

// Make authenticated request
const userResponse = await fetch('http://localhost:8000/api/auth/me', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
});
```

**Bubble (No-Code):**
1. Install API Connector plugin
2. Add API: `POST http://localhost:8000/api/auth/login`
3. Store response `access_token` in User's data
4. Use token in subsequent API calls

---

## 🗄️ Database in Detail

### Connection String Format

```
postgresql://username:password@host:port/database_name

Examples:
postgresql://postgres:devpassword@localhost:5432/accounting_platform
postgresql://user:pass@db.example.com:5432/mydb
```

### Table Relationships

```
users
  ↓ (1:many)
company_users (join table)
  ↓ (many:1)
companies
  ↓ (1:many)
customers
  ↓ (1:many)
invoices
  ↓ (1:many)
calls
```

### Multi-Tenancy (Important!)

Each company has its own data isolated by `company_id`:

```python
# ALWAYS filter by company_id
invoices = db.query(Invoice).filter(
    Invoice.company_id == current_user.company_id
).all()

# NEVER do this (security risk):
invoices = db.query(Invoice).all()  # ❌ Returns ALL companies' data
```

### Encryption Strategy

**Passwords:**
```python
from passlib.context import CryptContext

# Hash password (one-way, cannot be decrypted)
hashed = pwd_context.hash("user_password")

# Verify password
is_valid = pwd_context.verify("user_password", hashed)
```

**QuickBooks Tokens:**
```python
from cryptography.fernet import Fernet

# Encrypt (two-way, can be decrypted)
encrypted = cipher.encrypt(token.encode()).decode()

# Decrypt
decrypted = cipher.decrypt(encrypted.encode()).decode()
```

---

## 🔗 QuickBooks OAuth Setup

### Step 1: Create QuickBooks App

1. Go to https://developer.intuit.com/
2. Sign up / Log in
3. Go to "My Apps" → "Create an app"
4. Choose "QuickBooks Online and Payments"
5. App Name: "AI Accounting Platform"
6. Scopes: Select "Accounting"

### Step 2: Get Credentials

1. Copy **Client ID**
2. Copy **Client Secret**
3. Add Redirect URI: `http://localhost:8000/api/quickbooks/callback`
4. For production: `https://yourapp.com/api/quickbooks/callback`

### Step 3: Add to .env

```bash
QUICKBOOKS_CLIENT_ID=ABcD1234EfGh5678IjKl
QUICKBOOKS_CLIENT_SECRET=abcdefghijklmnopqrstuvwxyz123456
QUICKBOOKS_REDIRECT_URI=http://localhost:8000/api/quickbooks/callback
QUICKBOOKS_ENVIRONMENT=sandbox
```

### Step 4: Test OAuth Flow

**Full flow** (will be implemented in Phase 2):

```
User clicks "Connect QuickBooks"
  ↓
GET /api/quickbooks/connect
  ↓
Redirect to: https://appcenter.intuit.com/connect/oauth2?
  client_id=xxx&
  scope=com.intuit.quickbooks.accounting&
  redirect_uri=http://localhost:8000/api/quickbooks/callback&
  state=random-csrf-token
  ↓
User approves on QuickBooks
  ↓
Redirect back to: /api/quickbooks/callback?code=xxx&realmId=xxx
  ↓
POST to QuickBooks: Exchange code for tokens
  ↓
Receive: access_token, refresh_token, expires_in
  ↓
Store encrypted in database:
  company.quickbooks_access_token = encrypt(access_token)
  company.quickbooks_refresh_token = encrypt(refresh_token)
  company.quickbooks_realm_id = realmId
  ↓
Start syncing invoices automatically
```

---

## 🛠️ Troubleshooting

### Database Connection Error

**Error:** `psycopg2.OperationalError: could not connect to server`

**Solutions:**
```bash
# Check if PostgreSQL is running
psql postgres

# Start PostgreSQL (macOS)
brew services start postgresql@14

# Start PostgreSQL (Linux)
sudo systemctl start postgresql

# Check connection string in .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/accounting_platform
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'app'`

**Solutions:**
```bash
# Make sure you're in the project root
cd /workspace

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Token Errors

**Error:** `Invalid authentication token`

**Solutions:**
- Check token is being sent: `Authorization: Bearer <token>`
- Token might be expired (15 minutes) - login again
- Check SECRET_KEY is same in .env

### QuickBooks OAuth Errors

**Error:** `Invalid redirect URI`

**Solutions:**
- Must match exactly in QuickBooks app settings
- Include protocol: `http://` not `https://` for local dev
- No trailing slash

---

## 📊 Database Hosting Options

### For Development (Free)

**Option 1: Local PostgreSQL**
- Pros: Fast, full control
- Cons: Only available on your machine

**Option 2: Docker**
```bash
docker run --name postgres \
  -e POSTGRES_PASSWORD=pass \
  -e POSTGRES_DB=accounting_platform \
  -p 5432:5432 \
  -d postgres:14
```

### For Production

**Supabase** (Recommended for MVP)
- Free tier: 500MB, 2GB bandwidth
- Includes: Auth, Storage, Real-time
- Setup: 5 minutes
- URL: https://supabase.com

**Neon** (Serverless PostgreSQL)
- Free tier: 3GB storage
- Auto-scaling
- URL: https://neon.tech

**Railway**
- $5 credit/month free
- Easy deployment
- URL: https://railway.app

**AWS RDS**
- 750 hours free (first 12 months)
- Enterprise-grade
- More complex setup

---

## ✅ Checklist Before Moving to Phase 2

- [ ] PostgreSQL installed and running
- [ ] Database `accounting_platform` created
- [ ] Virtual environment activated
- [ ] Dependencies installed (`requirements.txt`)
- [ ] `.env` file configured
- [ ] Server starts without errors
- [ ] Can sign up a new user
- [ ] Can login and get JWT token
- [ ] Can access `/api/auth/me` with token
- [ ] QuickBooks developer account created
- [ ] QuickBooks Client ID and Secret added to `.env`

**When all checked:** Ready for Phase 2 (QuickBooks Integration)! 🎉

---

## 🎓 Key Concepts to Understand

### 1. JWT (JSON Web Token)
- Self-contained token
- Contains user info (no database lookup needed)
- Has expiration time
- Signed with secret key (cannot be forged)

### 2. OAuth 2.0
- Authorization framework
- Allows apps to access QuickBooks without password
- Uses authorization code flow
- Tokens refresh automatically

### 3. Multi-Tenancy
- One database, multiple companies
- Data isolated by `company_id`
- Each company has own users
- ALWAYS filter by `company_id`

### 4. Encryption vs Hashing
- **Hashing** (passwords): One-way, cannot decrypt
- **Encryption** (OAuth tokens): Two-way, can decrypt

### 5. API Keys
- For machine-to-machine auth
- No user login needed
- Used by Bubble, N8n, VAPI
- Format: `sk_live_random32chars`

---

## 📞 Get Help

**Issue:** Something not working?
1. Check error logs in terminal
2. Check `.env` file configuration
3. Verify database is running: `psql postgres`
4. Check API docs: http://localhost:8000/api/docs

**Questions about:**
- Authentication → See `AUTH_AND_DB_GUIDE.md`
- Project structure → See `PROJECT_PLAN.md`
- API usage → See `README.md`

---

## 🚀 Next Phase

Once setup is complete, move to:

**Phase 2: QuickBooks Integration**
- Implement OAuth endpoints
- Sync invoices from QuickBooks
- Create webhook handlers
- Build priority scoring algorithm

Let me know when you're ready to proceed! 🎯
