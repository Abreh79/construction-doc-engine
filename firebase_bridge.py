#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime

# Ensure user site-packages are accessible
sys.path.insert(0, '/home/yayock79/.local/lib/python3.12/site-packages')
from google.cloud import firestore

PROJECT_ID = 'studio-7106835876-c5253'
COLLECTION_NAME = 'construction_invoices'
DB_FILE = os.path.join(os.path.dirname(__file__), 'records_db.json')

def get_firestore_db():
    return firestore.Client(project=PROJECT_ID)

def sync_db_to_firestore():
    """Reads records_db.json and writes/updates all records in Firestore collection construction_invoices."""
    if not os.path.exists(DB_FILE):
        print(f"File {DB_FILE} not found.")
        return 0

    with open(DB_FILE, 'r') as f:
        records = json.load(f)

    db = get_firestore_db()
    count = 0
    for r in records:
        rec_id = r.get('id') or r.get('invoice_id')
        if not rec_id:
            continue
        
        doc_data = {
            "id": rec_id,
            "vendor": r.get('vendor', 'Unknown Vendor'),
            "date": r.get('date', datetime.utcnow().strftime('%Y-%m-%d')),
            "amount": float(r.get('amount') or r.get('total') or 0.0),
            "jobId": r.get('jobId') or r.get('job_id') or 'JOB-104-SUNSET-RIDGE',
            "costCode": r.get('costCode') or r.get('cost_code') or '03-3000-CONCRETE',
            "channel": r.get('channel') or r.get('source') or 'Python Engine',
            "status": r.get('status', 'REQUIRES_REVIEW'),
            "flags": r.get('flags', []),
            "waiverStatus": r.get('waiverStatus', 'MISSING'),
            "updatedAt": firestore.SERVER_TIMESTAMP
        }
        
        db.collection(COLLECTION_NAME).document(rec_id).set(doc_data, merge=True)
        count += 1

    print(f"Synced {count} record(s) from {DB_FILE} to Firestore '{COLLECTION_NAME}'")
    return count

if __name__ == '__main__':
    sync_db_to_firestore()
