# Secure Login System — Custom Backend (Django REST Framework)

A JWT-based authentication system with user profile access and per-user
file isolation, built with Django REST Framework + SQLite (dev).

## Tech Stack
- Django + Django REST Framework
- `djangorestframework-simplejwt` (JWT auth + token blacklist)
- PostgreSQL (via Docker for local development)
- `python-decouple` (environment-based configuration)
- `django-cors-headers` (for the provided `index.html` test client)

## Setup Instructions

### 1. Start PostgreSQL (via Docker)
\`\`\`bash
docker run --name pg-secure-login \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=secure_login_db \
  -p 5432:5432 \
  -d postgres
\`\`\`

If you already have PostgreSQL running locally instead, just make sure a
database matching your `.env` values exists.

### 2. Clone and configure the project
\`\`\`bash
git clone <your-repo-url>
cd auth
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then edit .env with your DB credentials
\`\`\`

### 3. Run migrations and seed test data
\`\`\`bash
python manage.py migrate
python manage.py seed_users     # creates 3 test users with sample files
python manage.py runserver
\`\`\`

Server runs at `http://localhost:8000`.

### Testing with the provided `index.html`
Open `index.html` directly in a browser, and set:
- **Backend mode**: Custom REST backend
- **Base URL**: `http://localhost:8000`
- **Cookie sessions checkbox**: leave **unchecked** (this backend uses JWT
  bearer tokens, not cookies)

  ## Seeded Test Users
Run `python manage.py seed_users` to create 3 users, each with 2 sample files:

| Email | Password |
|---|---|
| alice@example.com | Password123! |
| bob@example.com | Password123! |
| carol@example.com | Password123! |

These match the quick-fill buttons in `index.html`.

## Design Decisions & Reasoning

### 1. JWT vs Session-based authentication
I chose **JWT (access + refresh tokens)** via `djangorestframework-simplejwt`
over Django's built-in session auth, for these reasons:

- Stateless verification — protected routes don't need a DB/session lookup
  on every request, just a signature check.
- The provided `index.html` client is designed around a bearer token flow
  (`Authorization: Bearer <token>`), not cookies — matching that made
  integration cleaner.
- Trade-off: JWTs aren't inherently revocable before expiry. I mitigated
  this by keeping access tokens short-lived (15 min) and using the
  `token_blacklist` app for refresh tokens (see Logout below).

### 2. How logout is implemented
- On login, both an **access token** (15 min lifetime, returned as `token`)
  and a **refresh token** (7 days, returned as `refresh`) are issued.
- On logout, the refresh token is added to a blacklist table
  (`rest_framework_simplejwt.token_blacklist`). Once blacklisted, it can
  never be used again to obtain a new access token.
- **Known trade-off**: the *access* token itself is not blacklisted (JWTs
  are stateless by design — validating them doesn't hit the database).
  This means a still-valid access token issued before logout will keep
  working until its natural 15-minute expiry. This window is intentionally
  kept short to limit exposure. A stricter alternative (checking every
  access token against a DB/cache blacklist on each request) would remove
  this window but sacrifices the main performance benefit of JWTs — given
  more time, I'd make this configurable behind a setting.

### 3. How user data isolation is enforced
Two layers:

1. **UUID primary keys** instead of sequential integers, for both `User`
   and `UserFile`. This prevents ID-enumeration attacks (an attacker can't
   guess `/files/2`, `/files/3`, etc.).
2. **Queryset scoping at the ORM level**, not post-fetch permission checks.
   Every protected view filters `WHERE owner = request.user` *before*
   looking up the requested ID:

   \`\`\`python
   def get_queryset(self):
       return UserFile.objects.filter(owner=self.request.user)
   \`\`\`

   This means a request for another user's file ID returns the **same
   404 "not found"** response as a request for a file ID that doesn't
   exist at all — never a 403. This is deliberate: distinguishing
   "forbidden" from "not found" would let an attacker enumerate which
   file IDs exist, even without gaining access to them.

### 4. General security practices
- Passwords are hashed via Django's `set_password()` (PBKDF2 + salt) —
  never stored or compared in plaintext.
- Login failures return a generic `"Invalid email or password."` message
  regardless of whether the email exists, to avoid user enumeration.
- Login is rate-limited to 5 attempts/minute per IP via DRF throttling
  (`AnonRateThrottle`), returning `429 Too Many Requests` beyond that.
- All protected routes use the same `JWTAuthentication` class consistently
  (set globally in `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES`), so
  token validation logic isn't duplicated per view.

## API Endpoints

| Method | Path | Auth required | Description |
|---|---|---|---|
| POST | `/register` | No | Create a new account |
| POST | `/login` | No | Returns `{token, refresh}` |
| POST | `/logout` | Yes | Blacklists the refresh token |
| GET | `/me` | Yes | Current user's profile |
| GET | `/files` | Yes | Current user's files |
| GET | `/files/:id` | Yes | Single file (404 if not owned) |
| GET | `/files/:id/download` | Yes | Downloads the file |

## What I'd Improve With More Time
- Move `SECRET_KEY` and other config fully into environment variables
  (partially done via `.env.example`)
- Switch from SQLite to PostgreSQL for the dev setup (task suggested it;
  I used SQLite for local speed but the ORM code is DB-agnostic)
- Add a proper file upload endpoint (currently files are seeded only,
  since the provided `index.html` has no upload UI)
- Add automated tests for the cross-user access scenarios
- Make the "strict immediate token invalidation" trade-off configurable
