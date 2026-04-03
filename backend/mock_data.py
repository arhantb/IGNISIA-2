"""
Mock Data for Autonomous RFP Response & Competitive Quotation Orchestrator
- 30 SKUs (Indian electrical/industrial components)
- 5 competitors per SKU
- 6 sample RFPs covering different scenarios
- Currency conversion rates
- Tax rules
"""

CURRENCY_RATES = {
    "INR": 1.0,
    "USD": 0.01193,
    "EUR": 0.01095,
    "AED": 0.04381,
}

TAX_RULES = {
    "intra_state": {"cgst": 9.0, "sgst": 9.0, "igst": 0.0, "label": "CGST+SGST"},
    "inter_state": {"cgst": 0.0, "sgst": 0.0, "igst": 18.0, "label": "IGST"},
    "export": {"cgst": 0.0, "sgst": 0.0, "igst": 0.0, "label": "Export (Zero-rated)"},
    "sez": {"cgst": 0.0, "sgst": 0.0, "igst": 0.0, "label": "SEZ (Zero-rated)"},
}

COMPANY_PROFILE = {
    "name": "SmartQuote Electric Pvt. Ltd.",
    "address": "Plot No. 42, MIDC Industrial Area, Andheri East, Mumbai 400093, Maharashtra",
    "gstin": "27AABCS1429B1ZS",
    "pan": "AABCS1429B",
    "cin": "U31200MH2018PTC123456",
    "udyam": "UDYAM-MH-07-0012345",
    "email": "quotes@smartquote.in",
    "phone": "+91 22 4567 8900",
    "website": "www.smartquote.in",
    "bank_name": "HDFC Bank",
    "bank_account": "50200012345678",
    "bank_ifsc": "HDFC0001234",
    "bank_branch": "Andheri East, Mumbai",
    "state": "Maharashtra",
    "state_code": "27",
}

SKU_CATALOG = [
    {"sku_id": "SKU-MCB-001", "name": "Miniature Circuit Breaker 32A", "category": "Switchgear", "hsn": "8536", "unit": "Nos", "base_cost": 285, "sell_price": 450, "mrp": 520, "margin_target": 35, "margin_floor": 15, "stock": 500, "lead_time_days": 3, "warranty_months": 24, "specs": {"voltage": "240V AC", "current": "32A", "poles": 3, "breaking_capacity": "10kA"}},
    {"sku_id": "SKU-MCB-002", "name": "Miniature Circuit Breaker 63A", "category": "Switchgear", "hsn": "8536", "unit": "Nos", "base_cost": 420, "sell_price": 680, "mrp": 780, "margin_target": 38, "margin_floor": 15, "stock": 350, "lead_time_days": 3, "warranty_months": 24, "specs": {"voltage": "240V AC", "current": "63A", "poles": 3, "breaking_capacity": "10kA"}},
    {"sku_id": "SKU-MCCB-001", "name": "MCCB 250A 3P", "category": "Switchgear", "hsn": "8536", "unit": "Nos", "base_cost": 4200, "sell_price": 6800, "mrp": 7800, "margin_target": 38, "margin_floor": 18, "stock": 80, "lead_time_days": 7, "warranty_months": 36, "specs": {"voltage": "415V AC", "current": "250A", "poles": 3, "breaking_capacity": "36kA"}},
    {"sku_id": "SKU-MCCB-002", "name": "MCCB 400A 4P", "category": "Switchgear", "hsn": "8536", "unit": "Nos", "base_cost": 8500, "sell_price": 13500, "mrp": 15500, "margin_target": 37, "margin_floor": 18, "stock": 45, "lead_time_days": 10, "warranty_months": 36, "specs": {"voltage": "415V AC", "current": "400A", "poles": 4, "breaking_capacity": "50kA"}},
    {"sku_id": "SKU-ACB-001", "name": "Air Circuit Breaker 1600A", "category": "Switchgear", "hsn": "8536", "unit": "Nos", "base_cost": 85000, "sell_price": 135000, "mrp": 155000, "margin_target": 37, "margin_floor": 20, "stock": 12, "lead_time_days": 21, "warranty_months": 36, "specs": {"voltage": "415V AC", "current": "1600A", "poles": 4, "breaking_capacity": "65kA"}},
    {"sku_id": "SKU-TFR-001", "name": "Distribution Transformer 100kVA", "category": "Transformers", "hsn": "8504", "unit": "Nos", "base_cost": 185000, "sell_price": 275000, "mrp": 310000, "margin_target": 32, "margin_floor": 15, "stock": 8, "lead_time_days": 30, "warranty_months": 60, "specs": {"rating": "100kVA", "voltage": "11kV/433V", "type": "Oil-cooled", "efficiency": "98.5%"}},
    {"sku_id": "SKU-TFR-002", "name": "Distribution Transformer 250kVA", "category": "Transformers", "hsn": "8504", "unit": "Nos", "base_cost": 320000, "sell_price": 480000, "mrp": 545000, "margin_target": 33, "margin_floor": 15, "stock": 5, "lead_time_days": 45, "warranty_months": 60, "specs": {"rating": "250kVA", "voltage": "11kV/433V", "type": "Oil-cooled", "efficiency": "98.8%"}},
    {"sku_id": "SKU-CBL-001", "name": "XLPE Cable 3.5C x 240 sqmm", "category": "Cables", "hsn": "8544", "unit": "Mtr", "base_cost": 2800, "sell_price": 4200, "mrp": 4800, "margin_target": 33, "margin_floor": 12, "stock": 2000, "lead_time_days": 5, "warranty_months": 120, "specs": {"cores": "3.5C", "size": "240 sqmm", "type": "XLPE", "voltage_grade": "1.1kV"}},
    {"sku_id": "SKU-CBL-002", "name": "XLPE Cable 4C x 95 sqmm", "category": "Cables", "hsn": "8544", "unit": "Mtr", "base_cost": 1100, "sell_price": 1700, "mrp": 1950, "margin_target": 35, "margin_floor": 12, "stock": 3000, "lead_time_days": 3, "warranty_months": 120, "specs": {"cores": "4C", "size": "95 sqmm", "type": "XLPE", "voltage_grade": "1.1kV"}},
    {"sku_id": "SKU-CBL-003", "name": "Control Cable 12C x 2.5 sqmm", "category": "Cables", "hsn": "8544", "unit": "Mtr", "base_cost": 210, "sell_price": 340, "mrp": 390, "margin_target": 38, "margin_floor": 15, "stock": 5000, "lead_time_days": 3, "warranty_months": 60, "specs": {"cores": "12C", "size": "2.5 sqmm", "type": "PVC/PVC", "voltage_grade": "1.1kV"}},
    {"sku_id": "SKU-PNL-001", "name": "LT Distribution Panel 800A", "category": "Panels", "hsn": "8537", "unit": "Nos", "base_cost": 125000, "sell_price": 195000, "mrp": 225000, "margin_target": 36, "margin_floor": 18, "stock": 6, "lead_time_days": 25, "warranty_months": 24, "specs": {"rating": "800A", "type": "Indoor", "form": "Form-4", "ip_rating": "IP42"}},
    {"sku_id": "SKU-PNL-002", "name": "Motor Control Center 400A", "category": "Panels", "hsn": "8537", "unit": "Nos", "base_cost": 185000, "sell_price": 290000, "mrp": 335000, "margin_target": 36, "margin_floor": 18, "stock": 4, "lead_time_days": 35, "warranty_months": 24, "specs": {"rating": "400A", "type": "Indoor", "feeders": 12, "ip_rating": "IP42"}},
    {"sku_id": "SKU-PNL-003", "name": "APFC Panel 150kVAR", "category": "Panels", "hsn": "8537", "unit": "Nos", "base_cost": 95000, "sell_price": 148000, "mrp": 170000, "margin_target": 35, "margin_floor": 15, "stock": 8, "lead_time_days": 20, "warranty_months": 24, "specs": {"rating": "150kVAR", "steps": 6, "type": "Automatic", "ip_rating": "IP42"}},
    {"sku_id": "SKU-MTR-001", "name": "3-Phase Induction Motor 15HP", "category": "Motors", "hsn": "8501", "unit": "Nos", "base_cost": 18500, "sell_price": 28000, "mrp": 32000, "margin_target": 34, "margin_floor": 15, "stock": 25, "lead_time_days": 7, "warranty_months": 24, "specs": {"power": "15HP", "voltage": "415V", "rpm": 1440, "efficiency": "IE3"}},
    {"sku_id": "SKU-MTR-002", "name": "3-Phase Induction Motor 50HP", "category": "Motors", "hsn": "8501", "unit": "Nos", "base_cost": 52000, "sell_price": 82000, "mrp": 94000, "margin_target": 36, "margin_floor": 15, "stock": 10, "lead_time_days": 14, "warranty_months": 24, "specs": {"power": "50HP", "voltage": "415V", "rpm": 1470, "efficiency": "IE3"}},
    {"sku_id": "SKU-VFD-001", "name": "Variable Frequency Drive 15kW", "category": "Drives", "hsn": "8504", "unit": "Nos", "base_cost": 24000, "sell_price": 38000, "mrp": 44000, "margin_target": 36, "margin_floor": 15, "stock": 30, "lead_time_days": 5, "warranty_months": 24, "specs": {"power": "15kW", "voltage": "415V", "type": "AC Drive", "control": "V/F + Sensorless Vector"}},
    {"sku_id": "SKU-VFD-002", "name": "Variable Frequency Drive 37kW", "category": "Drives", "hsn": "8504", "unit": "Nos", "base_cost": 55000, "sell_price": 86000, "mrp": 99000, "margin_target": 36, "margin_floor": 15, "stock": 15, "lead_time_days": 7, "warranty_months": 24, "specs": {"power": "37kW", "voltage": "415V", "type": "AC Drive", "control": "Sensorless Vector + Torque"}},
    {"sku_id": "SKU-UPS-001", "name": "Online UPS 10kVA", "category": "Power Backup", "hsn": "8504", "unit": "Nos", "base_cost": 75000, "sell_price": 118000, "mrp": 135000, "margin_target": 36, "margin_floor": 18, "stock": 15, "lead_time_days": 7, "warranty_months": 36, "specs": {"rating": "10kVA", "type": "Online Double Conversion", "battery": "Internal SMF", "backup": "30 min"}},
    {"sku_id": "SKU-UPS-002", "name": "Online UPS 30kVA", "category": "Power Backup", "hsn": "8504", "unit": "Nos", "base_cost": 195000, "sell_price": 310000, "mrp": 355000, "margin_target": 37, "margin_floor": 18, "stock": 6, "lead_time_days": 14, "warranty_months": 36, "specs": {"rating": "30kVA", "type": "Online Double Conversion", "battery": "External", "backup": "Configurable"}},
    {"sku_id": "SKU-SOL-001", "name": "Solar Panel 540W Mono PERC", "category": "Solar", "hsn": "8541", "unit": "Nos", "base_cost": 12500, "sell_price": 19500, "mrp": 22500, "margin_target": 36, "margin_floor": 15, "stock": 200, "lead_time_days": 5, "warranty_months": 300, "specs": {"power": "540W", "type": "Mono PERC", "voltage": "41.2V", "efficiency": "21.3%"}},
    {"sku_id": "SKU-SOL-002", "name": "Solar Inverter 50kW Grid-Tie", "category": "Solar", "hsn": "8504", "unit": "Nos", "base_cost": 185000, "sell_price": 290000, "mrp": 335000, "margin_target": 36, "margin_floor": 18, "stock": 8, "lead_time_days": 10, "warranty_months": 60, "specs": {"rating": "50kW", "type": "Grid-Tie String", "mppt": 4, "efficiency": "98.6%"}},
    {"sku_id": "SKU-LED-001", "name": "LED Panel Light 40W 2x2", "category": "Lighting", "hsn": "9405", "unit": "Nos", "base_cost": 650, "sell_price": 1050, "mrp": 1200, "margin_target": 38, "margin_floor": 15, "stock": 1000, "lead_time_days": 3, "warranty_months": 36, "specs": {"power": "40W", "lumens": 4800, "cct": "4000K", "size": "600x600mm"}},
    {"sku_id": "SKU-LED-002", "name": "LED Street Light 120W", "category": "Lighting", "hsn": "9405", "unit": "Nos", "base_cost": 3200, "sell_price": 5100, "mrp": 5800, "margin_target": 37, "margin_floor": 15, "stock": 300, "lead_time_days": 5, "warranty_months": 60, "specs": {"power": "120W", "lumens": 16800, "cct": "5700K", "ip_rating": "IP66"}},
    {"sku_id": "SKU-MET-001", "name": "Multifunction Energy Meter", "category": "Metering", "hsn": "9028", "unit": "Nos", "base_cost": 3500, "sell_price": 5500, "mrp": 6300, "margin_target": 36, "margin_floor": 15, "stock": 100, "lead_time_days": 5, "warranty_months": 24, "specs": {"type": "Digital", "parameters": "V,A,kW,kWh,PF,Hz", "accuracy": "Class 0.5", "communication": "RS485 Modbus"}},
    {"sku_id": "SKU-MET-002", "name": "CT Ratio 400/5A Ring Type", "category": "Metering", "hsn": "8504", "unit": "Nos", "base_cost": 450, "sell_price": 720, "mrp": 820, "margin_target": 37, "margin_floor": 15, "stock": 200, "lead_time_days": 3, "warranty_months": 24, "specs": {"ratio": "400/5A", "type": "Ring", "accuracy": "Class 1.0", "burden": "5VA"}},
    {"sku_id": "SKU-ERT-001", "name": "Earthing Electrode Copper 3m", "category": "Earthing", "hsn": "7413", "unit": "Nos", "base_cost": 2800, "sell_price": 4500, "mrp": 5200, "margin_target": 38, "margin_floor": 15, "stock": 150, "lead_time_days": 5, "warranty_months": 120, "specs": {"material": "Pure Copper", "length": "3m", "diameter": "40mm", "type": "Solid Rod"}},
    {"sku_id": "SKU-SRG-001", "name": "Surge Protection Device Type-2", "category": "Protection", "hsn": "8536", "unit": "Nos", "base_cost": 3800, "sell_price": 6000, "mrp": 6900, "margin_target": 36, "margin_floor": 15, "stock": 80, "lead_time_days": 5, "warranty_months": 24, "specs": {"type": "Type-2", "Imax": "40kA", "Up": "1.5kV", "poles": 4}},
    {"sku_id": "SKU-BUS-001", "name": "Busbar Trunking System 1600A", "category": "Busbar", "hsn": "8536", "unit": "Mtr", "base_cost": 8500, "sell_price": 13500, "mrp": 15500, "margin_target": 37, "margin_floor": 18, "stock": 100, "lead_time_days": 21, "warranty_months": 36, "specs": {"rating": "1600A", "type": "Sandwich", "ip_rating": "IP54", "material": "Aluminium"}},
    {"sku_id": "SKU-DG-001", "name": "Diesel Generator 125kVA", "category": "Power Backup", "hsn": "8502", "unit": "Nos", "base_cost": 650000, "sell_price": 980000, "mrp": 1125000, "margin_target": 33, "margin_floor": 15, "stock": 3, "lead_time_days": 30, "warranty_months": 24, "specs": {"rating": "125kVA", "fuel": "Diesel", "type": "Silent", "ats": "Included"}},
    {"sku_id": "SKU-CAB-001", "name": "Cable Tray Perforated 300mm", "category": "Cable Management", "hsn": "7308", "unit": "Mtr", "base_cost": 320, "sell_price": 520, "mrp": 600, "margin_target": 38, "margin_floor": 15, "stock": 2000, "lead_time_days": 5, "warranty_months": 60, "specs": {"width": "300mm", "type": "Perforated", "material": "GI", "thickness": "1.6mm"}},
]

COMPETITORS = {
    "Larsen & Toubro": {"shortname": "L&T", "reputation": "Premium", "delivery_days_extra": 0, "warranty_extra_months": 0},
    "Siemens India": {"shortname": "Siemens", "reputation": "Premium", "delivery_days_extra": 5, "warranty_extra_months": 0},
    "Schneider Electric": {"shortname": "Schneider", "reputation": "Premium", "delivery_days_extra": 3, "warranty_extra_months": 0},
    "Havells India": {"shortname": "Havells", "reputation": "Mid-Premium", "delivery_days_extra": -2, "warranty_extra_months": 6},
    "ABB India": {"shortname": "ABB", "reputation": "Premium", "delivery_days_extra": 7, "warranty_extra_months": 0},
}

# Competitor prices per SKU - ratio relative to our sell_price
COMPETITOR_PRICE_RATIOS = {
    "SKU-MCB-001": {"Larsen & Toubro": 1.12, "Siemens India": 1.18, "Schneider Electric": 1.08, "Havells India": 0.92, "ABB India": 1.15},
    "SKU-MCB-002": {"Larsen & Toubro": 1.10, "Siemens India": 1.15, "Schneider Electric": 1.05, "Havells India": 0.90, "ABB India": 1.12},
    "SKU-MCCB-001": {"Larsen & Toubro": 1.08, "Siemens India": 1.20, "Schneider Electric": 1.12, "Havells India": 0.88, "ABB India": 1.15},
    "SKU-MCCB-002": {"Larsen & Toubro": 1.05, "Siemens India": 1.18, "Schneider Electric": 1.10, "Havells India": 0.85, "ABB India": 1.12},
    "SKU-ACB-001": {"Larsen & Toubro": 1.15, "Siemens India": 1.22, "Schneider Electric": 1.18, "Havells India": 0.95, "ABB India": 1.20},
    "SKU-TFR-001": {"Larsen & Toubro": 1.10, "Siemens India": 1.25, "Schneider Electric": 1.15, "Havells India": 0.82, "ABB India": 1.18},
    "SKU-TFR-002": {"Larsen & Toubro": 1.08, "Siemens India": 1.22, "Schneider Electric": 1.12, "Havells India": 0.80, "ABB India": 1.15},
    "SKU-CBL-001": {"Larsen & Toubro": 1.05, "Siemens India": 1.10, "Schneider Electric": 1.08, "Havells India": 0.88, "ABB India": 1.06},
    "SKU-CBL-002": {"Larsen & Toubro": 1.06, "Siemens India": 1.12, "Schneider Electric": 1.09, "Havells India": 0.90, "ABB India": 1.08},
    "SKU-CBL-003": {"Larsen & Toubro": 1.04, "Siemens India": 1.08, "Schneider Electric": 1.06, "Havells India": 0.92, "ABB India": 1.05},
    "SKU-PNL-001": {"Larsen & Toubro": 1.12, "Siemens India": 1.25, "Schneider Electric": 1.18, "Havells India": 0.78, "ABB India": 1.20},
    "SKU-PNL-002": {"Larsen & Toubro": 1.10, "Siemens India": 1.22, "Schneider Electric": 1.15, "Havells India": 0.75, "ABB India": 1.18},
    "SKU-PNL-003": {"Larsen & Toubro": 1.08, "Siemens India": 1.18, "Schneider Electric": 1.12, "Havells India": 0.85, "ABB India": 1.15},
    "SKU-MTR-001": {"Larsen & Toubro": 1.10, "Siemens India": 1.20, "Schneider Electric": 1.12, "Havells India": 0.90, "ABB India": 1.18},
    "SKU-MTR-002": {"Larsen & Toubro": 1.08, "Siemens India": 1.18, "Schneider Electric": 1.10, "Havells India": 0.88, "ABB India": 1.15},
    "SKU-VFD-001": {"Larsen & Toubro": 1.12, "Siemens India": 1.25, "Schneider Electric": 1.15, "Havells India": 0.92, "ABB India": 1.22},
    "SKU-VFD-002": {"Larsen & Toubro": 1.10, "Siemens India": 1.22, "Schneider Electric": 1.12, "Havells India": 0.90, "ABB India": 1.20},
    "SKU-UPS-001": {"Larsen & Toubro": 1.15, "Siemens India": 1.28, "Schneider Electric": 1.20, "Havells India": 0.88, "ABB India": 1.22},
    "SKU-UPS-002": {"Larsen & Toubro": 1.12, "Siemens India": 1.25, "Schneider Electric": 1.18, "Havells India": 0.85, "ABB India": 1.20},
    "SKU-SOL-001": {"Larsen & Toubro": 1.08, "Siemens India": 1.15, "Schneider Electric": 1.10, "Havells India": 0.90, "ABB India": 1.12},
    "SKU-SOL-002": {"Larsen & Toubro": 1.10, "Siemens India": 1.20, "Schneider Electric": 1.15, "Havells India": 0.88, "ABB India": 1.18},
    "SKU-LED-001": {"Larsen & Toubro": 1.05, "Siemens India": 1.10, "Schneider Electric": 1.08, "Havells India": 0.85, "ABB India": 1.06},
    "SKU-LED-002": {"Larsen & Toubro": 1.08, "Siemens India": 1.15, "Schneider Electric": 1.10, "Havells India": 0.88, "ABB India": 1.12},
    "SKU-MET-001": {"Larsen & Toubro": 1.10, "Siemens India": 1.20, "Schneider Electric": 1.12, "Havells India": 0.90, "ABB India": 1.15},
    "SKU-MET-002": {"Larsen & Toubro": 1.08, "Siemens India": 1.12, "Schneider Electric": 1.10, "Havells India": 0.92, "ABB India": 1.08},
    "SKU-ERT-001": {"Larsen & Toubro": 1.05, "Siemens India": 1.10, "Schneider Electric": 1.08, "Havells India": 0.90, "ABB India": 1.06},
    "SKU-SRG-001": {"Larsen & Toubro": 1.10, "Siemens India": 1.18, "Schneider Electric": 1.12, "Havells India": 0.88, "ABB India": 1.15},
    "SKU-BUS-001": {"Larsen & Toubro": 1.12, "Siemens India": 1.25, "Schneider Electric": 1.18, "Havells India": 0.82, "ABB India": 1.20},
    "SKU-DG-001": {"Larsen & Toubro": 1.08, "Siemens India": 1.15, "Schneider Electric": 1.12, "Havells India": 0.75, "ABB India": 1.10},
    "SKU-CAB-001": {"Larsen & Toubro": 1.05, "Siemens India": 1.08, "Schneider Electric": 1.06, "Havells India": 0.88, "ABB India": 1.04},
}

SAMPLE_RFPS = [
    {
        "title": "Municipal Office Electrical Supply - Standard",
        "client_name": "Pune Municipal Corporation",
        "client_email": "procurement@pmc.gov.in",
        "client_state": "Maharashtra",
        "scenario": "normal",
        "currency": "INR",
        "tax_type": "intra_state",
        "deadline": "2026-03-15",
        "raw_text": """REQUEST FOR PROPOSAL
Pune Municipal Corporation - Electrical Supply & Installation
Ref: PMC/ELECT/2026/0042

Dear Vendor,

We invite proposals for the supply and installation of electrical equipment for the new PMC Administrative Block at Shivajinagar, Pune.

Requirements:
1. MCB 32A Triple Pole - 120 numbers for office distribution boards
2. MCCB 250A Triple Pole - 4 numbers for main panel incoming
3. LT Distribution Panel 800A - 2 numbers for ground and first floor
4. XLPE Cable 4C x 95 sqmm - 500 meters for main feeders
5. Control Cable 12C x 2.5 sqmm - 300 meters
6. LED Panel Light 40W 2x2 - 250 numbers for office areas
7. Multifunction Energy Meter - 8 numbers for floor-wise metering
8. Cable Tray Perforated 300mm - 200 meters
9. Earthing Electrode Copper 3m - 12 numbers
10. Surge Protection Device Type-2 - 6 numbers

Delivery Timeline: Within 45 days of PO
Payment Terms: 30 days from delivery
Warranty: Minimum 2 years on all items
Quality: BIS/ISI marked, Type-tested as applicable

Please submit your best commercial offer with GST breakup.

Regards,
Chief Engineer (Electrical)
Pune Municipal Corporation"""
    },
    {
        "title": "Government Hospital Equipment - Below Cost Competitor",
        "client_name": "AIIMS Nagpur",
        "client_email": "stores@aiimsnagpur.edu.in",
        "client_state": "Maharashtra",
        "scenario": "below_cost_competitor",
        "currency": "INR",
        "tax_type": "intra_state",
        "deadline": "2026-02-28",
        "raw_text": """TENDER NOTICE
All India Institute of Medical Sciences, Nagpur
Tender No: AIIMS-NGP/ELECT/2025-26/089

Subject: Supply of Electrical Equipment for New OPD Block

AIIMS Nagpur invites sealed tenders for supply of following electrical items:

1. Online UPS 30kVA with 1-hour battery backup - 4 numbers (Critical for OT & ICU)
2. Online UPS 10kVA - 8 numbers (for diagnostic labs)
3. MCCB 400A 4-Pole - 6 numbers
4. Variable Frequency Drive 15kW - 10 numbers (AHU applications)
5. 3-Phase Induction Motor 15HP - 8 numbers
6. APFC Panel 150kVAR - 2 numbers
7. Multifunction Energy Meter - 15 numbers
8. CT Ratio 400/5A Ring Type - 30 numbers
9. Surge Protection Device Type-2 - 12 numbers

Note: L1 bidder from previous tender quoted 25% below market rates.
Government rates applicable. EMD of Rs 2,00,000 required.

Delivery: 30 days strict. Penalty of 0.5% per week for delay.
Payment: 60 days from successful commissioning.
Warranty: Minimum 3 years comprehensive.

This is a GeM/CPPP listed tender. MSME preference applicable."""
    },
    {
        "title": "Factory Emergency Power Backup - Urgent",
        "client_name": "Tata Motors Plant, Sanand",
        "client_email": "maintenance@tatamotors-sanand.com",
        "client_state": "Gujarat",
        "scenario": "urgent",
        "currency": "INR",
        "tax_type": "inter_state",
        "deadline": "2026-02-20",
        "raw_text": """URGENT REQUIREMENT - IMMEDIATE DELIVERY NEEDED

From: Tata Motors Ltd, Sanand Plant, Gujarat
To: All Empanelled Vendors

Subject: Emergency Power Backup System for Paint Shop

Due to critical transformer failure, we require IMMEDIATE supply of:

1. Diesel Generator 125kVA Silent - 2 numbers (URGENT - within 7 days)
2. Online UPS 30kVA - 2 numbers (within 10 days)
3. Air Circuit Breaker 1600A - 1 number (within 5 days)
4. MCCB 400A 4-Pole - 4 numbers (within 3 days)
5. XLPE Cable 3.5C x 240 sqmm - 200 meters (within 3 days)
6. Busbar Trunking System 1600A - 50 meters (within 14 days)
7. Distribution Transformer 250kVA - 1 number (within 21 days)

CRITICAL: Production line downtime costing Rs 15 lakhs/day.
Premium pricing acceptable for guaranteed delivery.

Payment: Advance payment possible for confirmed delivery.
Quality: Must meet Tata Motors vendor quality standards.

Contact: Mr. Rajesh Kumar, Head - Electrical Maintenance
Phone: +91 98765 43210"""
    },
    {
        "title": "Cross-State Industrial Project - Interstate IGST",
        "client_name": "Reliance Industries, Jamnagar",
        "client_email": "procurement@ril.com",
        "client_state": "Gujarat",
        "scenario": "interstate_igst",
        "currency": "INR",
        "tax_type": "inter_state",
        "deadline": "2026-04-30",
        "raw_text": """REQUEST FOR QUOTATION
Reliance Industries Limited
Jamnagar Refinery Complex, Gujarat

RFQ Ref: RIL/JAM/ELECT/2026/Q-1234

Dear Vendor,

Please quote for the following electrical equipment for our refinery expansion project:

1. Distribution Transformer 250kVA - 3 numbers
2. Distribution Transformer 100kVA - 5 numbers
3. LT Distribution Panel 800A - 4 numbers
4. Motor Control Center 400A - 3 numbers
5. Air Circuit Breaker 1600A - 2 numbers
6. MCCB 250A 3P - 20 numbers
7. Variable Frequency Drive 37kW - 8 numbers
8. Variable Frequency Drive 15kW - 15 numbers
9. 3-Phase Induction Motor 50HP - 6 numbers
10. 3-Phase Induction Motor 15HP - 12 numbers
11. XLPE Cable 3.5C x 240 sqmm - 1000 meters
12. XLPE Cable 4C x 95 sqmm - 2000 meters
13. Solar Panel 540W Mono PERC - 100 numbers
14. Solar Inverter 50kW Grid-Tie - 2 numbers

Note: Vendor must be from Maharashtra. IGST applicable.
Delivery: Staggered over 90 days as per our schedule.
Payment: 45 days from each delivery milestone.
Quality: PESO/BIS certified. Third-party inspection required."""
    },
    {
        "title": "Middle East Export Project - International USD",
        "client_name": "Dubai Electric & Water Authority (DEWA)",
        "client_email": "procurement@dewa.gov.ae",
        "client_state": "International",
        "scenario": "international_usd",
        "currency": "USD",
        "tax_type": "export",
        "deadline": "2026-05-15",
        "raw_text": """REQUEST FOR PROPOSAL
Dubai Electric & Water Authority
P.O. Box 564, Dubai, UAE

RFP No: DEWA/PROC/2026/EQ-789

Subject: Supply of Electrical Equipment for Al Quoz Substation Upgrade

DEWA invites proposals from qualified Indian manufacturers for:

1. Distribution Transformer 250kVA (11kV/433V) - 4 numbers
2. Distribution Transformer 100kVA (11kV/433V) - 6 numbers
3. LT Distribution Panel 800A - 6 numbers
4. Motor Control Center 400A - 4 numbers
5. Air Circuit Breaker 1600A - 3 numbers
6. MCCB 400A 4-Pole - 10 numbers
7. MCCB 250A 3-Pole - 25 numbers
8. Online UPS 30kVA - 4 numbers
9. LED Street Light 120W - 200 numbers
10. Multifunction Energy Meter - 20 numbers

Currency: All prices in USD. FOB Mumbai port.
Delivery: CIF Dubai within 120 days.
Payment: Letter of Credit, 90 days.
Standards: IEC certified, DEWA approved specifications.
Documentation: Material certificates, test reports, O&M manuals.

Note: Indian exporters with DEWA pre-qualification preferred.
Custom duties and local taxes handled by DEWA."""
    },
    {
        "title": "Smart Grid MSME Tender - Government",
        "client_name": "MSME Development Institute, Chennai",
        "client_email": "di-chennai@msme.gov.in",
        "client_state": "Tamil Nadu",
        "scenario": "govt_msme",
        "currency": "INR",
        "tax_type": "inter_state",
        "deadline": "2026-03-31",
        "raw_text": """GOVERNMENT OF INDIA
Ministry of Micro, Small and Medium Enterprises
MSME Development Institute, Chennai

TENDER NOTIFICATION
Tender No: MSME-DI-CHN/SMART-GRID/2025-26/012

Subject: Smart Grid Pilot Project for MSME Industrial Cluster, Ambattur

The MSME-DI Chennai invites tenders from registered MSME vendors for:

1. Solar Panel 540W Mono PERC - 50 numbers
2. Solar Inverter 50kW Grid-Tie - 1 number
3. APFC Panel 150kVAR - 3 numbers
4. Multifunction Energy Meter with IoT - 25 numbers
5. LED Panel Light 40W 2x2 - 150 numbers
6. LED Street Light 120W - 50 numbers
7. Online UPS 10kVA - 5 numbers
8. MCB 63A Triple Pole - 50 numbers
9. Earthing Electrode Copper 3m - 20 numbers
10. Cable Tray Perforated 300mm - 300 meters

Eligibility:
- Must be registered MSME/Udyam
- Turnover minimum Rs 1 crore in last 3 years
- Prior experience in government projects preferred

EMD: Rs 1,00,000 (MSME exempted with valid certificate)
Payment: 30 days from delivery and acceptance.
MSME preference: 25% purchase preference as per government policy.

Contact: Director, MSME-DI Chennai
Address: 65, GST Road, Guindy, Chennai - 600032"""
    },
]


def get_competitor_prices(sku_id: str) -> list:
    """Get competitor prices for a given SKU"""
    sku = next((s for s in SKU_CATALOG if s["sku_id"] == sku_id), None)
    if not sku:
        return []
    ratios = COMPETITOR_PRICE_RATIOS.get(sku_id, {})
    result = []
    for comp_name, ratio in ratios.items():
        comp_info = COMPETITORS[comp_name]
        result.append({
            "competitor": comp_name,
            "shortname": comp_info["shortname"],
            "price": round(sku["sell_price"] * ratio),
            "reputation": comp_info["reputation"],
            "delivery_extra_days": comp_info["delivery_days_extra"],
            "warranty_extra_months": comp_info["warranty_extra_months"],
        })
    return result


def convert_currency(amount_inr: float, target_currency: str) -> float:
    """Convert INR amount to target currency"""
    rate = CURRENCY_RATES.get(target_currency, 1.0)
    return round(amount_inr * rate, 2)


def get_tax_components(tax_type: str, taxable_value: float) -> dict:
    """Calculate tax components based on tax type"""
    rules = TAX_RULES.get(tax_type, TAX_RULES["intra_state"])
    cgst = round(taxable_value * rules["cgst"] / 100, 2)
    sgst = round(taxable_value * rules["sgst"] / 100, 2)
    igst = round(taxable_value * rules["igst"] / 100, 2)
    total_tax = cgst + sgst + igst
    return {
        "cgst_rate": rules["cgst"],
        "sgst_rate": rules["sgst"],
        "igst_rate": rules["igst"],
        "cgst": cgst,
        "sgst": sgst,
        "igst": igst,
        "total_tax": total_tax,
        "label": rules["label"],
    }
