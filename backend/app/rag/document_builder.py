"""
document_builder.py
Converts SQLAlchemy ORM records from all 4 departments into rich,
natural-language semantic documents tagged with unique record IDs.

These documents are what get embedded into ChromaDB for vector search.
The ID format mirrors the citation badges shown in the frontend UI.
"""

from typing import List, Dict, Any
from app.models import HREmployee, SalesDeal, FinanceInvoice, SupportTicket


# ─────────────────────────────────────────────────────────────
#  DEPARTMENT 1 — HR
# ─────────────────────────────────────────────────────────────

def build_hr_document(emp: HREmployee) -> Dict[str, Any]:
    """Serialize an HREmployee record into a semantic text chunk."""
    status_note = ""
    if emp.status == "on_leave":
        status_note = f" Currently on leave for {emp.leave_days} days."
    elif emp.status == "resigned":
        status_note = " This employee has resigned."

    text = (
        f"[HR-{emp.id:03d}] Employee Record — {emp.name} | "
        f"Role: {emp.role} | Department: {emp.department} | "
        f"Status: {emp.status.upper()}.{status_note} | "
        f"Joined: {emp.join_date} | "
        f"Annual Salary: ${emp.salary:,.0f} | "
        f"Email: {emp.email or 'N/A'}"
    )
    return {
        "id": f"HR-{emp.id:03d}",
        "text": text,
        "metadata": {
            "source": "hr",
            "record_id": f"HR-{emp.id:03d}",
            "department": emp.department,
            "status": emp.status,
            "name": emp.name,
            "role": emp.role,
        }
    }


def build_hr_documents(employees: List[HREmployee]) -> List[Dict[str, Any]]:
    return [build_hr_document(e) for e in employees]


# ─────────────────────────────────────────────────────────────
#  DEPARTMENT 2 — SALES
# ─────────────────────────────────────────────────────────────

def build_sales_document(deal: SalesDeal) -> Dict[str, Any]:
    """Serialize a SalesDeal record into a semantic text chunk."""
    close_info = f"Closed on {deal.close_date}" if deal.close_date else "Not yet closed"
    amount_fmt  = f"${deal.amount:,.0f}"

    text = (
        f"[DEAL-{deal.id:03d}] Sales Deal — Client: {deal.client_name} | "
        f"Product: {deal.product_name} | "
        f"Stage: {deal.stage.upper()} | "
        f"Deal Value: {amount_fmt} | "
        f"Account Rep: {deal.rep_name} | "
        f"{close_info}. "
        f"Notes: {deal.notes or 'None'}"
    )
    return {
        "id": f"DEAL-{deal.id:03d}",
        "text": text,
        "metadata": {
            "source": "sales",
            "record_id": f"DEAL-{deal.id:03d}",
            "stage": deal.stage,
            "product": deal.product_name,
            "client": deal.client_name,
            "rep": deal.rep_name,
            "amount": deal.amount,
        }
    }


def build_sales_documents(deals: List[SalesDeal]) -> List[Dict[str, Any]]:
    return [build_sales_document(d) for d in deals]


# ─────────────────────────────────────────────────────────────
#  DEPARTMENT 3 — FINANCE
# ─────────────────────────────────────────────────────────────

def build_finance_document(inv: FinanceInvoice) -> Dict[str, Any]:
    """Serialize a FinanceInvoice record into a semantic text chunk."""
    overdue_note = ""
    if inv.status == "overdue":
        overdue_note = f" ALERT: This invoice is {inv.days_overdue} days overdue. Immediate attention required."
    elif inv.status == "pending":
        overdue_note = " Payment is pending and due soon."

    text = (
        f"[{inv.invoice_number}] Finance Invoice — Client: {inv.client_name} | "
        f"Product: {inv.product_ref or 'General'} | "
        f"Amount: ${inv.amount:,.0f} | "
        f"Due Date: {inv.due_date} | "
        f"Status: {inv.status.upper()}.{overdue_note} | "
        f"Notes: {inv.notes or 'None'}"
    )
    return {
        "id": inv.invoice_number,
        "text": text,
        "metadata": {
            "source": "finance",
            "record_id": inv.invoice_number,
            "status": inv.status,
            "client": inv.client_name,
            "product": inv.product_ref or "",
            "amount": inv.amount,
            "days_overdue": inv.days_overdue,
        }
    }


def build_finance_documents(invoices: List[FinanceInvoice]) -> List[Dict[str, Any]]:
    return [build_finance_document(i) for i in invoices]


# ─────────────────────────────────────────────────────────────
#  DEPARTMENT 4 — CUSTOMER SUPPORT
# ─────────────────────────────────────────────────────────────

def build_support_document(ticket: SupportTicket) -> Dict[str, Any]:
    """Serialize a SupportTicket record into a semantic text chunk."""
    resolution_note = ""
    if ticket.status == "resolved" and ticket.resolved_at:
        resolution_note = f" Resolved on {ticket.resolved_at.date()}."
    elif ticket.status == "open":
        resolution_note = " This ticket is currently OPEN and unresolved."
    elif ticket.status == "in_progress":
        resolution_note = f" Assigned to {ticket.agent_name or 'unassigned agent'} — in progress."

    text = (
        f"[{ticket.ticket_code}] Support Ticket — Customer: {ticket.customer_name} | "
        f"Product: {ticket.product_tag or 'General'} | "
        f"Category: {ticket.department_tag.upper()} | "
        f"Priority: {ticket.priority.upper()} | "
        f"Status: {ticket.status.upper()}.{resolution_note} | "
        f"Created: {ticket.created_at.date() if ticket.created_at else 'Unknown'} | "
        f"Issue: {ticket.issue_summary}"
    )
    return {
        "id": ticket.ticket_code,
        "text": text,
        "metadata": {
            "source": "support",
            "record_id": ticket.ticket_code,
            "priority": ticket.priority,
            "status": ticket.status,
            "customer": ticket.customer_name,
            "product": ticket.product_tag or "",
            "tag": ticket.department_tag,
        }
    }


def build_support_documents(tickets: List[SupportTicket]) -> List[Dict[str, Any]]:
    return [build_support_document(t) for t in tickets]
