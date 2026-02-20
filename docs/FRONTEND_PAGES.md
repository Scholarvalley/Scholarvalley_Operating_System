# Frontend Pages – Scholarvalley

All static pages are served by FastAPI and share the same header, nav, and footer. Run the app (e.g. `docker compose up` or `uvicorn app.main:app --reload`) and open **http://localhost:8000**.

## Page list and functionality

| Page | URL | Purpose |
|------|-----|--------|
| **Home** | `/` | Hero, services grid, about/contact sections, nav to all other pages. |
| **About** | `/about` | About Scholarvalley; real copy, no placeholders. |
| **Services** | `/services` | Services list and links to Register / Contact. |
| **Contact** | `/contact` | Contact copy and links to Register, Login, API docs. |
| **Register** | `/register` | Client registration form: name, email, password, education, transcript + degree uploads. Submits to `/api/auth/register`, then login, then creates applicant and uploads documents via presigned URLs. |
| **Login** | `/login` | Email + password; submits to `/api/auth/login`, stores token in `localStorage`, redirects to `/dashboard` or to `?next=` if present. |
| **Dashboard** | `/dashboard` | Requires token; lists applicants via `/api/applicants/`. Clients see own; manager/root see all. Logout clears token and goes to `/`. |
| **API Docs** | `/docs` | FastAPI Swagger UI (no static page). |

## Validation

To check that each HTML page has the required structure (header, nav, main, footer):

```bash
python scripts/validate_archive_pages.py
```

All of `index`, `about`, `services`, `contact`, `register`, `login`, `dashboard` are validated.

## JS behaviour

- **main.js** – Nav toggle (mobile menu); loaded on every page.
- **register.js** – Form validation, `parseJson` for API responses (handles `detail` as string or array), register → login → create applicant → upload transcript/degree.
- **login.js** – Form submit, `parseJson`, token in `localStorage`, redirect to `?next=` or `/dashboard`.
- **dashboard.js** – Token check (redirect to `/login?next=/dashboard` if missing), `parseJson`, list applicants, null-safe DOM updates, logout button.

## Troubleshooting

- **Blank or broken page:** Ensure the app is running and you open `http://localhost:8000` (or your deployed URL). Check browser console for errors.
- **Login redirects to login again:** Token may be missing or invalid; clear `localStorage` for the site and log in again.
- **Register fails on upload:** Backend needs valid `AWS_S3_BUCKET` and credentials; see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) and [AWS_ARCHITECTURE.md](AWS_ARCHITECTURE.md).
- **Dashboard "Failed to load applicants":** Check network tab for 401 (re-login) or 500 (server error); see API logs.
