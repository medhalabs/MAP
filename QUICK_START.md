# Quick Start Guide

## Setup Database with Docker (Easiest)

Since you have PostgreSQL running locally with authentication, Docker Compose is the easiest option:

### Step 1: Stop Local PostgreSQL (Optional - only if you want to use Docker)

```bash
# Stop Homebrew PostgreSQL
brew services stop postgresql@15  # or postgresql@17, etc.

# Verify it's stopped
lsof -i :5432  # Should show nothing or Docker
```

### Step 2: Start PostgreSQL with Docker

```bash
# From project root
docker-compose up -d postgres

# Wait a few seconds, then verify it's running
docker-compose ps postgres

# Check logs if needed
docker-compose logs postgres
```

### Step 3: Start the Backend Server

```bash
cd backend
uv run uvicorn api.main:app --reload
```

The database will be automatically initialized with all tables!

## Alternative: Use Local PostgreSQL

If you want to use your existing PostgreSQL instead:

### Step 1: Connect to PostgreSQL

You'll need to authenticate first. Try one of these methods:

**Method A: Use peer authentication (if configured)**
```bash
# This might work if your user has access
sudo -u postgres psql
```

**Method B: Reset postgres password and connect**
```bash
# Stop PostgreSQL
brew services stop postgresql@15

# Start in single-user mode (no authentication)
postgres --single -D /usr/local/var/postgresql@15 postgres

# In the prompt, run:
ALTER USER postgres WITH PASSWORD 'your_password';
# Exit with Ctrl+D

# Restart normally
brew services start postgresql@15

# Now connect with password
psql -U postgres -h localhost
# Enter password when prompted
```

### Step 2: Create Database and User

Once connected, run:
```sql
CREATE USER map_user WITH PASSWORD 'map_password';
CREATE DATABASE map_db OWNER map_user;
GRANT ALL PRIVILEGES ON DATABASE map_db TO map_user;
\q
```

### Step 3: Update .env File

Create `backend/.env`:
```env
DATABASE_URL=postgresql://map_user:map_password@localhost:5432/map_db
```

### Step 4: Start the Backend

```bash
cd backend
uv run uvicorn api.main:app --reload
```

## Recommended Approach

**Use Docker Compose** - it's the easiest because:
- ✅ No authentication setup needed
- ✅ Automatically creates user and database
- ✅ Isolated from your local PostgreSQL
- ✅ Easy to reset/clean up

Just run:
```bash
# Stop local PostgreSQL (optional)
brew services stop postgresql@15

# Start Docker PostgreSQL
docker-compose up -d postgres

# Start backend
cd backend && uv run uvicorn api.main:app --reload
```

