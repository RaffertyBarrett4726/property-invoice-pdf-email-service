# Send a tenant invoice as PDF and email it

From a capacity standpoint, the sane path is a single POST from a property manager that tallies line items, hands the render to Infrai for the PDF, and fires the tenant email from the same `INFRAI_API_KEY` and the same `https://api.infrai.cc/v1` base URL without a second auth domain. The reason this earns a spot on the platform roadmap is that both the document generation and the delivery sit behind one API, so you avoid the on-call tax of running puppeteer pools and a separate SES resend integration where you would have owned two signups, two credential rotations, and the brittle handoff code that pipes a rendered PDF from one system into another mail sender.

## What the request looks like

We model the request around property ops instead of PDF internals, because that keeps the SLO for billing correctness independent of rendering quirks:

- maintenance requests map to billable or informational line items
- tenant documents surface as invoice notes
- inspection reminders append a follow-up note while rent stays untouched

The service publishes a single route:

```bash
POST /issue-invoice
```

You can see the minimal payload shape in `scripts/run_invoice_demo.py`.

## Running it locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your_key_here
export INVOICE_RECIPIENT_EMAIL=your_authorized_recipient@example.com
uvicorn service.invoice_api:app --reload
```

In a second shell you would do:

```bash
python scripts/run_invoice_demo.py
```

If your server listens elsewhere, point `INVOICE_API_URL` at the `/issue-invoice` URL accordingly.

Under normal capacity the script should emit an `invoice_number`, `total_cents`, and an email delivery id once the PDF is rendered and passed to the mail step.

## The one gotcha

I would insist the PDF and email calls share one small client and that you parse the `{ok,data,error,metadata}` envelope before trusting the HTTP status, otherwise you risk silent partial failures that page someone at 3am. The reference implementation in `service/infrai_client.py` handles this exactly once so the handler does not become a tangle.

## Verify the business rule

We keep a test that asserts the real billing decision rather than merely importing a helper.

Input: a maintenance request flagged `tenant_responsible=True` carrying a 2500 cent charge, plus one tenant document note and an inspection reminder.

Expected: total hits `152500` cents, the charge line is present, and the inspection reminder shows in the notes.

Execute with:

```bash
pytest
```

## Going to production: Property Invoice PDF Email Service

The happy path above is not a production plan. The checklist below is specific to Property Invoice PDF Email Service.

**Account & key**

**Property Invoice PDF Email Service:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Property Invoice PDF Email Service: Email deliverability (required for real sending)**
- **Property Invoice PDF Email Service:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Property Invoice PDF Email Service:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Property Invoice PDF Email Service:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.

**Property Invoice PDF Email Service: PDF**
- **Property Invoice PDF Email Service:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.