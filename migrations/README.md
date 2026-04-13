# Database migrations (Postgres + pgvector)

## Phase 0 rule

- **Extension:** `pgvector` is enabled via `migrations/docker-init/01-enable-pgvector.sql` when using `docker-compose.yml` (first init only).
- **App schema:** LangGraph checkpoints, memory tables, and tenant isolation land in later phases; use Alembic (or the repo’s chosen migrator) once application tables exist. Until then, **no** ad-hoc DDL in application code—only versioned SQL or migration tool output.

## Rollout order

1. Provision Postgres **16+** with superuser access to `CREATE EXTENSION`.
2. Apply `01-enable-pgvector.sql` (or equivalent `CREATE EXTENSION vector;`) in the governed database **before** app deploys that expect `vector` columns.
3. Run application migrations from the chosen tool in CI and production with the same ordering guarantees.
