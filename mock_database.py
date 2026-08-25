"""Mock database, Gmail inbox, and golden test datasets for Underwriting Multi-Agent Demo.

Covers:
- Gmail Inbox with "[underwriting] " subject triggers and email attachments
- Thai Department of Business Development (DBD) Corporate Registry
- Department of Provincial Administration (DOPA) Civil Identity Registry
- AML / PEP / Sanctions Watchlist
- 4 Comprehensive Golden Test Scenarios:
  1. Prime Pre-Approval (Siam Tech Logistics Co., Ltd.)
  2. Referred to Underwriter (Bangkok Fresh Retail Co., Ltd.)
  3. Knockout Rejection (Apex Global Trading Co., Ltd. - AML & Inactive DBD)
  4. Missing Documents (Chiang Mai Craft Brewery Co., Ltd.)
"""

from typing import Any, Dict, List, Optional
import datetime
import uuid

# ==========================================
# 0. Gmail Inbox Mock DB (Trigger: Subject "[underwriting] ")
# ==========================================
MOCK_GMAIL_INBOX: List[Dict[str, Any]] = [
    {
        "email_id": "MSG-GMAIL-98201",
        "sender": "somchai@siamtechlogistics.co.th",
        "recipient": "underwriting-intake@enterprise.gemini",
        "subject": "[underwriting] Credit Facility Application - Siam Tech Logistics Co., Ltd.",
        "received_at": "2026-08-24T09:30:00Z",
        "body_text": (
            "Dear Underwriting Team,\n\n"
            "Please find attached our complete loan application package for Siam Tech Logistics Co., Ltd. (Registration: 0105561023456).\n"
            "We are requesting a THB 10,000,000 credit facility for commercial fleet expansion.\n"
            "All 5 required documents including DBD certificate, BorOrJor.5, 6-month SCB bank statements, audited financials, and Director ID are attached.\n\n"
            "Best regards,\nSomchai Siriwattanakul\nManaging Director"
        ),
        "attachments": [
            {"filename": "dbd_affidavit_2026.pdf", "type": "DBD_CERTIFICATE", "size_kb": 1450, "legible": True, "issue_date": "2026-07-15"},
            {"filename": "shareholder_list_boj5.pdf", "type": "BOR_OR_JOR_5", "size_kb": 820, "legible": True, "issue_date": "2026-07-15"},
            {"filename": "scb_statement_6m.pdf", "type": "BANK_STATEMENT_6M", "size_kb": 4300, "legible": True, "months_count": 6},
            {"filename": "audited_financials_2025.pdf", "type": "FINANCIAL_STATEMENTS", "size_kb": 6200, "legible": True, "audited": True},
            {"filename": "director_somchai_id.pdf", "type": "DIRECTOR_NATIONAL_ID", "size_kb": 950, "legible": True, "holder_id": "1100400123456"},
        ],
        "application_id": "APP-2026-001",
        "processed": False,
    },
    {
        "email_id": "MSG-GMAIL-98202",
        "sender": "wichai@bangkokfresh.com",
        "recipient": "underwriting-intake@enterprise.gemini",
        "subject": "[underwriting] SME Loan Application - Bangkok Fresh Retail Co., Ltd.",
        "received_at": "2026-08-24T09:45:00Z",
        "body_text": (
            "Dear Credit Committee,\n\n"
            "Submitting application for Bangkok Fresh Retail Co., Ltd. (Registration: 0105562098765) for THB 3,000,000 working capital.\n"
            "Attached are our DBD certificate, BorOrJor.5, KBank statements, financials, and director ID.\n\n"
            "Thank you,\nWichai Ratanarungreang"
        ),
        "attachments": [
            {"filename": "dbd_affidavit_bfresh.pdf", "type": "DBD_CERTIFICATE", "size_kb": 1200, "legible": True, "issue_date": "2026-06-01"},
            {"filename": "boj5_bangkok_fresh.pdf", "type": "BOR_OR_JOR_5", "size_kb": 780, "legible": True, "issue_date": "2026-06-01"},
            {"filename": "kbank_statement_6m.pdf", "type": "BANK_STATEMENT_6M", "size_kb": 3900, "legible": True, "months_count": 6},
            {"filename": "financial_stmt_2025.pdf", "type": "FINANCIAL_STATEMENTS", "size_kb": 5100, "legible": True, "audited": True},
            {"filename": "id_wichai.pdf", "type": "DIRECTOR_NATIONAL_ID", "size_kb": 890, "legible": True, "holder_id": "3100800345678"},
        ],
        "application_id": "APP-2026-002",
        "processed": False,
    },
    {
        "email_id": "MSG-GMAIL-98203",
        "sender": "thanakrit@apexglobal.biz",
        "recipient": "underwriting-intake@enterprise.gemini",
        "subject": "[underwriting] Trade Credit Line Request - Apex Global Trading",
        "received_at": "2026-08-24T10:00:00Z",
        "body_text": (
            "Attn: Underwriting,\n\n"
            "Requesting THB 15,000,000 export facility for Apex Global Trading Co., Ltd. (Registration: 0105558012345).\n"
            "Attached documents enclosed."
        ),
        "attachments": [
            {"filename": "apex_dbd_2023.pdf", "type": "DBD_CERTIFICATE", "size_kb": 980, "legible": True, "issue_date": "2023-01-10"},
            {"filename": "apex_shareholders.pdf", "type": "BOR_OR_JOR_5", "size_kb": 650, "legible": True, "issue_date": "2023-01-10"},
            {"filename": "apex_bank_stmts.pdf", "type": "BANK_STATEMENT_6M", "size_kb": 2800, "legible": True, "months_count": 6},
            {"filename": "apex_financials.pdf", "type": "FINANCIAL_STATEMENTS", "size_kb": 3200, "legible": True, "audited": False},
            {"filename": "thanakrit_id.pdf", "type": "DIRECTOR_NATIONAL_ID", "size_kb": 750, "legible": True, "holder_id": "1100900456789"},
        ],
        "application_id": "APP-2026-003",
        "processed": False,
    },
    {
        "email_id": "MSG-GMAIL-98204",
        "sender": "karn@cmbrewery.th",
        "recipient": "underwriting-intake@enterprise.gemini",
        "subject": "[underwriting] Equipment Financing Application - Chiang Mai Craft Brewery",
        "received_at": "2026-08-24T10:15:00Z",
        "body_text": (
            "Hello,\n\n"
            "We are applying for THB 5,000,000 equipment financing for Chiang Mai Craft Brewery Co., Ltd. (Registration: 0505563045678).\n"
            "Attached are our DBD certificate, financial statements, and director ID. Note that our accountant is preparing the BorOrJor.5 and bank statements.\n\n"
            "Karn Suwannasit"
        ),
        "attachments": [
            {"filename": "cm_dbd_cert.pdf", "type": "DBD_CERTIFICATE", "size_kb": 1100, "legible": True, "issue_date": "2026-08-01"},
            # Missing BorOrJor.5 and Bank Statements
            {"filename": "financial_stmt_2025.pdf", "type": "FINANCIAL_STATEMENTS", "size_kb": 4800, "legible": True, "audited": True},
            {"filename": "karn_id.pdf", "type": "DIRECTOR_NATIONAL_ID", "size_kb": 920, "legible": True, "holder_id": "5500100567890"},
        ],
        "application_id": "APP-2026-004",
        "processed": False,
    },
]

# ==========================================
# 1. DBD (Department of Business Development) Mock DB
# ==========================================
DBD_MOCK_DATABASE: Dict[str, Dict[str, Any]] = {
    # Case 1: Prime Corporate
    "0105561023456": {
        "registration_number": "0105561023456",
        "company_name_th": "บริษัท สยามเทค โลจิสติกส์ จำกัด",
        "company_name_en": "Siam Tech Logistics Co., Ltd.",
        "registered_capital_thb": 20000000.0,
        "registration_date": "2018-03-15",
        "status": "ACTIVE",
        "business_category": "Transportation and Logistics",
        "isic_code": "49339",
        "registered_address": "88/12 Rama 9 Road, Huai Khwang, Bangkok 10310",
        "authorized_directors": [
            {
                "name": "นายสมชาย สิริวัฒนากุล",
                "national_id": "1100400123456",
                "shares_percentage": 60.0,
            },
            {
                "name": "นางสาวศิริพร วงศ์สุวรรณ",
                "national_id": "1100500234567",
                "shares_percentage": 40.0,
            },
        ],
        "authorized_signing_condition": "One director signs with company seal affixed.",
        "litigation_flags": [],
        "financial_statements_submitted_years": [2023, 2024, 2025],
        "latest_equity_thb": 14500000.0,
        "negative_equity": False,
    },
    # Case 2: Borderline / Referral Case
    "0105562098765": {
        "registration_number": "0105562098765",
        "company_name_th": "บริษัท บางกอก เฟรช รีเทล จำกัด",
        "company_name_en": "Bangkok Fresh Retail Co., Ltd.",
        "registered_capital_thb": 5000000.0,
        "registration_date": "2021-08-20",
        "status": "ACTIVE",
        "business_category": "Supermarkets and Grocery Stores",
        "isic_code": "47111",
        "registered_address": "452 Sukhumvit Soi 55, Watthana, Bangkok 10110",
        "authorized_directors": [
            {
                "name": "นายวิชัย รัตนรุ่งเรือง",
                "national_id": "3100800345678",
                "shares_percentage": 100.0,
            }
        ],
        "authorized_signing_condition": "Mr. Wichai Ratanarungreang signs solely.",
        "litigation_flags": ["Commercial dispute pending resolution (THB 150,000)"],
        "financial_statements_submitted_years": [2024, 2025],
        "latest_equity_thb": 2800000.0,
        "negative_equity": False,
    },
    # Case 3: Knockout Fraud / Dissolved / Watchlist Entity
    "0105558012345": {
        "registration_number": "0105558012345",
        "company_name_th": "บริษัท เอเปกซ์ โกลบอล เทรดดิ้ง จำกัด",
        "company_name_en": "Apex Global Trading Co., Ltd.",
        "registered_capital_thb": 1000000.0,
        "registration_date": "2015-01-10",
        "status": "DISSOLVED",  # Knockout Flag: Inactive status
        "business_category": "General Wholesalers",
        "isic_code": "46900",
        "registered_address": "12/4 Silom Road, Bang Rak, Bangkok 10500",
        "authorized_directors": [
            {
                "name": "นายธนกฤต มั่งคั่งอนันต์",
                "national_id": "1100900456789",
                "shares_percentage": 90.0,
            }
        ],
        "authorized_signing_condition": "Mr. Thanakrit Mungkunganant signs solely.",
        "litigation_flags": ["Bankruptcy court petition filed 2025"],
        "financial_statements_submitted_years": [2022],
        "latest_equity_thb": -1200000.0,  # Knockout Flag: Negative equity
        "negative_equity": True,
    },
    # Case 4: Missing Docs / Chiang Mai Craft Brewery
    "0505563045678": {
        "registration_number": "0505563045678",
        "company_name_th": "บริษัท เชียงใหม่ คราฟท์ บริวเวอรี่ จำกัด",
        "company_name_en": "Chiang Mai Craft Brewery Co., Ltd.",
        "registered_capital_thb": 10000000.0,
        "registration_date": "2020-05-18",
        "status": "ACTIVE",
        "business_category": "Beverage Manufacturing",
        "isic_code": "11050",
        "registered_address": "99 Nimmanahaeminda Road, Suthep, Mueang Chiang Mai 50200",
        "authorized_directors": [
            {
                "name": "นายกานต์ สุวรรณสิทธิ์",
                "national_id": "5500100567890",
                "shares_percentage": 70.0,
            }
        ],
        "authorized_signing_condition": "Mr. Karn Suwannasit signs solely with company seal.",
        "litigation_flags": [],
        "financial_statements_submitted_years": [2023, 2024, 2025],
        "latest_equity_thb": 6200000.0,
        "negative_equity": False,
    },
}

# ==========================================
# 2. DOPA (Civil Registration / Identity) Mock DB
# ==========================================
DOPA_MOCK_DATABASE: Dict[str, Dict[str, Any]] = {
    "1100400123456": {
        "national_id": "1100400123456",
        "full_name_th": "นายสมชาย สิริวัฒนากุล",
        "full_name_en": "Mr. Somchai Siriwattanakul",
        "dob": "1982-06-14",
        "laser_code": "JT0-1234567-89",
        "status": "VALID",
        "card_expiry_date": "2030-06-14",
        "address": "88/12 Rama 9 Road, Huai Khwang, Bangkok",
    },
    "1100500234567": {
        "national_id": "1100500234567",
        "full_name_th": "นางสาวศิริพร วงศ์สุวรรณ",
        "full_name_en": "Miss Siriporn Wongsuwan",
        "dob": "1988-11-23",
        "laser_code": "JT1-9876543-21",
        "status": "VALID",
        "card_expiry_date": "2029-11-23",
        "address": "14/2 Phahonyothin Road, Chatuchak, Bangkok",
    },
    "3100800345678": {
        "national_id": "3100800345678",
        "full_name_th": "นายวิชัย รัตนรุ่งเรือง",
        "full_name_en": "Mr. Wichai Ratanarungreang",
        "dob": "1975-02-19",
        "laser_code": "JT2-4567890-12",
        "status": "VALID",
        "card_expiry_date": "2028-02-19",
        "address": "452 Sukhumvit Soi 55, Watthana, Bangkok",
    },
    "1100900456789": {
        "national_id": "1100900456789",
        "full_name_th": "นายธนกฤต มั่งคั่งอนันต์",
        "full_name_en": "Mr. Thanakrit Mungkunganant",
        "dob": "1979-09-04",
        "laser_code": "JT9-9999999-99",
        "status": "EXPIRED",  # Invalid or flagged
        "card_expiry_date": "2024-09-04",
        "address": "12/4 Silom Road, Bang Rak, Bangkok",
    },
    "5500100567890": {
        "national_id": "5500100567890",
        "full_name_th": "นายกานต์ สุวรรณสิทธิ์",
        "full_name_en": "Mr. Karn Suwannasit",
        "dob": "1990-04-12",
        "laser_code": "JT5-1122334-45",
        "status": "VALID",
        "card_expiry_date": "2032-04-12",
        "address": "99 Nimmanahaeminda Road, Suthep, Chiang Mai",
    },
}

# ==========================================
# 3. AML / PEP / Sanctions Watchlist Mock DB
# ==========================================
AML_WATCHLIST_DATABASE: List[Dict[str, Any]] = [
    {
        "entity_name": "Apex Global Trading Co., Ltd.",
        "tax_id": "0105558012345",
        "entity_type": "CORPORATE",
        "match_type": "SANCTIONS_AMLO",
        "risk_level": "CRITICAL_KNOCKOUT",
        "details": "Flagged by Anti-Money Laundering Office (AMLO) List 4: Trade fraud and illicit cross-border transfers.",
    },
    {
        "entity_name": "นายธนกฤต มั่งคั่งอนันต์",
        "tax_id": "1100900456789",
        "entity_type": "INDIVIDUAL",
        "match_type": "PEP_DOMESTIC",
        "risk_level": "HIGH",
        "details": "Former political advisory board member under active regulatory investigation.",
    },
]

# ==========================================
# 4. Golden Pre-Populated Applications
# ==========================================
GOLDEN_APPLICATIONS: Dict[str, Dict[str, Any]] = {
    # Case 1: Prime Approval Case
    "APP-2026-001": {
        "application_id": "APP-2026-001",
        "created_at": "2026-08-24T10:00:00Z",
        "ingestion_channel": "GMAIL_ATTACHMENT_INGESTION",
        "email_id": "MSG-GMAIL-98201",
        "entity_type": "CORPORATE",
        "borrower_name": "Siam Tech Logistics Co., Ltd.",
        "registration_id": "0105561023456",
        "contact_email": "somchai@siamtechlogistics.co.th",
        "requested_facility_thb": 10000000.0,
        "loan_purpose": "Fleet expansion and working capital",
        "documents": [
            {"type": "DBD_CERTIFICATE", "filename": "dbd_affidavit_2026.pdf", "issue_date": "2026-07-15", "legible": True},
            {"type": "BOR_OR_JOR_5", "filename": "shareholder_list_boj5.pdf", "issue_date": "2026-07-15", "legible": True},
            {"type": "BANK_STATEMENT_6M", "filename": "scb_statement_6m.pdf", "months_count": 6, "legible": True},
            {"type": "FINANCIAL_STATEMENTS", "filename": "audited_financials_2025.pdf", "audited": True, "legible": True},
            {"type": "DIRECTOR_NATIONAL_ID", "filename": "director_somchai_id.pdf", "holder_id": "1100400123456", "legible": True},
        ],
        "raw_financials": {
            "monthly_turnover_avg_thb": 3500000.0,
            "monthly_net_operating_income_thb": 520000.0,
            "total_monthly_debt_service_thb": 180000.0,
            "annual_revenue_thb": 42000000.0,
            "annual_ebitda_thb": 6240000.0,
            "bank_inflows_total_6m_thb": 21000000.0,
            "pp30_vat_revenue_total_6m_thb": 20850000.0,
            "overdraft_limit_thb": 2000000.0,
            "overdraft_avg_utilization_pct": 35.0,
            "bounced_checks_count_6m": 0,
        },
    },
    # Case 2: Referred to Underwriter Case
    "APP-2026-002": {
        "application_id": "APP-2026-002",
        "created_at": "2026-08-24T10:15:00Z",
        "ingestion_channel": "GMAIL_ATTACHMENT_INGESTION",
        "email_id": "MSG-GMAIL-98202",
        "entity_type": "CORPORATE",
        "borrower_name": "Bangkok Fresh Retail Co., Ltd.",
        "registration_id": "0105562098765",
        "contact_email": "wichai@bangkokfresh.com",
        "requested_facility_thb": 3000000.0,
        "loan_purpose": "Inventory purchase for new store branch",
        "documents": [
            {"type": "DBD_CERTIFICATE", "filename": "dbd_affidavit_bfresh.pdf", "issue_date": "2026-06-01", "legible": True},
            {"type": "BOR_OR_JOR_5", "filename": "boj5_bangkok_fresh.pdf", "issue_date": "2026-06-01", "legible": True},
            {"type": "BANK_STATEMENT_6M", "filename": "kbank_statement_6m.pdf", "months_count": 6, "legible": True},
            {"type": "FINANCIAL_STATEMENTS", "filename": "financial_stmt_2025.pdf", "audited": True, "legible": True},
            {"type": "DIRECTOR_NATIONAL_ID", "filename": "id_wichai.pdf", "holder_id": "3100800345678", "legible": True},
        ],
        "raw_financials": {
            "monthly_turnover_avg_thb": 850000.0,
            "monthly_net_operating_income_thb": 92000.0,
            "total_monthly_debt_service_thb": 80000.0,
            "annual_revenue_thb": 10200000.0,
            "annual_ebitda_thb": 1104000.0,
            "bank_inflows_total_6m_thb": 5100000.0,
            "pp30_vat_revenue_total_6m_thb": 4980000.0,
            "overdraft_limit_thb": 500000.0,
            "overdraft_avg_utilization_pct": 78.0,
            "bounced_checks_count_6m": 1,
        },
    },
    # Case 3: Knockout Rejection Case
    "APP-2026-003": {
        "application_id": "APP-2026-003",
        "created_at": "2026-08-24T10:30:00Z",
        "ingestion_channel": "GMAIL_ATTACHMENT_INGESTION",
        "email_id": "MSG-GMAIL-98203",
        "entity_type": "CORPORATE",
        "borrower_name": "Apex Global Trading Co., Ltd.",
        "registration_id": "0105558012345",
        "contact_email": "thanakrit@apexglobal.biz",
        "requested_facility_thb": 15000000.0,
        "loan_purpose": "Cross-border export financing",
        "documents": [
            {"type": "DBD_CERTIFICATE", "filename": "apex_dbd_2023.pdf", "issue_date": "2023-01-10", "legible": True},
            {"type": "BOR_OR_JOR_5", "filename": "apex_shareholders.pdf", "issue_date": "2023-01-10", "legible": True},
            {"type": "BANK_STATEMENT_6M", "filename": "apex_bank_stmts.pdf", "months_count": 6, "legible": True},
            {"type": "FINANCIAL_STATEMENTS", "filename": "apex_financials.pdf", "audited": False, "legible": True},
            {"type": "DIRECTOR_NATIONAL_ID", "filename": "thanakrit_id.pdf", "holder_id": "1100900456789", "legible": True},
        ],
        "raw_financials": {
            "monthly_turnover_avg_thb": 450000.0,
            "monthly_net_operating_income_thb": -30000.0,
            "total_monthly_debt_service_thb": 120000.0,
            "annual_revenue_thb": 5400000.0,
            "annual_ebitda_thb": -360000.0,
            "bank_inflows_total_6m_thb": 2700000.0,
            "pp30_vat_revenue_total_6m_thb": 1200000.0,
            "overdraft_limit_thb": 1000000.0,
            "overdraft_avg_utilization_pct": 98.0,
            "bounced_checks_count_6m": 4,
        },
    },
    # Case 4: Missing Documents Case
    "APP-2026-004": {
        "application_id": "APP-2026-004",
        "created_at": "2026-08-24T10:45:00Z",
        "ingestion_channel": "GMAIL_ATTACHMENT_INGESTION",
        "email_id": "MSG-GMAIL-98204",
        "entity_type": "CORPORATE",
        "borrower_name": "Chiang Mai Craft Brewery Co., Ltd.",
        "registration_id": "0505563045678",
        "contact_email": "karn@cmbrewery.th",
        "requested_facility_thb": 5000000.0,
        "loan_purpose": "Brewing equipment procurement",
        "documents": [
            {"type": "DBD_CERTIFICATE", "filename": "cm_dbd_cert.pdf", "issue_date": "2026-08-01", "legible": True},
            # Missing BOR_OR_JOR_5
            # Missing BANK_STATEMENT_6M
            {"type": "FINANCIAL_STATEMENTS", "filename": "financial_stmt_2025.pdf", "audited": True, "legible": True},
            {"type": "DIRECTOR_NATIONAL_ID", "filename": "karn_id.pdf", "holder_id": "5500100567890", "legible": True},
        ],
        "raw_financials": {
            "monthly_turnover_avg_thb": 1200000.0,
            "monthly_net_operating_income_thb": 250000.0,
            "total_monthly_debt_service_thb": 70000.0,
            "annual_revenue_thb": 14400000.0,
            "annual_ebitda_thb": 3000000.0,
            "bank_inflows_total_6m_thb": 7200000.0,
            "pp30_vat_revenue_total_6m_thb": 7150000.0,
            "overdraft_limit_thb": 1000000.0,
            "overdraft_avg_utilization_pct": 20.0,
            "bounced_checks_count_6m": 0,
        },
    },
}

# ==========================================
# 5. In-Memory Store for Live Runtime Cases
# ==========================================
UNDERWRITING_CASES: Dict[str, Dict[str, Any]] = dict(GOLDEN_APPLICATIONS)
