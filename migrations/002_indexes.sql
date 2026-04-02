-- =============================================================
-- Art Event Finder — Indexes
-- Migration: 002_indexes.sql
-- Run after 001_schema.sql
-- =============================================================

-- ----- cities -----------------------------------------------
-- Fast lookup of active cities (used by the scheduler)
CREATE INDEX IF NOT EXISTS idx_cities_active
    ON cities(is_active)
    WHERE is_active = TRUE;

-- PostGIS spatial index for future "events near me" queries
CREATE INDEX IF NOT EXISTS idx_cities_location
    ON cities USING GIST(location_point);


-- ----- search_runs ------------------------------------------
-- Filter runs by city (dashboard, per-city history)
CREATE INDEX IF NOT EXISTS idx_search_runs_city
    ON search_runs(city_id, started_at DESC);

-- Filter by status (find stuck 'running' jobs)
CREATE INDEX IF NOT EXISTS idx_search_runs_status
    ON search_runs(status);


-- ----- raw_results ------------------------------------------
-- THE deduplication index.
-- Before processing a URL, query: has this URL been processed
-- successfully in the last 7 days?
--   SELECT 1 FROM raw_results
--   WHERE url = $1
--     AND was_processed = TRUE
--     AND created_at > NOW() - INTERVAL '7 days'
--   LIMIT 1;
CREATE UNIQUE INDEX IF NOT EXISTS idx_raw_results_url_unique
    ON raw_results(url);

-- Partial index: unprocessed rows only — fast queue drain
CREATE INDEX IF NOT EXISTS idx_raw_results_unprocessed
    ON raw_results(created_at)
    WHERE was_processed = FALSE AND was_skipped = FALSE;

-- Join back to search_run
CREATE INDEX IF NOT EXISTS idx_raw_results_search_run
    ON raw_results(search_run_id);


-- ----- events -----------------------------------------------
-- Active events by deadline (primary feed sort order)
CREATE INDEX IF NOT EXISTS idx_events_deadline
    ON events(application_deadline)
    WHERE is_active = TRUE;

-- Active events by event date
CREATE INDEX IF NOT EXISTS idx_events_date
    ON events(event_date)
    WHERE is_active = TRUE;

-- PostGIS spatial index — powers "events within X km" queries
CREATE INDEX IF NOT EXISTS idx_events_location
    ON events USING GIST(location_point)
    WHERE is_active = TRUE;

-- Filter by type (craft fair, art fair, pop-up, etc.)
CREATE INDEX IF NOT EXISTS idx_events_type
    ON events(event_type)
    WHERE is_active = TRUE;

-- Confidence score filter (hide low-confidence results)
CREATE INDEX IF NOT EXISTS idx_events_confidence
    ON events(confidence_score DESC)
    WHERE is_active = TRUE;

-- JSONB index on social_media — enables queries like:
--   WHERE social_media->>'instagram' IS NOT NULL
CREATE INDEX IF NOT EXISTS idx_events_social_media
    ON events USING GIN(social_media);

-- Source URL lookup (check if a URL already has an event row)
CREATE INDEX IF NOT EXISTS idx_events_source_url
    ON events(source_url);

-- Join to raw_result
CREATE INDEX IF NOT EXISTS idx_events_raw_result
    ON events(raw_result_id);
