import json, os, time
import sys
sys.path.append("/home/yayock79/construction_doc_engine")
from invoice_engine_v2 import ConstructionDocEngine

DASHBOARD_PATH = "/home/yayock79/dist/doc_engine/index.html"

class EmailInvoiceWebhookHandler:
    def __init__(self):
        self.engine = ConstructionDocEngine()

    def process_incoming_email(self, email_payload):
        sender = email_payload.get("from", "unknown@vendor.com")
        subject = email_payload.get("subject", "No Subject")
        attachments = email_payload.get("attachments", [])
        body = email_payload.get("body_text", "")

        print(f"📧 Incoming Email from: {sender}")
        print(f"   Subject: {subject}")
        print(f"   Attachments Found: {len(attachments)}")

        # Simulate OCR / extraction from email attachment or body
        inv_id = f"INV-MAIL-{int(time.time()) % 10000}"
        
        # Parse vendor from domain/sender
        vendor_name = sender.split("@")[-1].replace(".com", "").replace("-", " ").title() + " Services" if "@" in sender else "Email Vendor"
        
        doc_data = {
            "invoice_id": inv_id,
            "vendor": vendor_name,
            "subtotal": email_payload.get("parsed_subtotal", 1250.00),
            "tax": email_payload.get("parsed_tax", 100.00),
            "total": email_payload.get("parsed_total", 1350.00),
            "job_id": email_payload.get("parsed_job_id", "JOB-104-SUNSET-RIDGE"),
            "cost_code": email_payload.get("parsed_cost_code", "15-0000-PLUMBING"),
            "lien_waiver_attached": email_payload.get("has_lien_waiver", True)
        }

        record = self.engine.process_document(doc_data)
        self.engine.generate_dashboard_html(DASHBOARD_PATH)

        reply_status = "✓ Approved & Routed to ERP" if record["status"] == "APPROVED_FOR_ERP" else "⚠️ Flagged for Audit Review"
        reply_msg = f"Auto-Reply to {sender}: Received {subject}. Status: {reply_status}."
        print(f"   └─ {reply_msg}\n")

        return {
            "status": "success",
            "audit_record": record,
            "auto_reply": reply_msg
        }

if __name__ == '__main__':
    handler = EmailInvoiceWebhookHandler()
    
    # Test Email Payload
    sample_email = {
        "from": "accounting@columbiaplumbing.com",
        "subject": "Invoice #8842 - JOB-104 Sunset Ridge Plumbing Rough-In",
        "body_text": "Please find attached our plumbing rough-in invoice and signed partial lien waiver.",
        "attachments": ["invoice_8842.pdf", "lien_waiver_signed.pdf"],
        "parsed_subtotal": 4200.00,
        "parsed_tax": 0.00,
        "parsed_total": 4200.00,
        "parsed_job_id": "JOB-104-SUNSET-RIDGE",
        "parsed_cost_code": "15-0000-PLUMBING",
        "has_lien_waiver": True
    }
    
    handler.process_incoming_email(sample_email)
