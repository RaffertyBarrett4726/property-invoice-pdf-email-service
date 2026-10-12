from __future__ import annotations

import json
import os
from datetime import date
from urllib.request import Request, urlopen

payload = {
    "property_name": "Maple Court",
    "property_address": "18 River St, Unit Building A",
    "invoice_date": date.today().isoformat(),
    "period_label": "November 2026",
    "recipient": {
        "name": "Jamie Lee",
        "email": os.environ["INVOICE_RECIPIENT_EMAIL"],
        "unit": "A-12"
    },
    "base_rent_cents": 150000,
    "maintenance_requests": [
        {
            "title": "Lost mailbox key replacement",
            "status": "completed",
            "tenant_responsible": True,
            "charge_cents": 2500
        },
        {
            "title": "Hallway light inspection",
            "status": "scheduled",
            "tenant_responsible": False,
            "charge_cents": 0
        }
    ],
    "tenant_documents": [
        {
            "name": "Lease renewal 2026",
            "kind": "lease",
            "reference": "DOC-2026-RENEWAL"
        }
    ],
    "inspection_reminder": {
        "due_date": date.today().isoformat(),
        "note": "Please confirm access window with the property office."
    }
}

request = Request(
    url=os.environ.get("INVOICE_API_URL", "http://127.0.0.1:8000/issue-invoice"),
    method="POST",
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload).encode("utf-8"),
)

with urlopen(request) as response:
    print(response.read().decode("utf-8"))
