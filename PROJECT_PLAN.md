# AI B2B Accounting Platform - Development Plan

## 🎯 Project Overview

**Client Requirements:** AI-driven B2B SaaS platform for automated accounts receivable follow-up with QuickBooks integration and AI voice calling capabilities.

---

## 📊 System Architecture

### **Component Stack:**

```
┌─────────────────────────────────────────────────────────┐
│                   BUBBLE FRONTEND                        │
│  (Dashboard, Invoice Management, Call History, Reports)  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                 BACKEND API (Python/Node)                │
│     (Authentication, Business Logic, Data Layer)         │
└─────────────────────────────────────────────────────────┘
          ↓                    ↓                    ↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   QUICKBOOKS     │  │   N8N WORKFLOWS   │  │   VAPI AI VOICE  │
│      API         │  │   (Automation)    │  │   (Phone Calls)  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## 🚀 Phase-by-Phase Implementation

### **PHASE 1: Project Setup & Architecture** (Week 1)

#### Deliverables:
- [ ] Project repository structure
- [ ] Database schema design (PostgreSQL recommended)
- [ ] Environment configuration
- [ ] API documentation framework (Swagger/OpenAPI)
- [ ] Development environment setup guide

#### Tech Stack Decisions:
- **Backend**: Python (FastAPI) or Node.js (Express)
- **Database**: PostgreSQL with TimescaleDB for time-series data
- **Authentication**: JWT with OAuth2 for QuickBooks
- **Hosting**: AWS/GCP/Heroku

#### Data Models:
```
- Users (multi-tenant)
- Companies (linked to QuickBooks)
- Invoices (synced from QuickBooks)
- Customers (from QuickBooks)
- Calls (VAPI call records)
- FollowUpRules (AI decision logic)
- PaymentReminders (scheduled/completed)
```

---

### **PHASE 2: QuickBooks Integration** (Week 2-3)

#### Key Components:

**2.1 OAuth2 Authentication**
- [ ] Implement QuickBooks OAuth2 flow
- [ ] Store and refresh access tokens securely
- [ ] Handle token expiration and renewal

**2.2 QuickBooks API Wrapper**
- [ ] Fetch open invoices (Query API)
- [ ] Get customer information
- [ ] Retrieve invoice details (amount, due date, aging)
- [ ] Webhook integration for real-time updates
- [ ] Error handling and rate limiting

**2.3 Data Sync Module**
- [ ] Initial sync of all open invoices
- [ ] Incremental sync (every hour)
- [ ] Data transformation and normalization
- [ ] Conflict resolution

#### API Endpoints:
```
POST   /api/quickbooks/connect      - Initiate OAuth
GET    /api/quickbooks/callback     - OAuth callback
POST   /api/quickbooks/sync         - Manual sync trigger
GET    /api/quickbooks/status       - Connection status
GET    /api/invoices                - List all invoices
GET    /api/invoices/:id            - Get invoice details
```

---

### **PHASE 3: Backend API Development** (Week 3-4)

#### Core Features:

**3.1 User Management**
- [ ] Multi-tenant user authentication
- [ ] Role-based access control (Admin, User, Viewer)
- [ ] Company/workspace management
- [ ] API key generation for integrations

**3.2 Invoice Management**
- [ ] Invoice listing with filters (overdue, aging, amount)
- [ ] Invoice detail views
- [ ] Manual status updates
- [ ] Payment recording

**3.3 Call Scheduling Logic**
- [ ] Follow-up rules engine
  - Days overdue thresholds (7, 14, 30, 60 days)
  - Amount thresholds (>$100, >$1000, >$10000)
  - Call frequency limits (max 1 per week per customer)
- [ ] Priority scoring algorithm
- [ ] Call queue management

**3.4 Analytics & Reporting**
- [ ] Dashboard metrics (total AR, overdue amount, success rate)
- [ ] Call effectiveness tracking
- [ ] Payment conversion metrics

---

### **PHASE 4: N8n Workflow Automation** (Week 4-5)

#### Workflows to Build:

**4.1 Invoice Monitoring Workflow**
```
Trigger: Cron (every 4 hours)
  ↓
Fetch new/updated invoices from QuickBooks
  ↓
Calculate days overdue & priority score
  ↓
Update internal database
  ↓
Trigger alerts for critical invoices
```

**4.2 Payment Detection Workflow**
```
Trigger: QuickBooks webhook (payment received)
  ↓
Update invoice status
  ↓
Cancel scheduled follow-up calls
  ↓
Send success notification
```

**4.3 AI Call Trigger Workflow**
```
Trigger: Cron (daily at 9 AM local time)
  ↓
Query invoices meeting follow-up criteria
  ↓
Check customer contact preferences
  ↓
Generate personalized call script
  ↓
Schedule VAPI call
  ↓
Log call attempt
```

**4.4 Call Follow-up Workflow**
```
Trigger: VAPI call completed webhook
  ↓
Extract call outcome (promise to pay, dispute, no answer)
  ↓
Update invoice notes
  ↓
Schedule next follow-up if needed
  ↓
Notify account manager if escalation required
```

---

### **PHASE 5: VAPI AI Voice Integration** (Week 5-6)

#### Implementation Steps:

**5.1 VAPI Configuration**
- [ ] Create VAPI account and API keys
- [ ] Configure voice agents (male/female options)
- [ ] Set up phone numbers (Twilio integration)
- [ ] Define call parameters (max duration, retry logic)

**5.2 Dynamic Call Script Generation**
- [ ] Template system for different scenarios:
  - First reminder (friendly)
  - Second reminder (firm)
  - Final notice (urgent)
- [ ] Personalization variables:
  - Customer name
  - Invoice number
  - Amount owed
  - Due date
  - Days overdue
  - Payment methods available

**5.3 AI Agent Training**
- [ ] Define conversational flows
- [ ] Handle common responses:
  - "I'll pay today"
  - "I have a dispute"
  - "I need more time"
  - "I already paid"
- [ ] Escalation paths (transfer to human)
- [ ] Sentiment analysis

**5.4 Call Recording & Transcription**
- [ ] Store call recordings
- [ ] Automatic transcription
- [ ] Extract key information (payment promises, disputes)
- [ ] Compliance & consent handling

#### VAPI Integration Code:
```python
# Example call initiation
def initiate_payment_reminder_call(invoice, customer):
    call_data = {
        "phone_number": customer.phone,
        "assistant_id": VAPI_ASSISTANT_ID,
        "variables": {
            "customer_name": customer.name,
            "invoice_number": invoice.number,
            "amount_due": f"${invoice.amount_due:.2f}",
            "due_date": invoice.due_date.strftime("%B %d, %Y"),
            "days_overdue": (datetime.now() - invoice.due_date).days
        }
    }
    response = vapi_client.calls.create(call_data)
    return response
```

---

### **PHASE 6: Bubble Frontend Development** (Week 6-8)

#### Pages & Features:

**6.1 Authentication Pages**
- [ ] Login page
- [ ] Registration page
- [ ] Password reset
- [ ] QuickBooks connection page

**6.2 Dashboard (Home)**
- [ ] Key metrics cards:
  - Total outstanding AR
  - Overdue amount
  - Calls made this week
  - Payment conversion rate
- [ ] Recent activity feed
- [ ] Quick actions (sync QuickBooks, make test call)

**6.3 Invoices Page**
- [ ] Data table with filtering/sorting:
  - Customer name
  - Invoice number
  - Amount
  - Due date
  - Days overdue
  - Status
  - Last call date
- [ ] Bulk actions (mark paid, schedule call)
- [ ] Export to CSV

**6.4 Invoice Detail Page**
- [ ] Full invoice information
- [ ] Customer contact details
- [ ] Payment history timeline
- [ ] Call history with transcripts
- [ ] Manual call trigger button
- [ ] Add notes

**6.5 Call History Page**
- [ ] List of all calls made
- [ ] Filter by outcome, date, customer
- [ ] Play call recordings
- [ ] View transcripts
- [ ] Call analytics

**6.6 Settings Page**
- [ ] QuickBooks connection management
- [ ] Follow-up rules configuration:
  - Overdue thresholds
  - Call frequency
  - Business hours
  - Blackout dates
- [ ] Call script templates
- [ ] VAPI voice selection
- [ ] User management
- [ ] Notification preferences

**6.7 Reports Page**
- [ ] Aging report (30/60/90 days)
- [ ] Call effectiveness metrics
- [ ] Payment trends
- [ ] Customer response patterns
- [ ] Download PDF reports

#### Bubble-Backend Integration:
- API Connector plugin for backend endpoints
- Webhook configuration for real-time updates
- Data type definitions matching backend models

---

### **PHASE 7: Testing & Deployment** (Week 8-9)

#### Testing Checklist:

**7.1 Unit Testing**
- [ ] QuickBooks API wrapper tests
- [ ] Business logic tests
- [ ] Call scheduling algorithm tests

**7.2 Integration Testing**
- [ ] End-to-end invoice sync flow
- [ ] Call trigger to VAPI integration
- [ ] Payment detection flow
- [ ] N8n workflow testing

**7.3 User Acceptance Testing**
- [ ] Create test QuickBooks company
- [ ] Simulate invoice scenarios
- [ ] Test call flows with real phone numbers
- [ ] Verify data accuracy

**7.4 Security Testing**
- [ ] OAuth token security
- [ ] API authentication
- [ ] Data encryption at rest/transit
- [ ] GDPR compliance review

**7.5 Performance Testing**
- [ ] Load testing (1000+ invoices)
- [ ] Concurrent call handling
- [ ] API response times
- [ ] Database query optimization

**7.6 Deployment**
- [ ] Set up production environment
- [ ] Configure DNS and SSL
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Create backup strategy
- [ ] Deploy backend API
- [ ] Deploy N8n workflows
- [ ] Configure VAPI production credentials
- [ ] Launch Bubble frontend

---

## 💾 Database Schema (Key Tables)

### Companies
```sql
- id (uuid)
- name (text)
- quickbooks_realm_id (text)
- quickbooks_access_token (encrypted)
- quickbooks_refresh_token (encrypted)
- token_expires_at (timestamp)
- created_at (timestamp)
```

### Invoices
```sql
- id (uuid)
- company_id (uuid FK)
- quickbooks_invoice_id (text)
- invoice_number (text)
- customer_id (uuid FK)
- amount (decimal)
- amount_paid (decimal)
- amount_due (decimal)
- due_date (date)
- status (enum: open, paid, overdue)
- last_synced_at (timestamp)
```

### Customers
```sql
- id (uuid)
- company_id (uuid FK)
- quickbooks_customer_id (text)
- name (text)
- email (text)
- phone (text)
- preferred_contact_method (enum)
- do_not_call (boolean)
```

### Calls
```sql
- id (uuid)
- invoice_id (uuid FK)
- customer_id (uuid FK)
- vapi_call_id (text)
- initiated_at (timestamp)
- duration (integer)
- outcome (enum: answered, no_answer, promise_to_pay, dispute, voicemail)
- transcript (text)
- recording_url (text)
- next_follow_up (timestamp)
```

### FollowUpRules
```sql
- id (uuid)
- company_id (uuid FK)
- days_overdue_threshold (integer)
- amount_threshold (decimal)
- call_frequency_days (integer)
- business_hours_start (time)
- business_hours_end (time)
- active (boolean)
```

---

## 🔧 Technical Specifications

### Backend API (Recommended: FastAPI)

**Project Structure:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Environment variables
│   ├── database.py          # DB connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/
│   │   ├── auth.py
│   │   ├── quickbooks.py
│   │   ├── invoices.py
│   │   ├── calls.py
│   │   └── webhooks.py
│   ├── services/
│   │   ├── quickbooks_service.py
│   │   ├── vapi_service.py
│   │   ├── call_scheduler.py
│   │   └── analytics_service.py
│   └── utils/
│       ├── security.py
│       └── helpers.py
├── tests/
├── alembic/                 # DB migrations
├── requirements.txt
└── README.md
```

**Key Dependencies:**
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
python-quickbooks==0.10.0
pydantic==2.5.0
python-jose==3.3.0
passlib==1.7.4
httpx==0.25.2
celery==5.3.4
redis==5.0.1
```

---

## 🎨 Frontend (Bubble) Data Types

**User**
- email (text)
- name (text)
- company (Company)
- role (text)

**Company**
- name (text)
- quickbooks_connected (yes/no)
- total_ar (number)
- api_endpoint (text)

**Invoice**
- invoice_number (text)
- customer (Customer)
- amount (number)
- amount_due (number)
- due_date (date)
- days_overdue (number)
- status (option set)
- last_call (Call)

**Call**
- invoice (Invoice)
- customer (Customer)
- call_date (date)
- duration (number)
- outcome (option set)
- transcript (text)
- recording_url (text)

---

## 📋 Follow-Up Rules Logic

### Priority Scoring Algorithm

```python
def calculate_priority_score(invoice):
    score = 0
    
    # Age weight
    days_overdue = (datetime.now().date() - invoice.due_date).days
    if days_overdue > 90:
        score += 100
    elif days_overdue > 60:
        score += 75
    elif days_overdue > 30:
        score += 50
    elif days_overdue > 14:
        score += 25
    elif days_overdue > 7:
        score += 10
    
    # Amount weight
    if invoice.amount_due > 10000:
        score += 50
    elif invoice.amount_due > 5000:
        score += 30
    elif invoice.amount_due > 1000:
        score += 15
    elif invoice.amount_due > 500:
        score += 5
    
    # Previous call attempts
    recent_calls = get_recent_calls(invoice.id, days=30)
    if len(recent_calls) == 0:
        score += 20  # Never called, boost priority
    elif len(recent_calls) > 3:
        score -= 10  # Called too many times
    
    # Last call outcome
    if invoice.last_call:
        if invoice.last_call.outcome == 'promise_to_pay':
            if invoice.last_call.date < datetime.now() - timedelta(days=3):
                score += 30  # Broken promise
        elif invoice.last_call.outcome == 'no_answer':
            score += 10  # Try again
    
    return score
```

### Call Frequency Rules
- **First call**: 7 days after due date
- **Second call**: 14 days after due date
- **Third call**: 30 days after due date
- **Subsequent calls**: Every 14 days
- **Maximum**: 1 call per 7 days per customer
- **Respect**: Business hours (9 AM - 6 PM customer timezone)

---

## 🔐 Security & Compliance

### Data Protection
- [ ] Encrypt QuickBooks tokens (AES-256)
- [ ] Secure API key storage (environment variables)
- [ ] HTTPS only
- [ ] Rate limiting on API endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS protection

### Compliance
- [ ] TCPA compliance (do-not-call list)
- [ ] GDPR data handling
- [ ] Call recording consent
- [ ] Data retention policy
- [ ] Audit logs

---

## 📊 Success Metrics

### Platform Performance
- Invoice sync accuracy: >99%
- API response time: <500ms
- Call connection rate: >85%
- System uptime: >99.5%

### Business Impact
- Payment conversion rate: Track % of called invoices paid within 7 days
- Average days to payment: Measure reduction
- AR aging improvement: Reduce 60+ days bucket
- Customer satisfaction: Survey after calls

---

## 💰 Cost Estimates (Monthly for MVP)

| Service | Estimated Cost |
|---------|---------------|
| **Bubble** (Pro plan) | $115/month |
| **N8n** (Cloud starter) | $20/month |
| **VAPI** (Pay-as-you-go) | $0.10/min = ~$300 for 3000 mins |
| **Backend Hosting** (AWS/Heroku) | $50-100/month |
| **Database** (PostgreSQL managed) | $25/month |
| **Twilio** (Phone numbers + calls) | $50/month |
| **Monitoring** (Sentry/DataDog) | $25/month |
| **TOTAL** | ~$585-635/month |

---

## 🚧 Potential Challenges & Solutions

### Challenge 1: QuickBooks Rate Limits
**Solution**: Implement exponential backoff, queue requests, cache frequently accessed data

### Challenge 2: VAPI Call Quality
**Solution**: Test multiple voice models, optimize prompts, implement call quality monitoring

### Challenge 3: Timezone Handling
**Solution**: Store customer timezone, schedule calls in their business hours

### Challenge 4: Multi-Tenant Data Isolation
**Solution**: Use row-level security, company_id foreign keys on all tables

### Challenge 5: Call Script Personalization
**Solution**: Use template engine (Jinja2), A/B test different scripts

---

## 📅 Timeline Summary

| Phase | Duration | Key Milestone |
|-------|----------|---------------|
| Phase 1 | Week 1 | Architecture ready |
| Phase 2 | Week 2-3 | QuickBooks syncing invoices |
| Phase 3 | Week 3-4 | Backend API functional |
| Phase 4 | Week 4-5 | N8n workflows live |
| Phase 5 | Week 5-6 | AI calls working |
| Phase 6 | Week 6-8 | Frontend complete |
| Phase 7 | Week 8-9 | Production launch |
| **TOTAL** | **9 weeks** | **MVP Launch** |

---

## 🎯 MVP vs Full Version

### MVP (Minimum Viable Product)
- ✅ QuickBooks integration (read-only)
- ✅ Single follow-up rule (30 days overdue)
- ✅ Basic AI call script
- ✅ Simple dashboard
- ✅ Call logging

### Full Version (Future Enhancements)
- 📧 Email reminders (in addition to calls)
- 📱 SMS follow-ups
- 🤖 Advanced AI (learn from successful calls)
- 📊 Advanced analytics & ML predictions
- 🔗 Multi-platform support (Xero, Sage, FreshBooks)
- 👥 Team collaboration features
- 📱 Mobile app
- 🌐 Multi-language support

---

## 🛠️ Getting Started Checklist

- [ ] Set up development environment
- [ ] Create QuickBooks developer account
- [ ] Create VAPI account
- [ ] Create N8n account
- [ ] Create Bubble account
- [ ] Set up GitHub repository
- [ ] Configure local PostgreSQL
- [ ] Install required dependencies
- [ ] Create project documentation
- [ ] Set up project management (Trello/Jira)

---

## 📚 Resources & Documentation

### APIs
- [QuickBooks API Docs](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/invoice)
- [VAPI Documentation](https://docs.vapi.ai)
- [N8n Documentation](https://docs.n8n.io)
- [Bubble Manual](https://manual.bubble.io)

### Learning Resources
- QuickBooks OAuth 2.0 Guide
- VAPI Voice AI Best Practices
- N8n Workflow Examples
- Bubble API Connector Tutorial

---

**Next Steps:** Review this plan, confirm technical approach, and begin Phase 1 setup! 🚀
