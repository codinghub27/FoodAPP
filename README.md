# 🍔 FoodApp

A full-stack food menu manager built with **Django** and **Django REST Framework**. Users sign up, browse a paginated menu of food items, and add, edit or remove dishes through a clean Tailwind UI. The same data is exposed as a **JWT-secured REST API** with filtering, ordering and pagination, so a mobile app or SPA can use it too.

---

## 📚 Table of Contents

- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Architecture](#️-architecture)
- [Detailed Workflow](#-detailed-workflow)
  - [1. Request Pipeline and Middleware](#1-request-pipeline-and-middleware)
  - [2. Registration, Login and Profile](#2-registration-login-and-profile)
  - [3. Browsing the Menu](#3-browsing-the-menu)
  - [4. Adding an Item](#4-adding-an-item)
  - [5. Editing an Item](#5-editing-an-item)
  - [6. Soft Delete](#6-soft-delete)
  - [7. REST API with JWT](#7-rest-api-with-jwt)
- [Advantages](#-advantages)
- [Data Model](#️-data-model)
- [URL Routes](#️-url-routes)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Local Setup](#️-local-setup)
- [Environment Variables](#-environment-variables)
- [Deployment](#️-deployment)
- [Known Limitations and Future Improvements](#-known-limitations-and-future-improvements)
- [Author](#-author)

---

## 🚀 Features

- 🔐 **Accounts**: register, log in, log out, and a profile page with an avatar (`Profile` model with `ImageField`).
- 📋 **Menu listing**: food cards with image, name, description, price and owner, paginated 5 per page.
- ➕ **Create / ✏️ edit / 🗑️ delete items** through server-rendered Django forms.
- ✅ **Form validation**: price cannot be negative, and the description must add new information beyond the name.
- ♻️ **Soft delete**: deleted items are hidden but kept in the database with a `deleted_at` timestamp, so they can be restored.
- 🔌 **REST API**: full CRUD on `/myapp/api/items/` with a DRF `ModelViewSet` and router.
- 🔑 **JWT authentication** with `djangorestframework-simplejwt` (access + refresh tokens).
- 🔎 **Filtering and ordering** in the API by name and price (`django-filter`, `OrderingFilter`).
- 📄 **API pagination**: 5 items per page via DRF `PageNumberPagination`.
- 🧭 **Custom middleware** that logs every request path, response status and request duration.
- ⚡ **Database indexes** on item name, price, and a composite (owner, price) index for faster queries.
- 🌱 **Seed data**: a fixture with sample dishes (pizza, burger, and more).
- ☁️ **Deploy-ready**: WhiteNoise static files, `DATABASE_URL` support, Gunicorn and a `build.sh` script.

---

## 🛠️ Tech Stack

| Layer | Technology | Role in the project |
|-------|-----------|---------------------|
| Language | Python 3 | Runtime |
| Web framework | Django 6 | ORM, views, forms, auth, templates, admin |
| API | Django REST Framework 3.17 | Serializers, `APIView`, generics, `ModelViewSet`, router |
| API auth | `djangorestframework-simplejwt` | JWT access and refresh tokens |
| Filtering | `django-filter` | `?item_name=` and `?item_price=` filters |
| Frontend | Django templates + Tailwind CSS | Responsive cards, forms and navigation |
| Database | PostgreSQL (`psycopg` / `psycopg2`) | Persistent storage |
| DB config | `dj-database-url`, `python-dotenv` | `DATABASE_URL` or separate `DB_*` variables from `.env` |
| Images | Pillow | Profile picture uploads |
| Static files | WhiteNoise | Compressed static files in production |
| App server | Gunicorn | Production WSGI server |
| Logging | Python `logging` | Console and `debug.log` file handlers |

---

## 🏗️ Architecture

```
            ┌──────────────────────┐        ┌──────────────────────────┐
            │  Browser (Tailwind)  │        │  API client (mobile/SPA) │
            └──────────┬───────────┘        └────────────┬─────────────┘
                       │ session cookie                  │ Bearer JWT
                       ▼                                 ▼
        ┌────────────────────────────────────────────────────────────┐
        │                  Django middleware stack                   │
        │  LogRequestMiddleware → TimeMiddleware → Security →        │
        │  WhiteNoise → Session → CSRF → Auth → Messages             │
        └──────────────┬─────────────────────────────┬───────────────┘
                       │                             │
        ┌──────────────▼──────────────┐   ┌──────────▼─────────────────┐
        │  myapp template views       │   │  DRF ItemViewSet           │
        │  index, detail, create,     │   │  + JWT auth                │
        │  update, delete             │   │  + IsOwnerOrReadOnly       │
        │  (ItemForm validation)      │   │  + filter / order / paginate│
        ├─────────────────────────────┤   │  (ItemSerializer)          │
        │  users views                │   └──────────┬─────────────────┘
        │  register, login, logout,   │              │
        │  profile                    │              │
        └──────────────┬──────────────┘              │
                       └───────────────┬─────────────┘
                                       ▼
                     ┌────────────────────────────────────┐
                     │   Item model + ItemManager          │
                     │   (soft-delete aware queryset)      │
                     └─────────────────┬──────────────────┘
                                       ▼
                               ┌───────────────┐
                               │  PostgreSQL   │
                               └───────────────┘
```

Two Django apps:

- **`myapp`**: the food items, both the HTML pages and the REST API.
- **`users`**: registration, login, logout and the user profile.

---

## 🔄 Detailed Workflow

### 1. Request Pipeline and Middleware

Every request first passes through two custom middlewares in `myapp/middleware.py`:

1. **`LogRequestMiddleware`** prints the request path before the view runs, and the response status code after.
2. **`TimeMiddleware`** measures how long the full request took and prints it (for example `MW Req took 0.04 sec`).

Then the standard Django stack runs: security headers, WhiteNoise for static files, sessions, CSRF protection, authentication and messages. Python logging also writes DEBUG output to the console and to `debug.log`.

### 2. Registration, Login and Profile

1. `/users/register/` shows `RegisterForm` (Django's `UserCreationForm` plus a required email).
2. On success, a flash message ("Welcome <username>, your account has successfully registered") is shown and the user is sent to `/users/login/`.
3. Login uses Django's built-in `LoginView`; on success the user lands on `/myapp/` (`LOGIN_REDIRECT_URL`).
4. `/users/profile/` (login required) shows the username and profile picture from the `Profile` model.
5. `/users/logout/` ends the session and shows a logout page.
6. Django's built-in auth URLs (password change and reset) are also mounted under `/users/`.

### 3. Browsing the Menu

```
GET /myapp/?page=N
      │
      ▼
@login_required ── not logged in ──► redirect to login
      │
      ▼
Item.objects.all()   (ItemManager hides soft-deleted items)
      │
      ▼
Paginator(items, per_page=5) → page_obj
      │
      ▼
index.html: food cards + "Previous / Page X of Y / Next"
```

Clicking a card opens `/myapp/<id>/`, the detail page with a large image, description and price. **Edit** and **Delete** buttons only appear when the logged-in user owns the item.

### 4. Adding an Item

1. `/myapp/add/` renders `ItemForm` with fields for name, description, price and image URL.
2. On submit, the form validates:
   - `clean_item_price`: rejects negative prices.
   - `clean`: rejects a description that just repeats the name ("Desc should add new info").
3. If valid, the item is saved and the user is redirected to the menu. If no image URL is given, a default plate image is used.

### 5. Editing an Item

`/myapp/update/<id>` loads the existing item into `ItemForm(instance=item)`, runs the same validation, saves, and redirects to the menu.

### 6. Soft Delete

```
GET  /myapp/delete/<id>   → confirmation page
POST /myapp/delete/<id>   → item.delete()
                                 │
                                 ▼
                    Item.delete() is overridden:
                    is_deleted = True
                    deleted_at = now()
                    save()        (row stays in the database)
                                 │
                                 ▼
          Item.objects      → excludes is_deleted=True (hidden everywhere)
          Item.all_objects  → plain manager, still sees deleted rows
```

This protects against accidental deletes and keeps a history of removed dishes.

### 7. REST API with JWT

```
POST /myapp/api/token/  {username, password}
      │
      ▼
{ "access": "<JWT>", "refresh": "<JWT>" }
      │
      ▼
Request with header:  Authorization: Bearer <access>
      │
      ▼
ItemViewSet
  ├─ JWTAuthentication       → identifies request.user
  ├─ IsOwnerOrReadOnly       → only the owner may change an item
  ├─ DjangoFilterBackend     → ?item_name=Pizza  ?item_price=15.00
  ├─ OrderingFilter          → ?ordering=item_price  or  -item_price
  ├─ PageNumberPagination    → ?page=2  (5 per page)
  └─ ItemSerializer          → JSON in / out
      │
      ▼
perform_create() sets user_name = request.user automatically
      │
      ▼
When the access token expires: POST /myapp/api/token/refresh {refresh}
```

The repo also contains function-based (`@api_view`) and class-based (`APIView`, generics) versions of the same API, kept as learning references; the router-based `ItemViewSet` is the one wired to the URLs.

---

## ✅ Advantages

- **One backend, two interfaces.** The same `Item` model powers the HTML site and a JSON API, so a future mobile app or React frontend needs no new backend.
- **Stateless, scalable API auth.** JWT tokens need no server-side session storage, and short-lived access tokens plus refresh tokens limit the damage of a leaked token.
- **Safe deletes.** Soft delete means mistakes can be undone and historical data is kept, while users never see deleted items.
- **Clean data.** Form-level and field-level validation stop negative prices and low-quality descriptions before they reach the database.
- **Fast queries.** Indexes on name, price and (owner, price) speed up the filtering and ordering the API offers.
- **Efficient pages.** Pagination on both the site and the API keeps responses small as the menu grows.
- **Built-in observability.** The custom middleware shows every path, status code and response time, which makes debugging and spotting slow pages easy.
- **Ownership-aware UI.** Edit and delete controls are only shown to the item's owner.
- **Production-friendly config.** Secrets, debug mode, allowed hosts and the database come from environment variables; WhiteNoise and Gunicorn make it easy to deploy.
- **Admin for free.** Items are registered in the Django admin for quick management.
- **Great learning reference.** It shows several Django and DRF patterns side by side: function views, class-based views, `APIView`, generics, viewsets, custom managers, custom permissions and custom middleware.

---

## 🗄️ Data Model

```
User (django.contrib.auth)
 │ 1                       │ 1
 │                         │
 │ *                       │ 1
Item                      Profile
──────────────────────    ─────────────────────────
id                        id
user_name  → User         user      → User (OneToOne)
item_name  (200, indexed) image     (ImageField, profile_pic/)
item_desc                 location  (100)
item_price (6,2, indexed)
item_image (URL, default plate image)
is_available (bool)
is_deleted   (bool)
deleted_at   (datetime, nullable)

Index: (user_name, item_price)
Managers: objects = ItemManager (hides deleted), all_objects = Manager
```

---

## 🗺️ URL Routes

| Route | View | Description |
|-------|------|-------------|
| `/users/register/` | `register` | Create an account |
| `/users/login/` | `LoginView` | Log in |
| `/users/logout/` | `logout_view` | Log out |
| `/users/profile/` | `profile` | Your profile (login required) |
| `/myapp/` | `index` | Paginated menu (login required) |
| `/myapp/<id>/` | `detail` | Item details |
| `/myapp/add/` | `create_item` | Add an item |
| `/myapp/update/<id>` | `update_item` | Edit an item |
| `/myapp/delete/<id>` | `delete_item` | Confirm and soft-delete an item |
| `/admin/` | Django admin | Admin site |

---

## 🔌 API Reference

Base path: `/myapp/api/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/myapp/api/token/` | Get an access and refresh token |
| `POST` | `/myapp/api/token/refresh` | Get a new access token |
| `GET` | `/myapp/api/` | DRF browsable API root |
| `GET` | `/myapp/api/items/` | List items (paginated, filterable, orderable) |
| `POST` | `/myapp/api/items/` | Create an item (owner set from the token) |
| `GET` | `/myapp/api/items/<id>/` | Get one item |
| `PUT` / `PATCH` | `/myapp/api/items/<id>/` | Update an item |
| `DELETE` | `/myapp/api/items/<id>/` | Soft-delete an item |

Query parameters on the list endpoint:

| Parameter | Example | Effect |
|-----------|---------|--------|
| `item_name` | `?item_name=Pizza` | Exact name match |
| `item_price` | `?item_price=15.00` | Exact price match |
| `ordering` | `?ordering=-item_price` | Sort by `item_name` or `item_price` (prefix `-` for descending) |
| `page` | `?page=2` | Page number (5 per page) |

Example:

```bash
# 1. Get a token
curl -X POST http://127.0.0.1:8000/myapp/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "sravan", "password": "your_password"}'

# 2. List items, cheapest first
curl http://127.0.0.1:8000/myapp/api/items/?ordering=item_price \
  -H "Authorization: Bearer <access_token>"

# 3. Create an item
curl -X POST http://127.0.0.1:8000/myapp/api/items/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"item_name": "Pasta", "item_desc": "Creamy alfredo with garlic bread", "item_price": "12.50"}'
```

Sample response:

```json
{
  "count": 6,
  "next": "http://127.0.0.1:8000/myapp/api/items/?page=2",
  "previous": null,
  "results": [
    {
      "id": 2,
      "user_name": "admin",
      "item_name": "Pizza",
      "item_desc": "cheesy pizza",
      "item_price": "15.00",
      "item_image": "https://img.freepik.com/..."
    }
  ]
}
```

---

## 📁 Project Structure

```
FoodAPP/
├── mysite/                       # Django project
│   ├── settings.py               # Env config, DB, DRF, JWT, logging, WhiteNoise
│   ├── urls.py                   # /admin, /myapp, /users
│   └── wsgi.py / asgi.py
├── myapp/                        # Food items app
│   ├── models.py                 # Item (soft delete, indexes)
│   ├── managers.py               # ItemManager hides deleted items
│   ├── forms.py                  # ItemForm with custom validation
│   ├── views.py                  # Template views + API views + ItemViewSet
│   ├── serializers.py            # ItemSerializer
│   ├── permissions.py            # IsOwnerOrReadOnly
│   ├── middleware.py             # LogRequestMiddleware, TimeMiddleware
│   ├── urls.py                   # Pages, router, JWT token routes
│   ├── admin.py
│   ├── fixtures/items.json       # Sample dishes
│   ├── migrations/
│   ├── static/myapp/style.css
│   └── templates/myapp/          # base, index, detail, forms, delete
├── users/                        # Accounts app
│   ├── models.py                 # Profile (avatar, location)
│   ├── forms.py                  # RegisterForm
│   ├── views.py                  # register, logout, profile
│   ├── urls.py
│   └── templates/users/
├── build.sh                      # Install, collectstatic, migrate, superuser
├── requirements.txt
└── manage.py
```

---

## ⚙️ Local Setup

### Prerequisites

- Python 3.11+
- PostgreSQL

### 1. Clone the repository

```bash
git clone https://github.com/codinghub27/FoodAPP.git
cd FoodAPP
```

### 2. Create a virtual environment

```bash
python -m venv env

# Windows
env\Scripts\activate

# macOS / Linux
source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Option A: one URL
DATABASE_URL=postgres://user:password@localhost:5432/foodapp

# Option B: separate values (used when DATABASE_URL is not set)
DB_NAME=foodapp
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

### 5. Migrate, create an admin, load sample data

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata items      # sample dishes, owned by user id 1
```

### 6. Run

```bash
python manage.py runserver
```

- Website: http://127.0.0.1:8000/users/register/ then http://127.0.0.1:8000/myapp/
- API root: http://127.0.0.1:8000/myapp/api/
- Admin: http://127.0.0.1:8000/admin/

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` (or `DJANGO_SECRET_KEY`) | ✅ | Django secret key |
| `DATABASE_URL` | ➖ | Full PostgreSQL URL; takes priority over the `DB_*` values |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | ➖ | Used when `DATABASE_URL` is not set |
| `DEBUG` | ➖ | `True` for development; defaults to `False` |
| `ALLOWED_HOSTS` | ➖ | Comma-separated hostnames; defaults to `localhost` |
| `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` | ➖ | Used by `build.sh` to create an admin on deploy |

---

## ☁️ Deployment

`build.sh` prepares the app on a host like Render:

```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createsuperuser --noinput || true
```

Start command:

```bash
gunicorn mysite.wsgi:application
```

Set `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS` (your domain) and the `DJANGO_SUPERUSER_*` variables in the host's environment. Uploaded profile pictures are stored in `pictures/`, so attach a persistent disk or move media to cloud storage for production.

---

## 🚧 Known Limitations and Future Improvements

- **Owner on web-created items:** `create_item` does not set `user_name`, so items made through the website default to user id 1. Setting `form.instance.user_name = request.user` would fix it (the API already does this).
- **Ownership on web edit/delete:** the buttons are hidden for non-owners, but the `update` and `delete` URLs do not check ownership yet.
- **`IsOwnerOrReadOnly`** uses `is` instead of `in` for `SAFE_METHODS`, so read access on a single item is also limited to the owner.
- **`ItemSerializer.validate`** should `raise` the validation error and `return data`; right now it breaks API create and update calls.
- **Missing items** return a 500 in the web views; `get_object_or_404` would return a proper 404.
- **No automated tests** yet (`tests.py` files are empty).
- **Ideas:** restore endpoint for soft-deleted items, use `is_available` in the UI, image uploads for dishes, search, cart and ordering flow.

---

## 🙌 Author

**Sravan** ([@codinghub27](https://github.com/codinghub27))

Built to practice full-stack Django: server-rendered pages, Django REST Framework, JWT auth, custom managers, permissions and middleware.
