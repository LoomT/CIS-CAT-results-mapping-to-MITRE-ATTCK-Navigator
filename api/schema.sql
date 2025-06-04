CREATE TABLE IF NOT EXISTS metadata (
    id VARCHAR(36) PRIMARY KEY,
    ip_address TEXT,
    host_name TEXT,
    file_name TEXT,
    time_created DEFAULT CURRENT_TIMESTAMP,
    result TEXT
);
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    tag_key TEXT NOT NULL,
    tag_value TEXT NOT NULL,
    UNIQUE (tag_key, tag_value)
);
CREATE TABLE IF NOT EXISTS metadata_tag (
    metadata_id VARCHAR(36) REFERENCES metadata(id),
    tag_id INTEGER REFERENCES tags(id),
    PRIMARY KEY (metadata_id, tag_id)
);

INSERT OR IGNORE INTO tags (id, tag_key, tag_value) VALUES
(1, 'department', 'default');