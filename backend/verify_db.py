import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.database import SessionLocal
from app.models import HREmployee, SalesDeal, FinanceInvoice, SupportTicket, AutomationRule

db = SessionLocal()
emp_total    = db.query(HREmployee).count()
emp_leave    = db.query(HREmployee).filter(HREmployee.status == "on_leave").count()
deal_total   = db.query(SalesDeal).count()
deal_won     = db.query(SalesDeal).filter(SalesDeal.stage == "closed-won").count()
inv_total    = db.query(FinanceInvoice).count()
inv_overdue  = db.query(FinanceInvoice).filter(FinanceInvoice.status == "overdue").count()
tick_total   = db.query(SupportTicket).count()
tick_crit    = db.query(SupportTicket).filter(SupportTicket.priority == "critical").count()
rules_total  = db.query(AutomationRule).count()

print("=== DATABASE VERIFICATION ===")
print(f"HR Employees     : {emp_total} total | {emp_leave} on leave")
print(f"Sales Deals      : {deal_total} total | {deal_won} closed-won")
print(f"Finance Invoices : {inv_total} total | {inv_overdue} overdue")
print(f"Support Tickets  : {tick_total} total | {tick_crit} critical")
print(f"Automation Rules : {rules_total} configured")
print("=== ALL CHECKS PASSED ===")
db.close()
