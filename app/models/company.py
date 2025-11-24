"""
Company and CompanyUser models
"""
from sqlalchemy import Column, String, Boolean, DateTime, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # QuickBooks Integration
    quickbooks_realm_id = Column(String(255), unique=True, index=True)
    quickbooks_access_token = Column(String)  # Encrypted
    quickbooks_refresh_token = Column(String)  # Encrypted
    quickbooks_token_expires_at = Column(DateTime)
    quickbooks_connected = Column(Boolean, default=False)
    quickbooks_last_sync = Column(DateTime)
    
    # Settings
    timezone = Column(String(50), default="America/New_York")
    business_hours_start = Column(Time, default=datetime.strptime("09:00", "%H:%M").time())
    business_hours_end = Column(Time, default=datetime.strptime("17:00", "%H:%M").time())
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("CompanyUser", back_populates="company")
    customers = relationship("Customer", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")
    calls = relationship("Call", back_populates="company")
    api_keys = relationship("APIKey", back_populates="company")
    
    def __repr__(self):
        return f"<Company {self.name}>"


class CompanyUser(Base):
    """Many-to-many relationship between companies and users"""
    __tablename__ = "company_users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), default="member")  # owner, admin, member, viewer
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="users")
    user = relationship("User", back_populates="companies")
    
    def __repr__(self):
        return f"<CompanyUser company={self.company_id} user={self.user_id}>"
