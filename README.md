You want to check here and now:

[Live Demo](https://lensmaster-pro.onrender.com)
[👤 Demo Users](#-demo-users)

---

# 📷 LensMaster Pro

![Python](https://img.shields.io/badge/python-3.14-blue.svg)
![Django](https://img.shields.io/badge/django-6.0.3-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-latest-blue.svg)
![Bootstrap](https://img.shields.io/badge/bootstrap-5.3-purple.svg)
![Cloudinary](https://img.shields.io/badge/cloudinary-media_storage-3448C5.svg)
![License](https://img.shields.io/badge/license-educational-lightgrey.svg)

**LensMaster Pro** is a full-featured Django web application for professional photography and videography studios. It combines a curated portfolio showcase, service package management, client booking requests, studio equipment inventory, and a role-based access system — all wrapped in a polished dark-theme UI with green glow accents.

---

## 📌 Table of Contents
- [✨ Key Features](#-key-features)
- [🔐 Security & Permissions](#-security--permissions)
- [🏗️ Architecture Overview](#️-architecture-overview)
- [🧭 Site Map & Operations](#-site-map--operations)
- [🗂️ Directory Structure](#️-directory-structure)
- [🚀 Installation & Setup](#-installation--setup)
- [👤 Demo Users](#-demo-users)
- [🌐 Live Demo](#-live-demo)
- [🖼️ Screenshots](#️-screenshots)
- [🧪 Data Management](#-data-management)
- [🔒 Custom 403 Page](#-custom-403-page)
- [🧩 Custom 404 Page](#-custom-404-page)
- [💥 Custom 500 Page](#-custom-500-page)
- [📊 Studio Statistics](#-studio-statistics)
- [🔌 RESTful API Functionalities](#-restful-api-functionalities)
- [⚙️ Async Tasks on Render — Django Q2](#️-async-tasks-on-render--django-q2)
- [☁️ Async Tasks on Azure — Celery & REST](#️-async-tasks-on-azure--celery--rest)
- [🗃️ Tech Stack](#️-tech-stack)
- [🧾 Project Notes](#-project-notes)

---

## ✨ Key Features

- **Multi-app Architecture**: Clean separation of concerns across `accounts`, `bookings`, `productions`, `inventory`, and `common`.
- **Role-Based Access Control**: Custom `PhotographerRequiredMixin` restricts all CRUD operations to the `Photographers` group. Regular users and anonymous visitors have read-only access. The owner (super user) have full access (staff management).
- **Full CRUD Functionality**: Complete management for **Productions**, **Categories**, **Service Packages**, and **Equipment** — all protected behind permission checks.
- **Dynamic Portfolio**: Categorized project showcase with detailed production pages, related items, search, and pagination.
- **Client Booking System**: Public booking request form with auto-fill from user profile, server-side validation, and status tracking.
- **Favorites System**: Logged-in users can favorite Productions, Equipment, and Service Packages — all visible on their profile page.
- **Inventory Tracking**: Professional equipment management with auto-generated `INV-XXXX` IDs, type-based filtering, and production linkage.
- **Studio Statistics Dashboard**: Photographer-only analytics page with top productions, most-booked packages, equipment usage, booking breakdowns by status and source.
- **Package Filtering**: Service packages grouped by category with dedicated per-category listing pages.
- **Cloudinary Integration**: Production image storage via Cloudinary in deployed environments; local filesystem in development.
- **Production Ready**: PostgreSQL, environment-based configuration, WhiteNoise static files, and custom 403, 404, and 500 error handling.

---

## 🔐 Security & Permissions

LensMaster Pro implements a layered security model:

| Layer | Implementation |
|---|---|
| **CSRF Protection** | Django default — all forms protected |
| **SQL Injection** | Django ORM — no raw queries |
| **XSS Protection** | Django template auto-escaping |
| **Clickjacking** | `X_FRAME_OPTIONS = 'DENY'` in production |
| **Secure Cookies** | `SESSION_COOKIE_SECURE` + `CSRF_COOKIE_SECURE` in production |
| **Content Sniffing** | `SECURE_CONTENT_TYPE_NOSNIFF` in production |
| **Authentication** | Django `LoginRequiredMixin` for user-specific views |
| **Authorization** | Custom `PhotographerRequiredMixin` for all write operations |
| **Stats Access** | `UserPassesTestMixin` — Photographers and superusers only |
| **Profile Isolation** | `get_object()` always returns `request.user.profile` — no URL spoofing |
| **Image Validation** | Server-side file type and size checks on all image uploads |

### Permission Matrix

| Action | Anonymous | Logged-in User | Photographer |
|---|---|---|---|
| Browse portfolio, packages, inventory | ✅ | ✅ | ✅ |
| Submit booking request | ✅ | ✅ (auto-fill) | ✅ |
| Favorite productions / equipment / packages | ❌ | ✅ | ✅ |
| View own profile & bookings | ❌ | ✅ | ✅ |
| Create / Edit / Delete any content | ❌ | ❌ | ✅ |
| View Studio Statistics | ❌ | ❌ | ✅ |
| Django Admin | ❌ | ❌ | ✅ (superuser) |

---

## 🏗️ Architecture Overview

- **`accounts/`**: Custom user model, registration/login/logout, profile management, and the Studio Statistics dashboard.
- **`productions/`**: Portfolio categories and project showcases — public browsing + full CRUD for Photographers.
- **`bookings/`**: Service packages (with per-category filtering) and client booking request flow with status management.
- **`inventory/`**: Studio equipment tracking with type-based filtering, production linkage, and full CRUD.
- **`common/`**: Shared abstract models (`TimestampedMixin`, `SlugMixin`, `ActiveStatusMixin`), `PhotographerRequiredMixin`, custom template tags, and global views (Home, base, 403, 404, 500).
- **`lensmaster_pro/`**: Core project configuration, URL routing, and custom static file storage.

---

## 🧭 Site Map & Operations

| Feature / Page | Exact URL Path | Access | Operations |
| :--- | :--- | :--- | :--- |
| **Home** | `/` | Public | View featured categories and latest work |
| **Portfolio Categories** | `/portfolio/categories/` | Public | Browse all categories |
| **Add Category** | `/portfolio/category/create/` | Photographer | Create new category with cover image |
| **Edit Category** | `/portfolio/category/<pk>/edit/` | Photographer | Edit existing category |
| **Delete Category** | `/portfolio/category/<pk>/delete/` | Photographer | Remove with confirmation |
| **Category Details** | `/portfolio/category/<slug>/` | Public | List productions with search & pagination |
| **Production Details** | `/portfolio/production/<slug>/` | Public | Full project view with related productions |
| **Add Production** | `/portfolio/add/` | Photographer | Create new production |
| **Edit Production** | `/portfolio/production/<slug>/edit/` | Photographer | Edit existing production |
| **Delete Production** | `/portfolio/production/<slug>/delete/` | Photographer | Remove with confirmation |
| **Service Packages** | `/bookings/packages/` | Public | Browse packages grouped by category |
| **Packages by Category** | `/bookings/packages/by_category/<id>/` | Public | Filter packages by service category |
| **Add / Edit / Delete Package** | `/bookings/packages/create/` etc. | Photographer | Full package CRUD |
| **Booking Request** | `/bookings/request/` | Public | Client intake form with auto-fill for logged-in users |
| **Booking List** | `/bookings/` | Photographer | Manage all bookings with search & status filter |
| **Edit / Delete Booking** | `/bookings/<pk>/edit/` etc. | Photographer | Update status, notes, date, package |
| **Inventory** | `/inventory/` | Public | Studio gear grouped by type |
| **Equipment by Type** | `/inventory/type/<type>/` | Public | Filter by Camera, Drone, Lens, etc. |
| **Equipment Detail** | `/inventory/<pk>/` | Public | Full equipment view with linked productions |
| **Add / Edit / Delete Equipment** | `/inventory/create/` etc. | Photographer | Full equipment CRUD |
| **Profile** | `/accounts/profile/` | Logged-in | View favorites, bookings, personal info |
| **Edit Profile** | `/accounts/profile/edit/` | Logged-in | Update personal info and avatar |
| **Studio Statistics** | `/accounts/stats/` | Photographer | Analytics dashboard |
| **Admin Panel** | `/admin/` | Superuser | Full database management |

---

## 🗂️ Directory Structure

```text
lensmaster_pro/
├── accounts/          # User auth, profiles, statistics dashboard
├── bookings/          # Service packages & client booking requests
├── productions/       # Portfolio categories & project showcases
├── inventory/         # Studio equipment & gear tracking
├── common/            # Shared abstract models, mixins & utilities
├── lensmaster_pro/    # Core project configuration (settings, urls, storage)
├── static/            # Global CSS, JavaScript, and images
└── templates/         # HTML templates organized by application module
```

---

## 🚀 Installation & Setup

### 1) Clone the repository
```bash
git clone https://github.com/AlAleksandrov/lensmaster_pro.git
cd lensmaster_pro
```

### 2) Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3) Configuration
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True

ALLOWED_HOSTS=127.0.0.1,localhost,lensmaster-pro-2-0.onrender.com,lensmasterpro2-ghgmfnbbhfayfneh.spaincentral-01.azurewebsites.net
CSRF_TRUSTED_ORIGINS="http://127.0.0.1,http://localhost,https://lensmaster-pro-2-0.onrender.com,https://lensmasterpro2-ghgmfnbbhfayfneh.spaincentral-01.azurewebsites.net"

DB_ENGINE=django.db.backends.postgresql
DB_NAME=lensmaster_pro_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=5432
DATABASE_URL=postgresql://DB_USER:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME

CLOUDINARY_CLOUD_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

STATIC_URL=/static/
STATIC_ROOT=staticfiles

# Mailjet is used as the email provider for booking confirmation emails
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=in-v3.mailjet.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your_mailjet_API_key
EMAIL_HOST_PASSWORD=your_mailjet_secret_key
COMPANY_EMAIL=your_email_verified_in_mailjet
DEFAULT_FROM_EMAIL=your_email_verified_in_mailjet

ASYNC_TASK_BACKEND=celery # or django_q
REDIS_URL=redis://localhost:6379/0
```

### 4) Initialize Database
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Access the site at: **http://127.0.0.1:8000/**

### 5) Create the Photographers Group
The `Photographers` group is created automatically via a data migration (`0002_create_groups.py`). To assign a user:
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from django.contrib.auth.models import Group
>>> User = get_user_model()
>>> user = User.objects.get(username='your_username')
>>> group = Group.objects.get(name='Photographers')
>>> user.groups.add(group)
```
Or simply assign the group from the Django Admin panel.

---

## 👤 Demo Users

To simplify evaluation, the project includes pre-configured users:

| Role | Username |
|---|---|
| 3 Photographers | alex_lens, maria_photo, ivan_shoot → group Photographers |
| 7 Regular Users | sofia_bride, peter_corp, elena_events, georgi_client, anna_wedding, nikola_biz, diana_art → group Clients |
| Password | Test1234! 'for all') |

> Admin and Photographers has full CRUD + access to `/accounts/stats/`

---

## 🌐 Live Demo

- [Live Demo — Render](https://lensmaster-pro.onrender.com)
- [Live Demo — Azure](coming soon)

---

## 🖼️ Screenshots
![Home page](static/images/screenshot-home-new.png)
![Portfolio page](static/images/screenshot-our-portfolio.png)
![Production details](static/images/screenshot-production-new.png)
![Booking request](static/images/screenshot-booking_request.png)
![Profile page](static/images/screenshot-profile_page.png)
![Booking list](static/images/screenshot-booking_list.png)
![Studio stats](static/images/screenshot-stats.png)
![403 error](static/images/screenshot-403_access_denied.png)

---

## 🧪 Data Management

### Via the Site UI (recommended)
1. Register an account and assign it to the `Photographers` group via Admin.
2. Go to `/portfolio/categories/` → click **+ Add Category**.
3. Go to `/inventory/` → click **+ Add Equipment**.
4. Go to `/bookings/packages/` → click **+ Add Package**.
5. Go to `/portfolio/category/<slug>/` → click **+ Add New Production** inside a category.
6. Go to `/bookings/request/` to submit a booking as a client.

### Via Django Admin
1. Login at `/admin/`.
2. Add **Categories** first (required for Productions and Packages).
3. Add **Equipment** to the inventory.
4. Add **Service Packages**.
5. Add **Productions** linked to categories.
6. Manage **Booking Requests** and update their status.

---

## 🔒 Custom 403 Page
To test the access denied error handler, set `DEBUG=False` in your `.env`, go to a service package or inventory list page as an admin or photographer, choose any package or equipment from the list, then open its detail page and note the `<int:pk>` from the URL. Click the **Edit** button, uncheck **Active**, and save the changes. Visit the same route as an anonymous user or a regular client:
```
http://127.0.0.1:8000/bookings/packages/<int:pk>/

http://127.0.0.1:8000/inventory/<int:pk>/

http://127.0.0.1:8000/accounts/stats/
```

---

## 🧩 Custom 404 Page
To test the custom error handler, set `DEBUG=False` in your `.env` and visit any non-existent URL:
```
http://127.0.0.1:8000/non-existent-page/
```

---

## 💥 Custom 500 Page
To test the internal server error handler, set `DEBUG=False` in your `.env`, temporarily add a "division by zero" or raise Exception in one of your views, and visit that route:
```
http://127.0.0.1:8000/route-with-error/
```

---

## 📊 Studio Statistics

The `/accounts/stats/` page is accessible only to Photographers and superusers. It provides:

- **Top Productions** by number of user favorites
- **Top Service Packages** by favorites and by booking count
- **Most Favourite Equipment** by user favorites
- **Most Used Equipment** by number of linked productions
- **Categories** ranked by production count
- **Bookings by Status** (pending / confirmed / cancelled)
- **Bookings by Source** (how clients heard about the studio)
- **KPI Cards**: total productions, equipment, packages, bookings, confirmed bookings

---

## 🔌 RESTful API Functionalities

LensMaster Pro includes a REST API for bookings and service packages, implemented with **Django REST Framework**. The API currently exposes endpoints for listing, creating, and retrieving selected data from the `bookings` app.

### Available endpoints

#### Service Packages
- `GET /api/service-packages/`
  - Returns a list of active service packages.
  - Supports:
    - filtering via `ServicePackageFilter`
    - search by `name` and `description`
    - ordering by `price` and `duration_hours`

- `GET /api/service-packages/<int:pk>/`
  - Returns the details of a single service package.

#### Booking Requests
- `GET /api/booking-requests/`
  - Returns a list of booking requests.
  - Supports:
    - filtering via `BookingRequestFilter`
    - search by `first_name`, `last_name`, and `email`

- `POST /api/booking-requests/create/`
  - Creates a new booking request.
  - If the request is made by an authenticated user, the booking is linked to that user automatically.

### Permissions

- **Service packages**
  - Read access is available to authenticated and anonymous users.
  - The list endpoint returns only active packages.

- **Booking requests**
  - Both listing and creating booking requests require authentication.

### Serializers

The API uses serializer-based validation for:
- `ServicePackage`
- `BookingRequest`

For booking requests:
- `user` and `status` are read-only
- authenticated users are attached automatically on create

### Notes

The API is focused on the `bookings` app and is ready for future extension with additional endpoints if needed.

---

## ⚙️ Async Tasks on Render — Django Q2

LensMaster Pro uses **Django Q2** to process long-running background jobs without blocking the request/response cycle. This is especially important when a photographer confirms a booking request and the application needs to send a confirmation email immediately, but asynchronously.

Instead of sending the email directly inside the view or form save logic, the project:
1. detects the status change to `CONFIRMED`,
2. enqueues a background task with `async_task()`,
3. lets the Django Q worker process the email in the background,
4. returns control to the user immediately.

### How it works

```
              text Booking status changes to CONFIRMED
                                ↓
              Django signal detects the transition
                                ↓
              async_task() enqueues the email job
                                ↓
              Django Q cluster picks up the task
                                ↓
              Background worker sends the confirmation email
```

### Why Django Q2?

LensMaster Pro uses Django Q2 on Render because it is a practical fit for this deployment:

- **No external broker required** — it uses the existing PostgreSQL database
- **Simple local development** — no Redis server needed
- **Easy monitoring** — tasks are visible in Django Admin
- **Clean separation of concerns** — views stay focused on HTTP logic, while background jobs handle side effects

### Configuration (`settings.py`)

```python
Q_CLUSTER = {
    'name': 'lensmaster',
    'workers': 4,
    'timeout': 60,
    'retry': 90,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',
}
```

### Task workflow in the project

The booking confirmation flow is implemented in three layers:

#### 1. Signal layer
A Django signal watches for booking updates and checks whether the status changed from anything else to `CONFIRMED`.

#### 2. Queue layer
When that transition happens, the signal uses `async_task()` to place the email job into the Django Q queue.

#### 3. Worker layer
A running `qcluster` process picks up the task and executes the email-sending function in the background.

### Starting the worker

```bash
python manage.py qcluster
```

Run this in a separate terminal during development. On Render, the worker is configured as a separate background service.

### Example usage with shell:

```bash
python manage.py shell
```

```python
from django_q.tasks import async_task
from bookings.models import BookingRequest

booking = BookingRequest.objects.first()
if booking:
    async_task('bookings.tasks.send_booking_confirmation', booking_id=booking.pk)
```

### Task monitoring

Completed, failed, and queued tasks are visible in the Django Admin under the **Django Q** section. This makes background processing easy to inspect without additional tooling.

### Notes

- The booking confirmation email is sent only when the booking status changes to `CONFIRMED`.
- The task is executed asynchronously, so the user does not wait for the email server.
- This implementation is ideal for the Render deployment where PostgreSQL is already available and Redis is not necessary.

---

## ☁️ Async Tasks on Azure — Celery & Redis

For the Azure deployment, LensMaster Pro uses **Celery** with **Redis** to handle background jobs asynchronously. The main use case is the same as on Render: when a booking request is confirmed, the confirmation email should be sent without blocking the request/response cycle.

In this setup, the web application places the job into a Redis-backed queue, and a separate Celery worker processes it in the background. This keeps the user interface responsive and makes the system scalable for production use.

### How it works

```
              text Booking status changes to CONFIRMED
                                ↓
              Django view or signal triggers a Celery task
                                ↓
              Task is sent to Redis as the message broker
                                ↓
              Celery worker picks up the job
                                ↓
              Confirmation email is sent in the background
```

### Why Celery + Redis?

LensMaster Pro uses Celery on Azure because this stack is a strong fit for production environments:

- **Reliable task processing** with a mature background job system
- **Redis message broker** for fast task delivery
- **Scalable architecture** with separate web and worker processes
- **Better fit for cloud deployments** where independent worker instances are available
- **Clean separation of concerns** between the web app and asynchronous work
- **Mailjet SMTP** for transactional emails such as booking confirmations

### Configuration overview

Celery is configured to work with the Django project settings and to autodiscover task modules automatically.

**`lensmaster_pro/celery.py`**
```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lensmaster_pro.settings')

app = Celery('lensmaster_pro')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**`lensmaster_pro/__init__.py`**
```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

**`settings.py`**
```python
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Sofia'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 60 * 5

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
)

EMAIL_HOST = os.getenv("EMAIL_HOST", "in-v3.mailjet.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER or "noreply@lensmaster.com",
)

INSTALLED_APPS += ['django_celery_results']
```

### Task workflow in the project

The booking confirmation flow follows three steps:

#### 1. Application layer
A view or signal detects that a booking has been confirmed.

#### 2. Queue layer
The application enqueues a Celery task using `.delay()` or `.apply_async()`.

#### 3. Worker layer
A separate Celery worker receives the job from Redis and sends the confirmation email.

### Example task

```python
# bookings/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from bookings.models import BookingRequest

@shared_task
def send_booking_confirmation(booking_id):
    booking = BookingRequest.objects.get(pk=booking_id)
    send_mail(
        subject='Booking Confirmed — LensMaster Pro',
        message=f'Hi {booking.first_name}, your session on {booking.preferred_date} is confirmed.',
        from_email='noreply@lensmasterpro.com',
        recipient_list=[booking.email],
    )
```

### Triggering the task

```python
from bookings.tasks import send_booking_confirmation

booking = BookingRequest.objects.first()
booking_id = booking.pk
send_booking_confirmation.delay(booking_id)
```

### Running Redis with Docker locally

If you do not have Redis installed locally, you can start it with Docker:
```bash
# Start Redis server
docker run -d --name redis -p 6379:6379 redis

# Check Redis is working
docker ps
>STATUS: Up

# Test
docker exec -it redis redis-cli ping
>PONG
```

### Starting the worker

```bash
# Development
celery -A lensmaster_pro worker -P solo -l info

# Production (with concurrency)
celery -A lensmaster_pro worker --loglevel=warning --concurrency=2 --uid=nobody
```

### Azure deployment model

On Azure, the application is split into separate services:

| Component | Azure Service |
|---|---|
| **Web App** | Azure App Service |
| **Celery Worker** | Azure App Service / Web Job / Container Instance |
| **Message Broker** | Azure Cache for Redis |
| **Result Backend** | PostgreSQL via `django-celery-results` |
| **Media Storage** | Cloudinary |

### Notes

- Celery is used for production-grade asynchronous processing.
- Redis acts as the broker between the web app and worker.
- The worker must run continuously to process queued jobs.
- This architecture is a better match for Azure than Django Q, because it supports distributed task processing and independent worker scaling.

---

## 🗃️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 6.0 (Python 3.14) |
| **Database** | PostgreSQL |
| **Forms** | `django-crispy-forms` with Bootstrap 5 |
| **Images** | Pillow + Cloudinary (production) |
| **Static Files** | WhiteNoise |
| **Environment** | `python-dotenv` |
| **Frontend** | Bootstrap 5.3 + Bootstrap Icons + Custom CSS (dark theme, green glow panels) |
| **Admin** | `django-unfold` (enhanced admin UI) |
| **Task Queue** | `django-q` + Celery & Redis |
| **API** | `djangorestframework` |
| **Deployment** | Render + Azure |

---

## 🧾 Project Notes

- **Git History**: Includes commits on multiple separate days as required.
- **Custom Template Tags**: `formatting` templatetag library with `|eur` (currency formatter) and `|hours_label` (pluralization) filters.
- **Pagination**: Implemented across Portfolio Categories, Productions by Category, Equipment list, Equipment by Type, Booking list, and Package list.
- **Slug Auto-generation**: Categories and Productions auto-generate slugs from their `name`/`title` on save via `SlugMixin`.
- **Equipment IDs**: Auto-generated internal inventory IDs in format `INV-XXXX` if not provided manually.
- **Image Validation**: Server-side validation for cover images (file type and size checks) on Category, Production, and Equipment forms.
- **Favorites**: M2M relationship between `Profile` and Productions / Equipment / Packages — toggle via POST with `LoginRequiredMixin`.
- **Booking Auto-fill**: `BookingCreateView` pre-fills first name, last name, email, phone, and city from the logged-in user's profile.
- **Data Migrations**: `0002_create_groups.py` automatically creates the `Photographers` group on first migrate.
- **License**: Educational project — Django Advanced Exam.
