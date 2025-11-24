# 🚀 Quick Start - FastAPI Server is Running!

## ✅ Server Status: **RUNNING**

Your FastAPI backend is now live and working!

- **Server URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/health

---

## 🎯 What's Working

### ✅ Authentication Endpoints

#### 1. User Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "YourPass123",
    "full_name": "Your Name"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### 2. User Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "Demo1234"
  }'
```

#### 3. Get Current User
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response:**
```json
{
  "id": "a94c7757-9464-4cb8-b144-a9b3ababde1d",
  "email": "demo@example.com",
  "full_name": "Demo User",
  "role": "user",
  "is_active": true,
  "email_verified": false,
  "created_at": "2025-11-24T15:34:35.450913",
  "last_login_at": null
}
```

---

## 📊 Database

- **Type**: SQLite (for development)
- **File**: `/workspace/accounting_platform.db`
- **Tables Created**:
  - ✅ users
  - ✅ companies
  - ✅ company_users
  - ✅ customers
  - ✅ invoices
  - ✅ calls
  - ✅ api_keys

---

## 🔍 Interactive API Documentation

### Swagger UI
Open in your browser: **http://localhost:8000/api/docs**

Here you can:
- See all available endpoints
- Test API calls directly
- View request/response schemas
- Authorize with JWT tokens

### ReDoc
Alternative documentation: **http://localhost:8000/api/redoc**

---

## 🧪 Test It Out!

### 1. Sign Up a New User

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234",
    "full_name": "Test User"
  }'
```

### 2. Save the Token

Copy the `access_token` from the response.

### 3. Get User Info

```bash
TOKEN="paste_your_token_here"

curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📁 Project Structure

```
/workspace/
├── app/
│   ├── main.py              # ✅ FastAPI app (RUNNING)
│   ├── config.py            # ✅ Environment configuration
│   ├── database.py          # ✅ Database connection
│   ├── models/              # ✅ Database models
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── customer.py
│   │   ├── invoice.py
│   │   ├── call.py
│   │   └── api_key.py
│   ├── schemas/             # ✅ Pydantic schemas
│   │   └── auth.py
│   └── utils/               # ✅ Helper functions
│       └── security.py
├── .env                     # ✅ Environment variables
├── requirements.txt         # ✅ Dependencies
├── accounting_platform.db   # ✅ SQLite database
└── *.md                     # Documentation
```

---

## 🎨 Using with Bubble (No-Code Frontend)

### Step 1: Add API in Bubble

1. Go to Bubble Editor → Plugins → Add Plugins
2. Search for "API Connector" and install it
3. Add a new API

### Step 2: Configure Authentication API

**Name**: AI Accounting API

**Signup Endpoint:**
- Method: POST
- URL: `http://localhost:8000/api/auth/signup`
- Body type: JSON
- Body:
```json
{
  "email": "<email>",
  "password": "<password>",
  "full_name": "<full_name>"
}
```

**Login Endpoint:**
- Method: POST
- URL: `http://localhost:8000/api/auth/login`
- Body type: JSON
- Body:
```json
{
  "email": "<email>",
  "password": "<password>"
}
```

**Get User Endpoint:**
- Method: GET
- URL: `http://localhost:8000/api/auth/me`
- Headers:
  - Authorization: `Bearer <token>`

### Step 3: Store Token in Bubble

After login, store the `access_token` in the user's custom state or database field.

---

## 🔧 Troubleshooting

### Server Not Running?

Check if it's running:
```bash
curl http://localhost:8000/api/health
```

If not, restart it:
```bash
cd /workspace
export PATH="/home/ubuntu/.local/bin:$PATH"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Port Already in Use?

Kill existing processes:
```bash
pkill -9 -f uvicorn
```

### Database Issues?

Reset database:
```bash
cd /workspace
rm -f accounting_platform.db
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Can't Install Dependencies?

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

---

## 🚀 Next Steps

### Phase 2: QuickBooks Integration

Now that the backend is running, you can:

1. **Get QuickBooks Credentials**
   - Go to https://developer.intuit.com
   - Create an app
   - Get Client ID and Secret
   - Add to `.env` file

2. **Implement OAuth Endpoints**
   - `/api/quickbooks/connect`
   - `/api/quickbooks/callback`
   - `/api/quickbooks/sync`

3. **Sync Invoices**
   - Pull invoices from QuickBooks
   - Store in database
   - Calculate priority scores

4. **Set Up N8n Workflows**
   - Install N8n
   - Create workflows for automation
   - Connect to your backend

5. **Configure VAPI**
   - Get VAPI API key
   - Set up voice assistant
   - Create call scripts

---

## 📖 Documentation

- **Full Plan**: `PROJECT_PLAN.md`
- **Authentication Guide**: `AUTH_AND_DB_GUIDE.md`
- **Setup Instructions**: `SETUP_GUIDE.md`
- **This Guide**: `QUICK_START.md`
- **API Docs**: http://localhost:8000/api/docs

---

## 💡 Tips

### Using JWT Tokens

Tokens expire after 15 minutes. Use the refresh token to get a new one.

### Testing in Browser

1. Open http://localhost:8000/api/docs
2. Click "Try it out" on any endpoint
3. Click the 🔒 lock icon to add your token
4. Execute the request

### Using Postman

Import collection from API docs:
1. Go to http://localhost:8000/openapi.json
2. Copy the JSON
3. Import in Postman

---

## ✅ Current Status

**Phase 1: COMPLETE ✅**
- ✅ Project structure set up
- ✅ Database models defined
- ✅ Authentication working
- ✅ JWT tokens working
- ✅ API documentation available
- ✅ Server running successfully

**Next: Phase 2 - QuickBooks Integration**

---

## 🎯 Quick Commands Reference

```bash
# Start server
cd /workspace && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start server with auto-reload (for development)
cd /workspace && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Stop server
pkill -f uvicorn

# Check if running
curl http://localhost:8000/api/health

# View logs (if running in background)
tail -f /home/ubuntu/.cursor/projects/workspace/terminals/*.txt

# Reset database
rm -f /workspace/accounting_platform.db
```

---

## 🎉 Congratulations!

Your AI Accounting Platform backend is up and running! You now have:

- ✅ Working authentication system
- ✅ Database with all required tables
- ✅ JWT token-based security
- ✅ API documentation
- ✅ Foundation for QuickBooks integration
- ✅ Ready for N8n workflows
- ✅ Prepared for VAPI AI voice calls

**Ready to move to Phase 2!** 🚀
