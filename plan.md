# Implementation Plan — Django Jewelry Store ERP (Inventory, Sales, Customers, Suppliers)

## 0) Current state (codebase analysis)
- Workspace folder: `D:\Programming Projects\ERPapp`
- Current contents: **empty directory** (no existing Django project, no code).
- Approach: plan assumes a **greenfield** Django project.

## 1) Goals (MVP)
Build a simple web app for a jewelry store using:
- **Backend:** Django
- **UI:** Bootstrap
- **DB:** SQLite
- **Modules:** Inventory, Sales (invoice-style), Customers, Suppliers
- **Payments:** Stripe **Checkout Session** link generation + webhook to mark invoices paid
- **Documents:** Jewelry certificate **PDF generation** (server-side via ReportLab/WeasyPrint) saved to `MEDIA_ROOT`
- **Email:** Gmail SMTP (App Password) for payment confirmations + certificate sending
- **Environment:** Local/dev only (deployment later)

Non-goals for MVP (explicitly out-of-scope unless you later ask):
- Multi-store, advanced RBAC/permissions, multi-currency, accounting integrations, barcode scanning, returns/repairs, multi-warehouse, complex taxes, audit trails, full reporting suite.

## 2) High-level architecture
- **Django project** (single monolith) with apps:
  - `accounts` (optional but recommended): login, simple roles
  - `inventory`: products/jewelry items, categories, stock movements
  - `crm`: customers + suppliers
  - `sales`: invoices, line items, payments, Stripe integration
  - `documents`: certificate PDF generation + storage
  - `notifications`: email sending helpers + templates
- **Templates**: Django templates + Bootstrap 5.
- **Static files**: Bootstrap via CDN for simplicity.
- **Media files**: store generated PDFs under `media/certificates/...`.
- **Stripe**:
  - Create Checkout Session for an invoice
  - Receive Stripe webhook `checkout.session.completed` and mark invoice paid

## 3) Data model (proposed minimal schema)
### 3.1 Inventory
- `JewelryItem`
  - `sku` (unique)
  - `name`
  - `category` (FK)
  - `description`
  - `metal` (choices: Gold/Silver/Platinum/Other)
  - `purity` (e.g., 14K, 18K)
  - `weight_grams` (decimal)
  - `stone_details` (text)
  - `cost_price` (decimal)
  - `sale_price` (decimal)
  - `quantity_on_hand` (int)
  - `is_active` (bool)
  - `created_at`, `updated_at`
- `Category`
  - `name` (unique)

*(For MVP, keep stock simple via `quantity_on_hand`. Later you can add stock movement ledger.)*

### 3.2 CRM
- `Customer`
  - `name`, `email`, `phone`
  - `address` (text)
  - `notes` (text)
- `Supplier`
  - `name`, `email`, `phone`
  - `address` (text)
  - `notes` (text)

### 3.3 Sales (invoice-style)
- `Invoice`
  - `invoice_number` (unique, generated)
  - `customer` (FK, nullable for walk-ins)
  - `status` (Draft/Sent/Paid/Void)
  - `currency` (default `usd`)
  - `subtotal`, `tax`, `discount`, `total` (decimals)
  - `stripe_checkout_session_id` (nullable)
  - `stripe_payment_intent_id` (nullable)
  - `created_at`, `updated_at`
- `InvoiceLine`
  - `invoice` (FK)
  - `item` (FK to `JewelryItem`, nullable if custom line)
  - `description`
  - `quantity` (int)
  - `unit_price` (decimal)
  - `line_total` (decimal)

### 3.4 Documents
- `Certificate`
  - `item` (FK to `JewelryItem`)
  - `invoice` (FK nullable; link certificate to a sale if needed)
  - `pdf_file` (FileField)
  - `certificate_number` (unique)
  - `issued_at`

## 4) Key user flows (MVP)
1. **Manage inventory**: CRUD items/categories, adjust `quantity_on_hand`.
2. **Manage customers/suppliers**: CRUD.
3. **Create invoice**: add lines from inventory, compute totals.
4. **Send invoice**: email customer with Stripe Checkout link.
5. **Customer pays**: Stripe Checkout handles card payment.
6. **Webhook**: marks invoice Paid; triggers confirmation email.
7. **Generate certificate PDF**: for each sold item (or selected items) and email certificate.

## 5) Step-by-step implementation workplan

### 5.1 Project setup
- [ ] Create python venv
- [ ] `pip install django` (+ pinned versions)
- [ ] Start Django project (e.g., `erpapp`) and core apps
- [ ] Add `.env` support (e.g., `python-dotenv` or `django-environ`) for secrets
- [ ] Configure settings for:
  - [ ] `INSTALLED_APPS`
  - [ ] Templates/static
  - [ ] `MEDIA_ROOT`/`MEDIA_URL`
  - [ ] Local SQLite database

Deliverable: App boots locally, admin works.

### 5.2 Authentication & basic UI shell
- [ ] Use Django auth (username/password) and admin-created users
- [ ] Add login/logout views and protect app pages
- [ ] Create base Bootstrap template:
  - [ ] Navbar with Inventory / Sales / Customers / Suppliers / Certificates
  - [ ] Flash messages

Deliverable: Logged-in UI layout with navigation.

### 5.3 Inventory app
- [ ] Models: `Category`, `JewelryItem`
- [ ] Admin registration for quick management
- [ ] Views + templates:
  - [ ] List/search items
  - [ ] Create/edit/delete item
  - [ ] Category CRUD (optional in MVP UI; admin ok)
- [ ] Validations (SKU unique, non-negative quantities/prices)

Deliverable: Inventory CRUD from the web UI.

### 5.4 CRM app (Customers & Suppliers)
- [ ] Models: `Customer`, `Supplier`
- [ ] Admin registration
- [ ] Views + templates for CRUD + simple search

Deliverable: Customer/Supplier management.

### 5.5 Sales app (Invoices)
- [ ] Models: `Invoice`, `InvoiceLine`
- [ ] Invoice number generation (e.g., `INV-YYYYMMDD-####`)
- [ ] Business logic:
  - [ ] Compute totals (subtotal/tax/discount/total)
  - [ ] Update inventory on paid (MVP) or on invoice creation (choose one; default: **on paid**)
- [ ] Views + templates:
  - [ ] Create invoice (select customer)
  - [ ] Add/remove lines
  - [ ] Invoice detail page
  - [ ] Mark sent / void

Deliverable: Invoice lifecycle up to “Sent”.

### 5.6 Stripe integration (Checkout Sessions)
- [ ] Install Stripe SDK (`stripe`)
- [ ] Add environment variables:
  - [ ] `STRIPE_SECRET_KEY`
  - [ ] `STRIPE_WEBHOOK_SECRET`
  - [ ] `STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL`
- [ ] Implement “Generate payment link” action:
  - [ ] Create Stripe Checkout Session for invoice total
  - [ ] Store `stripe_checkout_session_id` on invoice
  - [ ] Redirect user to Stripe-hosted Checkout (or copy link)
- [ ] Implement webhook endpoint:
  - [ ] Verify Stripe signature
  - [ ] Handle `checkout.session.completed`
  - [ ] Mark invoice Paid
  - [ ] Store payment identifiers

Deliverable: Paying an invoice via Stripe updates status to Paid.

### 5.7 Email (Gmail SMTP)
- [ ] Add settings for Gmail SMTP via env vars:
  - [ ] `EMAIL_HOST=smtp.gmail.com`, `EMAIL_PORT=587`, `EMAIL_USE_TLS=True`
  - [ ] `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (App Password)
  - [ ] `DEFAULT_FROM_EMAIL`
- [ ] Email templates:
  - [ ] Invoice email with Stripe Checkout URL
  - [ ] Payment confirmation email
  - [ ] Certificate email with PDF attachment
- [ ] Trigger emails:
  - [ ] On invoice “Send”
  - [ ] On webhook payment completion
  - [ ] On certificate generation (manual + automatic option)

Deliverable: Emails successfully send in local/dev.

### 5.8 Certificate PDF generation
- [ ] Choose PDF generator:
  - [ ] Start with **ReportLab** (pure Python) or WeasyPrint if installed
- [ ] Implement certificate template fields:
  - [ ] Certificate number, item details (SKU, metal, purity, weight, stones), issue date
  - [ ] Optional: store logo
- [ ] Add `Certificate` model + storage
- [ ] Create UI:
  - [ ] Generate certificate for an item (and optionally link to invoice)
  - [ ] Download/view certificate
  - [ ] Email certificate to customer

Deliverable: PDF certificate created and emailed.

### 5.9 Admin, validation, and polish
- [ ] Django admin: register models with useful list filters/search
- [ ] Add basic permissions (Admin vs Staff):
  - [ ] Staff can view/create invoices
  - [ ] Admin can manage inventory/suppliers
  *(Keep minimal for MVP; can rely on admin site if desired.)*
- [ ] Add basic error handling and user-friendly messages

Deliverable: MVP usability.

### 5.10 Local dev ergonomics
- [ ] Add `requirements.txt`
- [ ] Add `.env.example` (no secrets)
- [ ] Document how to run:
  - [ ] migrate
  - [ ] create superuser
  - [ ] runserver
  - [ ] stripe webhook local testing (Stripe CLI optional)

Deliverable: Someone else can run the project locally.

## 6) Testing plan (lightweight)
- [ ] Model tests: totals calculation for invoice
- [ ] Stripe webhook signature verification test (unit-level)
- [ ] Email sending: use Django console backend in dev; one manual Gmail test
- [ ] PDF generation: smoke test that file is created

## 7) Security & configuration notes
- Store secrets only in environment variables (`.env` locally).
- Stripe webhooks must verify signatures.
- Gmail: use App Password; never commit credentials.
- Ensure media files are not served insecurely in production (future).

## 8) Suggested milestones (time-boxed)
- Milestone 1: Project + auth + UI shell
- Milestone 2: Inventory + CRM CRUD
- Milestone 3: Invoices + totals
- Milestone 4: Stripe Checkout + webhook
- Milestone 5: Email flows
- Milestone 6: PDF certificates + email attachment

## 9) Open decisions (confirm/adjust)
- Inventory adjustment timing: default plan updates inventory **when invoice becomes Paid**.
- Tax/discount rules: MVP assumes simple optional tax + discount at invoice level.
- Certificates: issue per sold item, stored in `media/`.
