"""
Pricing Engine Agent - Pure Deterministic Python Rules
Maps RFP line items to SKU catalog, calculates pricing, applies margin rules.
NO LLM involved - all logic is rule-based.
"""
import logging
from difflib import SequenceMatcher
from mock_data import SKU_CATALOG, get_tax_components, convert_currency

logger = logging.getLogger(__name__)

# Strategy thresholds
MARGIN_FLOOR_ABSOLUTE = 8  # Never go below 8% margin
VOLUME_DISCOUNT_TIERS = [
    {"min_qty": 100, "discount_pct": 3},
    {"min_qty": 50, "discount_pct": 2},
    {"min_qty": 20, "discount_pct": 1},
]
URGENCY_PREMIUM = {"normal": 0, "urgent": 8, "critical": 15}


def match_sku(description: str, keywords: list, specs: dict) -> dict:
    """Match an RFP line item to the best SKU using keyword similarity"""
    best_match = None
    best_score = 0

    desc_lower = description.lower()
    kw_lower = [k.lower() for k in keywords]

    for sku in SKU_CATALOG:
        score = 0
        sku_name_lower = sku["name"].lower()
        sku_cat_lower = sku["category"].lower()

        # Direct name similarity
        ratio = SequenceMatcher(None, desc_lower, sku_name_lower).ratio()
        score += ratio * 40

        # Keyword matches
        for kw in kw_lower:
            if kw in sku_name_lower or kw in sku_cat_lower:
                score += 10
            for spec_val in sku["specs"].values():
                if kw in str(spec_val).lower():
                    score += 5

        # Spec matching
        for spec_key, spec_val in specs.items():
            for sku_spec_key, sku_spec_val in sku["specs"].items():
                if str(spec_val).lower() in str(sku_spec_val).lower():
                    score += 15

        if score > best_score:
            best_score = score
            best_match = sku

    if best_match and best_score > 15:
        return {
            "matched": True,
            "sku": best_match,
            "match_score": round(min(best_score, 100), 1),
            "match_reason": f"Matched '{description}' to '{best_match['name']}' (score: {round(best_score, 1)})"
        }
    return {
        "matched": False,
        "sku": None,
        "match_score": 0,
        "match_reason": f"No matching SKU found for '{description}'"
    }


def calculate_line_item_price(sku: dict, quantity: int, urgency: str = "normal") -> dict:
    """Calculate pricing for a single line item with margin rules"""
    base_cost = sku["base_cost"]
    sell_price = sku["sell_price"]
    margin_target = sku["margin_target"]
    margin_floor = sku["margin_floor"]

    # Apply volume discount
    volume_discount_pct = 0
    for tier in VOLUME_DISCOUNT_TIERS:
        if quantity >= tier["min_qty"]:
            volume_discount_pct = tier["discount_pct"]
            break

    # Apply urgency premium
    urgency_premium_pct = URGENCY_PREMIUM.get(urgency, 0)

    # Calculate effective unit price
    discount_amount = sell_price * volume_discount_pct / 100
    premium_amount = sell_price * urgency_premium_pct / 100
    effective_unit_price = sell_price - discount_amount + premium_amount

    # Calculate margins
    unit_margin = effective_unit_price - base_cost
    margin_pct = (unit_margin / effective_unit_price * 100) if effective_unit_price > 0 else 0

    # Floor price (minimum we can sell at)
    floor_price = base_cost * (1 + margin_floor / 100)

    return {
        "sku_id": sku["sku_id"],
        "sku_name": sku["name"],
        "hsn": sku["hsn"],
        "unit": sku["unit"],
        "base_cost": base_cost,
        "sell_price": sell_price,
        "mrp": sku["mrp"],
        "volume_discount_pct": volume_discount_pct,
        "volume_discount_amount": round(discount_amount, 2),
        "urgency_premium_pct": urgency_premium_pct,
        "urgency_premium_amount": round(premium_amount, 2),
        "effective_unit_price": round(effective_unit_price, 2),
        "floor_price": round(floor_price, 2),
        "quantity": quantity,
        "line_total": round(effective_unit_price * quantity, 2),
        "base_cost_total": round(base_cost * quantity, 2),
        "margin_amount": round(unit_margin * quantity, 2),
        "margin_pct": round(margin_pct, 1),
        "margin_target": margin_target,
        "margin_floor": margin_floor,
        "margin_healthy": margin_pct >= margin_target,
        "margin_safe": margin_pct >= margin_floor,
        "stock_available": sku["stock"],
        "stock_sufficient": sku["stock"] >= quantity,
        "lead_time_days": sku["lead_time_days"],
        "warranty_months": sku["warranty_months"],
        "specs": sku["specs"],
    }


def compute_pricing(parsed_rfp: dict) -> dict:
    """Full pricing computation for all line items"""
    line_items = parsed_rfp.get("line_items", [])
    urgency = parsed_rfp.get("urgency_level", "normal")
    tax_type = parsed_rfp.get("tax_type", "intra_state")
    currency = parsed_rfp.get("currency", "INR")

    priced_items = []
    unmatched_items = []
    total_base_cost = 0
    total_sell_value = 0
    total_margin = 0
    warnings = []

    for item in line_items:
        # Match to SKU
        match_result = match_sku(
            item["description"],
            item.get("search_keywords", []),
            item.get("specs", {})
        )

        if not match_result["matched"]:
            unmatched_items.append({
                "description": item["description"],
                "quantity": item.get("quantity", 0),
                "reason": match_result["match_reason"]
            })
            continue

        sku = match_result["sku"]
        qty = item.get("quantity", 1)

        # Calculate pricing
        pricing = calculate_line_item_price(sku, qty, urgency)
        pricing["match_score"] = match_result["match_score"]
        pricing["match_reason"] = match_result["match_reason"]
        pricing["original_description"] = item["description"]

        # Calculate tax
        tax = get_tax_components(tax_type, pricing["line_total"])
        pricing["tax"] = tax
        pricing["line_total_with_tax"] = round(pricing["line_total"] + tax["total_tax"], 2)

        # Currency conversion
        if currency != "INR":
            pricing["currency_display"] = {
                "unit_price": convert_currency(pricing["effective_unit_price"], currency),
                "line_total": convert_currency(pricing["line_total"], currency),
                "line_total_with_tax": convert_currency(pricing["line_total_with_tax"], currency),
                "currency": currency
            }

        priced_items.append(pricing)
        total_base_cost += pricing["base_cost_total"]
        total_sell_value += pricing["line_total"]
        total_margin += pricing["margin_amount"]

        # Generate warnings
        if not pricing["stock_sufficient"]:
            warnings.append(f"Insufficient stock for {sku['name']}: need {qty}, have {sku['stock']}")
        if not pricing["margin_safe"]:
            warnings.append(f"Margin below floor for {sku['name']}: {pricing['margin_pct']}% < {pricing['margin_floor']}%")

    # Totals
    total_tax = get_tax_components(tax_type, total_sell_value)
    overall_margin_pct = (total_margin / total_sell_value * 100) if total_sell_value > 0 else 0

    return {
        "line_items": priced_items,
        "unmatched_items": unmatched_items,
        "summary": {
            "total_items": len(priced_items),
            "unmatched_count": len(unmatched_items),
            "total_base_cost": round(total_base_cost, 2),
            "total_sell_value": round(total_sell_value, 2),
            "total_tax": total_tax,
            "grand_total": round(total_sell_value + total_tax["total_tax"], 2),
            "total_margin": round(total_margin, 2),
            "overall_margin_pct": round(overall_margin_pct, 1),
            "currency": currency,
            "tax_type": tax_type,
            "urgency": urgency,
        },
        "warnings": warnings,
        "currency_totals": {
            "display_currency": currency,
            "total_inr": round(total_sell_value + total_tax["total_tax"], 2),
            "total_display": convert_currency(total_sell_value + total_tax["total_tax"], currency) if currency != "INR" else round(total_sell_value + total_tax["total_tax"], 2),
        }
    }
