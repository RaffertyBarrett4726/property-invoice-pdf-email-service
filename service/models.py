from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class MaintenanceRequest(BaseModel):
    title: str
    status: Literal["open", "scheduled", "completed"]
    tenant_responsible: bool = False
    charge_cents: int = Field(default=0, ge=0)


class TenantDocument(BaseModel):
    name: str
    kind: Literal["lease", "notice", "receipt", "inspection"]
    reference: str


class InspectionReminder(BaseModel):
    due_date: date
    note: str


class InvoiceRecipient(BaseModel):
    name: str
    email: EmailStr
    unit: str


class PropertyInvoiceRequest(BaseModel):
    property_name: str
    property_address: str
    invoice_date: date
    period_label: str
    recipient: InvoiceRecipient
    base_rent_cents: int = Field(ge=0)
    maintenance_requests: list[MaintenanceRequest] = Field(default_factory=list)
    tenant_documents: list[TenantDocument] = Field(default_factory=list)
    inspection_reminder: InspectionReminder | None = None


class InvoiceLineItem(BaseModel):
    description: str
    amount_cents: int = Field(ge=0)


class PreparedInvoice(BaseModel):
    invoice_number: str
    recipient_name: str
    recipient_email: EmailStr
    property_name: str
    property_address: str
    unit: str
    invoice_date: date
    period_label: str
    line_items: list[InvoiceLineItem]
    notes: list[str]
    total_cents: int = Field(ge=0)


class InvoiceResult(BaseModel):
    invoice_number: str
    total_cents: int
    pdf_job_id: str | None = None
    message_id: str
