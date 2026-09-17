import os, time, shutil, json
import sys
sys.path.append("/home/yayock79/construction_doc_engine")
from invoice_engine_v2 import ConstructionDocEngine

INBOX_DIR = "/home/yayock79/construction_doc_engine/watch_folder/inbox"
PROCESSED_DIR = "/home/yayock79/construction_doc_engine/watch_folder/processed"
FLAGGED_DIR = "/home/yayock79/construction_doc_engine/watch_folder/flagged"
DASHBOARD_PATH = "/home/yayock79/dist/doc_engine/index.html"

def run_watcher_sweep():
    engine = ConstructionDocEngine()
    print("🔎 Sweeping Cloud Watch Folder:", INBOX_DIR)
    
    files = [f for f in os.listdir(INBOX_DIR) if f.endswith('.json') or f.endswith('.pdf') or f.endswith('.jpg') or f.endswith('.png')]
    if not files:
        print("✓ Watch folder clean. No pending documents.")
        return 0

    processed_count = 0
    for filename in sorted(files):
        filepath = os.path.join(INBOX_DIR, filename)
        print(f"⚡ Processing incoming cloud document: {filename}")
        
        # Load invoice data or mock-parse PDF/image
        if filename.endswith('.json'):
            with open(filepath, 'r') as fp:
                data = json.load(fp)
        else:
            # Mock OCR parsing for PDF/Image
            data = {
                "invoice_id": f"INV-CLOUD-{int(time.time())}",
                "vendor": f"Auto-Scanned Vendor ({filename})",
                "subtotal": 3500.00,
                "tax": 280.00,
                "total": 3780.00,
                "job_id": "JOB-104-SUNSET-RIDGE",
                "cost_code": "06-1000-ROUGH-CARPENTRY",
                "lien_waiver_attached": False
            }

        record = engine.process_document(data)
        
        # Move file based on audit status
        dest_folder = FLAGGED_DIR if record["status"] == "REQUIRES_REVIEW" else PROCESSED_DIR
        dest_path = os.path.join(dest_folder, filename)
        shutil.move(filepath, dest_path)
        print(f"  └─ Audit Status: {record['status']} -> Moved to {dest_folder}")
        processed_count += 1

    # Regenerate dashboard
    engine.generate_dashboard_html(DASHBOARD_PATH)
    return processed_count

if __name__ == '__main__':
    run_watcher_sweep()
