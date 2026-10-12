from __future__ import annotations

from html import escape

from service.invoice_logic import cents_to_dollars
from service.models import PreparedInvoice


def render_invoice_html(invoice: PreparedInvoice) -> str:
    rows = "".join(
        f"<tr><td>{escape(item.description)}</td><td style='text-align:right'>{cents_to_dollars(item.amount_cents)}</td></tr>"
        for item in invoice.line_items
    )
    notes = "".join(f"<li>{escape(note)}</li>" for note in invoice.notes) or "<li>No additional notes.</li>"

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #222; padding: 24px;">
        <h1>Tenant Invoice</h1>
        <p><strong>Invoice:</strong> {escape(invoice.invoice_number)}</p>
        <p><strong>Property:</strong> {escape(invoice.property_name)}<br />
           <strong>Address:</strong> {escape(invoice.property_address)}<br />
           <strong>Unit:</strong> {escape(invoice.unit)}</p>
        <p><strong>Tenant:</strong> {escape(invoice.recipient_name)}<br />
           <strong>Period:</strong> {escape(invoice.period_label)}<br />
           <strong>Date:</strong> {invoice.invoice_date.isoformat()}</p>
        <table width="100%" cellspacing="0" cellpadding="8" style="border-collapse: collapse;">
          <thead>
            <tr>
              <th align="left" style="border-bottom:1px solid #ccc;">Line item</th>
              <th align="right" style="border-bottom:1px solid #ccc;">Amount</th>
            </tr>
          </thead>
          <tbody>
            {rows}
            <tr>
              <td style="border-top:1px solid #ccc;"><strong>Total due</strong></td>
              <td style="border-top:1px solid #ccc; text-align:right;"><strong>{cents_to_dollars(invoice.total_cents)}</strong></td>
            </tr>
          </tbody>
        </table>
        <h2 style="margin-top: 28px;">Notes</h2>
        <ul>{notes}</ul>
      </body>
    </html>
    """.strip()


def render_email_html(invoice: PreparedInvoice) -> str:
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #222;">
        <p>Hi {escape(invoice.recipient_name)},</p>
        <p>Your invoice {escape(invoice.invoice_number)} for {escape(invoice.period_label)} is ready.</p>
        <p>Total due: <strong>{cents_to_dollars(invoice.total_cents)}</strong></p>
        <p>The attached PDF includes maintenance notes, tenant document references, and any inspection reminder for this billing cycle.</p>
      </body>
    </html>
    """.strip()
