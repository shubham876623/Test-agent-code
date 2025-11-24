"""
Call model (VAPI integration)
"""
from sqlalchemy import Column, String, Boolean, Integer, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime


class Call(Base):
    __tablename__ = "calls"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # VAPI Data
    vapi_call_id = Column(String(255), unique=True, index=True)
    vapi_assistant_id = Column(String(255))
    
    # Call Details
    phone_number = Column(String(50))
    direction = Column(String(20), default="outbound")  # outbound, inbound
    status = Column(String(50), index=True)  # queued, ringing, in-progress, completed, failed
    
    # Timing
    initiated_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Outcome
    call_outcome = Column(String(50), index=True)  # answered, no_answer, voicemail, promise_to_pay, dispute
    customer_response = Column(String)
    sentiment = Column(String(50))  # positive, neutral, negative
    
    # Content
    transcript = Column(String)
    transcript_json = Column(JSONB)
    recording_url = Column(String)
    summary = Column(String)
    
    # Follow-up
    payment_promised = Column(Boolean, default=False)
    payment_promise_date = Column(Date)
    payment_promise_amount = Column(Numeric(12, 2))
    dispute_raised = Column(Boolean, default=False)
    dispute_reason = Column(String)
    requires_human_follow_up = Column(Boolean, default=False)
    
    # Metadata
    vapi_metadata = Column(JSONB)
    cost = Column(Numeric(8, 4))  # Call cost
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="calls")
    invoice = relationship("Invoice", back_populates="calls")
    customer = relationship("Customer", back_populates="calls")
    
    def __repr__(self):
        return f"<Call {self.vapi_call_id} - {self.status}>"
