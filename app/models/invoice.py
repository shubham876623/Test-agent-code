"""
Invoice model
"""
from sqlalchemy import Column, String, Integer, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime


class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # QuickBooks Data
    quickbooks_invoice_id = Column(String(255), index=True)
    sync_token = Column(String(50))
    doc_number = Column(String(100))  # Invoice number
    
    # Financial
    total_amount = Column(Numeric(12, 2), nullable=False)
    balance = Column(Numeric(12, 2), nullable=False, index=True)  # Amount still owed
    
    # Dates
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    
    # Status
    status = Column(String(50), default="open", index=True)  # open, paid, partially_paid, overdue, voided
    quickbooks_status = Column(String(50))
    
    # AI Follow-up
    priority_score = Column(Integer, default=0, index=True)
    last_call_date = Column(DateTime)
    next_follow_up_date = Column(DateTime)
    follow_up_count = Column(Integer, default=0)
    
    # Metadata
    line_items = Column(JSONB)
    quickbooks_data = Column(JSONB)
    internal_notes = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = Column(DateTime)
    
    # Relationships
    company = relationship("Company", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    calls = relationship("Call", back_populates="invoice")
    
    def __repr__(self):
        return f"<Invoice {self.doc_number} - ${self.balance}>"
