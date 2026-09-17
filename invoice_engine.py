import json, os, glob

class InvoiceEngine:
    def __init__(self):
        self.processed_ids = set()
        self.records = []

    def process_invoice(self, data):
        inv_id = data.get("invoice_id")
        vendor = data.get("vendor")
        subtotal = data.get("subtotal", 0.0)
        tax = data.get("tax", 0.0)
        total = data.get("total", 0.0)
        flags = []

        # 1. Duplicate check
        if inv_id in self.processed_ids:
            flags.append("DUPLICATE_INVOICE_ID")
        else:
            self.processed_ids.add(inv_id)

        # 2. Math verification (subtotal + tax == total)
        expected_total = round(subtotal + tax, 2)
        if abs(expected_total - total) > 0.01:
            flags.append(f"MATH_MISMATCH (Expected ${expected_total}, Got ${total})")

        # 3. Status determination
        status = "REQUIRES_REVIEW" if flags else "APPROVED_FOR_ERP"

        record = {
            "invoice_id": inv_id,
            "vendor": vendor,
            "job_id": data.get("job_id"),
            "cost_code": data.get("cost_code"),
            "total": total,
            "status": status,
            "flags": flags
        }
        self.records.append(record)
        return record

    def run_directory(self, folder_path):
        files = sorted(glob.glob(os.path.join(folder_path, "*.json")))
        results = []
        for f in files:
            with open(f, 'r') as fp:
                data = json.load(fp)
                results.append(self.process_invoice(data))
        return results

if __name__ == '__main__':
    engine = InvoiceEngine()
    res = engine.run_directory('/home/yayock79/construction_doc_engine/sample_invoices')
    print(json.dumps(res, indent=2))
