"""
RFP Parser Agent - Uses Gemini 3 Flash for intelligent extraction
Extracts structured requirements from unstructured RFP text.
Detects missing fields, flags ambiguity, outputs normalized JSON.
"""
import os
import json
import re
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """You are an expert RFP (Request for Proposal) parser for an Indian electrical/industrial equipment company.

Analyze the following RFP text and extract structured data in EXACT JSON format. Be thorough and precise.

Return ONLY valid JSON with this exact structure (no markdown, no code fences):
{
  "client_name": "extracted client/company name",
  "client_address": "extracted address if available or empty string",
  "client_state": "Indian state or International",
  "contact_person": "name if mentioned or empty string",
  "contact_phone": "phone if mentioned or empty string",
  "contact_email": "email if mentioned or empty string",
  "rfp_reference": "reference number if mentioned",
  "subject": "brief subject line",
  "deadline": "YYYY-MM-DD format if mentioned or empty string",
  "delivery_timeline_days": number or 0,
  "payment_terms": "extracted payment terms",
  "warranty_requirement": "extracted warranty requirement",
  "special_conditions": ["list of special conditions like EMD, MSME preference, etc."],
  "urgency_level": "normal|urgent|critical",
  "tax_type": "intra_state|inter_state|export",
  "currency": "INR|USD|EUR|AED",
  "line_items": [
    {
      "description": "item description as stated in RFP",
      "quantity": number,
      "unit": "Nos|Mtr|Set|Lot",
      "specs": {
        "key technical specs extracted": "values"
      },
      "search_keywords": ["keywords to match against SKU catalog"]
    }
  ],
  "compliance_requirements": ["BIS", "ISI", "IEC", etc.],
  "missing_fields": ["list of important fields not found in RFP"],
  "ambiguities": ["list of ambiguous or unclear requirements"],
  "confidence_score": 0.0 to 1.0
}

RFP TEXT:
"""


async def parse_rfp_with_llm(raw_text: str) -> dict:
    """Parse RFP using Gemini 3 Flash via emergentintegrations"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            logger.warning("EMERGENT_LLM_KEY not found, falling back to rule-based parsing")
            return parse_rfp_rules(raw_text)

        chat = LlmChat(
            api_key=api_key,
            session_id=f"rfp-parse-{datetime.now(timezone.utc).timestamp()}",
            system_message="You are a precise JSON extractor. Return ONLY valid JSON. No markdown formatting."
        ).with_model("gemini", "gemini-3-flash-preview")

        user_message = UserMessage(text=EXTRACTION_PROMPT + raw_text)
        response = await chat.send_message(user_message)

        # Clean response - remove markdown code fences if present
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)

        parsed = json.loads(cleaned)
        logger.info(f"LLM parsed RFP: {len(parsed.get('line_items', []))} items, confidence={parsed.get('confidence_score', 0)}")
        return parsed

    except json.JSONDecodeError as e:
        logger.error(f"LLM returned invalid JSON: {e}")
        return parse_rfp_rules(raw_text)
    except Exception as e:
        logger.error(f"LLM parsing failed: {e}")
        return parse_rfp_rules(raw_text)


def parse_rfp_rules(raw_text: str) -> dict:
    """Fallback rule-based parser when LLM is unavailable"""
    lines = raw_text.strip().split('\n')
    line_items = []
    special_conditions = []
    compliance = []

    # Extract numbered items with quantities
    item_pattern = re.compile(
        r'(\d+)\.\s+(.+?)\s*[-–]\s*(\d+)\s*(numbers?|nos?|meters?|mtr|sets?|lots?|pcs)',
        re.IGNORECASE
    )
    for line in lines:
        match = item_pattern.search(line)
        if match:
            desc = match.group(2).strip()
            qty = int(match.group(3))
            unit_raw = match.group(4).lower()
            unit = "Nos"
            if "meter" in unit_raw or "mtr" in unit_raw:
                unit = "Mtr"
            elif "set" in unit_raw:
                unit = "Set"
            elif "lot" in unit_raw:
                unit = "Lot"

            keywords = [w.strip() for w in desc.split() if len(w.strip()) > 2]
            line_items.append({
                "description": desc,
                "quantity": qty,
                "unit": unit,
                "specs": {},
                "search_keywords": keywords[:6]
            })

    # Detect urgency
    urgency = "normal"
    text_lower = raw_text.lower()
    if any(w in text_lower for w in ["urgent", "emergency", "immediate", "critical"]):
        urgency = "critical" if "critical" in text_lower or "emergency" in text_lower else "urgent"

    # Detect currency
    currency = "INR"
    if "usd" in text_lower or "dollar" in text_lower:
        currency = "USD"
    elif "eur" in text_lower or "euro" in text_lower:
        currency = "EUR"
    elif "aed" in text_lower or "dirham" in text_lower:
        currency = "AED"

    # Detect tax type
    tax_type = "intra_state"
    if currency != "INR" or "export" in text_lower or "international" in text_lower or "fob" in text_lower:
        tax_type = "export"
    elif "igst" in text_lower or "inter-state" in text_lower or "interstate" in text_lower:
        tax_type = "inter_state"

    # Detect compliance
    for std in ["BIS", "ISI", "IEC", "PESO", "CPRI", "IS"]:
        if std.lower() in text_lower:
            compliance.append(std)

    # Detect special conditions
    if "emd" in text_lower or "earnest money" in text_lower:
        special_conditions.append("EMD required")
    if "msme" in text_lower:
        special_conditions.append("MSME preference applicable")
    if "gem" in text_lower:
        special_conditions.append("GeM listed tender")

    # Extract deadline
    deadline = ""
    date_pattern = re.compile(r'(\d{4}[-/]\d{2}[-/]\d{2})')
    date_match = date_pattern.search(raw_text)
    if date_match:
        deadline = date_match.group(1).replace('/', '-')

    # Delivery timeline
    delivery_days = 0
    delivery_match = re.search(r'(\d+)\s*days', text_lower)
    if delivery_match:
        delivery_days = int(delivery_match.group(1))

    missing = []
    if not line_items:
        missing.append("No line items detected")
    if not deadline:
        missing.append("Deadline not specified")

    return {
        "client_name": "",
        "client_address": "",
        "client_state": "",
        "contact_person": "",
        "contact_phone": "",
        "contact_email": "",
        "rfp_reference": "",
        "subject": lines[0] if lines else "",
        "deadline": deadline,
        "delivery_timeline_days": delivery_days,
        "payment_terms": "",
        "warranty_requirement": "",
        "special_conditions": special_conditions,
        "urgency_level": urgency,
        "tax_type": tax_type,
        "currency": currency,
        "line_items": line_items,
        "compliance_requirements": compliance,
        "missing_fields": missing,
        "ambiguities": [],
        "confidence_score": 0.6 if line_items else 0.3,
    }
