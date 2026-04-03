"""
Governance Agent - Approval logic, guardrails, compliance checks
Determines if auto-approval is safe or owner review is required.
"""
import logging

logger = logging.getLogger(__name__)

# Policy thresholds
POLICY = {
    "auto_approve_max_value": 500000,  # Rs 5 lakhs
    "margin_floor_pct": 12,
    "max_discount_pct": 15,
    "max_items_auto": 15,
    "require_approval_strategies": ["VALUE_DEFENSE", "DEFEND_MARGIN"],
    "require_approval_currencies": ["USD", "EUR", "AED"],
    "require_approval_tax_types": ["export"],
}


def check_governance(pricing_result: dict, competitor_result: dict, parsed_rfp: dict) -> dict:
    """Run governance checks and determine approval path"""
    checks = []
    requires_approval = False
    approval_reasons = []
    risk_level = "low"  # low, medium, high, critical

    summary = pricing_result.get("summary", {})
    grand_total = summary.get("grand_total", 0)
    overall_margin = summary.get("overall_margin_pct", 0)
    currency = summary.get("currency", "INR")
    tax_type = summary.get("tax_type", "intra_state")
    strategy = competitor_result.get("overall_strategy", "STANDARD")

    # Check 1: Value threshold
    if grand_total > POLICY["auto_approve_max_value"]:
        requires_approval = True
        approval_reasons.append(f"Quote value Rs {grand_total:,.0f} exceeds auto-approval limit of Rs {POLICY['auto_approve_max_value']:,.0f}")
        checks.append({"check": "value_threshold", "status": "FLAGGED", "detail": f"Rs {grand_total:,.0f} > Rs {POLICY['auto_approve_max_value']:,.0f}"})
    else:
        checks.append({"check": "value_threshold", "status": "PASS", "detail": f"Rs {grand_total:,.0f} within limit"})

    # Check 2: Margin floor
    if overall_margin < POLICY["margin_floor_pct"]:
        requires_approval = True
        risk_level = "high"
        approval_reasons.append(f"Overall margin {overall_margin}% is below floor of {POLICY['margin_floor_pct']}%")
        checks.append({"check": "margin_floor", "status": "FLAGGED", "detail": f"{overall_margin}% < {POLICY['margin_floor_pct']}%"})
    else:
        checks.append({"check": "margin_floor", "status": "PASS", "detail": f"{overall_margin}% margin is healthy"})

    # Check 3: Strategy requires approval
    if strategy in POLICY["require_approval_strategies"]:
        requires_approval = True
        if strategy == "VALUE_DEFENSE":
            risk_level = "critical"
        elif risk_level != "critical":
            risk_level = "medium"
        approval_reasons.append(f"Pricing strategy '{strategy}' requires owner approval")
        checks.append({"check": "strategy_review", "status": "FLAGGED", "detail": f"Strategy: {strategy}"})
    else:
        checks.append({"check": "strategy_review", "status": "PASS", "detail": f"Strategy: {strategy}"})

    # Check 4: International/export
    if currency in POLICY["require_approval_currencies"] or tax_type in POLICY["require_approval_tax_types"]:
        requires_approval = True
        approval_reasons.append(f"International quote ({currency}, {tax_type}) requires approval")
        checks.append({"check": "international_review", "status": "FLAGGED", "detail": f"{currency} / {tax_type}"})
    else:
        checks.append({"check": "international_review", "status": "PASS", "detail": "Domestic transaction"})

    # Check 5: Item count
    item_count = summary.get("total_items", 0)
    if item_count > POLICY["max_items_auto"]:
        requires_approval = True
        approval_reasons.append(f"{item_count} line items exceed auto-approval limit of {POLICY['max_items_auto']}")
        checks.append({"check": "item_count", "status": "FLAGGED", "detail": f"{item_count} items"})
    else:
        checks.append({"check": "item_count", "status": "PASS", "detail": f"{item_count} items"})

    # Check 6: Unmatched items
    unmatched = len(pricing_result.get("unmatched_items", []))
    if unmatched > 0:
        requires_approval = True
        approval_reasons.append(f"{unmatched} items could not be matched to catalog")
        checks.append({"check": "unmatched_items", "status": "FLAGGED", "detail": f"{unmatched} unmatched"})
    else:
        checks.append({"check": "unmatched_items", "status": "PASS", "detail": "All items matched"})

    # Check 7: Stock availability
    stock_issues = [i for i in pricing_result.get("line_items", []) if not i.get("stock_sufficient", True)]
    if stock_issues:
        approval_reasons.append(f"{len(stock_issues)} items have insufficient stock")
        checks.append({"check": "stock_check", "status": "WARNING", "detail": f"{len(stock_issues)} items low stock"})

    # Check 8: Competitor risk items
    risk_items = competitor_result.get("risk_count", 0)
    if risk_items > 0:
        checks.append({"check": "competitor_risk", "status": "FLAGGED", "detail": f"{risk_items} items at competitive risk"})

    # Determine approval path
    if not requires_approval:
        approval_path = "auto_approve"
        approval_message = "Quote meets all auto-approval criteria. Can be sent to client directly."
    elif risk_level == "critical":
        approval_path = "owner_approval_required"
        approval_message = "CRITICAL: Owner/Director approval required. Value-defense strategy in play."
    elif risk_level == "high":
        approval_path = "owner_approval_required"
        approval_message = "HIGH RISK: Owner approval required before sharing with client."
    else:
        approval_path = "sales_manager_approval"
        approval_message = "Sales Manager approval sufficient for this quote."

    passed = sum(1 for c in checks if c["status"] == "PASS")
    flagged = sum(1 for c in checks if c["status"] == "FLAGGED")

    return {
        "requires_approval": requires_approval,
        "approval_path": approval_path,
        "approval_message": approval_message,
        "risk_level": risk_level,
        "approval_reasons": approval_reasons,
        "checks": checks,
        "checks_passed": passed,
        "checks_flagged": flagged,
        "checks_total": len(checks),
        "policy": POLICY,
    }
