-- CrimeJournal Initial Database Schema
-- Compatible with PostgreSQL (Supabase) and SQLite

-- Cases Table
CREATE TABLE IF NOT EXISTS cases (
    id SERIAL PRIMARY KEY,
    courtlistener_id INTEGER UNIQUE NOT NULL,

    -- Basic Information
    case_name VARCHAR(500) NOT NULL,
    case_name_full VARCHAR(1000),
    court VARCHAR(200),
    court_id VARCHAR(100),

    -- Dates
    date_filed TIMESTAMP,
    date_decided TIMESTAMP,

    -- Content
    citation VARCHAR(200),
    docket_number VARCHAR(200),
    source VARCHAR(100),

    -- Text content
    plain_text TEXT,
    html_text TEXT,

    -- AI-generated fields
    summary TEXT,
    keywords TEXT,  -- JSON array
    entities TEXT,  -- JSON object

    -- Vector embedding
    embedding TEXT,  -- Will store vector as JSON

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for cases table
CREATE INDEX idx_case_date_filed ON cases(date_filed);
CREATE INDEX idx_case_court ON cases(court);
CREATE INDEX idx_case_courtlistener ON cases(courtlistener_id);

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,

    -- Profile
    full_name VARCHAR(200),

    -- Subscription
    subscription_tier VARCHAR(50) DEFAULT 'free',
    stripe_customer_id VARCHAR(200),
    subscription_end_date TIMESTAMP,

    -- Usage tracking
    daily_search_count INTEGER DEFAULT 0,
    last_search_date TIMESTAMP,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for users
CREATE INDEX idx_user_email ON users(email);

-- Search History Table
CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    query VARCHAR(500) NOT NULL,
    filters VARCHAR(1000),  -- JSON string

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index for search history
CREATE INDEX idx_search_user ON search_history(user_id);
CREATE INDEX idx_search_date ON search_history(created_at);

-- Favorite Cases Table
CREATE TABLE IF NOT EXISTS favorite_cases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    case_id INTEGER NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,

    UNIQUE(user_id, case_id)
);

-- Indexes for favorites
CREATE INDEX idx_favorite_user ON favorite_cases(user_id);
CREATE INDEX idx_favorite_case ON favorite_cases(case_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_cases_updated_at BEFORE UPDATE ON cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
