-- create_tables.sql
-- psql -U postgres -d event_gatherer_db -f .\....\dw_api_football.sql

DROP TABLE IF EXISTS dw_api_football_venues;


CREATE TABLE IF NOT EXISTS dw_api_football_fixtures (
    api_id INT UNIQUE NOT NULL,          -- External API fixture ID
    timezone VARCHAR(50),                -- Timezone of the event
    date TIMESTAMP WITH TIME ZONE,       -- Date and time of the event
    timestamp BIGINT,                    -- Unix timestamp
    venue_api_id INT,                    -- Venue ID from the API
    league_id INT,                       -- League ID
    home_team_id INT,                    -- Home team ID
    home_team_name VARCHAR(255),         -- Home team name
    away_team_id INT,                    -- Away team ID
    away_team_name VARCHAR(255)          -- Away team name
);
