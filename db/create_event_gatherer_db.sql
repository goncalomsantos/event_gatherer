-- create_tables.sql
-- psql -U postgres -d event_gatherer_db -f .\db\create_event_gatherer_db.sql
-- Create venues table first to resolve foreign key reference

-- Create venues table first to resolve foreign key reference
DROP TABLE IF EXISTS venues;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS orders;

CREATE TABLE IF NOT EXISTS venues (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    address TEXT,
    city VARCHAR(255),
    state VARCHAR(255),
    country VARCHAR(255),
    postal_code VARCHAR(20),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255)
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255),
    email VARCHAR(255)
);

-- Create events table after venues and categories are defined
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    venue_id INT REFERENCES venues(id),
    category_id INT REFERENCES categories(id),
    capacity INT,
    tickets_sold INT
);


CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    event_id INT REFERENCES events(id),
    user_id INT REFERENCES users(id),
    amount DOUBLE PRECISION,
    status VARCHAR(50)
);
