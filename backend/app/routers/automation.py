"""
routers/automation.py
FastAPI routes for the NeuroCore Automation Engine:

  POST /api/automation/evaluate         — Evaluate all active rules
  GET  /api/automation/rules            — List all automation rules
  GET  /api/automation/pending          — List all pending approval actions
  POST /api/automation/approve/{log_id} — Approve a pending action
  POST /api/automation/reject/{log_id}  — Reject a pending action
  GET  /api/automation/audit            — Full audit trail
  GET  /api/automation/audit/{log_id}   — Single audit log detail
"""

import json
from datetime import datetime
from typing import List, Optional, Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import AutomationRule, AuditLog
from app.automation.rule_engine import evaluate_all_rules, ensure_rules_seeded

router = APIRouter(prefix="/api/automation", tags=["Automation"])


# ─────────────────────────────────────────────────────────────
#  Pydantic Schemas
# ─────────────────────────────────────────────────────────────

class RuleSchema(BaseModel):
    id:                 int
    name:               str
    description:        Optional[str]
    trigger_event:      str
    condition_summary:  str
    action_type:        str
    requires_approval:  bool
    is_active:          bool
    created_at:         Optional[str]

    class Config:
        from_attributes = True


class AuditLogSchema(BaseModel):
    id:              int
    timestamp:       Optional[str]
    rule_id:         Optional[int]
    rule_name:       Optional[str]
    trigger_reason:  str
    action_type:     str
    status:          str
    action_payload:  Optional[Any]   # parsed JSON
    reviewed_by:     Optional[str]
    reviewed_at:     Optional[str]
    department:      Optional[str]


class ApproveRequest(BaseModel):
    reviewed_by: str = Field(default="Manager", max_length=100, description="Name of the approving manager")


class EvaluateResponse(BaseModel):
    status:          str
    rules_evaluated: int
    rules_triggered: int
    logs_created:    int
    triggered_rules: List[Dict[str, Any]]
    skipped_rules:   List[str]
    evaluated_at:    str


# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────

def _serialize_log(log: AuditLog) -> AuditLogSchema:
    payload = None
    if log.action_payload:
        try:
            payload = json.loads(log.action_payload)
        except Exception:
            payload = log.action_payload

    return AuditLogSchema(
        id             = log.id,
        timestamp      = log.timestamp.isoformat() + "Z" if log.timestamp else None,
        rule_id        = log.rule_id,
        rule_name      = log.rule_name,
        trigger_reason = log.trigger_reason,
        action_type    = log.action_type,
        status         = log.status,
        action_payload = payload,
        reviewed_by    = log.reviewed_by,
        reviewed_at    = log.reviewed_at.isoformat() + "Z" if log.reviewed_at else None,
        department     = log.department,
    )


# ─────────────────────────────────────────────────────────────
#  ENDPOINTS
# ─────────────────────────────────────────────────────────────

@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate(db: Session = Depends(get_db)):
    """
    Evaluates all active automation rules against the current database state.
    Creates AuditLog entries (status='pending' or 'auto_executed') for triggered rules.
    
    Run this periodically or on-demand to surface new automation actions.
    """
    try:
        result = evaluate_all_rules(db)
        return EvaluateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rule evaluation failed: {str(e)}")


@router.get("/rules", response_model=List[RuleSchema])
def list_rules(db: Session = Depends(get_db)):
    """Returns all automation rule definitions."""
    ensure_rules_seeded(db)
    rules = db.query(AutomationRule).order_by(AutomationRule.id).all()
    return [
        RuleSchema(
            id                = r.id,
            name              = r.name,
            description       = r.description,
            trigger_event     = r.trigger_event,
            condition_summary = r.condition_summary,
            action_type       = r.action_type,
            requires_approval = r.requires_approval,
            is_active         = r.is_active,
            created_at        = r.created_at.isoformat() + "Z" if r.created_at else None,
        )
        for r in rules
    ]


@router.get("/pending", response_model=List[AuditLogSchema])
def list_pending(db: Session = Depends(get_db)):
    """Returns all pending approval actions (human-in-the-loop queue)."""
    logs = db.query(AuditLog).filter(
        AuditLog.status == "pending"
    ).order_by(desc(AuditLog.timestamp)).all()
    return [_serialize_log(log) for log in logs]


@router.post("/approve/{log_id}", response_model=AuditLogSchema)
def approve_action(
    log_id: int,
    body:   ApproveRequest,
    db:     Session = Depends(get_db),
):
    """
    Approves a pending automation action.
    
    Records the reviewer's name, approval timestamp, and sets status → 'approved'.
    """
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail=f"Audit log #{log_id} not found.")
    if log.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Action is not pending (current status: '{log.status}'). Cannot approve."
        )

    log.status      = "approved"
    log.reviewed_by = body.reviewed_by
    log.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(log)
    return _serialize_log(log)


@router.post("/reject/{log_id}", response_model=AuditLogSchema)
def reject_action(
    log_id: int,
    body:   ApproveRequest,
    db:     Session = Depends(get_db),
):
    """
    Rejects a pending automation action.
    
    Records the reviewer's name, timestamp, and sets status → 'rejected'.
    """
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail=f"Audit log #{log_id} not found.")
    if log.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Action is not pending (current status: '{log.status}'). Cannot reject."
        )

    log.status      = "rejected"
    log.reviewed_by = body.reviewed_by
    log.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(log)
    return _serialize_log(log)


@router.get("/audit", response_model=List[AuditLogSchema])
def get_audit_trail(
    department: Optional[str] = Query(None, description="Filter by department (HR, Sales, Finance, Support)"),
    status:     Optional[str] = Query(None, description="Filter by status (pending, approved, rejected, auto_executed)"),
    limit:      int           = Query(50, ge=1, le=200, description="Maximum number of records to return"),
    db:         Session       = Depends(get_db),
):
    """
    Returns the full immutable audit trail with optional filters.
    
    Ordered by most recent first.
    """
    q = db.query(AuditLog)
    if department:
        q = q.filter(AuditLog.department == department)
    if status:
        q = q.filter(AuditLog.status == status)
    logs = q.order_by(desc(AuditLog.timestamp)).limit(limit).all()
    return [_serialize_log(log) for log in logs]


@router.get("/audit/{log_id}", response_model=AuditLogSchema)
def get_audit_entry(log_id: int, db: Session = Depends(get_db)):
    """Returns a single audit log entry by ID."""
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail=f"Audit log #{log_id} not found.")
    return _serialize_log(log)
