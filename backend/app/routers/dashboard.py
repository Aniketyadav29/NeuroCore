"""
routers/dashboard.py
FastAPI routes for the executive KPI dashboard:
  GET /api/dashboard/stats   — Summary KPIs for all 4 departments
  GET /api/dashboard/hr      — HR department detail
  GET /api/dashboard/sales   — Sales pipeline detail
  GET /api/dashboard/finance — Finance invoice detail
  GET /api/dashboard/support — Support ticket detail
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any

from app.database import get_db
from app.models import HREmployee, SalesDeal, FinanceInvoice, SupportTicket

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Returns top-level KPI summary for the executive dashboard."""

    # HR stats
    total_employees   = db.query(HREmployee).count()
    active_employees  = db.query(HREmployee).filter(HREmployee.status == "active").count()
    on_leave          = db.query(HREmployee).filter(HREmployee.status == "on_leave").count()
    support_on_leave  = db.query(HREmployee).filter(
        HREmployee.department == "Support",
        HREmployee.status == "on_leave"
    ).count()
    total_support     = db.query(HREmployee).filter(HREmployee.department == "Support").count()

    # Sales stats
    total_deals       = db.query(SalesDeal).count()
    closed_won        = db.query(SalesDeal).filter(SalesDeal.stage == "closed-won").count()
    in_negotiation    = db.query(SalesDeal).filter(SalesDeal.stage == "negotiation").count()
    pipeline_value    = db.query(func.sum(SalesDeal.amount)).filter(
        SalesDeal.stage.in_(["prospect", "negotiation"])
    ).scalar() or 0
    closed_revenue    = db.query(func.sum(SalesDeal.amount)).filter(
        SalesDeal.stage == "closed-won"
    ).scalar() or 0

    # Finance stats
    total_invoices    = db.query(FinanceInvoice).count()
    overdue_invoices  = db.query(FinanceInvoice).filter(FinanceInvoice.status == "overdue").count()
    pending_invoices  = db.query(FinanceInvoice).filter(FinanceInvoice.status == "pending").count()
    paid_invoices     = db.query(FinanceInvoice).filter(FinanceInvoice.status == "paid").count()
    overdue_amount    = db.query(func.sum(FinanceInvoice.amount)).filter(
        FinanceInvoice.status == "overdue"
    ).scalar() or 0
    pending_amount    = db.query(func.sum(FinanceInvoice.amount)).filter(
        FinanceInvoice.status == "pending"
    ).scalar() or 0

    # Support stats
    total_tickets     = db.query(SupportTicket).count()
    open_tickets      = db.query(SupportTicket).filter(SupportTicket.status == "open").count()
    in_progress       = db.query(SupportTicket).filter(SupportTicket.status == "in_progress").count()
    resolved_tickets  = db.query(SupportTicket).filter(SupportTicket.status == "resolved").count()
    critical_tickets  = db.query(SupportTicket).filter(SupportTicket.priority == "critical").count()
    high_tickets      = db.query(SupportTicket).filter(SupportTicket.priority == "high").count()

    # Department health scores (0-100, simple heuristic)
    hr_health      = round((active_employees / total_employees) * 100) if total_employees else 100
    sales_health   = round((closed_won / total_deals) * 100) if total_deals else 0
    finance_health = round((paid_invoices / total_invoices) * 100) if total_invoices else 100
    support_health = round((resolved_tickets / total_tickets) * 100) if total_tickets else 100

    return {
        "hr": {
            "total_employees":  total_employees,
            "active":           active_employees,
            "on_leave":         on_leave,
            "support_on_leave": support_on_leave,
            "total_support":    total_support,
            "health_score":     hr_health,
            "alert":            on_leave > 2,
        },
        "sales": {
            "total_deals":     total_deals,
            "closed_won":      closed_won,
            "in_negotiation":  in_negotiation,
            "pipeline_value":  round(pipeline_value),
            "closed_revenue":  round(closed_revenue),
            "health_score":    sales_health,
            "alert":           False,
        },
        "finance": {
            "total_invoices":   total_invoices,
            "overdue":          overdue_invoices,
            "pending":          pending_invoices,
            "paid":             paid_invoices,
            "overdue_amount":   round(overdue_amount),
            "pending_amount":   round(pending_amount),
            "health_score":     finance_health,
            "alert":            overdue_invoices > 0,
        },
        "support": {
            "total_tickets":   total_tickets,
            "open":            open_tickets,
            "in_progress":     in_progress,
            "resolved":        resolved_tickets,
            "critical":        critical_tickets,
            "high":            high_tickets,
            "health_score":    support_health,
            "alert":           critical_tickets > 0,
        },
    }


@router.get("/hr")
def get_hr_data(db: Session = Depends(get_db)):
    """Returns all HR employee records."""
    employees = db.query(HREmployee).all()
    return [
        {
            "id":         e.id,
            "name":       e.name,
            "role":       e.role,
            "department": e.department,
            "status":     e.status,
            "leave_days": e.leave_days,
            "join_date":  str(e.join_date),
            "salary":     e.salary,
            "email":      e.email,
        }
        for e in employees
    ]


@router.get("/sales")
def get_sales_data(db: Session = Depends(get_db)):
    """Returns all sales deal records."""
    deals = db.query(SalesDeal).all()
    return [
        {
            "id":           d.id,
            "client_name":  d.client_name,
            "amount":       d.amount,
            "stage":        d.stage,
            "close_date":   str(d.close_date) if d.close_date else None,
            "rep_name":     d.rep_name,
            "product_name": d.product_name,
            "notes":        d.notes,
        }
        for d in deals
    ]


@router.get("/finance")
def get_finance_data(db: Session = Depends(get_db)):
    """Returns all finance invoice records."""
    invoices = db.query(FinanceInvoice).all()
    return [
        {
            "id":             i.id,
            "invoice_number": i.invoice_number,
            "client_name":    i.client_name,
            "amount":         i.amount,
            "due_date":       str(i.due_date),
            "status":         i.status,
            "days_overdue":   i.days_overdue,
            "product_ref":    i.product_ref,
            "notes":          i.notes,
        }
        for i in invoices
    ]


@router.get("/support")
def get_support_data(db: Session = Depends(get_db)):
    """Returns all support ticket records."""
    tickets = db.query(SupportTicket).all()
    return [
        {
            "id":             t.id,
            "ticket_code":    t.ticket_code,
            "customer_name":  t.customer_name,
            "issue_summary":  t.issue_summary,
            "department_tag": t.department_tag,
            "priority":       t.priority,
            "status":         t.status,
            "product_tag":    t.product_tag,
            "created_at":     str(t.created_at) if t.created_at else None,
            "resolved_at":    str(t.resolved_at) if t.resolved_at else None,
            "agent_name":     t.agent_name,
        }
        for t in tickets
    ]
