-- +goose Up
-- +goose StatementBegin

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create session_users table
CREATE TABLE IF NOT EXISTS session_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, session_id)
);

-- Create cells table
CREATE TABLE IF NOT EXISTS cells (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    cell_type cell_type NOT NULL,
    image_path VARCHAR(255),
    position INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(position)
);

-- Create players table
CREATE TABLE IF NOT EXISTS players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cell_id INTEGER NOT NULL REFERENCES cells(id),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE NOT NULL,
    profile_image VARCHAR(255) DEFAULT '',
    role user_rights NOT NULL,
    last_dice_value INTEGER DEFAULT 0,
    previous_cell_id INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create player_stats table
CREATE TABLE IF NOT EXISTS player_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    games_played INTEGER DEFAULT 0,
    games_won INTEGER DEFAULT 0,
    games_lost INTEGER DEFAULT 0,
    total_points INTEGER DEFAULT 0,
    total_dice_rolls INTEGER DEFAULT 0,
    items_collected INTEGER DEFAULT 0,
    items_used INTEGER DEFAULT 0,
    traps_triggered INTEGER DEFAULT 0,
    jail_time INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(player_id)
);

-- Create inventories table
CREATE TABLE IF NOT EXISTS inventories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    capacity INTEGER NOT NULL DEFAULT 10,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(player_id)
);

-- Create items table
CREATE TABLE IF NOT EXISTS items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    item_type item_type NOT NULL,
    image_path VARCHAR(255),
    effect_type effect_type NOT NULL,
    effect_category effect_category NOT NULL,
    effect_value TEXT,
    rarity INTEGER NOT NULL CHECK (rarity >= 1 AND rarity <= 10),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create item_instances table
CREATE TABLE IF NOT EXISTS item_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    inventory_id UUID NOT NULL REFERENCES inventories(id) ON DELETE CASCADE,
    is_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create player_effects table
CREATE TABLE IF NOT EXISTS player_effects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    effect_type effect_type NOT NULL,
    effect_category effect_category NOT NULL,
    effect_value TEXT,
    duration INTEGER NOT NULL DEFAULT -1, -- -1 for permanent
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create games table
CREATE TABLE IF NOT EXISTS games (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    status game_status NOT NULL,
    score INTEGER DEFAULT 0,
    game_conditions game_conditions NOT NULL,
    dice_modifier dice_modifier,
    game_modifier game_modifier,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_players_user_id ON players(user_id);
CREATE INDEX IF NOT EXISTS idx_players_cell_id ON players(cell_id);
CREATE INDEX IF NOT EXISTS idx_players_username ON players(username);
CREATE INDEX IF NOT EXISTS idx_player_stats_player_id ON player_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_inventories_player_id ON inventories(player_id);
CREATE INDEX IF NOT EXISTS idx_item_instances_item_id ON item_instances(item_id);
CREATE INDEX IF NOT EXISTS idx_item_instances_inventory_id ON item_instances(inventory_id);
CREATE INDEX IF NOT EXISTS idx_player_effects_player_id ON player_effects(player_id);
CREATE INDEX IF NOT EXISTS idx_player_effects_is_active ON player_effects(is_active);
CREATE INDEX IF NOT EXISTS idx_games_player_id ON games(player_id);
CREATE INDEX IF NOT EXISTS idx_games_status ON games(status);
CREATE INDEX IF NOT EXISTS idx_session_users_user_id ON session_users(user_id);
CREATE INDEX IF NOT EXISTS idx_session_users_session_id ON session_users(session_id);
CREATE INDEX IF NOT EXISTS idx_cells_position ON cells(position);
CREATE INDEX IF NOT EXISTS idx_cells_cell_type ON cells(cell_type);

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP INDEX IF EXISTS idx_cells_cell_type;
DROP INDEX IF EXISTS idx_cells_position;
DROP INDEX IF EXISTS idx_session_users_session_id;
DROP INDEX IF EXISTS idx_session_users_user_id;
DROP INDEX IF EXISTS idx_games_status;
DROP INDEX IF EXISTS idx_games_player_id;
DROP INDEX IF EXISTS idx_player_effects_is_active;
DROP INDEX IF EXISTS idx_player_effects_player_id;
DROP INDEX IF EXISTS idx_item_instances_inventory_id;
DROP INDEX IF EXISTS idx_item_instances_item_id;
DROP INDEX IF EXISTS idx_inventories_player_id;
DROP INDEX IF EXISTS idx_player_stats_player_id;
DROP INDEX IF EXISTS idx_players_username;
DROP INDEX IF EXISTS idx_players_cell_id;
DROP INDEX IF EXISTS idx_players_user_id;

DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS player_effects;
DROP TABLE IF EXISTS item_instances;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS inventories;
DROP TABLE IF EXISTS player_stats;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS cells;
DROP TABLE IF EXISTS session_users;
DROP TABLE IF EXISTS sessions;
-- +goose StatementEnd
