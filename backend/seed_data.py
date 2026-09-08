"""
seed_data.py — Populates the SQLite database with realistic, cross-department
correlated mock data designed to demonstrate the NeuroCore AI intelligence
capabilities.

SCENARIO NARRATIVE:
  In Q1 2026, the Sales team launched a major campaign for "ProPay Suite" and
  closed several enterprise deals. However, Finance has many corresponding
  invoices now overdue. Customer Support has seen a spike in "Billing Error"
  and "Checkout Failure" tickets related to ProPay Suite. Meanwhile, HR shows
  that 3 out of 8 Support team members are currently on leave — contributing
  to the slow ticket resolution times.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date, datetime, timedelta
from app.database import engine, SessionLocal
from app.models import (
    Base, HREmployee, SalesDeal, FinanceInvoice,
    SupportTicket, AutomationRule, AuditLog
)

def seed():
    print("[*] Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # ── Guard: skip if already seeded ──────────────────────────
    if db.query(HREmployee).count() > 0:
        print("[OK] Database already seeded. Skipping.")
        db.close()
        return

    print("[+] Seeding HR Employees...")

    today = date.today()

    # ───────────────────────────────────────────────────────────
    # DEPARTMENT 1 — HR EMPLOYEES (30 records)
    # ───────────────────────────────────────────────────────────
    employees = [
        # Support Team (8 members — 3 on leave -> understaffing scenario)
        HREmployee(name="Maya Patel",      role="Support Lead",       department="Support",     status="active",   leave_days=0,  join_date=date(2021, 3, 15), salary=72000, email="maya.patel@neurocore.ai"),
        HREmployee(name="Ravi Sharma",     role="Support Engineer",   department="Support",     status="on_leave", leave_days=5,  join_date=date(2022, 7, 1),  salary=55000, email="ravi.sharma@neurocore.ai"),
        HREmployee(name="Chen Wei",        role="Support Engineer",   department="Support",     status="on_leave", leave_days=3,  join_date=date(2022, 11, 20),salary=55000, email="chen.wei@neurocore.ai"),
        HREmployee(name="Sofia Garcia",    role="Support Analyst",    department="Support",     status="on_leave", leave_days=7,  join_date=date(2023, 2, 10), salary=50000, email="sofia.garcia@neurocore.ai"),
        HREmployee(name="James Okafor",    role="Support Engineer",   department="Support",     status="active",   leave_days=0,  join_date=date(2023, 6, 5),  salary=55000, email="james.okafor@neurocore.ai"),
        HREmployee(name="Priya Nair",      role="Support Analyst",    department="Support",     status="active",   leave_days=0,  join_date=date(2024, 1, 15), salary=48000, email="priya.nair@neurocore.ai"),
        HREmployee(name="Tom Nguyen",      role="Support Engineer",   department="Support",     status="active",   leave_days=0,  join_date=date(2023, 9, 12), salary=55000, email="tom.nguyen@neurocore.ai"),
        HREmployee(name="Aisha Malik",     role="Support Analyst",    department="Support",     status="active",   leave_days=0,  join_date=date(2024, 4, 1),  salary=48000, email="aisha.malik@neurocore.ai"),

        # Sales Team (6 members)
        HREmployee(name="David Chen",      role="Sales Director",     department="Sales",       status="active",   leave_days=0,  join_date=date(2019, 5, 1),  salary=120000, email="david.chen@neurocore.ai"),
        HREmployee(name="Elena Russo",     role="Account Executive",  department="Sales",       status="active",   leave_days=0,  join_date=date(2021, 8, 15), salary=85000,  email="elena.russo@neurocore.ai"),
        HREmployee(name="Marcus Johnson",  role="Account Executive",  department="Sales",       status="active",   leave_days=0,  join_date=date(2022, 3, 10), salary=80000,  email="marcus.johnson@neurocore.ai"),
        HREmployee(name="Lisa Park",       role="Sales Analyst",      department="Sales",       status="active",   leave_days=0,  join_date=date(2022, 9, 1),  salary=65000,  email="lisa.park@neurocore.ai"),
        HREmployee(name="Omar Abdullah",   role="Account Executive",  department="Sales",       status="active",   leave_days=0,  join_date=date(2023, 1, 20), salary=82000,  email="omar.abdullah@neurocore.ai"),
        HREmployee(name="Jessica Kim",     role="Sales Engineer",     department="Sales",       status="active",   leave_days=0,  join_date=date(2023, 7, 5),  salary=75000,  email="jessica.kim@neurocore.ai"),

        # Finance Team (5 members)
        HREmployee(name="Robert Mills",    role="CFO",                department="Finance",     status="active",   leave_days=0,  join_date=date(2018, 2, 1),  salary=180000, email="robert.mills@neurocore.ai"),
        HREmployee(name="Anna Kowalski",   role="Finance Manager",    department="Finance",     status="active",   leave_days=0,  join_date=date(2020, 6, 15), salary=95000,  email="anna.kowalski@neurocore.ai"),
        HREmployee(name="Sam Osei",        role="Financial Analyst",  department="Finance",     status="active",   leave_days=0,  join_date=date(2021, 11, 1), salary=70000,  email="sam.osei@neurocore.ai"),
        HREmployee(name="Nina Petrov",     role="Accountant",         department="Finance",     status="active",   leave_days=0,  join_date=date(2022, 5, 20), salary=62000,  email="nina.petrov@neurocore.ai"),
        HREmployee(name="Kai Tanaka",      role="Accountant",         department="Finance",     status="active",   leave_days=0,  join_date=date(2023, 3, 15), salary=60000,  email="kai.tanaka@neurocore.ai"),

        # HR Team (4 members)
        HREmployee(name="Patricia Owens",  role="HR Director",        department="HR",          status="active",   leave_days=0,  join_date=date(2018, 9, 1),  salary=105000, email="patricia.owens@neurocore.ai"),
        HREmployee(name="Ben Carter",      role="HR Manager",         department="HR",          status="active",   leave_days=0,  join_date=date(2020, 4, 10), salary=80000,  email="ben.carter@neurocore.ai"),
        HREmployee(name="Yuki Tanaka",     role="Talent Acquisition", department="HR",          status="active",   leave_days=0,  join_date=date(2022, 8, 1),  salary=65000,  email="yuki.tanaka@neurocore.ai"),
        HREmployee(name="Rachel Green",    role="HR Analyst",         department="HR",          status="active",   leave_days=0,  join_date=date(2023, 5, 15), salary=58000,  email="rachel.green@neurocore.ai"),

        # Engineering Team (7 members)
        HREmployee(name="Alex Turner",     role="CTO",                department="Engineering", status="active",   leave_days=0,  join_date=date(2017, 1, 15), salary=220000, email="alex.turner@neurocore.ai"),
        HREmployee(name="Zara Ahmed",      role="Lead Engineer",      department="Engineering", status="active",   leave_days=0,  join_date=date(2019, 7, 1),  salary=130000, email="zara.ahmed@neurocore.ai"),
        HREmployee(name="Liam O'Brien",    role="Backend Engineer",   department="Engineering", status="active",   leave_days=0,  join_date=date(2021, 3, 20), salary=100000, email="liam.obrien@neurocore.ai"),
        HREmployee(name="Mia Fischer",     role="Frontend Engineer",  department="Engineering", status="active",   leave_days=0,  join_date=date(2021, 9, 10), salary=95000,  email="mia.fischer@neurocore.ai"),
        HREmployee(name="Carlos Mendez",   role="ML Engineer",        department="Engineering", status="active",   leave_days=0,  join_date=date(2022, 6, 1),  salary=115000, email="carlos.mendez@neurocore.ai"),
        HREmployee(name="Dana White",      role="DevOps Engineer",    department="Engineering", status="active",   leave_days=0,  join_date=date(2023, 2, 1),  salary=98000,  email="dana.white@neurocore.ai"),
        HREmployee(name="Felix Wagner",    role="QA Engineer",        department="Engineering", status="active",   leave_days=0,  join_date=date(2023, 8, 15), salary=75000,  email="felix.wagner@neurocore.ai"),
    ]
    db.add_all(employees)
    db.commit()

    print("[+] Seeding Sales Deals...")

    # ───────────────────────────────────────────────────────────
    # DEPARTMENT 2 — SALES DEALS (18 records)
    # ───────────────────────────────────────────────────────────
    deals = [
        # ProPay Suite deals — closed in Q1 — linked to support spike & overdue invoices
        SalesDeal(client_name="Acme Corp",          amount=145000, stage="closed-won",  close_date=date(2026, 1, 15), rep_name="Elena Russo",    product_name="ProPay Suite",    notes="Enterprise plan signed. Billing integration required."),
        SalesDeal(client_name="GlobalTech Ltd",     amount=210000, stage="closed-won",  close_date=date(2026, 1, 28), rep_name="Marcus Johnson",  product_name="ProPay Suite",    notes="Large enterprise deal. 12-month contract."),
        SalesDeal(client_name="RetailMax Inc",      amount=87500,  stage="closed-won",  close_date=date(2026, 2, 5),  rep_name="Omar Abdullah",   product_name="ProPay Suite",    notes="Mid-market segment. Fast onboarding requested."),
        SalesDeal(client_name="StartupNest",        amount=32000,  stage="closed-won",  close_date=date(2026, 2, 14), rep_name="Elena Russo",    product_name="ProPay Suite",    notes="Startup accelerator deal. Discounted pricing."),
        SalesDeal(client_name="MegaLogistics",      amount=175000, stage="closed-won",  close_date=date(2026, 2, 20), rep_name="Marcus Johnson",  product_name="ProPay Suite",    notes="Logistics sector integration."),

        # DataVault Pro deals — healthy, no issues
        SalesDeal(client_name="FinServe Group",     amount=95000,  stage="closed-won",  close_date=date(2026, 3, 1),  rep_name="Omar Abdullah",   product_name="DataVault Pro",   notes="Finance compliance requirements met."),
        SalesDeal(client_name="HealthTech Systems", amount=120000, stage="closed-won",  close_date=date(2026, 3, 10), rep_name="Elena Russo",    product_name="DataVault Pro",   notes="HIPAA-compliant data handling."),
        SalesDeal(client_name="EduPlatform Co",    amount=45000,  stage="closed-won",  close_date=date(2026, 3, 18), rep_name="Jessica Kim",    product_name="DataVault Pro",   notes="Education sector pricing applied."),

        # CloudOps Plus deals — in negotiation
        SalesDeal(client_name="TechGiant Corp",     amount=380000, stage="negotiation", close_date=None,              rep_name="David Chen",     product_name="CloudOps Plus",   notes="Large enterprise. Security review pending."),
        SalesDeal(client_name="AutoDrive Inc",      amount=220000, stage="negotiation", close_date=None,              rep_name="Marcus Johnson",  product_name="CloudOps Plus",   notes="Automotive sector. Legal review in progress."),
        SalesDeal(client_name="CityBank",           amount=165000, stage="negotiation", close_date=None,              rep_name="Omar Abdullah",   product_name="CloudOps Plus",   notes="Banking compliance requirements."),

        # Prospects
        SalesDeal(client_name="PharmaCo",           amount=89000,  stage="prospect",    close_date=None,              rep_name="Lisa Park",      product_name="DataVault Pro",   notes="Initial demo completed. Follow-up scheduled."),
        SalesDeal(client_name="E-Commerce Hub",     amount=67000,  stage="prospect",    close_date=None,              rep_name="Jessica Kim",    product_name="ProPay Suite",    notes="Evaluation phase. Competitor comparison ongoing."),
        SalesDeal(client_name="MediaStream Ltd",    amount=42000,  stage="prospect",    close_date=None,              rep_name="Lisa Park",      product_name="CloudOps Plus",   notes="Product demo next week."),

        # Closed-lost
        SalesDeal(client_name="OldSchool Inc",      amount=55000,  stage="closed-lost", close_date=date(2026, 1, 10), rep_name="Marcus Johnson",  product_name="DataVault Pro",   notes="Lost to competitor on pricing."),
        SalesDeal(client_name="BudgetFirst Co",     amount=28000,  stage="closed-lost", close_date=date(2026, 2, 1),  rep_name="Lisa Park",      product_name="ProPay Suite",    notes="Budget constraints. Follow up Q3."),
        SalesDeal(client_name="LocalBiz Shop",      amount=15000,  stage="closed-lost", close_date=date(2026, 1, 25), rep_name="Jessica Kim",    product_name="CloudOps Plus",   notes="Product too complex for their size."),
        SalesDeal(client_name="TinyStartup",        amount=8000,   stage="closed-lost", close_date=date(2026, 3, 5),  rep_name="Elena Russo",    product_name="ProPay Suite",    notes="Went with free tier competitor."),
    ]
    db.add_all(deals)
    db.commit()

    print("[+] Seeding Finance Invoices...")

    # ───────────────────────────────────────────────────────────
    # DEPARTMENT 3 — FINANCE INVOICES (20 records)
    # ───────────────────────────────────────────────────────────
    invoices = [
        # Overdue — ProPay Suite clients (matches support ticket spike)
        FinanceInvoice(invoice_number="INV-2026-001", client_name="Acme Corp",      amount=145000, due_date=date(2026, 2, 15), status="overdue",  days_overdue=52, product_ref="ProPay Suite",  notes="Second reminder sent. No response from client billing dept."),
        FinanceInvoice(invoice_number="INV-2026-002", client_name="GlobalTech Ltd", amount=210000, due_date=date(2026, 2, 28), status="overdue",  days_overdue=39, product_ref="ProPay Suite",  notes="Client reports billing integration failure. Ticket escalated."),
        FinanceInvoice(invoice_number="INV-2026-003", client_name="RetailMax Inc",  amount=87500,  due_date=date(2026, 3, 5),  status="overdue",  days_overdue=34, product_ref="ProPay Suite",  notes="Client disputed amount due to checkout error issue."),
        FinanceInvoice(invoice_number="INV-2026-004", client_name="StartupNest",    amount=32000,  due_date=date(2026, 3, 14), status="overdue",  days_overdue=25, product_ref="ProPay Suite",  notes="Client payment method failed. Retry pending."),
        FinanceInvoice(invoice_number="INV-2026-005", client_name="MegaLogistics",  amount=175000, due_date=date(2026, 3, 20), status="overdue",  days_overdue=19, product_ref="ProPay Suite",  notes="Large invoice. Client requested extension."),

        # Pending — due soon
        FinanceInvoice(invoice_number="INV-2026-006", client_name="FinServe Group",     amount=95000,  due_date=today + timedelta(days=10), status="pending", days_overdue=0, product_ref="DataVault Pro",  notes="Net-30 terms. On track."),
        FinanceInvoice(invoice_number="INV-2026-007", client_name="HealthTech Systems", amount=120000, due_date=today + timedelta(days=7),  status="pending", days_overdue=0, product_ref="DataVault Pro",  notes="Invoice delivered. Awaiting payment."),
        FinanceInvoice(invoice_number="INV-2026-008", client_name="EduPlatform Co",    amount=45000,  due_date=today + timedelta(days=14), status="pending", days_overdue=0, product_ref="DataVault Pro",  notes="Educational discount applied."),
        FinanceInvoice(invoice_number="INV-2026-009", client_name="TechGiant Corp",     amount=95000,  due_date=today + timedelta(days=30), status="pending", days_overdue=0, product_ref="CloudOps Plus",  notes="Partial advance payment received."),
        FinanceInvoice(invoice_number="INV-2026-010", client_name="AutoDrive Inc",      amount=55000,  due_date=today + timedelta(days=45), status="pending", days_overdue=0, product_ref="CloudOps Plus",  notes="Initial setup fee invoice."),
        FinanceInvoice(invoice_number="INV-2026-011", client_name="PharmaCo",           amount=22000,  due_date=today + timedelta(days=20), status="pending", days_overdue=0, product_ref="DataVault Pro",  notes="Pilot program invoice."),
        FinanceInvoice(invoice_number="INV-2026-012", client_name="E-Commerce Hub",     amount=17000,  due_date=today + timedelta(days=25), status="pending", days_overdue=0, product_ref="ProPay Suite",   notes="POC engagement invoice."),

        # Paid — healthy history
        FinanceInvoice(invoice_number="INV-2025-088", client_name="GlobalTech Ltd",     amount=80000,  due_date=date(2025, 12, 1),  status="paid", days_overdue=0, product_ref="CloudOps Plus",  notes="Q4 2025 payment received on time."),
        FinanceInvoice(invoice_number="INV-2025-089", client_name="FinServe Group",     amount=45000,  due_date=date(2025, 12, 15), status="paid", days_overdue=0, product_ref="DataVault Pro",  notes="Advance payment. Reconciled."),
        FinanceInvoice(invoice_number="INV-2025-090", client_name="HealthTech Systems", amount=60000,  due_date=date(2025, 11, 30), status="paid", days_overdue=0, product_ref="DataVault Pro",  notes="Annual license fee paid."),
        FinanceInvoice(invoice_number="INV-2025-091", client_name="CityBank",           amount=35000,  due_date=date(2025, 12, 20), status="paid", days_overdue=0, product_ref="CloudOps Plus",  notes="Pilot project invoice paid."),
        FinanceInvoice(invoice_number="INV-2025-092", client_name="Acme Corp",          amount=50000,  due_date=date(2025, 11, 15), status="paid", days_overdue=0, product_ref="DataVault Pro",  notes="Previous product subscription."),
        FinanceInvoice(invoice_number="INV-2025-093", client_name="RetailMax Inc",      amount=28000,  due_date=date(2025, 12, 10), status="paid", days_overdue=0, product_ref="CloudOps Plus",  notes="Paid via wire transfer."),
        FinanceInvoice(invoice_number="INV-2025-094", client_name="MegaLogistics",      amount=65000,  due_date=date(2025, 12, 5),  status="paid", days_overdue=0, product_ref="ProPay Suite",   notes="Early payment. 2% discount applied."),
        FinanceInvoice(invoice_number="INV-2025-095", client_name="StartupNest",        amount=15000,  due_date=date(2025, 11, 25), status="paid", days_overdue=0, product_ref="ProPay Suite",   notes="Startup program invoice. Paid."),
    ]
    db.add_all(invoices)
    db.commit()

    print("[+] Seeding Support Tickets...")

    # ───────────────────────────────────────────────────────────
    # DEPARTMENT 4 — SUPPORT TICKETS (25 records)
    # ───────────────────────────────────────────────────────────
    base_time = datetime.now() - timedelta(days=30)

    tickets = [
        # Critical ProPay Suite billing errors — the spike scenario
        SupportTicket(ticket_code="TCK-501", customer_name="Acme Corp",      issue_summary="Payment gateway returning Error 402 during checkout. Customers cannot complete ProPay Suite billing flow. Revenue impact estimated at $50K/day.", department_tag="billing",  priority="critical", status="open",        product_tag="ProPay Suite", created_at=datetime.now()-timedelta(days=15), agent_name="Maya Patel"),
        SupportTicket(ticket_code="TCK-502", customer_name="GlobalTech Ltd", issue_summary="Billing API integration failure after ProPay Suite deployment. Invoice generation returns null for enterprise clients.", department_tag="billing",  priority="critical", status="in_progress", product_tag="ProPay Suite", created_at=datetime.now()-timedelta(days=14), agent_name="James Okafor"),
        SupportTicket(ticket_code="TCK-503", customer_name="RetailMax Inc",  issue_summary="Checkout flow crashes on the payment confirmation step. Approximately 30% of transactions are failing with ProPay Suite checkout.", department_tag="billing",  priority="critical", status="open",        product_tag="ProPay Suite", created_at=datetime.now()-timedelta(days=12), agent_name=None),
        SupportTicket(ticket_code="TCK-504", customer_name="MegaLogistics",  issue_summary="ProPay Suite payment reconciliation is generating duplicate invoice entries. Finance team reporting double charges for some accounts.", department_tag="billing",  priority="critical", status="open",        product_tag="ProPay Suite", created_at=datetime.now()-timedelta(days=10), agent_name=None),
        SupportTicket(ticket_code="TCK-505", customer_name="StartupNest",    issue_summary="Cannot access ProPay Suite dashboard after billing cycle reset. Authentication token is invalidated on payment attempt.", department_tag="billing",  priority="high",     status="open",        product_tag="ProPay Suite", created_at=datetime.now()-timedelta(days=9),  agent_name="Priya Nair"),

        # High priority — general issues
        SupportTicket(ticket_code="TCK-506", customer_name="Acme Corp",      issue_summary="Data export feature in ProPay Suite not functioning correctly — CSV exports are missing transaction metadata columns.", department_tag="technical", priority="high",     status="in_progress", product_tag="ProPay Suite", created_at=datetime.now()-timedelta(days=8),  agent_name="Tom Nguyen"),
        SupportTicket(ticket_code="TCK-507", customer_name="GlobalTech Ltd", issue_summary="User role permissions not applying correctly in ProPay Suite admin panel. Non-admin users can access billing settings.", department_tag="technical", priority="high",     status="open",        product_tag="ProPay Suite", created_at=datetime.now()-timedelta(days=7),  agent_name=None),
        SupportTicket(ticket_code="TCK-508", customer_name="FinServe Group", issue_summary="DataVault Pro backup schedule not triggering on configured time. Last successful backup was 72 hours ago.", department_tag="technical", priority="high",     status="in_progress", product_tag="DataVault Pro", created_at=datetime.now()-timedelta(days=6), agent_name="Aisha Malik"),

        # Refund requests — ProPay Suite billing issues
        SupportTicket(ticket_code="TCK-509", customer_name="RetailMax Inc",  issue_summary="Requesting full refund for failed transaction charges on Feb invoices. ProPay Suite billed for services not rendered due to checkout failures.", department_tag="refund",   priority="high",     status="open",        product_tag="ProPay Suite", created_at=datetime.now()-timedelta(days=5),  agent_name=None),
        SupportTicket(ticket_code="TCK-510", customer_name="StartupNest",    issue_summary="Double-charged for Q1 subscription. ProPay Suite billed twice in the same billing cycle. Requesting credit note.", department_tag="refund",   priority="medium",   status="in_progress", product_tag="ProPay Suite", created_at=datetime.now()-timedelta(days=5),  agent_name="Maya Patel"),

        # Medium priority — DataVault Pro
        SupportTicket(ticket_code="TCK-511", customer_name="HealthTech Systems", issue_summary="DataVault Pro compliance report generation taking over 2 hours. Performance degradation observed after last update.", department_tag="technical", priority="medium", status="open",        product_tag="DataVault Pro", created_at=datetime.now()-timedelta(days=4), agent_name=None),
        SupportTicket(ticket_code="TCK-512", customer_name="EduPlatform Co",    issue_summary="DataVault Pro integration with their LMS (Moodle) is throwing authentication errors after password policy change.", department_tag="technical", priority="medium", status="in_progress", product_tag="DataVault Pro", created_at=datetime.now()-timedelta(days=3), agent_name="Tom Nguyen"),

        # CloudOps Plus issues
        SupportTicket(ticket_code="TCK-513", customer_name="TechGiant Corp",   issue_summary="CloudOps Plus auto-scaling not triggering correctly during peak load. Server utilization hitting 95% without scaling response.", department_tag="technical", priority="high",   status="open",        product_tag="CloudOps Plus", created_at=datetime.now()-timedelta(days=3), agent_name="James Okafor"),
        SupportTicket(ticket_code="TCK-514", customer_name="AutoDrive Inc",    issue_summary="CloudOps Plus network latency increased significantly after region migration. P99 latency up 340%.", department_tag="technical", priority="high",   status="in_progress", product_tag="CloudOps Plus", created_at=datetime.now()-timedelta(days=2), agent_name="Priya Nair"),

        # Shipping/logistics
        SupportTicket(ticket_code="TCK-515", customer_name="MegaLogistics",  issue_summary="API documentation for shipping module is outdated. Integration guide references deprecated endpoints.", department_tag="shipping",  priority="medium", status="open",        product_tag="CloudOps Plus", created_at=datetime.now()-timedelta(days=2), agent_name=None),

        # Low priority — general inquiries
        SupportTicket(ticket_code="TCK-516", customer_name="PharmaCo",         issue_summary="Request for DataVault Pro HIPAA compliance certificate and SOC2 audit report for vendor assessment.", department_tag="billing",   priority="low",    status="open",        product_tag="DataVault Pro", created_at=datetime.now()-timedelta(days=2), agent_name=None),
        SupportTicket(ticket_code="TCK-517", customer_name="E-Commerce Hub",   issue_summary="Need guidance on ProPay Suite webhook configuration for order fulfillment notifications.", department_tag="technical", priority="low",    status="open",        product_tag="ProPay Suite", created_at=datetime.now()-timedelta(days=1), agent_name=None),
        SupportTicket(ticket_code="TCK-518", customer_name="CityBank",         issue_summary="Requesting training materials and onboarding documentation for CloudOps Plus admin users.", department_tag="technical", priority="low",    status="open",        product_tag="CloudOps Plus", created_at=datetime.now()-timedelta(days=1), agent_name=None),

        # Resolved tickets
        SupportTicket(ticket_code="TCK-499", customer_name="FinServe Group",  issue_summary="DataVault Pro API rate limits were incorrectly configured. Resolved by updating rate limit policy.", department_tag="technical", priority="medium", status="resolved", product_tag="DataVault Pro", created_at=datetime.now()-timedelta(days=20), resolved_at=datetime.now()-timedelta(days=18), agent_name="Tom Nguyen"),
        SupportTicket(ticket_code="TCK-498", customer_name="HealthTech Systems", issue_summary="User SSO login issue after identity provider migration. Resolved with SAML configuration update.", department_tag="technical", priority="high",   status="resolved", product_tag="DataVault Pro", created_at=datetime.now()-timedelta(days=22), resolved_at=datetime.now()-timedelta(days=20), agent_name="Aisha Malik"),
        SupportTicket(ticket_code="TCK-497", customer_name="Acme Corp",       issue_summary="Billing portal UI not loading on Safari browser. Resolved with CSS compatibility fix deployment.", department_tag="billing",   priority="medium", status="resolved", product_tag="ProPay Suite", created_at=datetime.now()-timedelta(days=25), resolved_at=datetime.now()-timedelta(days=23), agent_name="James Okafor"),
        SupportTicket(ticket_code="TCK-496", customer_name="RetailMax Inc",   issue_summary="Product catalogue sync between e-commerce platform and CloudOps inventory was failing. Resolved with API key refresh.", department_tag="technical", priority="medium", status="resolved", product_tag="CloudOps Plus", created_at=datetime.now()-timedelta(days=28), resolved_at=datetime.now()-timedelta(days=26), agent_name="Priya Nair"),
        SupportTicket(ticket_code="TCK-495", customer_name="GlobalTech Ltd",  issue_summary="Data import wizard was rejecting CSV files with UTF-8 encoding. Resolved with encoding parser update.", department_tag="technical", priority="low",    status="resolved", product_tag="DataVault Pro", created_at=datetime.now()-timedelta(days=30), resolved_at=datetime.now()-timedelta(days=29), agent_name="Maya Patel"),
        SupportTicket(ticket_code="TCK-494", customer_name="MegaLogistics",   issue_summary="ProPay Suite mobile checkout returning 503 on Android devices. Resolved by fixing CDN routing.", department_tag="billing",   priority="high",   status="resolved", product_tag="ProPay Suite", created_at=datetime.now()-timedelta(days=30), resolved_at=datetime.now()-timedelta(days=28), agent_name="Tom Nguyen"),
        SupportTicket(ticket_code="TCK-493", customer_name="EduPlatform Co",  issue_summary="Bulk user import via CSV was timing out for >1000 users. Resolved with background job queue implementation.", department_tag="technical", priority="medium", status="resolved", product_tag="DataVault Pro", created_at=datetime.now()-timedelta(days=30), resolved_at=datetime.now()-timedelta(days=27), agent_name="James Okafor"),
    ]
    db.add_all(tickets)
    db.commit()

    print("[+] Seeding Automation Rules...")

    # ───────────────────────────────────────────────────────────
    # AUTOMATION RULE DEFINITIONS (3 core rules)
    # ───────────────────────────────────────────────────────────
    rules = [
        AutomationRule(
            name="Overdue Invoice Payment Reminder",
            description="Automatically drafts a payment reminder email for clients with invoices overdue by more than 7 days.",
            trigger_event="overdue_invoice_check",
            condition_summary="finance_invoices.status == 'overdue' AND days_overdue > 7",
            action_type="DRAFT_PAYMENT_REMINDER",
            requires_approval=True,
            is_active=True
        ),
        AutomationRule(
            name="Critical Support Ticket Surge Alert",
            description="Alerts the product and engineering lead when more than 3 critical support tickets are open for a single product.",
            trigger_event="support_ticket_check",
            condition_summary="COUNT(support_tickets WHERE priority == 'critical' AND status != 'resolved' AND product_tag == X) > 3",
            action_type="ESCALATE_TO_PRODUCT_LEAD",
            requires_approval=False,
            is_active=True
        ),
        AutomationRule(
            name="Support Department Understaffing Alert",
            description="Notifies HR Manager when more than 25% of Support team is on leave while open ticket count exceeds 8.",
            trigger_event="hr_staffing_check",
            condition_summary="(hr_employees on_leave IN Support / total_support_employees) > 0.25 AND COUNT(open_tickets) > 8",
            action_type="NOTIFY_HR_MANAGER",
            requires_approval=False,
            is_active=True
        ),
    ]
    db.add_all(rules)
    db.commit()

    db.close()

    print("")
    print("[OK] Database seeding complete!")
    print("   [-] 30 HR Employees (3 Support staff on leave)")
    print("   [-] 18 Sales Deals (5 ProPay Suite Q1 closures)")
    print("   [-] 20 Finance Invoices (5 overdue — all ProPay Suite)")
    print("   [-] 25 Support Tickets (4 critical ProPay Suite billing errors)")
    print("   [-]  3 Automation Rules configured")
    print("")
    print("[~] Cross-department correlation scenario ready:")
    print("   ProPay Suite Q1 launch -> billing errors -> support spike -> overdue invoices -> understaffed team")


if __name__ == "__main__":
    seed()
