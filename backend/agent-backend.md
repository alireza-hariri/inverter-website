# Working on this backend

Operational rules for an agent changing this project. `README.md` explains the project for a
person; this file is the short version of what breaks a run.

## Commands

This is a `uv` project (`pyproject.toml`). Nothing is installed globally:

- add a dependency: `uv add --directory backend <pkg>`
- run anything Django: `uv run --directory backend python manage.py <cmd>`

Pass the non-interactive flag to every command that has one (`--noinput`). A command that stops to
ask a question hangs the whole run, because nobody is at the terminal.

Never start a server in the foreground — it blocks the run. Start it in the background with its
output redirected to a log file, curl what you need, read the log, then kill the process.

## Migrations

The template ships no migration files; they are generated per project.

1. `makemigrations --noinput`
2. `migrate --noinput`
3. `makemigrations --check --dry-run`, which must report **"No changes detected"**.

Step 3 is not redundant. `makemigrations --noinput` *skips* a new non-nullable field with no
default when the table already holds rows: it writes no migration for it and still exits 0.
`migrate` then has nothing to apply and is equally happy, so the drift surfaces much later as
`OperationalError: no such column` on the first request that touches the field. When the check
fails, give the field `null=True` or a `default=`, or write a data migration, then run
`makemigrations` again. The serve pipeline runs this same check and refuses to start a project
that fails it.

## Seed data

`manage.py seed` is idempotent and is what fills the database
(`apps/common/management/commands/seed.py`). Run it after migrating so the endpoints answer with
real rows and real image URLs instead of empty lists.

Without the catalogue app it seeds demo accounts only. Extend it with a handful of rows for the
models you add, rather than leaving empty responses behind — a later seeding step replaces that
data with this business's own.

Leave the seeded database in place when you are done. The frontend agent develops against it, and
the pipeline throws it away before the seeding step runs.

## Configuration

A new setting is three things and never `os.getenv()`:

1. a typed field on `Settings` in `config/env.py`,
2. a documented default in `.env.sample`,
3. a line in `config/settings.py` — but only if Django or an app reads it through
   `django.conf.settings`.

`os.getenv()` skips the startup validation, leaves the key undocumented, and fails
`tests/test_settings.py` on the missing sample entry. The project loads `.env.sample`, then `.env`,
then the process environment, so a value you add is picked up without anything having to export it.

## Verifying endpoints

Call them. A response shape you reasoned about is not verified.

- health first, then each endpoint the pages need, with its real query parameters;
- anything behind login goes through a token from `POST /api/token/`;
- check the status code *and* the body shape against `API.md`.

Never return a shape the documents do not promise: a response the frontend cannot rely on is a
backend bug, not a frontend one.

## Editing files

Use `edit` for a local change and `write` for a rewrite of most of a file. A large multi-part
`edit` that fails validation costs a whole model turn and is then usually rewritten wholesale
anyway.
