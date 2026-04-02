-- =============================================================
-- Art Event Finder — Database Schema
-- Migration: 001_schema.sql
-- Run this first, then 002_indexes.sql
-- Requires: PostgreSQL 14+ with PostGIS extension
-- =============================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- =============================================================
-- cities
-- One row per market the engine covers.
-- =============================================================
CREATE TABLE IF NOT EXISTS cities (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(120)  NOT NULL,
    country_code    CHAR(2)       NOT NULL,                -- ISO 3166-1 alpha-2, e.g. 'CA'
    region          VARCHAR(120),                          -- province/state, e.g. 'Quebec'
    lat             NUMERIC(9,6)  NOT NULL,
    lng             NUMERIC(9,6)  NOT NULL,
    location_point  GEOGRAPHY(POINT, 4326) GENERATED ALWAYS AS (
                        ST_Point(lng, lat)::GEOGRAPHY
                    ) STORED,
    is_active       BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- Seed Montreal
INSERT INTO cities (name, country_code, region, lat, lng)
VALUES ('Montreal', 'CA', 'Quebec', 45.5017, -73.5673)
ON CONFLICT DO NOTHING;


-- =============================================================
-- search_runs
-- One row per engine execution. Tracks cost and outcome.
-- =============================================================
CREATE TABLE IF NOT EXISTS search_runs (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    city_id             UUID          NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    status              VARCHAR(20)   NOT NULL DEFAULT 'running'
                            CHECK (status IN ('running', 'completed', 'failed')),
    urls_found          INTEGER       NOT NULL DEFAULT 0,
    urls_processed      INTEGER       NOT NULL DEFAULT 0,
    urls_skipped        INTEGER       NOT NULL DEFAULT 0,
    events_extracted    INTEGER       NOT NULL DEFAULT 0,
    tavily_queries_used INTEGER       NOT NULL DEFAULT 0,
    -- Cost tracking (USD)
    tavily_cost_usd     NUMERIC(8,4)  NOT NULL DEFAULT 0,
    claude_cost_usd     NUMERIC(8,4)  NOT NULL DEFAULT 0,
    error_message       TEXT,
    started_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    finished_at         TIMESTAMPTZ
);


-- =============================================================
-- raw_results
-- Every URL returned by Tavily. The UNIQUE constraint on url
-- is the foundation for deduplication — skip URLs already
-- processed in the last 7 days.
-- =============================================================
CREATE TABLE IF NOT EXISTS raw_results (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    search_run_id   UUID          NOT NULL REFERENCES search_runs(id) ON DELETE CASCADE,
    url             TEXT          NOT NULL,
    source_type     VARCHAR(20)   NOT NULL DEFAULT 'webpage'
                        CHECK (source_type IN ('webpage', 'social_snippet')),
    snippet         TEXT,                                  -- Tavily snippet (always stored)
    raw_html        TEXT,                                  -- fetched page text (nullable, large)
    was_processed   BOOLEAN       NOT NULL DEFAULT FALSE,  -- Claude was called
    was_skipped     BOOLEAN       NOT NULL DEFAULT FALSE,  -- skipped (recent duplicate, blocked, etc.)
    skip_reason     VARCHAR(80),                           -- 'recent_duplicate' | 'blocked_domain' | 'no_keywords'
    processing_ms   INTEGER,                               -- how long Claude took
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    processed_at    TIMESTAMPTZ
);


-- =============================================================
-- events
-- One row per extracted event. Mirrors the 18 fields Claude
-- returns. raw_result_id links back to the source URL.
-- is_active = FALSE hides stale/superseded events (soft delete).
-- =============================================================
CREATE TABLE IF NOT EXISTS events (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    raw_result_id           UUID          NOT NULL REFERENCES raw_results(id) ON DELETE CASCADE,

    -- Core event fields (mirrors Claude extraction output)
    event_name              TEXT          NOT NULL,
    event_type              VARCHAR(80),                   -- 'art fair' | 'craft fair' | 'pop-up' | 'gallery show' | etc.
    event_date              DATE,
    application_deadline    DATE,
    location_text           TEXT,                          -- raw string as Claude extracted it
    location_point          GEOGRAPHY(POINT, 4326),        -- geocoded later; enables distance queries
    description             TEXT,
    theme                   TEXT,
    how_to_apply            TEXT,
    estimated_size          VARCHAR(80),                   -- e.g. '50–100 vendors'
    years_running           SMALLINT,
    organizer               TEXT,
    social_media            JSONB,                         -- { instagram, facebook, website }
    booth_fee               VARCHAR(80),                   -- kept as text; formats vary too much
    confidence_score        NUMERIC(3,2)  NOT NULL DEFAULT 0
                                CHECK (confidence_score >= 0 AND confidence_score <= 1),

    -- Source tracking
    source_url              TEXT          NOT NULL,
    source_type             VARCHAR(20)   NOT NULL DEFAULT 'webpage'
                                CHECK (source_type IN ('webpage', 'social_snippet')),

    -- Lifecycle
    is_active               BOOLEAN       NOT NULL DEFAULT TRUE,
    deactivation_reason     VARCHAR(80),                   -- 'past_deadline' | 'duplicate' | 'manual'
    created_at              TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);


-- =============================================================
-- updated_at auto-maintenance
-- Keeps updated_at current without application-level logic.
-- =============================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER cities_updated_at
    BEFORE UPDATE ON cities
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
