"""FastAPI Underwriting Multi-Agent Backend & Tool Provider.

Exposes OpenAPI 3.0-compliant tool endpoints for Gemini Enterprise Agent Designer v2 (ge_demo).
Supports Gmail email scanning with subject filter '[underwriting] ', attachment ingestion,
and direct GE App document uploads.
"""

from typing import Any, Dict, List, Optional
import datetime
import uuid

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from mock_database import (
    AML_WATCHLIST_DATABASE,
    DBD_MOCK_DATABASE,
    DOPA_MOCK_DATABASE,
    GOLDEN_APPLICATIONS,
    MOCK_GMAIL_INBOX,
    UNDERWRITING_CASES,
)

app = FastAPI(
    title="Gemini Enterprise Underwriting Multi-Agent Tools API",
    description=(
        "Specialized tool APIs and mock database for enterprise-grade automated credit "
        "and business underwriting in Gemini Enterprise Agent Designer v2 (ge_demo). "
        "Includes Gmail '[underwriting] ' scanner and GE App upload ingestors."
    ),
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def mask_pii(val: Optional[str]) -> str:
    """Masks sensitive PII keeping only the last 4 characters."""
    if not val:
        return "N/A"
    s = str(val).strip()
    if len(s) <= 4:
        return s
    return "X" * (len(s) - 4) + s[-4:]


# ==========================================
# Pydantic Request & Response Schemas
# ==========================================


class DocumentItem(BaseModel):
    type: str = Field(
        ...,
        description="Document type (e.g. DBD_CERTIFICATE, BOR_OR_JOR_5, BANK_STATEMENT_6M, FINANCIAL_STATEMENTS, DIRECTOR_NATIONAL_ID)",
    )
    filename: Optional[str] = Field(None, description="Uploaded file name")
    issue_date: Optional[str] = Field(None, description="Issue date in YYYY-MM-DD")
    months_count: Optional[int] = Field(None, description="Number of statement months")
    audited: Optional[bool] = Field(None, description="Whether statement is audited")
    holder_id: Optional[str] = Field(None, description="ID of director / individual")
    legible: bool = Field(True, description="Whether document passed legibility scan")


class ScanGmailInboxRequest(BaseModel):
    subject_filter: Optional[str] = Field("[underwriting]", description="Subject prefix to scan for (default: '[underwriting]')")
    max_results: Optional[int] = Field(10, description="Max emails to return")


class EmailAttachmentItem(BaseModel):
    filename: str
    type: str
    size_kb: Optional[int] = None
    legible: bool = True
    issue_date: Optional[str] = None
    months_count: Optional[int] = None
    audited: Optional[bool] = None
    holder_id: Optional[str] = None


class IngestedEmailCase(BaseModel):
    email_id: str
    sender: str
    subject: str
    received_at: str
    body_snippet: str
    attachments: List[EmailAttachmentItem]
    application_id: str
    status: str = "READY_FOR_INTAKE"


class ScanGmailInboxResponse(BaseModel):
    total_matching_emails: int
    subject_filter_applied: str
    scanned_at: str
    emails: List[IngestedEmailCase]


class IngestGEAppUploadRequest(BaseModel):
    borrower_name: str = Field(..., description="Name of borrowing company or individual")
    registration_id: Optional[str] = Field(None, description="13-digit DBD registration number or Tax ID")
    contact_email: Optional[str] = Field(None, description="Contact email address")
    requested_facility_thb: float = Field(..., description="Requested credit amount in THB")
    loan_purpose: Optional[str] = Field("Working Capital", description="Purpose of loan")
    documents: List[DocumentItem] = Field(..., description="List of uploaded documents from GE App")


class IngestGEAppUploadResponse(BaseModel):
    application_id: str
    status: str
    created_at: str
    borrower_name: str
    documents_count: int
    message: str


class ValidateDocumentsRequest(BaseModel):
    application_id: str = Field(..., description="Unique Underwriting Application ID")
    entity_type: str = Field("CORPORATE", description="CORPORATE or INDIVIDUAL")
    documents: Optional[List[DocumentItem]] = Field(None, description="List of submitted documents")


class ValidateDocumentsResponse(BaseModel):
    application_id: str
    entity_type: str
    status: str = Field(..., description="DOCS_VALIDATED or DOCS_MISSING")
    missing_documents: List[str] = Field(default_factory=list)
    document_summary: Dict[str, Any]
    message: str


class ParseDocumentsRequest(BaseModel):
    application_id: str = Field(..., description="Unique Underwriting Application ID")
    documents: Optional[List[DocumentItem]] = None


class ParseDocumentsResponse(BaseModel):
    application_id: str
    parsed_financials: Dict[str, Any]
    parsed_corporate: Dict[str, Any]
    parsing_status: str
    timestamp: str


class VerifyRegistriesRequest(BaseModel):
    application_id: str = Field(..., description="Unique Underwriting Application ID")
    registration_id: Optional[str] = Field(None, description="Thai DBD 13-digit Company Registration ID")
    director_ids: Optional[List[str]] = Field(None, description="List of 13-digit National IDs")
    entity_name: Optional[str] = Field(None, description="Entity or Company Name")


class VerifyRegistriesResponse(BaseModel):
    application_id: str
    verification_status: str = Field(..., description="PASSED, WARNING_LITIGATION, or FAILED_KNOCKOUT")
    dbd_result: Dict[str, Any]
    dopa_results: List[Dict[str, Any]]
    aml_watchlist_result: Dict[str, Any]
    knockout_flags: List[str]


class AnalyzeFraudRequest(BaseModel):
    application_id: str = Field(..., description="Unique Underwriting Application ID")
    bank_inflows_total_6m_thb: Optional[float] = Field(None, description="Total 6M bank deposits")
    pp30_vat_revenue_total_6m_thb: Optional[float] = Field(None, description="Total 6M revenue reported in P.P.30")
    bounced_checks_count_6m: Optional[int] = Field(0, description="Bounced checks in 6 months")


class AnalyzeFraudResponse(BaseModel):
    application_id: str
    fraud_risk_score: int = Field(..., description="Score 0 (Low) to 100 (Critical)")
    risk_level: str = Field(..., description="LOW, MEDIUM, or HIGH_ANOMALY")
    revenue_variance_pct: float
    fraud_flags: List[str]
    details: str


class ScoreCreditRequest(BaseModel):
    application_id: str = Field(..., description="Unique Underwriting Application ID")
    monthly_net_operating_income_thb: Optional[float] = None
    total_monthly_debt_service_thb: Optional[float] = None
    monthly_turnover_avg_thb: Optional[float] = None
    requested_facility_thb: Optional[float] = None
    overdraft_avg_utilization_pct: Optional[float] = None
    bounced_checks_count_6m: Optional[int] = None


class ScoreCreditResponse(BaseModel):
    application_id: str
    dscr: float
    avg_monthly_turnover_thb: float
    risk_tier: str = Field(..., description="TIER_A (Prime), TIER_B (Standard), TIER_C (Borderline), TIER_D (High Risk)")
    inflow_to_installment_ratio: float
    overdraft_utilization_pct: float
    bounced_checks_count: int
    policy_breaches: List[str]
    credit_summary: str


class MakeDecisionRequest(BaseModel):
    application_id: str = Field(..., description="Unique Underwriting Application ID")
    requested_facility_thb: Optional[float] = None


class MakeDecisionResponse(BaseModel):
    application_id: str
    decision: str = Field(..., description="PRE_APPROVED, REFERRED_TO_UW, or REJECTED")
    recommended_credit_limit_thb: Optional[float] = None
    interest_rate_pct_pa: Optional[float] = None
    recommended_tenor_months: Optional[int] = None
    required_collateral: Optional[str] = None
    conditions_precedent: List[str]
    underwriter_memo: Optional[Dict[str, Any]] = None
    adverse_action_reasons: List[str]
    audit_trail: Dict[str, Any]


class SendNotificationRequest(BaseModel):
    application_id: str = Field(..., description="Unique Underwriting Application ID")
    recipient_email: Optional[str] = None
    custom_message_override: Optional[str] = None


class SendNotificationResponse(BaseModel):
    application_id: str
    notification_status: str
    recipient_email: str
    template_type: str
    subject: str
    body_markdown: str
    dispatched_at: str


# ==========================================
# Core Endpoints & Tools
# ==========================================


@app.get("/healthz", tags=["System"])
def health_check():
    """Health check endpoint for Cloud Run and monitoring."""
    return {
        "status": "HEALTHY",
        "service": "underwriting-multi-agent-tools",
        "version": "2.1.0",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "loaded_cases_count": len(UNDERWRITING_CASES),
        "inbox_emails_count": len(MOCK_GMAIL_INBOX),
    }


@app.get("/cases", tags=["Case Management"])
def list_cases():
    """List all underwriting cases in the mock database."""
    summaries = []
    for app_id, case in UNDERWRITING_CASES.items():
        summaries.append(
            {
                "application_id": app_id,
                "borrower_name": case.get("borrower_name"),
                "entity_type": case.get("entity_type"),
                "requested_facility_thb": case.get("requested_facility_thb"),
                "created_at": case.get("created_at"),
                "ingestion_channel": case.get("ingestion_channel"),
            }
        )
    return {"total": len(summaries), "cases": summaries}


@app.get("/cases/{application_id}", tags=["Case Management"])
def get_case(application_id: str):
    """Retrieve full application details by ID."""
    if application_id not in UNDERWRITING_CASES:
        raise HTTPException(status_code=404, detail=f"Application {application_id} not found.")
    return UNDERWRITING_CASES[application_id]


# ==========================================
# Tool 0: Gmail Scanner & Email Attachment Intake Tool
# ==========================================
@app.post(
    "/tools/scan-gmail-inbox",
    response_model=ScanGmailInboxResponse,
    tags=["Agent Tools - Ingestion"],
    summary="GmailScanner: Scan Gmail inbox for incoming emails with subject '[underwriting] ' and extract attachments",
)
def scan_gmail_inbox(req: ScanGmailInboxRequest = ScanGmailInboxRequest()):
    """Scan Gmail for incoming applications containing '[underwriting] ' in the subject line and prepare them for underwriting."""
    query = (req.subject_filter or "[underwriting]").lower()
    matching_emails: List[IngestedEmailCase] = []

    for msg in MOCK_GMAIL_INBOX:
        if query in msg.get("subject", "").lower():
            attachments = [EmailAttachmentItem(**att) for att in msg.get("attachments", [])]
            matching_emails.append(
                IngestedEmailCase(
                    email_id=msg["email_id"],
                    sender=msg["sender"],
                    subject=msg["subject"],
                    received_at=msg["received_at"],
                    body_snippet=msg["body_text"][:200] + "...",
                    attachments=attachments,
                    application_id=msg["application_id"],
                    status="READY_FOR_INTAKE",
                )
            )

    return ScanGmailInboxResponse(
        total_matching_emails=len(matching_emails),
        subject_filter_applied=req.subject_filter or "[underwriting]",
        scanned_at=datetime.datetime.utcnow().isoformat() + "Z",
        emails=matching_emails[: req.max_results],
    )


# ==========================================
# Tool 0.1: Direct GE App Upload Ingestor
# ==========================================
@app.post(
    "/tools/ingest-ge-app-upload",
    response_model=IngestGEAppUploadResponse,
    tags=["Agent Tools - Ingestion"],
    summary="GEAppIngestor: Directly ingest documents uploaded by underwriter or customer in Gemini Enterprise App",
)
def ingest_ge_app_upload(req: IngestGEAppUploadRequest):
    """Directly ingest documents submitted through the Gemini Enterprise chat/portal UI."""
    new_app_id = f"APP-GE-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    # Build default mock financials for newly created case
    raw_fin = {
        "monthly_turnover_avg_thb": 2500000.0,
        "monthly_net_operating_income_thb": 380000.0,
        "total_monthly_debt_service_thb": 120000.0,
        "annual_revenue_thb": 30000000.0,
        "annual_ebitda_thb": 4560000.0,
        "bank_inflows_total_6m_thb": 15000000.0,
        "pp30_vat_revenue_total_6m_thb": 14900000.0,
        "overdraft_limit_thb": 1000000.0,
        "overdraft_avg_utilization_pct": 30.0,
        "bounced_checks_count_6m": 0,
    }

    UNDERWRITING_CASES[new_app_id] = {
        "application_id": new_app_id,
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "ingestion_channel": "GE_APP_DIRECT_UPLOAD",
        "entity_type": "CORPORATE",
        "borrower_name": req.borrower_name,
        "registration_id": req.registration_id or "0105561023456",
        "contact_email": req.contact_email or "underwriter@enterprise.gemini",
        "requested_facility_thb": req.requested_facility_thb,
        "loan_purpose": req.loan_purpose,
        "documents": [d.dict() for d in req.documents],
        "raw_financials": raw_fin,
    }

    return IngestGEAppUploadResponse(
        application_id=new_app_id,
        status="INITIALIZED",
        created_at=datetime.datetime.utcnow().isoformat() + "Z",
        borrower_name=req.borrower_name,
        documents_count=len(req.documents),
        message=f"Application {new_app_id} successfully created from GE App upload and initialized in Underwriting State Machine.",
    )


# ==========================================
# Tool 1: DocIntakeAgent Tool
# ==========================================
@app.post(
    "/tools/validate-documents",
    response_model=ValidateDocumentsResponse,
    tags=["Agent Tools - Underwriting Workflow"],
    summary="DocIntakeAgent: Validate presence, legibility, and completeness of required underwriting documents",
)
def validate_documents(req: ValidateDocumentsRequest):
    """Step 1: Check document completeness against entity type requirements (Corporate vs. Individual)."""
    case = UNDERWRITING_CASES.get(req.application_id, {})
    docs = req.documents or [DocumentItem(**d) for d in case.get("documents", [])]

    doc_types_present = {d.type for d in docs if d.legible}

    required_corporate = {
        "DBD_CERTIFICATE": "DBD Company Affidavit (<= 3 months)",
        "BOR_OR_JOR_5": "Shareholder List Form BorOrJor.5",
        "BANK_STATEMENT_6M": "6-Month Consecutive Bank Statements",
        "FINANCIAL_STATEMENTS": "Audited Financial Statements",
        "DIRECTOR_NATIONAL_ID": "Director National ID Cards",
    }
    required_individual = {
        "DIRECTOR_NATIONAL_ID": "National ID Card",
        "PROOF_OF_INCOME": "Proof of Income / Salary Slip",
        "BANK_STATEMENT_6M": "6-Month Bank Statement",
    }

    req_map = required_corporate if req.entity_type == "CORPORATE" else required_individual
    missing = [desc for doc_key, desc in req_map.items() if doc_key not in doc_types_present]

    is_validated = len(missing) == 0
    status_str = "DOCS_VALIDATED" if is_validated else "DOCS_MISSING"

    return ValidateDocumentsResponse(
        application_id=req.application_id,
        entity_type=req.entity_type,
        status=status_str,
        missing_documents=missing,
        document_summary={
            "submitted_count": len(docs),
            "valid_count": len(doc_types_present),
            "submitted_types": list(doc_types_present),
        },
        message=(
            "All mandatory underwriting documents are present and legible."
            if is_validated
            else f"Missing {len(missing)} required document(s): {', '.join(missing)}"
        ),
    )


# ==========================================
# Tool 2: DocParserAgent Tool
# ==========================================
@app.post(
    "/tools/parse-documents",
    response_model=ParseDocumentsResponse,
    tags=["Agent Tools - Underwriting Workflow"],
    summary="DocParserAgent: Extract and structure financial metrics and corporate registry data into JSON schema",
)
def parse_documents(req: ParseDocumentsRequest):
    """Step 2: Parse unstructured and semi-structured documents into standardized float values and timestamps."""
    case = UNDERWRITING_CASES.get(req.application_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {req.application_id} not found.")

    raw_fin = case.get("raw_financials", {})
    reg_id = case.get("registration_id")
    dbd_entry = DBD_MOCK_DATABASE.get(reg_id, {})

    parsed_financials = {
        "monthly_turnover_avg_thb": float(raw_fin.get("monthly_turnover_avg_thb", 0.0)),
        "monthly_net_operating_income_thb": float(raw_fin.get("monthly_net_operating_income_thb", 0.0)),
        "total_monthly_debt_service_thb": float(raw_fin.get("total_monthly_debt_service_thb", 0.0)),
        "annual_revenue_thb": float(raw_fin.get("annual_revenue_thb", 0.0)),
        "annual_ebitda_thb": float(raw_fin.get("annual_ebitda_thb", 0.0)),
        "bank_inflows_total_6m_thb": float(raw_fin.get("bank_inflows_total_6m_thb", 0.0)),
        "pp30_vat_revenue_total_6m_thb": float(raw_fin.get("pp30_vat_revenue_total_6m_thb", 0.0)),
        "overdraft_limit_thb": float(raw_fin.get("overdraft_limit_thb", 0.0)),
        "overdraft_avg_utilization_pct": float(raw_fin.get("overdraft_avg_utilization_pct", 0.0)),
        "bounced_checks_count_6m": int(raw_fin.get("bounced_checks_count_6m", 0)),
    }

    parsed_corporate = {
        "registration_number": mask_pii(reg_id),
        "company_name_en": dbd_entry.get("company_name_en", case.get("borrower_name")),
        "registered_capital_thb": dbd_entry.get("registered_capital_thb", 0.0),
        "registration_date": dbd_entry.get("registration_date"),
        "authorized_signing_condition": dbd_entry.get("authorized_signing_condition"),
        "directors_count": len(dbd_entry.get("authorized_directors", [])),
    }

    return ParseDocumentsResponse(
        application_id=req.application_id,
        parsed_financials=parsed_financials,
        parsed_corporate=parsed_corporate,
        parsing_status="SUCCESS",
        timestamp=datetime.datetime.utcnow().isoformat() + "Z",
    )


# ==========================================
# Tool 3: VerificationAgent Tool
# ==========================================
@app.post(
    "/tools/verify-registries",
    response_model=VerifyRegistriesResponse,
    tags=["Agent Tools - Underwriting Workflow"],
    summary="VerificationAgent: Query DBD corporate registry, DOPA identity database, and AML/PEP sanctions list",
)
def verify_registries(req: VerifyRegistriesRequest):
    """Step 3: Cross-check business status, civil registration, and anti-money laundering watchlists."""
    case = UNDERWRITING_CASES.get(req.application_id, {})
    reg_id = req.registration_id or case.get("registration_id", "")
    entity_name = req.entity_name or case.get("borrower_name", "")

    knockout_flags = []

    # 1. DBD Registry Check
    dbd_entry = DBD_MOCK_DATABASE.get(reg_id)
    if not dbd_entry:
        dbd_result = {
            "found": False,
            "status": "NOT_FOUND",
            "message": f"Registration ID {reg_id} not registered with DBD.",
        }
        knockout_flags.append("DBD Registration ID Not Found")
    else:
        dbd_status = dbd_entry.get("status")
        neg_equity = dbd_entry.get("negative_equity", False)
        lit_flags = dbd_entry.get("litigation_flags", [])

        if dbd_status != "ACTIVE":
            knockout_flags.append(f"DBD Status is {dbd_status} (Non-Operational)")
        if neg_equity:
            knockout_flags.append("Negative Net Equity on Balance Sheet")

        dbd_result = {
            "found": True,
            "company_name_en": dbd_entry.get("company_name_en"),
            "status": dbd_status,
            "registered_capital_thb": dbd_entry.get("registered_capital_thb"),
            "litigation_flags": lit_flags,
            "latest_equity_thb": dbd_entry.get("latest_equity_thb"),
            "negative_equity": neg_equity,
        }

    # 2. DOPA Civil Registry Check
    dopa_results = []
    director_ids = req.director_ids
    if not director_ids and dbd_entry:
        director_ids = [d["national_id"] for d in dbd_entry.get("authorized_directors", [])]

    if director_ids:
        for nid in director_ids:
            dopa_entry = DOPA_MOCK_DATABASE.get(nid)
            if not dopa_entry:
                dopa_results.append({
                    "national_id": mask_pii(nid),
                    "status": "NOT_FOUND",
                    "valid": False,
                })
                knockout_flags.append(f"Director National ID {mask_pii(nid)} Not Found in DOPA")
            else:
                c_status = dopa_entry.get("status")
                is_valid = c_status == "VALID"
                if not is_valid:
                    knockout_flags.append(f"Director National ID {mask_pii(nid)} Status: {c_status}")
                dopa_results.append({
                    "national_id": mask_pii(nid),
                    "full_name_en": dopa_entry.get("full_name_en"),
                    "status": c_status,
                    "valid": is_valid,
                    "laser_code_verified": True,
                    "expiry_date": dopa_entry.get("card_expiry_date"),
                })

    # 3. AML / PEP Watchlist Check
    aml_matches = []
    for item in AML_WATCHLIST_DATABASE:
        if (
            (item.get("tax_id") == reg_id)
            or (item.get("entity_name").lower() in entity_name.lower())
            or (req.director_ids and any(item.get("tax_id") == d for d in req.director_ids))
        ):
            aml_matches.append(item)
            if item.get("risk_level") == "CRITICAL_KNOCKOUT":
                knockout_flags.append(f"Critical AML/Sanctions Match: {item.get('details')}")

    aml_result = {
        "matched": len(aml_matches) > 0,
        "matches_count": len(aml_matches),
        "matches": aml_matches,
    }

    # Determine status
    if knockout_flags:
        verif_status = "FAILED_KNOCKOUT"
    elif dbd_result.get("litigation_flags"):
        verif_status = "WARNING_LITIGATION"
    else:
        verif_status = "PASSED"

    return VerifyRegistriesResponse(
        application_id=req.application_id,
        verification_status=verif_status,
        dbd_result=dbd_result,
        dopa_results=dopa_results,
        aml_watchlist_result=aml_result,
        knockout_flags=knockout_flags,
    )


# ==========================================
# Tool 4: FraudRiskAgent Tool
# ==========================================
@app.post(
    "/tools/analyze-fraud",
    response_model=AnalyzeFraudResponse,
    tags=["Agent Tools - Underwriting Workflow"],
    summary="FraudRiskAgent: Cross-validate bank statement inflows against P.P.30 VAT filings and detect anomalies",
)
def analyze_fraud(req: AnalyzeFraudRequest):
    """Step 4: Cross-validate reported revenues, calculate deposit-to-tax variances, and evaluate document forgery risk."""
    case = UNDERWRITING_CASES.get(req.application_id, {})
    raw_fin = case.get("raw_financials", {})

    bank_inflows = (
        req.bank_inflows_total_6m_thb
        if req.bank_inflows_total_6m_thb is not None
        else float(raw_fin.get("bank_inflows_total_6m_thb", 0.0))
    )
    pp30_vat = (
        req.pp30_vat_revenue_total_6m_thb
        if req.pp30_vat_revenue_total_6m_thb is not None
        else float(raw_fin.get("pp30_vat_revenue_total_6m_thb", 0.0))
    )
    bounces = (
        req.bounced_checks_count_6m
        if req.bounced_checks_count_6m is not None
        else int(raw_fin.get("bounced_checks_count_6m", 0))
    )

    fraud_flags = []
    score = 5  # Base clean score

    # Revenue Variance Calculation: |Bank - PP30| / max(Bank, 1)
    if bank_inflows > 0:
        variance_pct = round(abs(bank_inflows - pp30_vat) / bank_inflows * 100.0, 2)
    else:
        variance_pct = 0.0

    if variance_pct > 30.0:
        fraud_flags.append(f"Severe Revenue Discrepancy: {variance_pct}% variance between Bank Inflows and P.P.30 Tax Filings")
        score += 55
    elif variance_pct > 15.0:
        fraud_flags.append(f"Moderate Revenue Discrepancy: {variance_pct}% variance between Bank Inflows and Tax Filings")
        score += 25

    if bounces >= 3:
        fraud_flags.append(f"High Frequency Bounced Checks: {bounces} bounces detected in 6 months")
        score += 35
    elif bounces >= 1:
        fraud_flags.append(f"Technical Bounced Check: {bounces} bounce noted in statement history")
        score += 10

    score = min(score, 100)

    if score >= 60:
        risk_level = "HIGH_ANOMALY"
    elif score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return AnalyzeFraudResponse(
        application_id=req.application_id,
        fraud_risk_score=score,
        risk_level=risk_level,
        revenue_variance_pct=variance_pct,
        fraud_flags=fraud_flags,
        details=(
            "No significant fraud anomalies or forgery signals detected."
            if not fraud_flags
            else f"Flagged {len(fraud_flags)} anomaly item(s)."
        ),
    )


# ==========================================
# Tool 5: ScoringEngineAgent Tool
# ==========================================
@app.post(
    "/tools/score-credit",
    response_model=ScoreCreditResponse,
    tags=["Agent Tools - Underwriting Workflow"],
    summary="ScoringEngineAgent: Compute DSCR, Average Monthly Turnover, and assign credit risk rating tiers (A, B, C, D)",
)
def score_credit(req: ScoreCreditRequest):
    """Step 5: Apply deterministic credit policy rules, calculate financial ratios, and evaluate covenant thresholds."""
    case = UNDERWRITING_CASES.get(req.application_id, {})
    raw_fin = case.get("raw_financials", {})

    noi = (
        req.monthly_net_operating_income_thb
        if req.monthly_net_operating_income_thb is not None
        else float(raw_fin.get("monthly_net_operating_income_thb", 0.0))
    )
    debt_service = (
        req.total_monthly_debt_service_thb
        if req.total_monthly_debt_service_thb is not None
        else float(raw_fin.get("total_monthly_debt_service_thb", 1.0))
    )
    turnover = (
        req.monthly_turnover_avg_thb
        if req.monthly_turnover_avg_thb is not None
        else float(raw_fin.get("monthly_turnover_avg_thb", 0.0))
    )
    od_util = (
        req.overdraft_avg_utilization_pct
        if req.overdraft_avg_utilization_pct is not None
        else float(raw_fin.get("overdraft_avg_utilization_pct", 0.0))
    )
    bounces = (
        req.bounced_checks_count_6m
        if req.bounced_checks_count_6m is not None
        else int(raw_fin.get("bounced_checks_count_6m", 0))
    )

    # Debt Service Coverage Ratio (DSCR) = NOI / Total Debt Service
    dscr = round(noi / max(debt_service, 1.0), 2) if noi > 0 else round(noi / max(debt_service, 1.0), 2)

    # Inflow-to-Installment Ratio (Monthly Turnover / Debt Service)
    inflow_ratio = round(turnover / max(debt_service, 1.0), 2)

    policy_breaches = []
    if dscr < 1.25:
        policy_breaches.append(f"DSCR of {dscr}x is below standard policy threshold of 1.25x")
    if turnover < 500000.0:
        policy_breaches.append(f"Average Monthly Turnover THB {turnover:,.2f} is below minimum threshold of THB 500,000")
    if od_util > 85.0:
        policy_breaches.append(f"Overdraft Utilization {od_util}% exceeds warning limit of 85%")
    if bounces >= 2:
        policy_breaches.append(f"Multiple bounced checks ({bounces}) violate credit hygiene standards")

    # Risk Tiering
    if dscr >= 1.50 and turnover >= 2000000.0 and bounces == 0 and od_util < 70.0:
        risk_tier = "TIER_A"
        summary = "Prime Credit Profile: Strong cash flow buffer, excellent turnover, no policy exceptions."
    elif dscr >= 1.25 and turnover >= 500000.0 and bounces == 0:
        risk_tier = "TIER_B"
        summary = "Standard Credit Profile: Satisfactory debt service coverage, compliant with core credit parameters."
    elif (dscr >= 1.10 and turnover >= 500000.0) or (bounces == 1):
        risk_tier = "TIER_C"
        summary = "Borderline / Referral Profile: Thin debt service margin or minor technical exceptions. Requires mitigating structure."
    else:
        risk_tier = "TIER_D"
        summary = "High Risk Profile: Insufficient cash flow to service debt, negative NOI, or severe credit policy violations."

    return ScoreCreditResponse(
        application_id=req.application_id,
        dscr=dscr,
        avg_monthly_turnover_thb=turnover,
        risk_tier=risk_tier,
        inflow_to_installment_ratio=inflow_ratio,
        overdraft_utilization_pct=od_util,
        bounced_checks_count=bounces,
        policy_breaches=policy_breaches,
        credit_summary=summary,
    )


# ==========================================
# Tool 6: DecisionAgent Tool
# ==========================================
@app.post(
    "/tools/make-decision",
    response_model=MakeDecisionResponse,
    tags=["Agent Tools - Underwriting Workflow"],
    summary="DecisionAgent: Synthesize verification, fraud risk, and credit scoring into final underwriting decision",
)
def make_decision(req: MakeDecisionRequest):
    """Step 6: Determine PRE_APPROVED, REFERRED_TO_UW, or REJECTED status with loan terms and audit trail."""
    case = UNDERWRITING_CASES.get(req.application_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {req.application_id} not found.")

    requested_facility = (
        req.requested_facility_thb
        if req.requested_facility_thb is not None
        else float(case.get("requested_facility_thb", 5000000.0))
    )

    # 1. Evaluate Document Completeness
    doc_res = validate_documents(ValidateDocumentsRequest(application_id=req.application_id, entity_type=case.get("entity_type", "CORPORATE")))
    if doc_res.status == "DOCS_MISSING":
        return MakeDecisionResponse(
            application_id=req.application_id,
            decision="DOCS_MISSING",
            recommended_credit_limit_thb=0.0,
            interest_rate_pct_pa=0.0,
            recommended_tenor_months=0,
            conditions_precedent=[],
            adverse_action_reasons=[f"Missing mandatory documents: {', '.join(doc_res.missing_documents)}"],
            audit_trail={
                "evaluated_at": datetime.datetime.utcnow().isoformat() + "Z",
                "intake_status": "DOCS_MISSING",
                "missing_items": doc_res.missing_documents,
            },
        )

    # 2. Evaluate Registry & AML Knockouts
    verif_res = verify_registries(VerifyRegistriesRequest(application_id=req.application_id))
    fraud_res = analyze_fraud(AnalyzeFraudRequest(application_id=req.application_id))
    score_res = score_credit(ScoreCreditRequest(application_id=req.application_id))

    adverse_reasons = list(verif_res.knockout_flags)

    # Knockout check
    if verif_res.verification_status == "FAILED_KNOCKOUT" or fraud_res.risk_level == "HIGH_ANOMALY" or score_res.risk_tier == "TIER_D":
        if fraud_res.fraud_flags:
            adverse_reasons.extend(fraud_res.fraud_flags)
        if score_res.policy_breaches:
            adverse_reasons.extend(score_res.policy_breaches)

        return MakeDecisionResponse(
            application_id=req.application_id,
            decision="REJECTED",
            recommended_credit_limit_thb=0.0,
            interest_rate_pct_pa=0.0,
            recommended_tenor_months=0,
            conditions_precedent=[],
            adverse_action_reasons=adverse_reasons,
            audit_trail={
                "evaluated_at": datetime.datetime.utcnow().isoformat() + "Z",
                "verification_status": verif_res.verification_status,
                "fraud_risk_score": fraud_res.fraud_risk_score,
                "credit_risk_tier": score_res.risk_tier,
                "dscr": score_res.dscr,
                "knockout_flags_count": len(adverse_reasons),
            },
        )

    # Referral check (Borderline DSCR / Litigation / Minor flags)
    if score_res.risk_tier == "TIER_C" or verif_res.verification_status == "WARNING_LITIGATION" or fraud_res.risk_level == "MEDIUM":
        memo = {
            "referral_reason": "Policy breach within mitigatable credit committee risk envelope.",
            "dscr_observed": score_res.dscr,
            "dscr_required": 1.25,
            "litigation_notes": verif_res.dbd_result.get("litigation_flags", []),
            "fraud_variance_pct": fraud_res.revenue_variance_pct,
            "mitigating_factors": [
                "Established operational track record (> 3 years in DBD registry)",
                "Solid monthly turnover supporting installment servicing",
                "Directors provide joint personal guarantee",
            ],
            "committee_recommendation": (
                f"Conditional Approval with facility capped at THB {min(requested_facility, 3000000.0):,.2f} "
                f"at MLR + 0.50% (6.25% p.a.) subject to first mortgage on commercial premises."
            ),
        }

        return MakeDecisionResponse(
            application_id=req.application_id,
            decision="REFERRED_TO_UW",
            recommended_credit_limit_thb=min(requested_facility, 3000000.0),
            interest_rate_pct_pa=6.25,
            recommended_tenor_months=48,
            required_collateral="Commercial Property Mortgage (Coverage >= 120%) + Joint Director Guarantee",
            conditions_precedent=[
                "Submission of formal dispute resolution agreement for pending commercial claim",
                "Execution of personal guarantee from authorized director Mr. Wichai Ratanarungreang",
            ],
            underwriter_memo=memo,
            adverse_action_reasons=[],
            audit_trail={
                "evaluated_at": datetime.datetime.utcnow().isoformat() + "Z",
                "routing_queue": "CREDIT_COMMITTEE_ESCALATION_TIER_2",
                "dscr": score_res.dscr,
                "risk_tier": score_res.risk_tier,
            },
        )

    # Pre-Approval (Tier A or Tier B)
    if score_res.risk_tier == "TIER_A":
        interest_rate = 4.75  # MLR - 1.25%
        tenor = 60
        collateral = "Clean Facility with Director Joint Guarantee"
        approved_limit = requested_facility
    else:
        interest_rate = 5.50  # MLR - 0.50%
        tenor = 48
        collateral = "Corporate Account Pledge & Director Guarantee"
        approved_limit = min(requested_facility, 8000000.0)

    return MakeDecisionResponse(
        application_id=req.application_id,
        decision="PRE_APPROVED",
        recommended_credit_limit_thb=approved_limit,
        interest_rate_pct_pa=interest_rate,
        recommended_tenor_months=tenor,
        required_collateral=collateral,
        conditions_precedent=[
            "Execution of standard Master Credit Facility Agreement",
            "Board of Directors resolution approving borrowing",
            "Verification of original Director ID cards prior to drawdown",
        ],
        underwriter_memo={
            "assessment": "Automated Fast-Track Approval: Prime financials, excellent DSCR and turnover.",
            "calculated_dscr": score_res.dscr,
            "monthly_turnover": score_res.avg_monthly_turnover_thb,
        },
        adverse_action_reasons=[],
        audit_trail={
            "evaluated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "fast_track_qualified": True,
            "risk_tier": score_res.risk_tier,
            "dscr": score_res.dscr,
            "fraud_score": fraud_res.fraud_risk_score,
        },
    )


# ==========================================
# Tool 7: NotificationAgent Tool
# ==========================================
@app.post(
    "/tools/send-notification",
    response_model=SendNotificationResponse,
    tags=["Agent Tools - Underwriting Workflow"],
    summary="NotificationAgent: Generate and dispatch pre-approval letters, missing doc notices, and underwriter memos",
)
def send_notification(req: SendNotificationRequest):
    """Step 7: Draft formatted customer or internal communications based on the final decision state."""
    case = UNDERWRITING_CASES.get(req.application_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {req.application_id} not found.")

    recipient = req.recipient_email or case.get("contact_email", "applicant@example.com")
    borrower = case.get("borrower_name", "Valued Customer")
    reg_id_masked = mask_pii(case.get("registration_id", ""))

    # Evaluate decision to know what template to trigger
    dec_res = make_decision(MakeDecisionRequest(application_id=req.application_id))
    decision = dec_res.decision

    timestamp_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if decision == "PRE_APPROVED":
        template = "CUSTOMER_PRE_APPROVAL_LETTER"
        subject = f"🎉 Pre-Approval Notice: Credit Facility Approved for {borrower} [Ref: {req.application_id}]"
        body = f"""# OFFICIAL CREDIT FACILITY PRE-APPROVAL LETTER

**Date:** {timestamp_str}  
**To:** Authorized Representative of **{borrower}** (Registration No: {reg_id_masked})  
**Application Reference:** `{req.application_id}`  

Dear Financial Officer,

We are pleased to inform you that your commercial credit facility application has successfully passed our automated underwriting evaluation and has been **PRE-APPROVED** under the following indicative terms:

---

### 💳 Indicative Credit Facility Terms
* **Approved Credit Limit:** **THB {dec_res.recommended_credit_limit_thb:,.2f}**
* **Interest Rate:** **{dec_res.interest_rate_pct_pa}% p.a.** (Floating MLR spread)
* **Repayment Tenor:** **{dec_res.recommended_tenor_months} Months**
* **Collateral Structure:** {dec_res.required_collateral}

### 📋 Conditions Precedent
{chr(10).join(f"- {c}" for c in dec_res.conditions_precedent)}

---

### 🚀 Next Steps to Drawdown
1. Log in to the Gemini Enterprise Customer Portal to review and accept the Letter of Offer.
2. Schedule a physical or digital identity verification session for authorized directors.

Sincerely,  
**Enterprise Credit & Underwriting Division**  
*Gemini Enterprise Automated Decision Engine*
"""

    elif decision == "DOCS_MISSING":
        template = "CUSTOMER_MISSING_DOCUMENTS_NOTICE"
        subject = f"⚠️ Action Required: Missing Documents for Application {req.application_id} ({borrower})"
        body = f"""# UNDERWRITING DOCUMENTATION NOTICE

**Date:** {timestamp_str}  
**To:** **{borrower}** (Registration: {reg_id_masked})  
**Application ID:** `{req.application_id}`  

Dear Applicant,

Thank you for your application. Our automated document intake agent detected that some mandatory documents are missing or require re-upload:

### 📑 Outstanding Documents Required
{chr(10).join(f"- ❌ {r}" for r in dec_res.adverse_action_reasons)}

### 📤 Secure Upload Link
Please upload clear, legible copies within **7 business days** via your dedicated portal:  
🔗 `https://portal.enterprise.gemini/upload?app_id={req.application_id}`

Sincerely,  
**Intake & Onboarding Operations**
"""

    elif decision == "REFERRED_TO_UW":
        template = "INTERNAL_CREDIT_COMMITTEE_MEMO"
        subject = f"📋 [Referral Memo] Underwriting Case Escalation: {borrower} [Ref: {req.application_id}]"
        memo_data = dec_res.underwriter_memo or {}
        body = f"""# CREDIT COMMITTEE UNDERWRITING REFERRAL MEMO

**Application Reference:** `{req.application_id}`  
**Borrower:** **{borrower}** (Tax ID: {reg_id_masked})  
**Timestamp:** {timestamp_str}  
**Routing Queue:** `CREDIT_COMMITTEE_ESCALATION_TIER_2`  

---

### 🔍 Executive Summary
* **Observed DSCR:** **{memo_data.get('dscr_observed')}x** (Policy Standard: {memo_data.get('dscr_required')}x)
* **Turnover & Cash Flow:** Solid operational volume supporting proposed facility.
* **Litigation Flags:** {', '.join(memo_data.get('litigation_notes', [])) or 'None'}

### 🛡️ Recommended Mitigating Structure
{memo_data.get('committee_recommendation')}

### 📝 Required Sign-Offs
* [ ] Senior Credit Underwriter
* [ ] Enterprise Risk Officer
"""

    else:  # REJECTED
        template = "CUSTOMER_ADVERSE_ACTION_NOTICE"
        subject = f"Notice of Credit Decision: Application {req.application_id} ({borrower})"
        body = f"""# ADVERSE ACTION CREDIT NOTICE

**Date:** {timestamp_str}  
**To:** **{borrower}** (Registration: {reg_id_masked})  
**Application ID:** `{req.application_id}`  

Dear Applicant,

Thank you for your interest in our business financing solutions. After careful automated evaluation of your credit application and external registry records, we regret to inform you that we are unable to approve your credit facility at this time.

### 📌 Decision Factors
{chr(10).join(f"- {reason}" for reason in dec_res.adverse_action_reasons)}

In accordance with compliance standards, you may request a copy of the evaluation audit trail or re-apply after 90 days.

Sincerely,  
**Credit Risk Management**
"""

    return SendNotificationResponse(
        application_id=req.application_id,
        notification_status="DISPATCHED",
        recipient_email=recipient,
        template_type=template,
        subject=subject,
        body_markdown=body,
        dispatched_at=timestamp_str,
    )
