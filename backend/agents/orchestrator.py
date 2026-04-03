"""
Orchestrator Agent - Coordinates all agents, manages state transitions.
This is the brain that runs the full pipeline: Parse → Price → Compete → Govern → Draft
"""
import logging
from datetime import datetime, timezone
from agents.rfp_parser import parse_rfp_with_llm
from agents.pricing_engine import compute_pricing
from agents.competitor_analysis import full_competitor_analysis
from agents.governance import check_governance

logger = logging.getLogger(__name__)

WORKFLOW_STATES = [
    "DRAFT", "SUBMITTED", "PARSING", "PARSED", "PRICING", "PRICED",
    "MARKET_CHECK", "MARKET_CHECKED", "STRATEGIZED",
    "PENDING_APPROVAL", "APPROVED", "REJECTED", "REVISION_REQUESTED",
    "QUOTE_GENERATED", "SHARED_WITH_CLIENT", "CLIENT_APPROVED",
    "CLIENT_REVISION", "REWORKED", "CONVERTED_TO_ORDER", "CLOSED_LOST", "ARCHIVED"
]


def create_audit_event(rfp_id: str, agent: str, action: str, details: str, user: str = "system") -> dict:
    return {
        "rfp_id": rfp_id,
        "agent": agent,
        "action": action,
        "details": details,
        "user": user,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def run_pipeline(rfp_id: str, raw_text: str, rfp_metadata: dict) -> dict:
    """
    Run the full agent pipeline on an RFP.
    Returns complete analysis results and audit trail.
    """
    audit_trail = []
    pipeline_start = datetime.now(timezone.utc)

    # ===== STEP 1: Parse RFP =====
    audit_trail.append(create_audit_event(rfp_id, "RFP_PARSER", "START", "Beginning RFP parsing"))
    try:
        parsed = await parse_rfp_with_llm(raw_text)

        # Merge metadata overrides
        if rfp_metadata.get("client_name"):
            parsed["client_name"] = rfp_metadata["client_name"]
        if rfp_metadata.get("client_state"):
            parsed["client_state"] = rfp_metadata["client_state"]
        if rfp_metadata.get("currency"):
            parsed["currency"] = rfp_metadata["currency"]
        if rfp_metadata.get("tax_type"):
            parsed["tax_type"] = rfp_metadata["tax_type"]
        if rfp_metadata.get("deadline"):
            parsed["deadline"] = rfp_metadata["deadline"]

        item_count = len(parsed.get("line_items", []))
        confidence = parsed.get("confidence_score", 0)
        audit_trail.append(create_audit_event(
            rfp_id, "RFP_PARSER", "COMPLETE",
            f"Extracted {item_count} line items, confidence: {confidence}"
        ))
    except Exception as e:
        logger.error(f"Parse failed: {e}")
        audit_trail.append(create_audit_event(rfp_id, "RFP_PARSER", "ERROR", str(e)))
        return {"error": f"Parsing failed: {e}", "audit_trail": audit_trail, "status": "PARSING_FAILED"}

    # ===== STEP 2: Pricing =====
    audit_trail.append(create_audit_event(rfp_id, "PRICING_ENGINE", "START", "Computing pricing"))
    try:
        pricing_result = compute_pricing(parsed)
        summary = pricing_result.get("summary", {})
        audit_trail.append(create_audit_event(
            rfp_id, "PRICING_ENGINE", "COMPLETE",
            f"Priced {summary.get('total_items', 0)} items, total: Rs {summary.get('grand_total', 0):,.0f}, margin: {summary.get('overall_margin_pct', 0)}%"
        ))
    except Exception as e:
        logger.error(f"Pricing failed: {e}")
        audit_trail.append(create_audit_event(rfp_id, "PRICING_ENGINE", "ERROR", str(e)))
        return {"error": f"Pricing failed: {e}", "audit_trail": audit_trail, "status": "PRICING_FAILED", "parsed": parsed}

    # ===== STEP 3: Competitor Analysis =====
    audit_trail.append(create_audit_event(rfp_id, "COMPETITOR_ANALYSIS", "START", "Analyzing market"))
    try:
        urgency = parsed.get("urgency_level", "normal")
        competitor_result = full_competitor_analysis(pricing_result, urgency)
        audit_trail.append(create_audit_event(
            rfp_id, "COMPETITOR_ANALYSIS", "COMPLETE",
            f"Strategy: {competitor_result['overall_strategy']}, Risk items: {competitor_result['risk_count']}"
        ))
    except Exception as e:
        logger.error(f"Competitor analysis failed: {e}")
        audit_trail.append(create_audit_event(rfp_id, "COMPETITOR_ANALYSIS", "ERROR", str(e)))
        competitor_result = {"overall_strategy": "STANDARD", "item_analyses": [], "needs_owner_approval": True, "approval_reasons": ["Competitor analysis failed"]}

    # ===== STEP 4: Governance Check =====
    audit_trail.append(create_audit_event(rfp_id, "GOVERNANCE", "START", "Running compliance checks"))
    try:
        governance_result = check_governance(pricing_result, competitor_result, parsed)
        audit_trail.append(create_audit_event(
            rfp_id, "GOVERNANCE", "COMPLETE",
            f"Approval: {governance_result['approval_path']}, Risk: {governance_result['risk_level']}, Checks: {governance_result['checks_passed']}/{governance_result['checks_total']} passed"
        ))
    except Exception as e:
        logger.error(f"Governance check failed: {e}")
        audit_trail.append(create_audit_event(rfp_id, "GOVERNANCE", "ERROR", str(e)))
        governance_result = {"requires_approval": True, "approval_path": "owner_approval_required", "risk_level": "high", "checks": []}

    # ===== STEP 5: Determine next status =====
    pipeline_end = datetime.now(timezone.utc)
    duration_seconds = (pipeline_end - pipeline_start).total_seconds()

    if governance_result.get("requires_approval"):
        next_status = "PENDING_APPROVAL"
    else:
        next_status = "APPROVED"

    audit_trail.append(create_audit_event(
        rfp_id, "ORCHESTRATOR", "PIPELINE_COMPLETE",
        f"Pipeline completed in {duration_seconds:.1f}s. Next status: {next_status}"
    ))

    return {
        "status": next_status,
        "parsed": parsed,
        "pricing": pricing_result,
        "competitor_analysis": competitor_result,
        "governance": governance_result,
        "audit_trail": audit_trail,
        "pipeline_duration_seconds": round(duration_seconds, 1),
    }
