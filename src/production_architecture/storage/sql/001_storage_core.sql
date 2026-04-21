CREATE TABLE IF NOT EXISTS pa_events (
    event_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    event_seq BIGINT NOT NULL,
    idempotency_key TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_json JSONB NOT NULL,
    payload_sha256 TEXT NOT NULL,
    prev_payload_sha256 TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (run_id, event_seq),
    UNIQUE (run_id, idempotency_key)
);

CREATE TABLE IF NOT EXISTS pa_projection_run_state (
    run_id TEXT PRIMARY KEY,
    latest_event_seq BIGINT NOT NULL,
    status TEXT NOT NULL,
    summary_json JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pa_projection_checkpoint (
    projection_name TEXT PRIMARY KEY,
    last_event_seq BIGINT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pa_vectors (
    vector_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    chunk_id TEXT NOT NULL,
    embedding VECTOR(__PA_VECTOR_DIM__) NOT NULL,
    content TEXT NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    metadata_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (run_id, chunk_id)
);
