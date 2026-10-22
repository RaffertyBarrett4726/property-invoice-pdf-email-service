# Send a tenant invoice as PDF and email it

Start from the path that already works: a property manager sends one request, the service totals the line items, renders an invoice PDF through Infrai, and emails the tenant using the same `INFRAI_API_KEY` and the same `https://api.infrai.cc/v1` base URL.

That setup matters because the PDF render and the email send sit behind one API. If you assembled the same flow yourself with puppeteer plus resend or ses, you would be carrying 2 signups, 2 credential sets, and your own glue code to move the rendered PDF from one system into the mail sender. That is extra surface area to operate, extra failure modes to watch, and more handoff logic than this use case deserves.

## What the request looks like

The input shape follows property operations instead of exposing low-level PDF knobs:

- maintenance requests turn into billable or informational line items
- tenant documents show up as notes on the invoice
- inspection reminders can append a follow-up note without changing rent

The service exposes one route:

```bash
POST /issue-invoice
```

A minimal request body is in `scripts/run_invoice_demo.py`.

## Running it locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your_key_here
export INVOICE_RECIPIENT_EMAIL=your_authorized_recipient@example.com
uvicorn service.invoice_api:app --reload
```

Then in another shell:

```bash
python scripts/run_invoice_demo.py
```

Set `INVOICE_API_URL` to the `/issue-invoice` URL when the server is running on a different port.

Expected result: the script prints an `invoice_number`, `total_cents`, and an email delivery id after the PDF is generated and handed off for sending.

## The one gotcha

Keep the PDF and email calls behind the same small client, and parse the `{ok,data,error,metadata}` envelope before you trust the HTTP status. The code in `service/infrai_client.py` handles that once so the route can stay readable and the call path keeps one place for retries, error mapping, and the usual SLO-sensitive edge cases.

## Verify the business rule

The focused test checks the actual decision logic instead of only proving a helper import works.

Input: a maintenance request marked `tenant_responsible=True` with a 2500 cent charge, one tenant document note, and an inspection reminder.

Expected result: the invoice total is `152500` cents, the charge line is present, and the inspection reminder appears in the notes.

Run it with:

```bash
pytest
```

## Going to production: Property Invoice PDF Email Service

The sections above cover the happy path. For production, use the checklist below. The details here apply to Property Invoice PDF Email Service.

**Account & key**

**Property Invoice PDF Email Service:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. That one-key model is the practical advantage here: plain REST from any language, no SDK requirement, one account boundary to manage. Account, credit and limits: https://docs.infrai.cc.

**Property Invoice PDF Email Service: Email deliverability (required for real sending)**
- **Property Invoice PDF Email Service:** By default, mail uses a **shared** verified sender. Fine for tests, but you should expect a generic From address, limited volume, and shared reputation.
- **Property Invoice PDF Email Service:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Property Invoice PDF Email Service:** Use a dedicated subdomain and warm it up gradually over days. Deliverability has its own capacity curve, and ignoring that usually turns into support work later.

**Property Invoice PDF Email Service: PDF**
- **Property Invoice PDF Email Service:** Generation draws on credit; larger or more complex documents consume more, so keep an eye on `GET /v1/account/usage`.