# Backend integration skill

Build the frontend against the REST contract in `API.md`; do not import Django modules or rely on database internals. The API is JSON.

Read the API base URL from `process.env.NEXT_PUBLIC_API_URL` (no trailing slash, no `/api` suffix), falling back to `http://127.0.0.1:8000`. The serving layer allocates the backend's port at run time and writes that variable into `frontend/.env.local`, so never hard-code a port. Browser-side requests are cross-origin; the backend enables `django-cors-headers` and allows every origin while `DEBUG` is on.

For passwordless mobile login, call `POST /api/users/mobile/request-code/` with `{mobile}` and then `POST /api/users/mobile/verify-code/` with `{mobile, code}`. The code arrives by SMS and verification returns JWTs plus the user. Call the request endpoint SMS in the UI. It answers `202` for any well-formed number — never treat that as proof the number exists — so send the user to the code screen on `202`, show a wait-and-retry message on `429`, and a generic try-again on `503`. Codes expire after two minutes and allow five wrong guesses, so offer a resend after the 60-second throttle window. Password registration remains available at `POST /api/users/register/`; obtain its JWTs from `/api/token/`. Store access and refresh tokens securely, send the access token as `Authorization: Bearer <access>`, and refresh on a 401 before asking the user to log in again.

Display API errors from `error.detail`, including field-level validation dictionaries.

This backend ships authentication and the shared API conventions only; the resources this site needs are created during implementation. Follow the same conventions when consuming them: the paginated `results` envelope for lists, `Authorization: Bearer <access>` for anything user-owned, and `error.detail` for failures.
