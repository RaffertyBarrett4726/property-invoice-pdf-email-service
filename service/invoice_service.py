from __future__ import annotations

from service.infrai_client import InfraiClient
from service.invoice_logic import build_invoice
from service.invoice_renderer import render_email_html, render_invoice_html
from service.models import InvoiceResult, PropertyInvoiceRequest


class PropertyInvoiceService:
    def __init__(self, infrai: InfraiClient):
        self.infrai = infrai

    def issue_invoice(self, request: PropertyInvoiceRequest) -> InvoiceResult:
        prepared = build_invoice(request)
        invoice_html = render_invoice_html(prepared)
        email_html = render_email_html(prepared)

        pdf_env = self.infrai.pdf.generate(
            {
                "html": invoice_html,
                "page_size": "A4",
                "orientation": "portrait",
                "store": True,
            }
        )

        pdf_data = pdf_env["data"]
        pdf_content = pdf_data["url"].split(",", 1)[1]

        email_env = self.infrai.email.send(
            {
                "to": prepared.recipient_email,
                "subject": f"Your invoice {prepared.invoice_number}",
                "html": email_html,
                "attachments": [{"filename": f"{prepared.invoice_number}.pdf", "content": pdf_content}],
            }
        )

        return InvoiceResult(
            invoice_number=prepared.invoice_number,
            total_cents=prepared.total_cents,
            pdf_job_id=pdf_data.get("job_id"),
            message_id=email_env["data"]["message_id"],
        )
