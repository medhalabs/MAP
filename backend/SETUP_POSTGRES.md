# PostgreSQL Setup Instructions

## On macOS (Homebrew PostgreSQL)

If you have PostgreSQL installed via Homebrew, try these methods:

### Method 1: Connect as postgres user

```bash
# Try connecting as postgres user (no password usually)
psql -U postgres

# If that works, run these commands:
CREATE USER map_user WITH PASSWORD 'map_password';
CREATE DATABASE map_db OWNER map_user;
GRANT ALL PRIVILEGES ON DATABASE map_db TO map_user;
\q
```

### Method 2: Use your macOS username

```bash
# Connect using your macOS username
psql -U $(whoami) -d postgres

# Then create the user and database
CREATE USER map_user WITH PASSWORD 'map_password';
CREATE DATABASE map_db OWNER map_user;
GRANT ALL PRIVILEGES ON DATABASE map_db TO map_user;
\q
```

### Method 3: Reset PostgreSQL password

If you can't connect, you may need to reset the postgres user password:

```bash
# Stop PostgreSQL
brew services stop postgresql@15  # or postgresql@14, etc.

# Start PostgreSQL in single-user mode (no authentication)
postgres --single -D /usr/local/var/postgresql@15 postgres

# In the PostgreSQL prompt, run:
ALTER USER postgres WITH PASSWORD 'your_password';
# Then exit with Ctrl+D

# Restart PostgreSQL normally
brew services start postgresql@15
```

### Method 4: Use Docker (Recommended - Easiest)

If you have Docker installed:

```bash
# From project root
docker-compose up -d postgres

# Wait a few seconds, then verify it's running
docker-compose ps postgres

# Database is ready! User and database are created automatically.
```

## Quick Setup Script

You can also try this automated setup (if you can connect as postgres):

```bash
# Connect and create in one command
psql -U postgres -c "CREATE USER map_user WITH PASSWORD 'map_password';" || true
psql -U postgres -c "CREATE DATABASE map_db OWNER map_user;" || true
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE map_db TO map_user;" || true
```

## Verify Setup

After setup, verify the database exists:

```bash
# List databases
psql -U map_user -d map_db -c "\l"

# Or connect to the database
psql -U map_user -d map_db
# You should be able to connect without errors
```

## Troubleshooting

### "FATAL: password authentication failed"

This usually means:
1. The user doesn't exist - Create it first
2. Wrong password - Reset it or check your `.env` file
3. PostgreSQL authentication method is set to require password

### "FATAL: role does not exist"

Create the user first:
```sql
CREATE USER map_user WITH PASSWORD 'map_password';
```

### "FATAL: database does not exist"

Create the database:
```sql
CREATE DATABASE map_db OWNER map_user;
```

### Can't connect at all

Check if PostgreSQL is running:
```bash
# macOS
brew services list | grep postgres

# Or check process
ps aux | grep postgres

# Start it if needed
brew services start postgresql@15
```

## Alternative: Use Docker Compose (Easiest)

If you're having trouble with local PostgreSQL, Docker Compose is the easiest option:

```bash
# Start PostgreSQL in Docker
docker-compose up -d postgres

# That's it! The database is ready.
# Check it's running:
docker-compose ps

# View logs if needed:
docker-compose logs postgres
```

The Docker setup automatically:
- Creates the user `map_user`
- Creates the database `map_db`
- Sets the password to `map_password`
- Exposes it on port 5432

