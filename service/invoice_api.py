from __future__ import annotations

from fastapi import FastAPI, HTTPException

from service.infrai_client import InfraiClient, InfraiError
from service.invoice_service import PropertyInvoiceService
from service.models import InvoiceResult, PropertyInvoiceRequest

app = FastAPI(title="Property Invoice Service")


@app.post("/issue-invoice", response_model=InvoiceResult)
def issue_invoice(request: PropertyInvoiceRequest) -> InvoiceResult:
    service = PropertyInvoiceService(InfraiClient())
    try:
        return service.issue_invoice(request)
    except InfraiError as exc:
        raise HTTPException(status_code=400, detail={"code": exc.code, "error": exc.detail}) from exc
