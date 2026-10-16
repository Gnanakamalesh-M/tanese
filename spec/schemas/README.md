# spec/schemas

JSON Schema (draft 2020-12) definitions for the machine-readable rule files in `spec/`.
One schema per spec file family, named `<stem>.schema.json`.

`tanese_nlp/speccheck.py` maps spec files to schemas via `SCHEMA_MAP`. A `.yaml` file
under `spec/` that no pattern claims is reported as an error, so adding a spec file
without a schema cannot pass silently.

Run the check with:

    python scripts/check_yaml_schema.py
