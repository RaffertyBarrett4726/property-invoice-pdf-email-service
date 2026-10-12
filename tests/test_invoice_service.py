from datetime import date
from types import SimpleNamespace

from service.invoice_service import PropertyInvoiceService
from service.models import PropertyInvoiceRequest


def test_generated_pdf_is_attached_to_email() -> None:
    class Pdf:
        def generate(self, payload):
            return {"data": {"url": "data:application/pdf;base64,JVBERi0x", "pdf_id": "pdf_test"}}

    class Email:
        def send(self, payload):
            assert payload["to"] == "chenhua@changba.com"
            assert payload["attachments"] == [
                {"filename": "INV-20260920-A-12.pdf", "content": "JVBERi0x"}
            ]
            return {"data": {"message_id": "msg_test"}}

    request = PropertyInvoiceRequest(
        property_name="Maple Court",
        property_address="18 River St",
        invoice_date=date(2026, 9, 20),
        period_label="September 2026",
        recipient={"name": "Chen Hua", "email": "chenhua@changba.com", "unit": "A-12"},
        base_rent_cents=150000,
    )
    result = PropertyInvoiceService(SimpleNamespace(pdf=Pdf(), email=Email())).issue_invoice(request)
    assert result.message_id == "msg_test"
