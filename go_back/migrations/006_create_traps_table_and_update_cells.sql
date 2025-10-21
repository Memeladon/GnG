-- +goose Up
-- +goose StatementBegin

-- Create traps table
CREATE TABLE IF NOT EXISTS traps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cell_id INTEGER NOT NULL REFERENCES cells(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    effect_type effect_type NOT NULL,
    effect_value TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    triggered_by UUID REFERENCES players(id) ON DELETE SET NULL,
    triggered_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Remove traps column from cells table (if it exists)
ALTER TABLE cells DROP COLUMN IF EXISTS traps;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_traps_cell_id ON traps(cell_id);
CREATE INDEX IF NOT EXISTS idx_traps_is_active ON traps(is_active);
CREATE INDEX IF NOT EXISTS idx_traps_triggered_by ON traps(triggered_by);
CREATE INDEX IF NOT EXISTS idx_traps_effect_type ON traps(effect_type);

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin

-- Drop indexes
DROP INDEX IF EXISTS idx_traps_effect_type;
DROP INDEX IF EXISTS idx_traps_triggered_by;
DROP INDEX IF EXISTS idx_traps_is_active;
DROP INDEX IF EXISTS idx_traps_cell_id;

-- Add traps column back to cells table as JSONB
ALTER TABLE cells ADD COLUMN traps JSONB;

-- Drop traps table
DROP TABLE IF EXISTS traps;

-- +goose StatementEnd
