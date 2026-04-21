CREATE INDEX IF NOT EXISTS pa_events_run_seq_idx ON pa_events (run_id, event_seq);
CREATE INDEX IF NOT EXISTS pa_events_run_created_idx ON pa_events (run_id, created_at);
CREATE INDEX IF NOT EXISTS pa_vectors_run_conf_idx ON pa_vectors (run_id, confidence);
