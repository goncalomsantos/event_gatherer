CREATE TABLE IF NOT EXISTS app_venues (
    id SERIAL PRIMARY KEY,
    api_id INT UNIQUE NOT NULL,   -- External API venue ID
    address VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    city VARCHAR(255),
    country VARCHAR(255),
    source_api VARCHAR(50) NOT NULL  -- Source API or data source
);
