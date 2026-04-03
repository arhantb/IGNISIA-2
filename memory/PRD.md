# SmartQuote - Autonomous RFP Response & Competitive Quotation Orchestrator

## Original Problem Statement
Build an end-to-end Autonomous RFP Response & Competitive Quotation Orchestrator for Indian SMEs. Multi-agent AI pipeline that parses RFPs, matches products to SKU catalog, analyzes competitor pricing, applies pricing strategies, generates Indian-standard GST-compliant PDF quotations, with approval workflows for both SME owners and clients.

## Architecture
- **Backend**: FastAPI + MongoDB + 6 Python agents + WeasyPrint PDF
- **Frontend**: React + Tailwind + Shadcn UI (Swiss design system)
- **LLM**: Gemini 3 Flash (only for RFP parsing/extraction)
- **Pricing**: Pure deterministic Python rules engine (NO LLM)
- **Auth**: JWT role-based (Client, Sales, Owner, Admin)
- **PDF**: WeasyPrint Indian business standard quotation

## User Personas
1. **Client/Buyer**: Submits RFPs, reviews quotations, approves/rejects
2. **Sales Executive**: Processes RFPs, runs pipeline, manages quotes
3. **Business Owner**: Approves high-risk quotes, reviews strategy rationale
4. **Admin**: Full system access, manages users

## Core Requirements (Static)
- Multi-agent pipeline: Parse → Price → Compete → Govern → Draft
- Indian business quotation: GSTIN, HSN/SAC, CGST/SGST/IGST
- Competitive pricing intelligence with value-defense strategy
- Role-based approval workflow
- Client self-service portal
- PDF generation with WeasyPrint
- 30 SKU catalog, 5 competitors per SKU, 6 sample RFPs

## What's Been Implemented (April 3, 2026)
### Backend (PRIORITY - 96.2% test pass rate)
- [x] JWT auth with 4 roles (admin, owner, sales, client)
- [x] 4 demo accounts seeded on startup
- [x] RFP submission and listing
- [x] 6-agent pipeline: RFP Parser (Gemini 3 Flash), Pricing Engine, Competitor Analysis, Governance, Orchestrator, PDF Generator
- [x] 30 SKU electrical/industrial catalog
- [x] 5 competitor pricing sources per SKU
- [x] 6 sample RFPs (normal, below-cost, urgent, IGST, international USD, MSME)
- [x] Pricing strategy engine: STANDARD / DEFEND_MARGIN / VALUE_DEFENSE / PREMIUM_URGENCY
- [x] Tax logic: CGST+SGST (intra), IGST (inter), Export (zero-rated)
- [x] Multi-currency: INR, USD, EUR, AED
- [x] Governance checks: value threshold, margin floor, strategy review, international, stock
- [x] Owner approval workflow with decision log
- [x] Client portal: quote view, approve/reject/request changes
- [x] PDF generation: Indian standard with GSTIN, HSN/SAC, bank details
- [x] Audit trail for every action
- [x] Dashboard KPIs: total RFPs, pending, pipeline value, avg margin

### Frontend (85% test pass rate)
- [x] Landing page with Swiss design, feature cards, stats
- [x] Login with demo account buttons
- [x] Registration with role selection
- [x] SME Dashboard with KPI cards and RFP table
- [x] Submit RFP page with sample RFP loading
- [x] RFP Detail with 5-tab view (Pricing, Competitor, Governance, Parsed, Audit)
- [x] Client Portal with quote review and action buttons
- [x] PDF download functionality

## Prioritized Backlog
### P0 (Critical)
- None - core MVP complete

### P1 (Next Sprint)
- File upload for RFP (PDF/DOCX support)
- Editable line items in approval screen
- Interactive "what-if" pricing sliders
- Quote version history
- Email notifications on status change

### P2 (Enhancement)
- Real competitor API integration
- Recharts-based analytics dashboard
- Automated go/no-go scoring
- Cross-selling recommendations
- Continuous learning from won/lost bids
- Mobile responsive optimization

## Next Tasks
1. Add file upload for PDF/DOCX RFPs
2. Add interactive pricing sliders (what-if analysis)
3. Add email notifications
4. Add recharts analytics
5. Enhance client portal with PDF preview

## Update Log - April 3, 2026 (Iteration 2)
### Changes Made:
- Renamed from "SmartQuote" to "RFPFlow" across all pages (Landing, Login, Register, Dashboard, RFPDetail, ClientPortal)
- Updated logo to custom infinity-shaped blue logo with Indian flag colors
- Completely revamped SME Dashboard with 3 tabs:
  1. Pipeline & RFPs - 6 KPI cards + MSME India stats strip + RFP queue table
  2. MSME Insights - Economy share (45% exports, 30% GDP), Key MSME states bar chart, Registration breakdown, MSME infographic, Challenges, How RFPFlow Helps
  3. Govt Schemes - CHAMPIONS 2.0, RAMP, TReDS, PMEGP, CGTMSE, Classification table, Financial schemes, 25% purchase preference CTA
