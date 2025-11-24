# 🔐 Authentication & Database Architecture Guide

## Table of Contents
1. [Authentication Strategy Overview](#authentication-strategy)
2. [Database Setup](#database-setup)
3. [User Authentication (JWT)](#user-authentication)
4. [QuickBooks OAuth 2.0](#quickbooks-oauth)
5. [API Key Authentication](#api-key-authentication)
6. [Security Best Practices](#security-best-practices)
7. [Implementation Code](#implementation-code)

---

## 🎯 Authentication Strategy

We need **THREE types of authentication**:

### 1. **User Authentication** (For your platform users)
- **Method**: JWT (JSON Web Tokens)
- **Flow**: Email/Password → JWT Token → Access platform
- **Used by**: Companies using your dashboard

### 2. **QuickBooks OAuth 2.0** (For QuickBooks integration)
- **Method**: OAuth 2.0 with Intuit
- **Flow**: User clicks "Connect QuickBooks" → OAuth → Store tokens
- **Used by**: Your backend to access QuickBooks data

### 3. **API Key Authentication** (For Bubble, N8n, VAPI webhooks)
- **Method**: API Keys / Bearer tokens
- **Flow**: External services send API key in headers
- **Used by**: N8n workflows, VAPI webhooks, Bubble frontend

---

## 🗄️ Database Setup

### **Recommended Stack:**
- **Database**: PostgreSQL 14+ (best for JSONB, full-text search, scalability)
- **ORM**: SQLAlchemy (Python) or Prisma (Node.js)
- **Migrations**: Alembic (Python) or Prisma Migrate
- **Hosting Options**:
  - **Development**: Local PostgreSQL
  - **Production**: AWS RDS, Supabase, Neon, or Render

### **Why PostgreSQL?**
✅ JSONB for flexible QuickBooks data storage  
✅ Row-level security for multi-tenancy  
✅ Full-text search for invoices/customers  
✅ Excellent performance with proper indexing  
✅ Free tier available on most platforms  

---

## 📊 Complete Database Schema

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user', -- admin, user, viewer
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- ============================================
-- COMPANIES (Multi-tenant)
-- ============================================

CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    owner_id UUID REFERENCES users(id),
    
    -- QuickBooks Integration
    quickbooks_realm_id VARCHAR(255) UNIQUE,
    quickbooks_access_token TEXT, -- Encrypted
    quickbooks_refresh_token TEXT, -- Encrypted
    quickbooks_token_expires_at TIMESTAMP,
    quickbooks_connected BOOLEAN DEFAULT FALSE,
    quickbooks_last_sync TIMESTAMP,
    
    -- Settings
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    business_hours_start TIME DEFAULT '09:00:00',
    business_hours_end TIME DEFAULT '17:00:00',
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_companies_realm_id ON companies(quickbooks_realm_id);
CREATE INDEX idx_companies_owner ON companies(owner_id);

-- ============================================
-- COMPANY USERS (Many-to-Many)
-- ============================================

CREATE TABLE company_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member', -- owner, admin, member, viewer
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, user_id)
);

CREATE INDEX idx_company_users_company ON company_users(company_id);
CREATE INDEX idx_company_users_user ON company_users(user_id);

-- ============================================
-- CUSTOMERS
-- ============================================

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    -- QuickBooks Data
    quickbooks_customer_id VARCHAR(255),
    sync_token VARCHAR(50), -- For QB updates
    
    -- Contact Info
    display_name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    mobile VARCHAR(50),
    
    -- Address
    billing_address JSONB,
    
    -- Preferences
    preferred_contact_method VARCHAR(50) DEFAULT 'phone', -- phone, email, sms
    do_not_call BOOLEAN DEFAULT FALSE,
    do_not_email BOOLEAN DEFAULT FALSE,
    notes TEXT,
    
    -- Metadata
    quickbooks_data JSONB, -- Full QB customer object
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_synced_at TIMESTAMP,
    
    UNIQUE(company_id, quickbooks_customer_id)
);

CREATE INDEX idx_customers_company ON customers(company_id);
CREATE INDEX idx_customers_qb_id ON customers(quickbooks_customer_id);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone);

-- ============================================
-- INVOICES
-- ============================================

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    
    -- QuickBooks Data
    quickbooks_invoice_id VARCHAR(255),
    sync_token VARCHAR(50),
    doc_number VARCHAR(100), -- Invoice number
    
    -- Financial
    total_amount DECIMAL(12, 2) NOT NULL,
    balance DECIMAL(12, 2) NOT NULL, -- Amount still owed
    
    -- Dates
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    
    -- Status
    status VARCHAR(50) DEFAULT 'open', -- open, paid, partially_paid, overdue, voided
    quickbooks_status VARCHAR(50), -- QB's status
    
    -- AI Follow-up
    priority_score INTEGER DEFAULT 0,
    last_call_date TIMESTAMP,
    next_follow_up_date TIMESTAMP,
    follow_up_count INTEGER DEFAULT 0,
    
    -- Metadata
    line_items JSONB, -- Invoice line items
    quickbooks_data JSONB, -- Full QB invoice object
    internal_notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_synced_at TIMESTAMP,
    
    UNIQUE(company_id, quickbooks_invoice_id)
);

CREATE INDEX idx_invoices_company ON invoices(company_id);
CREATE INDEX idx_invoices_customer ON invoices(customer_id);
CREATE INDEX idx_invoices_qb_id ON invoices(quickbooks_invoice_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_due_date ON invoices(due_date);
CREATE INDEX idx_invoices_balance ON invoices(balance);
CREATE INDEX idx_invoices_priority ON invoices(priority_score DESC);

-- ============================================
-- CALLS (VAPI Integration)
-- ============================================

CREATE TABLE calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    
    -- VAPI Data
    vapi_call_id VARCHAR(255) UNIQUE,
    vapi_assistant_id VARCHAR(255),
    
    -- Call Details
    phone_number VARCHAR(50),
    direction VARCHAR(20) DEFAULT 'outbound', -- outbound, inbound
    status VARCHAR(50), -- queued, ringing, in-progress, completed, failed
    
    -- Timing
    initiated_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Outcome
    call_outcome VARCHAR(50), -- answered, no_answer, voicemail, busy, promise_to_pay, dispute, refused
    customer_response TEXT, -- What customer said
    sentiment VARCHAR(50), -- positive, neutral, negative
    
    -- Content
    transcript TEXT,
    transcript_json JSONB, -- Structured transcript
    recording_url TEXT,
    summary TEXT, -- AI-generated summary
    
    -- Follow-up
    payment_promised BOOLEAN DEFAULT FALSE,
    payment_promise_date DATE,
    payment_promise_amount DECIMAL(12, 2),
    dispute_raised BOOLEAN DEFAULT FALSE,
    dispute_reason TEXT,
    requires_human_follow_up BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    vapi_metadata JSONB,
    cost DECIMAL(8, 4), -- Call cost in USD
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_calls_company ON calls(company_id);
CREATE INDEX idx_calls_invoice ON calls(invoice_id);
CREATE INDEX idx_calls_customer ON calls(customer_id);
CREATE INDEX idx_calls_vapi_id ON calls(vapi_call_id);
CREATE INDEX idx_calls_status ON calls(status);
CREATE INDEX idx_calls_outcome ON calls(call_outcome);
CREATE INDEX idx_calls_initiated ON calls(initiated_at DESC);

-- ============================================
-- FOLLOW-UP RULES
-- ============================================

CREATE TABLE follow_up_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0, -- Higher = evaluated first
    
    -- Trigger Conditions (JSON logic)
    conditions JSONB NOT NULL,
    /* Example:
    {
        "days_overdue": {"min": 7, "max": 30},
        "amount_due": {"min": 100},
        "previous_calls": {"max": 3},
        "last_call_days_ago": {"min": 7}
    }
    */
    
    -- Action to take
    action_type VARCHAR(50) NOT NULL, -- call, email, sms, notify_admin
    
    -- Call Settings
    call_script_template TEXT,
    vapi_assistant_id VARCHAR(255),
    
    -- Frequency
    max_calls_per_period INTEGER DEFAULT 3,
    period_days INTEGER DEFAULT 30,
    min_days_between_calls INTEGER DEFAULT 7,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_follow_up_rules_company ON follow_up_rules(company_id);
CREATE INDEX idx_follow_up_rules_active ON follow_up_rules(is_active);

-- ============================================
-- API KEYS (For external integrations)
-- ============================================

CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE, -- Hashed API key
    key_prefix VARCHAR(10), -- First few chars for identification (e.g., "sk_live_")
    
    -- Permissions
    scopes JSONB DEFAULT '["read"]', -- ["read", "write", "admin"]
    
    -- Usage
    last_used_at TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    revoked_at TIMESTAMP
);

CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_company ON api_keys(company_id);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);

-- ============================================
-- AUDIT LOGS
-- ============================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    action VARCHAR(100) NOT NULL, -- login, invoice_synced, call_made, etc.
    entity_type VARCHAR(50), -- invoice, customer, call
    entity_id UUID,
    
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_company ON audit_logs(company_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);

-- ============================================
-- WEBHOOK LOGS
-- ============================================

CREATE TABLE webhook_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    source VARCHAR(50) NOT NULL, -- quickbooks, vapi, n8n
    event_type VARCHAR(100),
    
    payload JSONB,
    headers JSONB,
    
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    error TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_webhook_logs_source ON webhook_logs(source);
CREATE INDEX idx_webhook_logs_processed ON webhook_logs(processed);
CREATE INDEX idx_webhook_logs_created ON webhook_logs(created_at DESC);

-- ============================================
-- SYNC JOBS (Track QuickBooks sync status)
-- ============================================

CREATE TABLE sync_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    job_type VARCHAR(50) NOT NULL, -- full_sync, incremental_sync
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed
    
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Statistics
    entities_synced INTEGER DEFAULT 0,
    entities_created INTEGER DEFAULT 0,
    entities_updated INTEGER DEFAULT 0,
    entities_failed INTEGER DEFAULT 0,
    
    error TEXT,
    metadata JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sync_jobs_company ON sync_jobs(company_id);
CREATE INDEX idx_sync_jobs_status ON sync_jobs(status);
CREATE INDEX idx_sync_jobs_created ON sync_jobs(created_at DESC);
```

---

## 🔐 User Authentication (JWT)

### **How it Works:**

```
1. User signs up → Password hashed with bcrypt → Store in DB
2. User logs in → Verify password → Generate JWT token
3. User makes request → Send JWT in Authorization header
4. Backend verifies JWT → Allow access
```

### **JWT Token Structure:**

```json
{
  "user_id": "uuid-here",
  "company_id": "uuid-here",
  "role": "admin",
  "exp": 1735689600,
  "iat": 1735603200
}
```

### **Token Expiration:**
- **Access Token**: 15 minutes (short-lived)
- **Refresh Token**: 30 days (long-lived, stored in httpOnly cookie)

---

## 🔗 QuickBooks OAuth 2.0 Flow

### **Step-by-Step Process:**

```
Step 1: User clicks "Connect QuickBooks"
   ↓
Step 2: Redirect to Intuit authorization page
   URL: https://appcenter.intuit.com/connect/oauth2
   Params: client_id, scope, redirect_uri, state
   ↓
Step 3: User approves access
   ↓
Step 4: Intuit redirects back with authorization code
   Callback: https://yourapp.com/api/quickbooks/callback?code=xxx&realmId=xxx
   ↓
Step 5: Exchange code for tokens
   POST to: https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer
   Get: access_token, refresh_token, expires_in
   ↓
Step 6: Encrypt & store tokens in database
   ↓
Step 7: Use access_token for API calls
```

### **Token Refresh (Every 60 days):**

```python
# When access token expires (after 1 hour):
def refresh_quickbooks_token(company_id):
    company = db.get_company(company_id)
    
    response = requests.post(
        'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'grant_type': 'refresh_token',
            'refresh_token': decrypt(company.quickbooks_refresh_token)
        },
        auth=(QB_CLIENT_ID, QB_CLIENT_SECRET)
    )
    
    tokens = response.json()
    
    # Update database
    company.quickbooks_access_token = encrypt(tokens['access_token'])
    company.quickbooks_refresh_token = encrypt(tokens['refresh_token'])
    company.quickbooks_token_expires_at = datetime.now() + timedelta(seconds=tokens['expires_in'])
    db.commit()
```

### **Important: Store QuickBooks Tokens ENCRYPTED**

```python
from cryptography.fernet import Fernet

# Generate key once, store in environment variable
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_token(token: str) -> str:
    return cipher.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    return cipher.decrypt(encrypted_token.encode()).decode()
```

---

## 🔑 API Key Authentication (For Bubble, N8n, VAPI)

### **Why API Keys?**
- Bubble frontend needs to call your backend
- N8n workflows need to trigger actions
- VAPI needs to send webhook callbacks

### **API Key Format:**
```
sk_live_abc123def456... (32 characters)
```

### **Generation & Storage:**

```python
import secrets
import hashlib

def generate_api_key(company_id, user_id, name):
    # Generate random key
    key = f"sk_live_{secrets.token_urlsafe(32)}"
    
    # Hash for storage (like passwords)
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    
    # Store in DB
    api_key = APIKey(
        company_id=company_id,
        user_id=user_id,
        name=name,
        key_hash=key_hash,
        key_prefix=key[:10],  # For display only
        scopes=["read", "write"]
    )
    db.add(api_key)
    db.commit()
    
    # Return key ONCE (never show again)
    return key
```

### **Validation:**

```python
def validate_api_key(key: str):
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    api_key = db.query(APIKey).filter(
        APIKey.key_hash == key_hash,
        APIKey.is_active == True
    ).first()
    
    if not api_key:
        raise Unauthorized("Invalid API key")
    
    # Update usage stats
    api_key.last_used_at = datetime.now()
    api_key.usage_count += 1
    db.commit()
    
    return api_key
```

---

## 🛡️ Security Best Practices

### **1. Password Security**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash("user_password")

# Verify password
is_valid = pwd_context.verify("user_password", hashed)
```

### **2. Environment Variables (NEVER hardcode)**
```bash
# .env file (NEVER commit to git)
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-super-secret-jwt-key-here
ENCRYPTION_KEY=your-fernet-encryption-key-here
QUICKBOOKS_CLIENT_ID=your-qb-client-id
QUICKBOOKS_CLIENT_SECRET=your-qb-client-secret
VAPI_API_KEY=your-vapi-key
```

### **3. SQL Injection Prevention**
```python
# ✅ GOOD (Parameterized query)
user = db.query(User).filter(User.email == email).first()

# ❌ BAD (String concatenation)
user = db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### **4. Rate Limiting**
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")  # Max 5 attempts per minute
async def login(credentials: LoginSchema):
    # ...
```

### **5. CORS Configuration**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourbubbleapp.com"],  # Specific domains only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### **6. Multi-Tenancy Security**
```python
# ALWAYS filter by company_id
def get_invoices(company_id: str, user: User):
    # Verify user belongs to company
    if not user_has_access(user.id, company_id):
        raise Forbidden("Access denied")
    
    return db.query(Invoice).filter(
        Invoice.company_id == company_id
    ).all()
```

---

## 💻 Implementation Code

### **Database Setup Script**

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### **User Model Example**

```python
# models/user.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
```

### **JWT Authentication**

```python
# auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise JWTError("Invalid token")
        return payload
    except JWTError:
        raise JWTError("Could not validate credentials")
```

### **QuickBooks OAuth Implementation**

```python
# services/quickbooks_auth.py
import requests
from urllib.parse import urlencode
import os

QB_CLIENT_ID = os.getenv("QUICKBOOKS_CLIENT_ID")
QB_CLIENT_SECRET = os.getenv("QUICKBOOKS_CLIENT_SECRET")
QB_REDIRECT_URI = os.getenv("QUICKBOOKS_REDIRECT_URI")
QB_ENVIRONMENT = os.getenv("QB_ENVIRONMENT", "sandbox")  # or "production"

def get_authorization_url(state: str):
    """Generate QuickBooks OAuth URL"""
    base_url = "https://appcenter.intuit.com/connect/oauth2"
    params = {
        "client_id": QB_CLIENT_ID,
        "response_type": "code",
        "scope": "com.intuit.quickbooks.accounting",
        "redirect_uri": QB_REDIRECT_URI,
        "state": state  # CSRF protection
    }
    return f"{base_url}?{urlencode(params)}"

def exchange_code_for_tokens(code: str):
    """Exchange authorization code for access/refresh tokens"""
    token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    
    response = requests.post(
        token_url,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": QB_REDIRECT_URI
        },
        auth=(QB_CLIENT_ID, QB_CLIENT_SECRET)
    )
    
    if response.status_code != 200:
        raise Exception(f"Token exchange failed: {response.text}")
    
    return response.json()

def refresh_access_token(refresh_token: str):
    """Refresh expired access token"""
    token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    
    response = requests.post(
        token_url,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        },
        auth=(QB_CLIENT_ID, QB_CLIENT_SECRET)
    )
    
    if response.status_code != 200:
        raise Exception(f"Token refresh failed: {response.text}")
    
    return response.json()
```

### **FastAPI Endpoint Examples**

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from auth import create_access_token, verify_password, get_password_hash, verify_token
from models.user import User
from pydantic import BaseModel

app = FastAPI()
security = HTTPBearer()

# ============================================
# SCHEMAS
# ============================================

class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ============================================
# DEPENDENCY: Get current user from JWT
# ============================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = verify_token(token)
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")

# ============================================
# AUTH ENDPOINTS
# ============================================

@app.post("/api/auth/signup", response_model=TokenResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        full_name=request.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate token
    token = create_access_token({"user_id": str(user.id), "role": user.role})
    return {"access_token": token}

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Generate token
    token = create_access_token({"user_id": str(user.id), "role": user.role})
    return {"access_token": token}

@app.get("/api/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role
    }

# ============================================
# QUICKBOOKS OAUTH ENDPOINTS
# ============================================

from services.quickbooks_auth import get_authorization_url, exchange_code_for_tokens
from utils.encryption import encrypt_token, decrypt_token
import secrets

@app.get("/api/quickbooks/connect")
async def connect_quickbooks(
    company_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Generate CSRF state token
    state = secrets.token_urlsafe(32)
    
    # Store state in session or DB for verification
    # ... (implementation depends on your session management)
    
    auth_url = get_authorization_url(state)
    return {"authorization_url": auth_url}

@app.get("/api/quickbooks/callback")
async def quickbooks_callback(
    code: str,
    realmId: str,
    state: str,
    db: Session = Depends(get_db)
):
    # Verify state token (CSRF protection)
    # ...
    
    # Exchange code for tokens
    tokens = exchange_code_for_tokens(code)
    
    # Find or create company
    company = db.query(Company).filter(Company.quickbooks_realm_id == realmId).first()
    
    if not company:
        company = Company(quickbooks_realm_id=realmId)
        db.add(company)
    
    # Store encrypted tokens
    company.quickbooks_access_token = encrypt_token(tokens["access_token"])
    company.quickbooks_refresh_token = encrypt_token(tokens["refresh_token"])
    company.quickbooks_token_expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
    company.quickbooks_connected = True
    
    db.commit()
    
    return {"success": True, "company_id": str(company.id)}
```

---

## 🗄️ Database Hosting Options

### **Development:**
```bash
# Local PostgreSQL (Docker)
docker run --name postgres-dev \
  -e POSTGRES_PASSWORD=devpassword \
  -e POSTGRES_DB=accounting_platform \
  -p 5432:5432 \
  -d postgres:14
```

### **Production Options:**

| Provider | Free Tier | Paid Plan | Pros |
|----------|-----------|-----------|------|
| **Supabase** | 500MB, 2GB bandwidth | $25/month | Easy setup, includes auth |
| **Neon** | 3GB storage | $19/month | Serverless, auto-scaling |
| **Railway** | $5 credit/month | Pay as you go | Simple deployment |
| **AWS RDS** | 750 hours free (12mo) | $15+/month | Enterprise-grade |
| **Render** | None | $7/month | Easy setup |

**Recommendation for MVP**: **Supabase** or **Neon** (easiest to start)

---

## 📝 Next Steps

1. **Choose database hosting** (Supabase recommended)
2. **Set up PostgreSQL database**
3. **Run schema SQL script**
4. **Implement authentication endpoints**
5. **Test QuickBooks OAuth flow**
6. **Generate API keys for Bubble/N8n**

Let me know if you want me to:
- Generate the complete FastAPI backend code
- Set up database migrations with Alembic
- Create environment variable templates
- Build the authentication system
