# Build Prompt: Job Application Tracker (paste this whole thing into Antigravity)

## What to build

A personal job-application tracker web app, multi-user, each user sees only
their own data. This is a learning project — the person building it is
practicing SQL/Postgres and Python backend development for a Data Analyst
career track, so favor **explicit, readable raw SQL over ORM magic**
wherever reasonable.

## Tech stack (required, do not substitute)

- **Database:** PostgreSQL (raw SQL via `psycopg2`, no ORM like SQLAlchemy
  models/ActiveRecord-style abstraction — write real `SELECT`/`INSERT`/
  `UPDATE`/`DELETE` statements, parameterized)
- **Backend:** Python, **FastAPI**
- **Frontend:** plain HTML/CSS/JavaScript (no framework needed), calling the
  backend via `fetch()`
- **Hosting target (design for this, don't need to actually deploy):**
  Postgres on Neon, backend on Render, frontend on Vercel

## Database schema

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company TEXT NOT NULL,
    role TEXT,
    status TEXT NOT NULL DEFAULT 'wishlist'
        CHECK (status IN ('wishlist','applied','interview','offer','rejected')),
    date_applied DATE,
    link TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_applications_user_id ON applications(user_id);
```

## Auth requirements (this is the important part — build all of it)

- **Separate Login and Sign Up pages** (not a combined/auto-detect form).
- Passwords hashed with **bcrypt** (via `passlib` or `bcrypt` package), strong
  cost factor. Never store or log plaintext passwords.
- On login success, issue a **short-lived JWT access token (~15 min)** and a
  **longer-lived refresh token**, both delivered as **httpOnly, Secure,
  SameSite=Strict cookies** — never store tokens in localStorage or
  sessionStorage, never expose them to JavaScript.
- A `/auth/refresh` endpoint that uses the refresh token to issue a new
  access token when the access token expires.
- A `/auth/logout` endpoint that clears both cookies.
- **Rate limiting** on `/auth/login` and `/auth/signup`: max 5 attempts per
  IP per 15 minutes (use `slowapi` or equivalent).
- Login failure messages must be **generic** ("invalid email or password") —
  never reveal whether an email exists in the system.
- Every request to `/applications*` endpoints must verify the JWT and scope
  the query to `WHERE user_id = <id from token>` — a logged-in user must
  never be able to read/edit/delete another user's row, even by guessing an
  ID in the URL.
- All SQL must be parameterized (`%s` placeholders via psycopg2, never
  string-formatted SQL) — this must fully close SQL injection, not just
  reduce it.
- Set standard security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options).
- Explicitly **out of scope for this version**: OTP login, 2FA, email
  verification. Structure the code so these could be added later without a
  rewrite, but do not build them now.

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | /auth/signup | create account (email, password) |
| POST | /auth/login | log in, sets auth cookies |
| POST | /auth/refresh | refresh access token |
| POST | /auth/logout | clear cookies |
| GET | /applications | list current user's entries |
| POST | /applications | create an entry |
| PUT | /applications/{id} | update an entry (must own it) |
| DELETE | /applications/{id} | delete an entry (must own it) |

Application fields: `company` (required), `role`, `status` (one of
wishlist/applied/interview/offer/rejected), `date_applied`, `link`, `notes`.

## Frontend requirements

- Two pages: **Login** and **Sign Up**, separate, with a link between them.
- Main app screen after login: stats summary (count per status), a form to
  add/edit an entry, filter chips by status, a search box (company/role),
  and a list of entries showing company, role, status, date, link, notes,
  with edit/delete/status-change controls.
- Visual style: a "case file / dossier" aesthetic — warm paper/manila
  background tones, dark ink text, a typewriter-style display font for
  headings (e.g. "Special Elite" from Google Fonts) paired with a clean sans
  body font and a monospace font for company names/data, and status shown
  as small rotated "stamp" badges (color-coded per status: wishlist=gray,
  applied=amber, interview=blue, offer=green, rejected=red). Keep it clean
  and usable, not overly decorative.
- Fully usable on mobile screen widths.

## Testing requirement — do this before saying anything is done

For every endpoint, actually run a real request against it (curl, httpie,
or FastAPI's `/docs` interactive UI) and confirm the real response —
don't just write the code and assume it works. Specifically verify:
- Signup creates a user with a hashed (not plaintext) password in the DB
- Login with wrong password fails with a generic error
- Login with correct password sets httpOnly cookies
- A request to `/applications` without a valid token is rejected (401)
- A logged-in user cannot fetch/edit/delete another user's entry by ID
- Rate limiting actually kicks in after repeated failed logins
- All CRUD operations work end-to-end from the frontend

## Required output: end with a status report in this exact format

```
STATUS REPORT

Database:
- [ ] schema created and applied
- [ ] tested with real inserts

Backend:
- [ ] signup endpoint — built / tested
- [ ] login endpoint — built / tested
- [ ] refresh endpoint — built / tested
- [ ] logout endpoint — built / tested
- [ ] rate limiting — built / tested
- [ ] applications GET — built / tested
- [ ] applications POST — built / tested
- [ ] applications PUT — built / tested
- [ ] applications DELETE — built / tested
- [ ] ownership checks (can't touch another user's data) — built / tested

Frontend:
- [ ] login page — built
- [ ] signup page — built
- [ ] main tracker UI — built
- [ ] connected to real backend (not mock data) — confirmed

Security checklist:
- [ ] passwords hashed with bcrypt, never stored plaintext
- [ ] JWTs in httpOnly/Secure/SameSite cookies, not localStorage
- [ ] all SQL parameterized
- [ ] generic login error messages (no email enumeration)
- [ ] security headers set

Known issues / not yet done:
(list anything incomplete, broken, or skipped, and why)

How to run it locally:
(exact commands)
```

Fill this in honestly based on what you actually built and tested — mark
anything unfinished or untested clearly rather than checking boxes that
aren't true. This report will be handed to someone else to review.