"""
Migration script to make broker_account_id nullable in strategy_runs table.

This allows broker accounts to be deleted while preserving strategy run history.
Run with: uv run python scripts/migrate_broker_account_nullable.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.session import engine, init_db
from sqlalchemy import text


def migrate():
    """Migrate database to make broker_account_id nullable."""
    print("Starting migration: Make broker_account_id nullable in strategy_runs...")
    
    try:
        with engine.connect() as conn:
            # Check current schema
            result = conn.execute(text("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='strategy_runs'
            """))
            current_sql = result.fetchone()
            if current_sql:
                print(f"Current schema: {current_sql[0][:100]}...")
            
            # SQLite doesn't support ALTER COLUMN directly, so we need to:
            # 1. Create new table with nullable column
            # 2. Copy data
            # 3. Drop old table
            # 4. Rename new table
            
            print("Step 1: Creating new table structure...")
            conn.execute(text("""
                CREATE TABLE strategy_runs_new (
                    id INTEGER NOT NULL PRIMARY KEY,
                    strategy_id INTEGER NOT NULL,
                    broker_account_id INTEGER,
                    trading_mode VARCHAR(20) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    config TEXT NOT NULL,
                    started_at DATETIME,
                    stopped_at DATETIME,
                    error_message TEXT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY(strategy_id) REFERENCES strategies (id) ON DELETE CASCADE,
                    FOREIGN KEY(broker_account_id) REFERENCES broker_accounts (id) ON DELETE SET NULL
                )
            """))
            conn.commit()
            
            print("Step 2: Copying data from old table...")
            conn.execute(text("""
                INSERT INTO strategy_runs_new 
                SELECT * FROM strategy_runs
            """))
            conn.commit()
            
            print("Step 3: Dropping old table...")
            conn.execute(text("DROP TABLE strategy_runs"))
            conn.commit()
            
            print("Step 4: Renaming new table...")
            conn.execute(text("ALTER TABLE strategy_runs_new RENAME TO strategy_runs"))
            conn.commit()
            
            print("Step 5: Recreating indexes...")
            conn.execute(text("""
                CREATE INDEX ix_strategy_runs_strategy_id ON strategy_runs (strategy_id)
            """))
            conn.execute(text("""
                CREATE INDEX ix_strategy_runs_broker_account_id ON strategy_runs (broker_account_id)
            """))
            conn.execute(text("""
                CREATE INDEX ix_strategy_runs_status ON strategy_runs (status)
            """))
            conn.execute(text("""
                CREATE INDEX idx_strategy_run_status ON strategy_runs (status, trading_mode)
            """))
            conn.commit()
            
            print("✅ Migration completed successfully!")
            print("broker_account_id is now nullable and will be set to NULL when broker accounts are deleted.")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("Rolling back...")
        try:
            with engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS strategy_runs_new"))
                conn.commit()
        except:
            pass
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Make broker_account_id nullable")
    print("=" * 60)
    print()
    print("This migration will:")
    print("  1. Make broker_account_id nullable in strategy_runs table")
    print("  2. Change foreign key constraint to SET NULL")
    print("  3. Preserve all existing data")
    print()
    
    response = input("Do you want to proceed? (yes/no): ")
    if response.lower() != "yes":
        print("Migration cancelled.")
        sys.exit(0)
    
    print()
    migrate()

