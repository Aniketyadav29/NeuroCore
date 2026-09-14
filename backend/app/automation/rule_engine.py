"""
automation/rule_engine.py
NeuroCore AI — Deterministic Rule Evaluation Engine

Evaluates 3 built-in rules against the live SQLite database and creates
AuditLog entries for triggered conditions. Rules that require approval
get status='pending'; low-impact rules get status='auto_executed'.

Rules:
  1. overdue_invoice_check   — Finance invoices overdue > 30 days
  2. support_spike_check     — CRITICAL support tickets exceed threshold
  3. hr_understaffing_check  — Support dept on_leave > 2 members
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models import (
    HREmployee, SalesDeal, FinanceInvoice, SupportTicket,
    AutomationRule, AuditLog,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
#  RULE DEFINITIONS
# ─────────────────────────────────────────────────────────────

RULES: List[Dict[str, Any]] = [
    {
        "trigger_event":     "overdue_invoice_check",
        "name":              "Overdue Invoice Alert",
        "description":       "Fires when one or more Finance invoices are overdue by more than 30 days.",
        "condition_summary": "FinanceInvoice.status == 'overdue' AND days_overdue > 30",
        "action_type":       "DRAFT_PAYMENT_REMINDER",
        "requires_approval": True,
    },
    {
        "trigger_event":     "support_spike_check",
        "name":              "Support Ticket Spike Alert",
        "description":       "Fires when CRITICAL-priority support tickets exceed 2.",
        "condition_summary": "SupportTicket.priority == 'critical' AND count > 2",
        "action_type":       "ALERT_DEPT_LEAD",
        "requires_approval": True,
    },
    {
        "trigger_event":     "hr_understaffing_check",
        "name":              "Support Team Understaffing Alert",
        "description":       "Fires when more than 2 Support team members are on leave simultaneously.",
        "condition_summary": "HREmployee.department == 'Support' AND status == 'on_leave' AND count > 2",
        "action_type":       "ESCALATE_HR_STAFFING",
        "requires_approval": False,
    },
]


# ─────────────────────────────────────────────────────────────
#  SEED RULES — called on startup / manually
# ─────────────────────────────────────────────────────────────

def ensure_rules_seeded(db: Session) -> None:
    """Inserts default automation rules if they don't already exist."""
    existing = {r.trigger_event for r in db.query(AutomationRule).all()}
    for rule_def in RULES:
        if rule_def["trigger_event"] not in existing:
            db.add(AutomationRule(
                name              = rule_def["name"],
                description       = rule_def["description"],
                trigger_event     = rule_def["trigger_event"],
                condition_summary = rule_def["condition_summary"],
                action_type       = rule_def["action_type"],
                requires_approval = rule_def["requires_approval"],
                is_active         = True,
            ))
    db.commit()
    logger.info("Automation rules seeded/verified.")


# ─────────────────────────────────────────────────────────────
#  INDIVIDUAL RULE EVALUATORS
# ─────────────────────────────────────────────────────────────

def _evaluate_overdue_invoices(db: Session, rule: AutomationRule) -> List[AuditLog]:
    """Rule 1: Draft payment reminders for invoices overdue > 30 days."""
    overdue = db.query(FinanceInvoice).filter(
        FinanceInvoice.status == "overdue",
        FinanceInvoice.days_overdue > 30,
    ).all()

    if not overdue:
        return []

    # Check if a pending log already exists for this rule to avoid duplicates
    existing_pending = db.query(AuditLog).filter(
        AuditLog.rule_id == rule.id,
        AuditLog.status == "pending",
    ).first()
    if existing_pending:
        logger.info(f"Rule '{rule.name}' already has a pending action — skipping.")
        return []

    total_at_risk = sum(inv.amount for inv in overdue)
    invoice_ids   = [inv.invoice_number for inv in overdue]

    payload = {
        "invoice_ids":    invoice_ids,
        "count":          len(overdue),
        "total_at_risk":  round(total_at_risk, 2),
        "action":         "Draft payment reminder emails to all overdue clients",
        "template":       "PAYMENT_REMINDER_V1",
    }

    log = AuditLog(
        rule_id       = rule.id,
        rule_name     = rule.name,
        trigger_reason = (
            f"{len(overdue)} invoice(s) are overdue by more than 30 days. "
            f"Total at risk: ${total_at_risk:,.2f}. "
            f"Invoices: {', '.join(invoice_ids[:5])}"
        ),
        action_type   = rule.action_type,
        status        = "pending" if rule.requires_approval else "auto_executed",
        action_payload = json.dumps(payload),
        department    = "Finance",
    )
    return [log]


def _evaluate_support_spike(db: Session, rule: AutomationRule) -> List[AuditLog]:
    """Rule 2: Alert dept lead when critical tickets exceed threshold."""
    critical = db.query(SupportTicket).filter(
        SupportTicket.priority == "critical",
        SupportTicket.status.in_(["open", "in_progress"]),
    ).all()

    THRESHOLD = 2
    if len(critical) <= THRESHOLD:
        return []

    existing_pending = db.query(AuditLog).filter(
        AuditLog.rule_id == rule.id,
        AuditLog.status == "pending",
    ).first()
    if existing_pending:
        return []

    ticket_codes = [t.ticket_code for t in critical]
    payload = {
        "ticket_codes":   ticket_codes,
        "critical_count": len(critical),
        "threshold":      THRESHOLD,
        "action":         "Send escalation alert to Support Department Lead",
        "priority":       "URGENT",
    }

    log = AuditLog(
        rule_id        = rule.id,
        rule_name      = rule.name,
        trigger_reason = (
            f"{len(critical)} CRITICAL support tickets are currently open/in-progress "
            f"(threshold: {THRESHOLD}). Tickets: {', '.join(ticket_codes[:5])}"
        ),
        action_type    = rule.action_type,
        status         = "pending" if rule.requires_approval else "auto_executed",
        action_payload  = json.dumps(payload),
        department     = "Support",
    )
    return [log]


def _evaluate_hr_understaffing(db: Session, rule: AutomationRule) -> List[AuditLog]:
    """Rule 3: Auto-escalate when Support dept has > 2 people on leave."""
    on_leave = db.query(HREmployee).filter(
        HREmployee.department == "Support",
        HREmployee.status == "on_leave",
    ).all()

    THRESHOLD = 2
    if len(on_leave) <= THRESHOLD:
        return []

    existing = db.query(AuditLog).filter(
        AuditLog.rule_id == rule.id,
        AuditLog.status.in_(["pending", "auto_executed"]),
    ).first()
    if existing:
        return []

    names = [emp.name for emp in on_leave]
    total_support = db.query(HREmployee).filter(
        HREmployee.department == "Support"
    ).count()

    payload = {
        "employees_on_leave": names,
        "leave_count":        len(on_leave),
        "total_support_team": total_support,
        "coverage_pct":       round(((total_support - len(on_leave)) / total_support) * 100, 1),
        "action":             "Notify HR to arrange temporary coverage or contractor support",
        "urgency":            "HIGH",
    }

    log = AuditLog(
        rule_id        = rule.id,
        rule_name      = rule.name,
        trigger_reason = (
            f"{len(on_leave)} of {total_support} Support team members are on leave "
            f"({payload['coverage_pct']}% coverage remaining). "
            f"Employees: {', '.join(names)}"
        ),
        action_type    = rule.action_type,
        status         = "pending" if rule.requires_approval else "auto_executed",
        action_payload  = json.dumps(payload),
        department     = "HR",
    )
    return [log]


# ─────────────────────────────────────────────────────────────
#  MAIN EVALUATOR
# ─────────────────────────────────────────────────────────────

_EVALUATORS = {
    "overdue_invoice_check":  _evaluate_overdue_invoices,
    "support_spike_check":    _evaluate_support_spike,
    "hr_understaffing_check": _evaluate_hr_understaffing,
}


def evaluate_all_rules(db: Session) -> Dict[str, Any]:
    """
    Evaluates all active automation rules against the current database state.
    Creates AuditLog entries for triggered rules.

    Returns a summary of triggered rules and created log entries.
    """
    ensure_rules_seeded(db)

    active_rules = db.query(AutomationRule).filter(AutomationRule.is_active == True).all()
    triggered    = []
    skipped      = []
    new_logs     = []

    for rule in active_rules:
        evaluator = _EVALUATORS.get(rule.trigger_event)
        if not evaluator:
            logger.warning(f"No evaluator found for rule '{rule.trigger_event}' — skipping.")
            skipped.append(rule.trigger_event)
            continue

        logs = evaluator(db, rule)
        if logs:
            for log in logs:
                db.add(log)
            new_logs.extend(logs)
            triggered.append({
                "rule":        rule.name,
                "trigger":     rule.trigger_event,
                "action_type": rule.action_type,
                "logs_created": len(logs),
                "requires_approval": rule.requires_approval,
            })
            logger.info(f"Rule TRIGGERED: '{rule.name}' → {len(logs)} audit log(s) created.")
        else:
            skipped.append(rule.trigger_event)
            logger.info(f"Rule OK (not triggered): '{rule.name}'")

    db.commit()

    return {
        "status":           "success",
        "rules_evaluated":  len(active_rules),
        "rules_triggered":  len(triggered),
        "logs_created":     len(new_logs),
        "triggered_rules":  triggered,
        "skipped_rules":    skipped,
        "evaluated_at":     datetime.utcnow().isoformat() + "Z",
    }
