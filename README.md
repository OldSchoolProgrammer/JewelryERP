# Jewelry Store ERP

A Django-based web application for managing a jewelry store's inventory, sales, customers, and suppliers.

## Features

- **Inventory Management**: Track jewelry items with SKU, metal type, purity, weight, and stone details
- **Customer & Supplier Management**: Maintain customer and supplier records
- **Invoice System**: Create and manage invoices with line items
- **Stripe Payment Integration**: Generate payment links via Stripe Checkout Sessions
- **Email Notifications**: Send invoices, payment confirmations, and certificates via Gmail SMTP
- **PDF Certificates**: Generate jewelry authenticity certificates

## Tech Stack

- Django 6.0
- Bootstrap 5
- SQLite (dev) / Microsoft SQL Server (prod)
- Stripe API
- ReportLab (PDF generation)

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

Required environment variables:
- `SECRET_KEY`: Django secret key
- `STRIPE_SECRET_KEY`: Your Stripe secret key (starts with `sk_`)
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook signing secret
- `EMAIL_HOST_USER`: Gmail address
- `EMAIL_HOST_PASSWORD`: Gmail app password

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000

## Stripe Webhook (Local Testing)

For local webhook testing, use Stripe CLI:

```bash
stripe listen --forward-to localhost:8000/sales/webhook/stripe/
```

Copy the webhook signing secret to your `.env` file.

## Production (Docker + Traefik + SQL Server)

This repo includes a production Docker setup intended to run behind Traefik (TLS termination) and connect to an existing SQL Server container named `sqlserver` on the `backend` Docker network.

### 1) Configure environment

- Copy `.env.example` to `.env` and fill in:
	- `SA_PASSWORD` (SQL Server `sa` password)
	- `DJANGO_SECRET_KEY` (used as Django `SECRET_KEY` in compose)
	- Stripe + email variables

### 2) Start with docker compose

The app service is defined in `web_apps_docker-compose.yml` and is meant to join external networks `frontend` (Traefik) and `backend` (SQL Server).

```bash
docker compose -f web_apps_docker-compose.yml up -d --build
```

On startup, the container will:

- Create the SQL Server database `michaellobmdb` if it doesn't exist yet
- Run `migrate`
- Run `collectstatic`
- Start Gunicorn on port 8000 (internal Docker networking)

### 3) Traefik routing

Traefik labels in `web_apps_docker-compose.yml` route:

- `https://michaellobmapp.pandoraio.net` → the Django container

### 4) Build and push to Docker Hub

Docker Hub repositories are namespaced by your username. Build and push like:

```bash
docker build -t <your_dockerhub_username>/michaellobmapp:latest .
docker login
docker push <your_dockerhub_username>/michaellobmapp:latest
```

Then set `MICHAELLOBMAPP_IMAGE=<your_dockerhub_username>/michaellobmapp:latest` in `.env` and run:

```bash
docker compose -f web_apps_docker-compose.yml pull michaellobmapp
docker compose -f web_apps_docker-compose.yml up -d
```

## Project Structure

```
ERPapp/
├── config/          # Django project settings
├── inventory/       # Inventory management app
├── crm/             # Customer & Supplier management
├── sales/           # Invoices & Stripe integration
├── documents/       # Certificate PDF generation
├── notifications/   # Email services
├── templates/       # HTML templates
├── static/          # Static files
└── media/           # Uploaded files & generated PDFs
```

## Usage

1. Log in with your superuser credentials
2. Add categories and inventory items
3. Add customers and suppliers
4. Create invoices and add line items
5. Send invoices (generates Stripe payment link and emails customer)
6. After payment, generate certificates for sold items
