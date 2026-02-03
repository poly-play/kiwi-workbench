CREATE TABLE IF NOT EXISTS assets (
    id TEXT PRIMARY KEY,          -- UUID
    file_hash TEXT NOT NULL,      -- SHA256, used for deduplication
    original_name TEXT,           -- Original filename
    mime_type TEXT,               -- e.g., 'image/jpeg', 'video/mp4'
    size_bytes INTEGER,           -- File size in bytes
    local_path TEXT NOT NULL,     -- Relative path in storage/ e.g. 'ad_creatives/2026/01/hash.jpg'
    r2_key TEXT,                  -- Key in Cloudflare R2 bucket (if uploaded)
    category TEXT,                -- 'ad_creatives', 'game_icons', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(file_hash)             -- Prevent duplicate files
);

CREATE INDEX IF NOT EXISTS idx_assets_hash ON assets(file_hash);
CREATE INDEX IF NOT EXISTS idx_assets_category ON assets(category);
