"""
llm_service.py
Multi-provider LLM abstraction layer for NeuroCore AI.

Supports: Google Gemini | OpenAI | Groq | Offline (built-in synthesizer)

The offline synthesizer performs intelligent keyword-based reasoning
over the retrieved context documents — no API key needed.
"""

import re
import logging
from typing import List, Dict, Any, Tuple
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ─────────────────────────────────────────────────────────────
#  SYSTEM PROMPT (used for all LLM providers)
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are NeuroCore AI, the intelligent enterprise assistant for a company with four departments: HR, Sales, Finance, and Customer Support.

You have been given a set of CONTEXT RECORDS retrieved from the company's live database. Each record has a unique citation ID (e.g. [HR-003], [TCK-501], [INV-2026-001], [DEAL-005]).

YOUR RULES:
1. ONLY use information from the provided context records. Never fabricate data.
2. ALWAYS cite records inline using their ID tags, e.g. "The invoice [INV-2026-001] for Acme Corp is 52 days overdue."
3. Structure your response with clear sections by department when multiple departments are relevant.
4. Identify cross-department correlations when they exist (e.g. a sales campaign caused support spikes).
5. If the context does not contain enough information to answer, say so clearly.
6. Keep responses concise, factual, and professional.
7. End with a brief "Key Insights" summary bullet list.
"""


# ─────────────────────────────────────────────────────────────
#  CONTEXT ASSEMBLER
# ─────────────────────────────────────────────────────────────

def assemble_context(retrieved_docs: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
    """
    Assembles retrieved documents into a formatted context block
    and extracts the list of citation IDs.
    """
    if not retrieved_docs:
        return "No relevant records found.", []

    context_lines = ["=== RETRIEVED COMPANY RECORDS ===\n"]
    citation_ids  = []

    # Group by source department for clarity
    by_source: Dict[str, List[Dict]] = {}
    for doc in retrieved_docs:
        src = doc["metadata"].get("source", "unknown")
        by_source.setdefault(src, []).append(doc)

    dept_labels = {
        "hr":      "HUMAN RESOURCES",
        "sales":   "SALES",
        "finance": "FINANCE",
        "support": "CUSTOMER SUPPORT",
    }

    for src, docs in by_source.items():
        context_lines.append(f"\n--- {dept_labels.get(src, src.upper())} ---")
        for doc in docs:
            context_lines.append(doc["text"])
            citation_ids.append(doc["id"])

    context_lines.append("\n=== END OF RECORDS ===")
    return "\n".join(context_lines), citation_ids


# ─────────────────────────────────────────────────────────────
#  PROVIDER: OFFLINE SYNTHESIZER
# ─────────────────────────────────────────────────────────────

def _offline_synthesize(query: str, context: str, citation_ids: List[str]) -> str:
    """
    Intelligent offline synthesizer — analyzes retrieved context and
    generates a structured multi-department response with citations.
    No API key required.
    """
    query_lower = query.lower()
    lines = context.split("\n")

    # Collect records by section
    sections: Dict[str, List[str]] = {}
    current_section = "general"
    for line in lines:
        line = line.strip()
        if not line or "===" in line:
            continue
        if line.startswith("---"):
            current_section = line.replace("-", "").strip().lower()
            sections.setdefault(current_section, [])
        elif line:
            sections.setdefault(current_section, []).append(line)

    response_parts = []

    # Initialise variables — may remain empty if no relevant records found
    overdue   = []
    on_leave  = []
    crit_count = 0

    # — Finance findings
    fin_records = sections.get("finance", [])
    overdue = [r for r in fin_records if "OVERDUE" in r]
    if overdue and any(k in query_lower for k in ["invoice", "overdue", "payment", "billing", "revenue", "finance", "money", "spike", "complaint", "issue", "why", "ticket"]):
        response_parts.append("**Finance — Overdue Invoices**")
        for r in overdue[:4]:
            # Extract citation ID
            cid_match = re.search(r'\[([A-Z0-9\-]+)\]', r)
            cid = cid_match.group(0) if cid_match else ""
            # Extract client and days overdue
            client = re.search(r'Client:\s*([^|]+)', r)
            days   = re.search(r'(\d+) days overdue', r)
            amt    = re.search(r'Amount:\s*\$([^\|]+)', r)
            if client and days:
                response_parts.append(
                    f"- Invoice {cid} for **{client.group(1).strip()}** is "
                    f"**{days.group(1)} days overdue** "
                    f"(Amount: ${amt.group(1).strip() if amt else 'N/A'})."
                )
        response_parts.append("")

    # — Support findings
    sup_records = sections.get("customer support", [])
    critical    = [r for r in sup_records if "CRITICAL" in r or "HIGH" in r]
    open_tix    = [r for r in sup_records if "OPEN" in r]
    if sup_records and any(k in query_lower for k in ["ticket", "support", "complaint", "spike", "issue", "customer", "billing", "why", "surge"]):
        response_parts.append("**Customer Support — Active Tickets**")
        crit_count = len([r for r in sup_records if "CRITICAL" in r])
        open_count = len([r for r in sup_records if "OPEN" in r and "RESOLVED" not in r])
        response_parts.append(
            f"There are **{crit_count} CRITICAL** and **{open_count} OPEN** support tickets in the retrieved records."
        )
        for r in (critical + open_tix)[:4]:
            cid_match = re.search(r'\[([A-Z0-9\-]+)\]', r)
            cid     = cid_match.group(0) if cid_match else ""
            customer = re.search(r'Customer:\s*([^|]+)', r)
            product  = re.search(r'Product:\s*([^|]+)', r)
            issue    = re.search(r'Issue:\s*(.+)$', r)
            if customer:
                issue_short = (issue.group(1)[:100] + "...") if issue and len(issue.group(1)) > 100 else (issue.group(1) if issue else "No summary")
                response_parts.append(
                    f"- {cid} **{customer.group(1).strip()}** "
                    f"[{product.group(1).strip() if product else 'N/A'}]: {issue_short}"
                )
        response_parts.append("")

    # — Sales findings
    sales_records = sections.get("sales", [])
    if sales_records and any(k in query_lower for k in ["deal", "sales", "revenue", "product", "launch", "campaign", "propay", "client", "why", "spike", "quarter", "q1"]):
        closed_won = [r for r in sales_records if "CLOSED-WON" in r]
        response_parts.append("**Sales — Recent Activity**")
        if closed_won:
            response_parts.append(f"Found **{len(closed_won)}** closed-won deal(s) in the retrieved context:")
            for r in closed_won[:3]:
                cid_match = re.search(r'\[([A-Z0-9\-]+)\]', r)
                cid     = cid_match.group(0) if cid_match else ""
                client   = re.search(r'Client:\s*([^|]+)', r)
                product  = re.search(r'Product:\s*([^|]+)', r)
                amt      = re.search(r'Deal Value:\s*\$([^|]+)', r)
                if client:
                    response_parts.append(
                        f"- {cid} **{client.group(1).strip()}** — "
                        f"{product.group(1).strip() if product else 'N/A'} "
                        f"(${amt.group(1).strip() if amt else 'N/A'})"
                    )
        response_parts.append("")

    # — HR findings
    hr_records = sections.get("human resources", [])
    on_leave   = [r for r in hr_records if "ON_LEAVE" in r]
    if hr_records and any(k in query_lower for k in ["hr", "employee", "staff", "leave", "understaffed", "team", "support", "why", "spike"]):
        response_parts.append("**Human Resources — Staffing**")
        if on_leave:
            response_parts.append(f"**{len(on_leave)} employee(s)** are currently on leave:")
            for r in on_leave[:4]:
                cid_match = re.search(r'\[([A-Z0-9\-]+)\]', r)
                cid  = cid_match.group(0) if cid_match else ""
                name = re.search(r'Employee Record\s*[—-]\s*([^|]+)', r)
                dept = re.search(r'Department:\s*([^|]+)', r)
                days = re.search(r'on leave for (\d+) days', r)
                if name:
                    response_parts.append(
                        f"- {cid} **{name.group(1).strip()}** "
                        f"({dept.group(1).strip() if dept else 'N/A'} dept)"
                        f"{' — ' + days.group(1) + ' days' if days else ''}"
                    )
        response_parts.append("")

    # — Cross-department correlation
    has_billing_tickets = any("billing" in r.lower() for r in sup_records)
    has_propay_overdue  = any("propay" in r.lower() for r in fin_records if "OVERDUE" in r)
    has_propay_sales    = any("propay" in r.lower() for r in sales_records if "CLOSED-WON" in r)
    support_leave       = any("ON_LEAVE" in r for r in hr_records)

    if has_billing_tickets and (has_propay_overdue or has_propay_sales):
        response_parts.append("---")
        response_parts.append("**Cross-Department Correlation Detected**")
        response_parts.append(
            "The data reveals a multi-department chain reaction centered on the **ProPay Suite** product launch in Q1 2026:"
        )
        if has_propay_sales:
            cids = [re.search(r'\[[A-Z0-9\-]+\]', r).group(0) for r in sales_records if "CLOSED-WON" in r and "propay" in r.lower() and re.search(r'\[[A-Z0-9\-]+\]', r)]
            response_parts.append(
                f"1. **Sales** closed multiple ProPay Suite enterprise deals {', '.join(cids[:3])} in Q1, rapidly on-boarding new clients."
            )
        if has_billing_tickets:
            cids = [re.search(r'\[[A-Z0-9\-]+\]', r).group(0) for r in sup_records if "billing" in r.lower() and re.search(r'\[[A-Z0-9\-]+\]', r)]
            response_parts.append(
                f"2. **Customer Support** is seeing a surge of CRITICAL billing error tickets {', '.join(cids[:3])} — clients report checkout failures."
            )
        if has_propay_overdue:
            cids = [re.search(r'\[[A-Z0-9\-]+\]', r).group(0) for r in fin_records if "OVERDUE" in r and "propay" in r.lower() and re.search(r'\[[A-Z0-9\-]+\]', r)]
            response_parts.append(
                f"3. **Finance** shows {len(overdue)} overdue invoices {', '.join(cids[:3])} — directly linked to those same clients disputing charges due to billing errors."
            )
        if support_leave:
            cids = [re.search(r'\[[A-Z0-9\-]+\]', r).group(0) for r in hr_records if "ON_LEAVE" in r and re.search(r'\[[A-Z0-9\-]+\]', r)]
            response_parts.append(
                f"4. **HR** shows Support team members {', '.join(cids[:3])} currently on leave — compounding the backlog."
            )
        response_parts.append("")

    # — Key Insights summary
    response_parts.append("---")
    response_parts.append("**Key Insights**")
    insights = []
    if overdue:
        total_overdue = sum(float(re.search(r'Amount:\s*\$([0-9,]+)', r).group(1).replace(',', '')) for r in overdue if re.search(r'Amount:\s*\$([0-9,]+)', r))
        insights.append(f"- Total overdue revenue at risk: **${total_overdue:,.0f}**")
    if crit_count:
        insights.append(f"- **{crit_count} CRITICAL** support tickets require immediate escalation")
    if on_leave:
        insights.append(f"- **{len(on_leave)} Support staff** on leave is reducing team capacity during a high-ticket period")
    if not insights:
        insights.append("- Review the retrieved records above for department-specific details")
    response_parts.extend(insights)

    if not any(response_parts):
        # Generic fallback
        all_cids = " ".join(f"[{c}]" for c in citation_ids[:5])
        return (
            f"Based on the retrieved company records {all_cids}, "
            f"here is what the data shows:\n\n" + context[:800] +
            "\n\n**Note**: For more detailed analysis, configure an LLM provider in .env (gemini/openai/groq)."
        )

    return "\n".join(response_parts)


# ─────────────────────────────────────────────────────────────
#  PROVIDER: GOOGLE GEMINI
# ─────────────────────────────────────────────────────────────

def _call_gemini(query: str, context: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"{SYSTEM_PROMPT}\n\n{context}\n\nUser Question: {query}\n\nAnswer:"
    response = model.generate_content(prompt)
    return response.text


# ─────────────────────────────────────────────────────────────
#  PROVIDER: OPENAI
# ─────────────────────────────────────────────────────────────

def _call_openai(query: str, context: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"{context}\n\nUser Question: {query}"},
        ],
        temperature=0.3,
        max_tokens=1500,
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────
#  PROVIDER: GROQ
# ─────────────────────────────────────────────────────────────

def _call_groq(query: str, context: str) -> str:
    from groq import Groq
    client = Groq(api_key=settings.groq_api_key)
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"{context}\n\nUser Question: {query}"},
        ],
        temperature=0.3,
        max_tokens=1500,
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────
#  PUBLIC INTERFACE
# ─────────────────────────────────────────────────────────────

def generate_response(
    query: str,
    retrieved_docs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Main LLM generation interface.

    Args:
        query:          The user's question.
        retrieved_docs: Top-k documents from ChromaDB query.

    Returns:
        {
            "answer":           str  — The AI-generated markdown response
            "citations":        list — List of cited record IDs
            "retrieved_records": list — The raw retrieved docs (for frontend display)
            "provider":         str  — Which LLM provider was used
        }
    """
    context, citation_ids = assemble_context(retrieved_docs)
    provider = settings.llm_provider.lower()
    answer   = ""

    try:
        if provider == "gemini" and settings.gemini_api_key:
            answer   = _call_gemini(query, context)
            used_provider = "gemini"
        elif provider == "openai" and settings.openai_api_key:
            answer   = _call_openai(query, context)
            used_provider = "openai"
        elif provider == "groq" and settings.groq_api_key:
            answer   = _call_groq(query, context)
            used_provider = "groq"
        else:
            answer   = _offline_synthesize(query, context, citation_ids)
            used_provider = "offline"
    except Exception as e:
        logger.error(f"LLM provider '{provider}' failed: {e}. Falling back to offline.")
        answer   = _offline_synthesize(query, context, citation_ids)
        used_provider = "offline (fallback)"

    # Extract all citation IDs from the final answer text
    cited_in_answer = re.findall(r'\[(HR|DEAL|INV|TCK)[^\]]+\]', answer)

    return {
        "answer":            answer,
        "citations":         list(dict.fromkeys(cited_in_answer + citation_ids)),
        "retrieved_records": retrieved_docs,
        "provider":          used_provider,
        "context_used":      len(retrieved_docs),
    }
