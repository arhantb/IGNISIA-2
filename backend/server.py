from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging
import io
import uuid
import bcrypt
import jwt as pyjwt
import secrets
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
from typing import Optional

from agents.orchestrator import run_pipeline, create_audit_event
from mock_data import SKU_CATALOG, SAMPLE_RFPS, COMPANY_PROFILE, CURRENCY_RATES, COMPETITORS
from pdf_generator import generate_pdf_bytes

# Config
mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"

app = FastAPI(title="SmartQuote RFP Orchestrator")
api = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ==================== AUTH HELPERS ====================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_access_token(user_id: str, email: str, role: str) -> str:
    return pyjwt.encode({"sub": user_id, "email": email, "role": role, "exp": datetime.now(timezone.utc) + timedelta(hours=24), "type": "access"}, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    return pyjwt.encode({"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "refresh"}, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
        return user
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_roles(*roles):
    async def checker(request: Request):
        user = await get_current_user(request)
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return checker

# ==================== PYDANTIC MODELS ====================
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = "client"
    company_name: Optional[str] = ""
    state: Optional[str] = "Maharashtra"

class LoginRequest(BaseModel):
    email: str
    password: str

class RFPSubmitRequest(BaseModel):
    title: str
    raw_text: str
    client_name: Optional[str] = ""
    client_email: Optional[str] = ""
    client_state: Optional[str] = ""
    currency: Optional[str] = "INR"
    tax_type: Optional[str] = "intra_state"
    deadline: Optional[str] = ""

class ApprovalRequest(BaseModel):
    action: str  # approve, reject, revision
    comments: Optional[str] = ""
    edited_items: Optional[list] = None

class ClientActionRequest(BaseModel):
    action: str  # approve, reject, request_changes
    comments: Optional[str] = ""

# ==================== AUTH ENDPOINTS ====================
@api.post("/auth/register")
async def register(body: RegisterRequest, response: Response):
    email = body.email.strip().lower()
    if body.role not in ("client", "sales", "owner", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role")
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    doc = {
        "email": email, "password_hash": hash_password(body.password),
        "name": body.name, "role": body.role,
        "company_name": body.company_name, "state": body.state,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = await db.users.insert_one(doc)
    user_id = str(result.inserted_id)
    access = create_access_token(user_id, email, body.role)
    refresh = create_refresh_token(user_id)
    response.set_cookie("access_token", access, httponly=True, secure=False, samesite="lax", max_age=86400, path="/")
    response.set_cookie("refresh_token", refresh, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    return {"id": user_id, "email": email, "name": body.name, "role": body.role, "token": access}

@api.post("/auth/login")
async def login(body: LoginRequest, response: Response):
    email = body.email.strip().lower()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user_id = str(user["_id"])
    access = create_access_token(user_id, email, user["role"])
    refresh = create_refresh_token(user_id)
    response.set_cookie("access_token", access, httponly=True, secure=False, samesite="lax", max_age=86400, path="/")
    response.set_cookie("refresh_token", refresh, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    return {"id": user_id, "email": email, "name": user["name"], "role": user["role"], "token": access}

@api.get("/auth/me")
async def me(request: Request):
    user = await get_current_user(request)
    return user

@api.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out"}

# ==================== RFP ENDPOINTS ====================
@api.post("/rfp/submit")
async def submit_rfp(body: RFPSubmitRequest, request: Request):
    user = await get_current_user(request)
    rfp_id = str(uuid.uuid4())[:12].upper()
    doc = {
        "rfp_id": rfp_id,
        "title": body.title,
        "raw_text": body.raw_text,
        "client_name": body.client_name or user.get("company_name", user["name"]),
        "client_email": body.client_email or user["email"],
        "client_state": body.client_state or user.get("state", ""),
        "currency": body.currency,
        "tax_type": body.tax_type,
        "deadline": body.deadline,
        "status": "SUBMITTED",
        "submitted_by": user["_id"],
        "submitted_by_name": user["name"],
        "submitted_by_role": user["role"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_result": None,
        "quote_number": None,
        "approval_history": [],
        "client_responses": [],
        "version": 1,
    }
    await db.rfps.insert_one(doc)
    await db.audit_events.insert_one({
        "rfp_id": rfp_id, "agent": "SYSTEM", "action": "RFP_SUBMITTED",
        "details": f"RFP submitted by {user['name']} ({user['role']})",
        "user": user["name"], "timestamp": datetime.now(timezone.utc).isoformat()
    })
    return {"rfp_id": rfp_id, "status": "SUBMITTED", "message": "RFP submitted successfully"}

@api.get("/rfp/list")
async def list_rfps(request: Request):
    user = await get_current_user(request)
    query = {}
    if user["role"] == "client":
        query["submitted_by"] = user["_id"]
    rfps = await db.rfps.find(query, {"_id": 0, "raw_text": 0, "pipeline_result": 0}).sort("created_at", -1).to_list(100)
    return rfps

@api.get("/rfp/{rfp_id}")
async def get_rfp(rfp_id: str, request: Request):
    user = await get_current_user(request)
    rfp = await db.rfps.find_one({"rfp_id": rfp_id}, {"_id": 0})
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    if user["role"] == "client" and rfp.get("submitted_by") != user["_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return rfp

@api.post("/rfp/{rfp_id}/run-pipeline")
async def run_rfp_pipeline(rfp_id: str, request: Request):
    user = await get_current_user(request)
    if user["role"] not in ("admin", "owner", "sales"):
        raise HTTPException(status_code=403, detail="Only SME team can run pipeline")
    rfp = await db.rfps.find_one({"rfp_id": rfp_id}, {"_id": 0})
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")

    await db.rfps.update_one({"rfp_id": rfp_id}, {"$set": {"status": "PARSING", "updated_at": datetime.now(timezone.utc).isoformat()}})

    metadata = {
        "client_name": rfp.get("client_name", ""),
        "client_state": rfp.get("client_state", ""),
        "currency": rfp.get("currency", "INR"),
        "tax_type": rfp.get("tax_type", "intra_state"),
        "deadline": rfp.get("deadline", ""),
    }

    result = await run_pipeline(rfp_id, rfp["raw_text"], metadata)

    quote_number = f"SQ-{datetime.now(timezone.utc).strftime('%Y%m')}-{rfp_id[:6]}"
    status = result.get("status", "PARSED")

    await db.rfps.update_one({"rfp_id": rfp_id}, {"$set": {
        "status": status,
        "pipeline_result": result,
        "quote_number": quote_number,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }})

    # Store audit events
    for event in result.get("audit_trail", []):
        event["rfp_id"] = rfp_id
        await db.audit_events.insert_one(event)

    return {
        "rfp_id": rfp_id,
        "status": status,
        "quote_number": quote_number,
        "pipeline_duration": result.get("pipeline_duration_seconds", 0),
        "items_priced": result.get("pricing", {}).get("summary", {}).get("total_items", 0),
        "strategy": result.get("competitor_analysis", {}).get("overall_strategy", ""),
        "needs_approval": result.get("governance", {}).get("requires_approval", True),
        "risk_level": result.get("governance", {}).get("risk_level", "medium"),
    }

@api.post("/rfp/{rfp_id}/approve")
async def approve_rfp(rfp_id: str, body: ApprovalRequest, request: Request):
    user = await get_current_user(request)
    if user["role"] not in ("admin", "owner"):
        raise HTTPException(status_code=403, detail="Only owner/admin can approve")
    rfp = await db.rfps.find_one({"rfp_id": rfp_id}, {"_id": 0})
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")

    action_map = {"approve": "APPROVED", "reject": "REJECTED", "revision": "REVISION_REQUESTED"}
    new_status = action_map.get(body.action)
    if not new_status:
        raise HTTPException(status_code=400, detail="Invalid action")

    approval_entry = {
        "action": body.action,
        "status": new_status,
        "comments": body.comments,
        "approved_by": user["name"],
        "approved_by_role": user["role"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    await db.rfps.update_one({"rfp_id": rfp_id}, {
        "$set": {"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()},
        "$push": {"approval_history": approval_entry}
    })

    await db.audit_events.insert_one({
        "rfp_id": rfp_id, "agent": "GOVERNANCE",
        "action": f"OWNER_{body.action.upper()}",
        "details": f"{user['name']} {body.action}d the quote. Comments: {body.comments}",
        "user": user["name"], "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {"rfp_id": rfp_id, "status": new_status, "message": f"Quote {body.action}d successfully"}

@api.post("/rfp/{rfp_id}/share")
async def share_with_client(rfp_id: str, request: Request):
    user = await get_current_user(request)
    if user["role"] not in ("admin", "owner", "sales"):
        raise HTTPException(status_code=403, detail="Not authorized")
    rfp = await db.rfps.find_one({"rfp_id": rfp_id}, {"_id": 0})
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    if rfp["status"] not in ("APPROVED", "REWORKED"):
        raise HTTPException(status_code=400, detail="Quote must be approved before sharing")

    share_token = secrets.token_urlsafe(32)
    await db.rfps.update_one({"rfp_id": rfp_id}, {"$set": {
        "status": "SHARED_WITH_CLIENT",
        "share_token": share_token,
        "shared_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }})

    await db.audit_events.insert_one({
        "rfp_id": rfp_id, "agent": "SYSTEM", "action": "SHARED_WITH_CLIENT",
        "details": f"Quote shared by {user['name']}", "user": user["name"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {"rfp_id": rfp_id, "status": "SHARED_WITH_CLIENT", "share_token": share_token}

# ==================== CLIENT PORTAL ====================
@api.get("/client/quote/{rfp_id}")
async def client_view_quote(rfp_id: str, request: Request):
    """Client views their quote - either via auth or share token"""
    token = request.query_params.get("token")
    rfp = await db.rfps.find_one({"rfp_id": rfp_id}, {"_id": 0})
    if not rfp:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify access
    if token:
        if rfp.get("share_token") != token:
            raise HTTPException(status_code=403, detail="Invalid share link")
    else:
        user = await get_current_user(request)
        if user["role"] == "client" and rfp.get("submitted_by") != user["_id"]:
            raise HTTPException(status_code=403, detail="Access denied")

    # Return client-safe data
    pipeline = rfp.get("pipeline_result", {})
    pricing = pipeline.get("pricing", {}) if pipeline else {}
    summary = pricing.get("summary", {})
    line_items = []
    for item in pricing.get("line_items", []):
        line_items.append({
            "name": item.get("sku_name", ""),
            "description": item.get("original_description", ""),
            "hsn": item.get("hsn", ""),
            "quantity": item.get("quantity", 0),
            "unit": item.get("unit", ""),
            "unit_price": item.get("effective_unit_price", 0),
            "line_total": item.get("line_total", 0),
            "tax": item.get("tax", {}),
            "total_with_tax": item.get("line_total_with_tax", 0),
            "warranty_months": item.get("warranty_months", 0),
        })

    value_adds = []
    comp = pipeline.get("competitor_analysis", {}) if pipeline else {}
    for va in comp.get("value_adds_recommended", []):
        value_adds.append(va.get("label", ""))

    return {
        "rfp_id": rfp_id,
        "quote_number": rfp.get("quote_number", ""),
        "title": rfp.get("title", ""),
        "status": rfp.get("status", ""),
        "client_name": rfp.get("client_name", ""),
        "currency": summary.get("currency", "INR"),
        "line_items": line_items,
        "subtotal": summary.get("total_sell_value", 0),
        "tax": summary.get("total_tax", {}),
        "grand_total": summary.get("grand_total", 0),
        "value_adds": value_adds,
        "version": rfp.get("version", 1),
        "shared_at": rfp.get("shared_at", ""),
        "client_responses": rfp.get("client_responses", []),
        "company": COMPANY_PROFILE,
    }

@api.post("/client/quote/{rfp_id}/action")
async def client_quote_action(rfp_id: str, body: ClientActionRequest, request: Request):
    user = await get_current_user(request)
    rfp = await db.rfps.find_one({"rfp_id": rfp_id}, {"_id": 0})
    if not rfp:
        raise HTTPException(status_code=404, detail="Quote not found")

    action_map = {
        "approve": "CLIENT_APPROVED",
        "reject": "CLOSED_LOST",
        "request_changes": "CLIENT_REVISION",
    }
    new_status = action_map.get(body.action)
    if not new_status:
        raise HTTPException(status_code=400, detail="Invalid action")

    response_entry = {
        "action": body.action,
        "comments": body.comments,
        "by": user["name"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    await db.rfps.update_one({"rfp_id": rfp_id}, {
        "$set": {"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()},
        "$push": {"client_responses": response_entry}
    })

    await db.audit_events.insert_one({
        "rfp_id": rfp_id, "agent": "CLIENT_PORTAL", "action": f"CLIENT_{body.action.upper()}",
        "details": f"Client {user['name']}: {body.action}. Comments: {body.comments}",
        "user": user["name"], "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {"rfp_id": rfp_id, "status": new_status}

# ==================== PDF GENERATION ====================
@api.get("/rfp/{rfp_id}/pdf")
async def generate_pdf(rfp_id: str, request: Request):
    # Allow access via token query param for browser download
    token_param = request.query_params.get("token")
    if token_param and token_param != "dummy":
        try:
            payload = pyjwt.decode(token_param, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except Exception:
            pass  # Fall through to normal auth
    else:
        try:
            await get_current_user(request)
        except Exception:
            raise HTTPException(status_code=401, detail="Authentication required")

    rfp = await db.rfps.find_one({"rfp_id": rfp_id}, {"_id": 0})
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    pipeline = rfp.get("pipeline_result")
    if not pipeline:
        raise HTTPException(status_code=400, detail="Pipeline not run yet")

    quote_data = {**pipeline, "quote_number": rfp.get("quote_number", "SQ-DRAFT")}
    pdf_bytes = generate_pdf_bytes(quote_data)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Quote_{rfp_id}.pdf"}
    )

# ==================== DASHBOARD ====================
@api.get("/dashboard/kpis")
async def dashboard_kpis(request: Request):
    user = await get_current_user(request)
    if user["role"] not in ("admin", "owner", "sales"):
        raise HTTPException(status_code=403, detail="Not authorized")

    total_rfps = await db.rfps.count_documents({})
    pending = await db.rfps.count_documents({"status": "PENDING_APPROVAL"})
    approved = await db.rfps.count_documents({"status": {"$in": ["APPROVED", "SHARED_WITH_CLIENT", "CLIENT_APPROVED"]}})
    client_approved = await db.rfps.count_documents({"status": "CLIENT_APPROVED"})
    rejected = await db.rfps.count_documents({"status": {"$in": ["REJECTED", "CLOSED_LOST"]}})

    # Aggregate total quote value
    pipeline_agg = await db.rfps.aggregate([
        {"$match": {"pipeline_result.pricing.summary.grand_total": {"$exists": True}}},
        {"$group": {"_id": None, "total_value": {"$sum": "$pipeline_result.pricing.summary.grand_total"}, "avg_margin": {"$avg": "$pipeline_result.pricing.summary.overall_margin_pct"}}}
    ]).to_list(1)

    agg = pipeline_agg[0] if pipeline_agg else {"total_value": 0, "avg_margin": 0}

    return {
        "total_rfps": total_rfps,
        "pending_approval": pending,
        "approved": approved,
        "client_approved": client_approved,
        "rejected": rejected,
        "total_pipeline_value": round(agg.get("total_value", 0), 2),
        "avg_margin_pct": round(agg.get("avg_margin", 0), 1),
        "conversion_rate": round(client_approved / total_rfps * 100, 1) if total_rfps > 0 else 0,
    }

# ==================== AUDIT ====================
@api.get("/rfp/{rfp_id}/audit")
async def get_audit_trail(rfp_id: str, request: Request):
    user = await get_current_user(request)
    events = await db.audit_events.find({"rfp_id": rfp_id}, {"_id": 0}).sort("timestamp", 1).to_list(200)
    return events

# ==================== CATALOG ====================
@api.get("/skus")
async def get_skus(request: Request):
    await get_current_user(request)
    return SKU_CATALOG

@api.get("/competitors")
async def get_competitors(request: Request):
    await get_current_user(request)
    return COMPETITORS

@api.get("/sample-rfps")
async def get_sample_rfps(request: Request):
    await get_current_user(request)
    return [{"title": r["title"], "scenario": r["scenario"], "currency": r["currency"], "raw_text": r["raw_text"]} for r in SAMPLE_RFPS]

@api.get("/company-profile")
async def get_company_profile():
    return COMPANY_PROFILE

# ==================== STARTUP ====================
@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    # Seed admin + demo users
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@smartquote.in")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin@123")
    existing = await db.users.find_one({"email": admin_email})
    if not existing:
        await db.users.insert_one({"email": admin_email, "password_hash": hash_password(admin_password), "name": "Admin", "role": "admin", "company_name": "SmartQuote Electric", "state": "Maharashtra", "created_at": datetime.now(timezone.utc).isoformat()})
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one({"email": admin_email}, {"$set": {"password_hash": hash_password(admin_password)}})

    # Seed demo users
    demo_users = [
        {"email": "owner@smartquote.in", "password": "Owner@123", "name": "Rajesh Mehta", "role": "owner", "company_name": "SmartQuote Electric", "state": "Maharashtra"},
        {"email": "sales@smartquote.in", "password": "Sales@123", "name": "Priya Sharma", "role": "sales", "company_name": "SmartQuote Electric", "state": "Maharashtra"},
        {"email": "client@pmc.gov.in", "password": "Client@123", "name": "Amit Kulkarni", "role": "client", "company_name": "Pune Municipal Corporation", "state": "Maharashtra"},
    ]
    for u in demo_users:
        if not await db.users.find_one({"email": u["email"]}):
            await db.users.insert_one({"email": u["email"], "password_hash": hash_password(u["password"]), "name": u["name"], "role": u["role"], "company_name": u["company_name"], "state": u["state"], "created_at": datetime.now(timezone.utc).isoformat()})

    # Write test credentials
    os.makedirs("/app/memory", exist_ok=True)
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write("# Test Credentials\n\n")
        f.write(f"## Admin\n- Email: {admin_email}\n- Password: {admin_password}\n- Role: admin\n\n")
        f.write("## Owner\n- Email: owner@smartquote.in\n- Password: Owner@123\n- Role: owner\n\n")
        f.write("## Sales\n- Email: sales@smartquote.in\n- Password: Sales@123\n- Role: sales\n\n")
        f.write("## Client\n- Email: client@pmc.gov.in\n- Password: Client@123\n- Role: client\n\n")
        f.write("## Auth Endpoints\n- POST /api/auth/register\n- POST /api/auth/login\n- POST /api/auth/logout\n- GET /api/auth/me\n")

    logger.info("Startup complete. Demo users seeded.")

@api.get("/")
async def root():
    return {"service": "SmartQuote RFP Orchestrator", "version": "1.0.0", "status": "running"}

app.include_router(api)
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("shutdown")
async def shutdown():
    client.close()
