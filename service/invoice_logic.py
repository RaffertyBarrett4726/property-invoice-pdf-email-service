from __future__ import annotations

from service.models import InvoiceLineItem, PreparedInvoice, PropertyInvoiceRequest


def build_invoice(request: PropertyInvoiceRequest) -> PreparedInvoice:
    line_items = [
        InvoiceLineItem(description=f"Rent for {request.period_label}", amount_cents=request.base_rent_cents)
    ]
    notes: list[str] = []

    for maintenance in request.maintenance_requests:
        if maintenance.tenant_responsible and maintenance.charge_cents > 0:
            line_items.append(
                InvoiceLineItem(
                    description=f"Maintenance charge: {maintenance.title}",
                    amount_cents=maintenance.charge_cents,
                )
            )
        else:
            notes.append(f"Maintenance update: {maintenance.title} ({maintenance.status})")

    for document in request.tenant_documents:
        notes.append(f"Document on file: {document.kind} {document.name} ({document.reference})")

    if request.inspection_reminder:
        notes.append(
            f"Inspection reminder for {request.inspection_reminder.due_date.isoformat()}: "
            f"{request.inspection_reminder.note}"
        )

    total_cents = sum(item.amount_cents for item in line_items)
    invoice_number = (
        f"INV-{request.invoice_date.strftime('%Y%m%d')}-"
        f"{request.recipient.unit.replace(' ', '').replace('#', '')}"
    )

    return PreparedInvoice(
        invoice_number=invoice_number,
        recipient_name=request.recipient.name,
        recipient_email=request.recipient.email,
        property_name=request.property_name,
        property_address=request.property_address,
        unit=request.recipient.unit,
        invoice_date=request.invoice_date,
        period_label=request.period_label,
        line_items=line_items,
        notes=notes,
        total_cents=total_cents,
    )


def cents_to_dollars(cents: int) -> str:
    return f"${cents / 100:.2f}"
