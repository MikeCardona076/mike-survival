PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seed INTEGER NOT NULL,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    ended_at TEXT,
    status TEXT NOT NULL DEFAULT 'alive',
    cause_of_death TEXT,
    refugio7_x INTEGER NOT NULL,
    refugio7_y INTEGER NOT NULL,
    trait TEXT NOT NULL DEFAULT 'neutral'
);

CREATE TABLE world_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    chunk_x INTEGER NOT NULL,
    chunk_y INTEGER NOT NULL,
    seed INTEGER NOT NULL,
    data TEXT NOT NULL,
    generated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE,
    UNIQUE(run_id, chunk_x, chunk_y)
);

CREATE TABLE agent_state (
    run_id INTEGER PRIMARY KEY,
    health INTEGER NOT NULL DEFAULT 100,
    hunger INTEGER NOT NULL DEFAULT 0,
    thirst INTEGER NOT NULL DEFAULT 0,
    infection INTEGER NOT NULL DEFAULT 0,
    radio_battery INTEGER NOT NULL DEFAULT 100,
    pos_x REAL NOT NULL DEFAULT 0,
    pos_y REAL NOT NULL DEFAULT 0,
    inventory TEXT NOT NULL DEFAULT '[]',
    objective TEXT,
    turn_count INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT,
    tool_name TEXT,
    tool_args TEXT,
    tool_call_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE TABLE memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    importance INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE SET NULL
);

CREATE TABLE assets_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_key TEXT NOT NULL UNIQUE,
    asset_type TEXT NOT NULL,
    description TEXT NOT NULL,
    params TEXT,
    data BLOB NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    resolved INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE TABLE meta_progression (
    unlock_key TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    unlocked_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE stats (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    runs_played INTEGER NOT NULL DEFAULT 0,
    runs_won INTEGER NOT NULL DEFAULT 0,
    total_deaths INTEGER NOT NULL DEFAULT 0,
    best_distance_to_r7 REAL NOT NULL DEFAULT 999999,
    total_playtime_seconds INTEGER NOT NULL DEFAULT 0
);

INSERT OR IGNORE INTO stats (id) VALUES (1);

CREATE TABLE shelter (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    level INTEGER NOT NULL DEFAULT 0,
    weapon_level INTEGER NOT NULL DEFAULT 0
);

INSERT OR IGNORE INTO shelter (id) VALUES (1);
