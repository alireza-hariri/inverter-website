#!/usr/bin/env python
"""Destructive: throw the local database away and rebuild it from scratch.

Local development only. It deletes the SQLite file outright, so point it at a
production database and the data is gone.
"""
import os
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.core.management import call_command

if __name__ == "__main__":
    db = Path(__file__).resolve().parents[1] / "db.sqlite3"
    # The journal files too: a crashed process leaves a `-wal` beside the
    # database, and leaving one behind risks replaying the rows this script was
    # run to be rid of.
    for path in (db, *(db.with_name(db.name + suffix) for suffix in ("-wal", "-shm", "-journal"))):
        path.unlink(missing_ok=True)
    call_command("migrate", interactive=False)
    call_command("seed")
    print("Database reset, migrations applied, and seed data loaded.")
