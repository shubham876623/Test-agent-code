"""
Customer model
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # QuickBooks Data
    quickbooks_customer_id = Column(String(255), index=True)
    sync_token = Column(String(50))
    
    # Contact Info
    display_name = Column(String(255), nullable=False)
    company_name = Column(String(255))
    email = Column(String(255), index=True)
    phone = Column(String(50), index=True)
    mobile = Column(String(50))
    
    # Address
    billing_address = Column(JSONB)
    
    # Preferences
    preferred_contact_method = Column(String(50), default="phone")
    do_not_call = Column(Boolean, default=False)
    do_not_email = Column(Boolean, default=False)
    notes = Column(String)
    
    # Metadata
    quickbooks_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = Column(DateTime)
    
    # Relationships
    company = relationship("Company", back_populates="customers")
    invoices = relationship("Invoice", back_populates="customer")
    calls = relationship("Call", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer {self.display_name}>"
