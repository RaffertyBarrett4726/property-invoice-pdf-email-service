from datetime import date

from service.invoice_logic import build_invoice
from service.models import InspectionReminder, InvoiceRecipient, MaintenanceRequest, PropertyInvoiceRequest, TenantDocument


def test_build_invoice_adds_tenant_charge_and_notes() -> None:
    request = PropertyInvoiceRequest(
        property_name="Maple Court",
        property_address="18 River St",
        invoice_date=date(2026, 11, 1),
        period_label="November 2026",
        recipient=InvoiceRecipient(name="Jamie Lee", email="jamie.lee@example.com", unit="A-12"),
        base_rent_cents=150000,
        maintenance_requests=[
            MaintenanceRequest(
                title="Lost mailbox key replacement",
                status="completed",
                tenant_responsible=True,
                charge_cents=2500,
            )
        ],
        tenant_documents=[
            TenantDocument(name="Lease renewal 2026", kind="lease", reference="DOC-2026-RENEWAL")
        ],
        inspection_reminder=InspectionReminder(
            due_date=date(2026, 11, 15),
            note="Please confirm access window with the property office.",
        ),
    )

    invoice = build_invoice(request)

    assert invoice.total_cents == 152500
    assert invoice.invoice_number == "INV-20261101-A-12"
    assert any(item.description == "Maintenance charge: Lost mailbox key replacement" for item in invoice.line_items)
    assert any("Inspection reminder for 2026-11-15" in note for note in invoice.notes)
