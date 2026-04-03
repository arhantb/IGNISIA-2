"""
PDF Generator - Indian Business Standard Quotation
Uses WeasyPrint to generate professional PDF quotations with:
- Company details, GSTIN, PAN, CIN
- Line items with HSN/SAC, quantities, taxes
- CGST/SGST/IGST breakup
- Payment terms, warranty, validity
- AI pricing rationale appendix
"""
import io
import logging
from datetime import datetime, timezone, timedelta
from mock_data import COMPANY_PROFILE

logger = logging.getLogger(__name__)


def generate_quotation_html(quote_data: dict) -> str:
    """Generate HTML for Indian-standard quotation"""
    company = COMPANY_PROFILE
    rfp = quote_data.get("parsed", {})
    pricing = quote_data.get("pricing", {})
    competitor = quote_data.get("competitor_analysis", {})
    governance = quote_data.get("governance", {})
    summary = pricing.get("summary", {})
    line_items = pricing.get("line_items", [])
    quote_number = quote_data.get("quote_number", "SQ-2026-0001")
    quote_date = datetime.now(timezone.utc).strftime("%d-%b-%Y")
    validity_date = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%d-%b-%Y")
    currency = summary.get("currency", "INR")
    tax_type = summary.get("tax_type", "intra_state")

    currency_symbol = {"INR": "Rs", "USD": "$", "EUR": "EUR", "AED": "AED"}.get(currency, "Rs")

    # Build line items rows
    items_html = ""
    for i, item in enumerate(line_items, 1):
        tax = item.get("tax", {})
        taxable = item["line_total"]
        tax_amount = tax.get("total_tax", 0)
        total_with_tax = item.get("line_total_with_tax", taxable + tax_amount)

        tax_cols = ""
        if tax_type == "intra_state":
            tax_cols = f"""
                <td class="num">{tax.get('cgst_rate', 9)}%</td>
                <td class="num">{format_currency(tax.get('cgst', 0))}</td>
                <td class="num">{tax.get('sgst_rate', 9)}%</td>
                <td class="num">{format_currency(tax.get('sgst', 0))}</td>
            """
        else:
            tax_cols = f"""
                <td class="num">{tax.get('igst_rate', 18)}%</td>
                <td class="num">{format_currency(tax.get('igst', 0))}</td>
            """

        discount_display = ""
        if item.get("volume_discount_pct", 0) > 0:
            discount_display = f"({item['volume_discount_pct']}%)"

        items_html += f"""
        <tr>
            <td class="center">{i}</td>
            <td>{item['sku_name']}<br><small class="specs">{item.get('original_description', '')}</small></td>
            <td class="center">{item['hsn']}</td>
            <td class="center">{item['quantity']}</td>
            <td class="center">{item['unit']}</td>
            <td class="num">{format_currency(item['effective_unit_price'])}</td>
            <td class="num">{discount_display}</td>
            <td class="num">{format_currency(taxable)}</td>
            {tax_cols}
            <td class="num strong">{format_currency(total_with_tax)}</td>
        </tr>
        """

    # Tax column headers
    if tax_type == "intra_state":
        tax_headers = """
            <th>CGST%</th><th>CGST Amt</th>
            <th>SGST%</th><th>SGST Amt</th>
        """
        total_tax_rows = f"""
        <tr><td colspan="7"></td><td class="right">CGST:</td><td colspan="3" class="num">{currency_symbol} {format_currency(summary['total_tax']['cgst'])}</td></tr>
        <tr><td colspan="7"></td><td class="right">SGST:</td><td colspan="3" class="num">{currency_symbol} {format_currency(summary['total_tax']['sgst'])}</td></tr>
        """
    elif tax_type == "inter_state":
        tax_headers = "<th>IGST%</th><th>IGST Amt</th>"
        total_tax_rows = f"""
        <tr><td colspan="7"></td><td class="right">IGST:</td><td colspan="2" class="num">{currency_symbol} {format_currency(summary['total_tax']['igst'])}</td></tr>
        """
    else:
        tax_headers = "<th>Tax</th><th>Tax Amt</th>"
        total_tax_rows = ""

    # Value adds section
    value_adds_html = ""
    value_adds = competitor.get("value_adds_recommended", [])
    if value_adds:
        vas = "".join(f"<li>{va['label']}</li>" for va in value_adds)
        value_adds_html = f"""
        <div class="section">
            <h3>Complimentary Value-Added Services</h3>
            <ul>{vas}</ul>
        </div>
        """

    # Strategy appendix
    strategy = competitor.get("overall_strategy", "STANDARD")
    strategy_detail = competitor.get("overall_strategy_detail", {})
    strategy_html = ""
    if strategy != "STANDARD":
        strategy_html = f"""
        <div class="appendix">
            <h3>Pricing Rationale (Internal Reference)</h3>
            <p><strong>Strategy Applied:</strong> {strategy_detail.get('label', strategy)}</p>
            <p>{strategy_detail.get('description', '')}</p>
            <p><strong>Action:</strong> {strategy_detail.get('action', '')}</p>
        </div>
        """

    delivery_days = rfp.get("delivery_timeline_days", 45)
    warranty_text = rfp.get("warranty_requirement", "As per individual product warranty (24-60 months)")
    payment_terms = rfp.get("payment_terms", "30 days from delivery & acceptance")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {{ size: A4; margin: 15mm; }}
body {{ font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 9pt; color: #1a1a1a; line-height: 1.4; }}
.header {{ display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid #002FA7; padding-bottom: 12px; margin-bottom: 15px; }}
.company-name {{ font-size: 18pt; font-weight: bold; color: #002FA7; margin-bottom: 4px; }}
.company-details {{ font-size: 7.5pt; color: #444; }}
.quote-title {{ text-align: center; font-size: 14pt; font-weight: bold; color: #002FA7; margin: 15px 0; text-transform: uppercase; letter-spacing: 2px; }}
.info-grid {{ display: flex; justify-content: space-between; margin-bottom: 15px; }}
.info-box {{ width: 48%; }}
.info-box h4 {{ font-size: 8pt; text-transform: uppercase; color: #002FA7; border-bottom: 1px solid #ddd; padding-bottom: 3px; margin-bottom: 6px; }}
.info-box p {{ font-size: 8.5pt; margin: 2px 0; }}
table {{ width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 8pt; }}
th {{ background: #002FA7; color: white; padding: 6px 4px; text-align: center; font-size: 7.5pt; }}
td {{ padding: 5px 4px; border-bottom: 1px solid #e5e5e5; }}
td.num {{ text-align: right; font-family: 'Courier New', monospace; }}
td.center {{ text-align: center; }}
td.right {{ text-align: right; font-weight: bold; }}
td.strong {{ font-weight: bold; }}
.specs {{ font-size: 7pt; color: #666; }}
.totals {{ margin-top: 10px; }}
.totals table {{ width: 50%; margin-left: auto; }}
.grand-total {{ font-size: 12pt; font-weight: bold; color: #002FA7; background: #f0f4ff !important; }}
.section {{ margin: 15px 0; }}
.section h3 {{ font-size: 10pt; color: #002FA7; border-bottom: 1px solid #ddd; padding-bottom: 3px; }}
.section ul {{ padding-left: 20px; }}
.section li {{ margin: 3px 0; font-size: 8.5pt; }}
.terms {{ font-size: 8pt; }}
.terms td {{ padding: 3px 8px; }}
.terms td:first-child {{ font-weight: bold; width: 30%; color: #333; }}
.appendix {{ margin-top: 20px; padding: 10px; background: #f9f9f9; border-left: 3px solid #002FA7; font-size: 8pt; }}
.footer {{ margin-top: 30px; border-top: 2px solid #002FA7; padding-top: 10px; }}
.signature {{ margin-top: 40px; }}
.signature-line {{ border-top: 1px solid #333; width: 200px; margin-top: 40px; padding-top: 5px; font-size: 8pt; }}
.stamp {{ font-size: 7pt; color: #888; text-align: center; margin-top: 20px; }}
</style>
</head>
<body>
<div class="header">
    <div>
        <div class="company-name">{company['name']}</div>
        <div class="company-details">
            {company['address']}<br>
            GSTIN: {company['gstin']} | PAN: {company['pan']}<br>
            CIN: {company['cin']} | UDYAM: {company['udyam']}<br>
            Email: {company['email']} | Phone: {company['phone']}
        </div>
    </div>
    <div style="text-align: right;">
        <div style="font-size: 8pt; color: #666;">Tax Invoice / Quotation</div>
        <div style="font-size: 11pt; font-weight: bold; color: #002FA7;">{quote_number}</div>
        <div style="font-size: 8pt;">Date: {quote_date}</div>
    </div>
</div>

<div class="quote-title">Commercial Quotation</div>

<div class="info-grid">
    <div class="info-box">
        <h4>Bill To / Client Details</h4>
        <p><strong>{rfp.get('client_name', 'Valued Client')}</strong></p>
        <p>{rfp.get('client_address', '')}</p>
        <p>State: {rfp.get('client_state', '')}</p>
        <p>Contact: {rfp.get('contact_person', '')}</p>
        <p>Email: {rfp.get('contact_email', '')}</p>
    </div>
    <div class="info-box">
        <h4>Quotation Details</h4>
        <p>Reference: {rfp.get('rfp_reference', 'As per your enquiry')}</p>
        <p>Subject: {rfp.get('subject', '')}</p>
        <p>Currency: {currency}</p>
        <p>Tax Mode: {summary.get('total_tax', {}).get('label', '')}</p>
        <p>Valid Until: {validity_date}</p>
    </div>
</div>

<table>
    <thead>
        <tr>
            <th>Sr</th><th>Description</th><th>HSN/SAC</th><th>Qty</th><th>Unit</th>
            <th>Unit Price ({currency_symbol})</th><th>Disc</th><th>Taxable Value</th>
            {tax_headers}
            <th>Total</th>
        </tr>
    </thead>
    <tbody>
        {items_html}
    </tbody>
</table>

<div class="totals">
    <table>
        <tr><td colspan="7"></td><td class="right">Subtotal:</td><td colspan="3" class="num">{currency_symbol} {format_currency(summary.get('total_sell_value', 0))}</td></tr>
        {total_tax_rows}
        <tr class="grand-total"><td colspan="7"></td><td class="right">GRAND TOTAL:</td><td colspan="3" class="num">{currency_symbol} {format_currency(summary.get('grand_total', 0))}</td></tr>
    </table>
</div>

{value_adds_html}

<div class="section">
    <h3>Terms & Conditions</h3>
    <table class="terms">
        <tr><td>Payment Terms</td><td>{payment_terms}</td></tr>
        <tr><td>Delivery</td><td>Within {delivery_days} days from PO receipt</td></tr>
        <tr><td>Warranty</td><td>{warranty_text}</td></tr>
        <tr><td>Validity</td><td>This quotation is valid for 30 days from date of issue</td></tr>
        <tr><td>Freight</td><td>Ex-works / FOB as applicable</td></tr>
        <tr><td>Packing</td><td>Standard industrial packing included</td></tr>
    </table>
</div>

<div class="section">
    <h3>Exclusions & Assumptions</h3>
    <ul>
        <li>Prices are subject to change in case of statutory levy changes</li>
        <li>Installation charges not included unless specified</li>
        <li>Civil/structural work not in scope</li>
        <li>Prices based on current raw material rates</li>
    </ul>
</div>

{strategy_html}

<div class="footer">
    <div class="info-grid">
        <div class="info-box">
            <h4>Bank Details for Payment</h4>
            <p>Bank: {company['bank_name']}</p>
            <p>Account: {company['bank_account']}</p>
            <p>IFSC: {company['bank_ifsc']}</p>
            <p>Branch: {company['bank_branch']}</p>
        </div>
        <div class="info-box signature">
            <div class="signature-line">
                Authorized Signatory<br>
                For {company['name']}
            </div>
        </div>
    </div>
</div>

<div class="stamp">
    This is a computer-generated quotation. Generated by SmartQuote AI Quotation Engine.
</div>
</body>
</html>"""
    return html


def format_currency(amount) -> str:
    """Format number in Indian numbering system"""
    if amount is None:
        return "0.00"
    amount = float(amount)
    if amount < 0:
        return f"-{format_currency(-amount)}"
    s = f"{amount:,.2f}"
    # Convert to Indian format (xx,xx,xxx.xx)
    parts = s.split('.')
    integer_part = parts[0].replace(',', '')
    decimal_part = parts[1] if len(parts) > 1 else "00"

    if len(integer_part) <= 3:
        return f"{integer_part}.{decimal_part}"

    last3 = integer_part[-3:]
    remaining = integer_part[:-3]
    groups = []
    while remaining:
        groups.insert(0, remaining[-2:])
        remaining = remaining[:-2]

    return f"{','.join(groups)},{last3}.{decimal_part}"


def generate_pdf_bytes(quote_data: dict) -> bytes:
    """Generate PDF bytes from quote data using WeasyPrint"""
    try:
        from weasyprint import HTML
        html_content = generate_quotation_html(quote_data)
        pdf_bytes = HTML(string=html_content).write_pdf()
        logger.info(f"PDF generated: {len(pdf_bytes)} bytes")
        return pdf_bytes
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise
