# Observability Run Project API

Base URL: `/api`. JSON errors use `{ "error": { "code": 400, "detail": ... } }`.

## Public endpoints

- `GET /health/` → `{ "status": "ok" }`.
- `POST /token/` with `{ "email", "password" }` → `{ "access", "refresh" }`.
- `POST /token/refresh/` with `{ "refresh" }` → a new access token.

This backend ships no domain endpoints of its own beyond authentication and health: the site's own resources are built during implementation. New list endpoints should return the same paginated envelope the shared pagination class produces, `{ "count": number, "next": string|null, "previous": string|null, "results": [...] }`, and detail endpoints one object.

## Authenticated customer endpoints

Send `Authorization: Bearer <access>`.

- `POST /users/register/` (public) with `{ "email", "username", "password", "mobile?", "first_name?", "last_name?" }`.
- `POST /users/mobile/request-code/` (public) with `{ "mobile": "0912..." }` → `202`; sends a login code to the number by SMS (`OTP_CODE_LENGTH` digits, five by default). Always `202` when the number is well-formed, whether or not it is registered. `429` if a code was sent in the last 60 seconds, `503` if the code could not be sent.
- `POST /users/mobile/verify-code/` (public) with `{ "mobile": "0912...", "code": "12345" }` → `{ "access", "refresh", "user" }`. A verified new mobile number creates an account automatically. `400` if the code is wrong, expired (2 minutes), already used, or out of attempts (5).
- `GET/PATCH /users/me/`.

The Django admin is at `/admin/` and manages users.
