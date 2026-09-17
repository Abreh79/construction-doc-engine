import json, os, time
import sys
sys.path.append("/home/yayock79/construction_doc_engine")
from invoice_engine_v2 import ConstructionDocEngine

DASHBOARD_PATH = "/home/yayock79/dist/doc_engine/index.html"

class SMSPhotoReceiptReceiver:
    def __init__(self):
        self.engine = ConstructionDocEngine()

    def handle_incoming_sms_mms(self, sms_payload):
        sender_phone = sms_payload.get("From", "+15735550199")
        media_url = sms_payload.get("MediaUrl0")
        body_text = sms_payload.get("Body", "")

        print(f"📱 Incoming SMS/MMS from Field: {sender_phone}")
        print(f"   Message Text: '{body_text}'")
        print(f"   Photo Attachment URL: {media_url or 'None'}")

        inv_id = f"MMS-{int(time.time()) % 10000}"
        
        parsed_vendor = "Home Depot Pro - Columbia" if "depot" in body_text.lower() else "Lowe's Commercial Supply"
        parsed_total = sms_payload.get("simulated_total", 348.50)
        parsed_subtotal = round(parsed_total / 1.0825, 2)
        parsed_tax = round(parsed_total - parsed_subtotal, 2)

        doc_data = {
            "invoice_id": inv_id,
            "vendor": parsed_vendor,
            "subtotal": parsed_subtotal,
            "tax": parsed_tax,
            "total": parsed_total,
            "job_id": "JOB-104-SUNSET-RIDGE",
            "cost_code": "06-1000-ROUGH-CARPENTRY",
            "lien_waiver_attached": True
        }

        record = self.engine.process_document(doc_data)
        self.engine.generate_dashboard_html(DASHBOARD_PATH)

        sms_reply = f"✓ Logged ${parsed_total:,.2f} receipt from {parsed_vendor} for JOB-104. Status: {record['status']}."
        print(f"   └─ Outbound SMS Reply -> {sender_phone}: '{sms_reply}'\n")

        return {
            "status": "success",
            "audit_record": record,
            "outbound_sms": sms_reply
        }

if __name__ == '__main__':
    receiver = SMSPhotoReceiptReceiver()
    
    sample_mms = {
        "From": "+15738813277",
        "Body": "Home Depot receipt for extra framing anchors & lag screws on Sunset Ridge job",
        "MediaUrl0": "https://media.twiliocdn.com/2026/receipt_snapshot_88102.jpg",
        "simulated_total": 348.50
    }
    
    receiver.handle_incoming_sms_mms(sample_mms)
