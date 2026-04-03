"""
Competitor Analysis Agent - Mock competitor DB + Strategy Selection
Queries competitor pricing, computes deltas, selects pricing strategy.
CORE RULE: Never let the system blindly match a below-cost competitor.
"""
import logging
from mock_data import get_competitor_prices

logger = logging.getLogger(__name__)

# Strategy definitions
STRATEGIES = {
    "STANDARD": {
        "label": "Standard Margin",
        "description": "Competitor prices are higher. Maintain standard markup for healthy profit.",
        "action": "Keep target margin. No adjustments needed.",
        "risk": "low"
    },
    "DEFEND_MARGIN": {
        "label": "Defend Margin",
        "description": "Competitor is close but above our cost. Tighten margin within safe floor to stay competitive.",
        "action": "Reduce price to midpoint between floor and target. Emphasize quality and reliability.",
        "risk": "medium"
    },
    "VALUE_DEFENSE": {
        "label": "Value Differentiation",
        "description": "Competitor price is below our base cost. Price-matching would be unprofitable.",
        "action": "DO NOT match price. Instead add value: free warranty extension, bundled AMC, faster delivery, free installation, premium support, or training.",
        "risk": "high",
        "value_adds": [
            {"type": "warranty_extension", "label": "Free Extended Warranty (+12 months)", "cost_pct": 3},
            {"type": "free_installation", "label": "Free Installation & Commissioning", "cost_pct": 5},
            {"type": "amc_bundle", "label": "1-Year Free AMC (Annual Maintenance Contract)", "cost_pct": 4},
            {"type": "priority_support", "label": "24/7 Priority Technical Support", "cost_pct": 2},
            {"type": "training", "label": "Free Operator Training (2 days)", "cost_pct": 1},
            {"type": "faster_delivery", "label": "Guaranteed Express Delivery", "cost_pct": 3},
        ]
    },
    "PREMIUM_URGENCY": {
        "label": "Premium Urgency Pricing",
        "description": "Client needs urgent delivery. Premium pricing justified by speed and availability.",
        "action": "Apply urgency premium. Guarantee delivery timeline. Highlight stock availability.",
        "risk": "low"
    }
}


def analyze_competitor_for_item(priced_item: dict) -> dict:
    """Analyze competitor pricing for a single line item"""
    sku_id = priced_item["sku_id"]
    our_price = priced_item["effective_unit_price"]
    base_cost = priced_item["base_cost"]
    floor_price = priced_item["floor_price"]

    competitors = get_competitor_prices(sku_id)
    if not competitors:
        return {
            "sku_id": sku_id,
            "competitors": [],
            "strategy": "STANDARD",
            "strategy_detail": STRATEGIES["STANDARD"],
            "rationale": "No competitor data available. Using standard pricing.",
            "price_adjustment": 0,
            "value_adds": [],
            "lowest_competitor": None,
            "avg_competitor_price": 0,
        }

    # Compute deltas
    for comp in competitors:
        comp["delta"] = round(comp["price"] - our_price, 2)
        comp["delta_pct"] = round((comp["price"] - our_price) / our_price * 100, 1) if our_price > 0 else 0
        comp["below_our_cost"] = comp["price"] < base_cost

    lowest = min(competitors, key=lambda c: c["price"])
    avg_price = sum(c["price"] for c in competitors) / len(competitors)

    # Strategy selection logic (pure deterministic)
    strategy = "STANDARD"
    rationale = ""
    price_adjustment = 0
    value_adds = []

    if lowest["price"] < base_cost:
        # CRITICAL: Competitor is below our cost - VALUE DEFENSE
        strategy = "VALUE_DEFENSE"
        rationale = (
            f"ALERT: {lowest['competitor']} quotes Rs {lowest['price']} which is BELOW our base cost "
            f"of Rs {base_cost}. Price-matching would result in a LOSS. "
            f"Strategy: Maintain margin and differentiate through added value services. "
            f"The customer receives more overall value even at a higher price point."
        )
        # Select appropriate value adds
        va_list = STRATEGIES["VALUE_DEFENSE"]["value_adds"]
        # Pick top 3 value adds
        value_adds = va_list[:3]

    elif lowest["price"] < floor_price:
        # Competitor below our floor but above cost - DEFEND with tight margin
        strategy = "DEFEND_MARGIN"
        midpoint = (floor_price + our_price) / 2
        price_adjustment = round(midpoint - our_price, 2)
        rationale = (
            f"Competitor {lowest['competitor']} at Rs {lowest['price']} is below our floor price "
            f"of Rs {floor_price} but above base cost. Tightening margin to midpoint Rs {round(midpoint)}. "
            f"This preserves minimum acceptable margin while staying competitive."
        )

    elif lowest["price"] < our_price:
        # Competitor is cheaper but we can still compete
        strategy = "DEFEND_MARGIN"
        adjusted = round((lowest["price"] + our_price) / 2, 2)
        price_adjustment = round(adjusted - our_price, 2)
        rationale = (
            f"Competitor {lowest['competitor']} at Rs {lowest['price']} is below our price "
            f"of Rs {our_price}. Adjusting to Rs {round(adjusted)} to remain competitive "
            f"while preserving margin above floor."
        )
    else:
        # We are cheapest or competitive
        strategy = "STANDARD"
        rationale = (
            f"Our price of Rs {our_price} is competitive. Lowest competitor "
            f"({lowest['competitor']}) at Rs {lowest['price']}. Maintaining standard margin."
        )

    return {
        "sku_id": sku_id,
        "sku_name": priced_item["sku_name"],
        "our_price": our_price,
        "base_cost": base_cost,
        "floor_price": floor_price,
        "competitors": competitors,
        "lowest_competitor": {
            "name": lowest["competitor"],
            "price": lowest["price"],
            "delta": lowest["delta"],
            "below_cost": lowest["price"] < base_cost,
        },
        "avg_competitor_price": round(avg_price, 2),
        "strategy": strategy,
        "strategy_detail": STRATEGIES[strategy],
        "rationale": rationale,
        "price_adjustment": price_adjustment,
        "value_adds": value_adds,
    }


def full_competitor_analysis(pricing_result: dict, urgency: str = "normal") -> dict:
    """Run competitor analysis for all priced items and determine overall strategy"""
    item_analyses = []
    strategies_used = set()
    total_adjustments = 0
    all_value_adds = []
    risk_items = []

    for item in pricing_result.get("line_items", []):
        analysis = analyze_competitor_for_item(item)

        # Override with PREMIUM if urgent
        if urgency in ("urgent", "critical") and analysis["strategy"] != "VALUE_DEFENSE":
            analysis["strategy"] = "PREMIUM_URGENCY"
            analysis["strategy_detail"] = STRATEGIES["PREMIUM_URGENCY"]
            analysis["rationale"] = (
                f"URGENT delivery required. Premium pricing applied. "
                f"Original strategy was {analysis['strategy']}. " + analysis["rationale"]
            )

        strategies_used.add(analysis["strategy"])
        total_adjustments += analysis["price_adjustment"]
        all_value_adds.extend(analysis["value_adds"])

        if analysis["strategy"] in ("VALUE_DEFENSE", "DEFEND_MARGIN"):
            risk_items.append({
                "sku_name": item["sku_name"],
                "strategy": analysis["strategy"],
                "reason": analysis["rationale"][:100]
            })

        item_analyses.append(analysis)

    # Determine overall strategy
    if "VALUE_DEFENSE" in strategies_used:
        overall_strategy = "VALUE_DEFENSE"
    elif "PREMIUM_URGENCY" in strategies_used:
        overall_strategy = "PREMIUM_URGENCY"
    elif "DEFEND_MARGIN" in strategies_used:
        overall_strategy = "DEFEND_MARGIN"
    else:
        overall_strategy = "STANDARD"

    # Deduplicate value adds
    seen = set()
    unique_value_adds = []
    for va in all_value_adds:
        if va["type"] not in seen:
            seen.add(va["type"])
            unique_value_adds.append(va)

    # Determine if owner approval is needed
    needs_approval = (
        overall_strategy in ("VALUE_DEFENSE", "DEFEND_MARGIN") or
        len(risk_items) > 0 or
        urgency in ("urgent", "critical")
    )

    approval_reasons = []
    if "VALUE_DEFENSE" in strategies_used:
        approval_reasons.append("Competitor pricing below our base cost detected")
    if "DEFEND_MARGIN" in strategies_used:
        approval_reasons.append("Margin tightening required to stay competitive")
    if urgency in ("urgent", "critical"):
        approval_reasons.append("Urgent delivery - premium pricing applied")
    if len(risk_items) > 2:
        approval_reasons.append(f"{len(risk_items)} items have pricing risk")

    return {
        "item_analyses": item_analyses,
        "overall_strategy": overall_strategy,
        "overall_strategy_detail": STRATEGIES[overall_strategy],
        "strategies_used": list(strategies_used),
        "total_price_adjustment": round(total_adjustments, 2),
        "value_adds_recommended": unique_value_adds,
        "risk_items": risk_items,
        "risk_count": len(risk_items),
        "needs_owner_approval": needs_approval,
        "approval_reasons": approval_reasons,
        "market_position": "competitive" if overall_strategy == "STANDARD" else "challenged",
    }
