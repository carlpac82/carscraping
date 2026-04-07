-- Add can_manage_commissioners column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS can_manage_commissioners BOOLEAN DEFAULT FALSE;

-- Add comment to describe the column purpose
COMMENT ON COLUMN users.can_manage_commissioners IS 'Determines if user can manage commissioners (only for support role)';
