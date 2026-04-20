# Folder: `src/event_sourced_architecture`

## Why this folder exists
This folder groups code and artifacts for `event_sourced_architecture` within the repository architecture.

## What is present
- `auditability` (folder): Groups related implementation for this subdomain boundary.
- `event_store` (folder): Handles event lineage, event contracts, or event persistence logic.
- `learning_lineage` (folder): Groups related implementation for this subdomain boundary.
- `replay` (folder): Groups related implementation for this subdomain boundary.
- `__init__.py` (file): Implements a concrete part of this folder responsibility.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
