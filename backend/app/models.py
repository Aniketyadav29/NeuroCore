"""
SQLAlchemy ORM models for all 4 enterprise departments
plus automation rules and audit logs.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime,
    Boolean, Text, ForeignKey
)
from sqlalchemy.sql import func
from app.database import Base


# ─────────────────────────────────────────
#  DEPARTMENT 1 — HUMAN RESOURCES
# ─────────────────────────────────────────

class HREmployee(Base):
    __tablename__ = "hr_employees"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    role          = Column(String(100), nullable=False)
    department    = Column(String(50),  nullable=False)   # HR, Sales, Finance, Support, Engineering
    status        = Column(String(20),  nullable=False, default="active")  # active | on_leave | resigned
    leave_days    = Column(Integer, default=0)            # Number of current leave days
    join_date     = Column(Date,   nullable=False)
    salary        = Column(Float,  nullable=False)
    email         = Column(String(150), nullable=True)


# ─────────────────────────────────────────
#  DEPARTMENT 2 — SALES
# ─────────────────────────────────────────

class SalesDeal(Base):
    __tablename__ = "sales_deals"

    id           = Column(Integer, primary_key=True, index=True)
    client_name  = Column(String(150), nullable=False)
    amount       = Column(Float,       nullable=False)
    stage        = Column(String(50),  nullable=False)    # prospect | negotiation | closed-won | closed-lost
    close_date   = Column(Date,        nullable=True)
    rep_name     = Column(String(100), nullable=False)
    product_name = Column(String(100), nullable=False)
    notes        = Column(Text,        nullable=True)


# ─────────────────────────────────────────
#  DEPARTMENT 3 — FINANCE
# ─────────────────────────────────────────

class FinanceInvoice(Base):
    __tablename__ = "finance_invoices"

    id             = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(30), unique=True, nullable=False)
    client_name    = Column(String(150), nullable=False)
    amount         = Column(Float,       nullable=False)
    due_date       = Column(Date,        nullable=False)
    status         = Column(String(20),  nullable=False, default="pending")  # paid | pending | overdue
    days_overdue   = Column(Integer, default=0)
    product_ref    = Column(String(100), nullable=True)  # Links to SalesDeal product
    notes          = Column(Text, nullable=True)


# ─────────────────────────────────────────
#  DEPARTMENT 4 — CUSTOMER SUPPORT
# ─────────────────────────────────────────

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id              = Column(Integer, primary_key=True, index=True)
    ticket_code     = Column(String(20), unique=True, nullable=False)
    customer_name   = Column(String(150), nullable=False)
    issue_summary   = Column(Text,        nullable=False)
    department_tag  = Column(String(50),  nullable=False)  # billing | shipping | technical | refund
    priority        = Column(String(20),  nullable=False, default="medium")  # low | medium | high | critical
    status          = Column(String(20),  nullable=False, default="open")     # open | in_progress | resolved
    product_tag     = Column(String(100), nullable=True)   # Links to Sales product
    created_at      = Column(DateTime, server_default=func.now())
    resolved_at     = Column(DateTime, nullable=True)
    agent_name      = Column(String(100), nullable=True)


# ─────────────────────────────────────────
#  AUTOMATION — RULE DEFINITIONS
# ─────────────────────────────────────────

class AutomationRule(Base):
    __tablename__ = "automation_rules"

    id                   = Column(Integer, primary_key=True, index=True)
    name                 = Column(String(150), nullable=False)
    description          = Column(Text,        nullable=True)
    trigger_event        = Column(String(100), nullable=False)  # e.g. "overdue_invoice_check"
    condition_summary    = Column(Text,        nullable=False)  # Human-readable condition
    action_type          = Column(String(100), nullable=False)  # DRAFT_PAYMENT_REMINDER | ALERT_DEPT_LEAD | etc.
    requires_approval    = Column(Boolean, default=True)
    is_active            = Column(Boolean, default=True)
    created_at           = Column(DateTime, server_default=func.now())


# ─────────────────────────────────────────
#  AUTOMATION — AUDIT LOG
# ─────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id              = Column(Integer, primary_key=True, index=True)
    timestamp       = Column(DateTime, server_default=func.now())
    rule_id         = Column(Integer, ForeignKey("automation_rules.id"), nullable=True)
    rule_name       = Column(String(150), nullable=True)
    trigger_reason  = Column(Text, nullable=False)
    action_type     = Column(String(100), nullable=False)
    status          = Column(String(30), nullable=False, default="pending")
    # pending | approved | rejected | auto_executed
    action_payload  = Column(Text, nullable=True)   # JSON string of action details
    reviewed_by     = Column(String(100), nullable=True)
    reviewed_at     = Column(DateTime, nullable=True)
    department      = Column(String(50), nullable=True)
