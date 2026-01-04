# Database Setup Guide

## Quick Start with Docker

The easiest way to set up PostgreSQL is using Docker Compose:

```bash
# From project root
docker-compose up -d postgres
```

This will start PostgreSQL with:
- User: `map_user`
- Password: `map_password`
- Database: `map_db`
- Port: `5432`

## Manual PostgreSQL Setup

### 1. Install PostgreSQL

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create Database and User

```bash
# Connect to PostgreSQL
psql postgres

# Create user and database
CREATE USER map_user WITH PASSWORD 'map_password';
CREATE DATABASE map_db OWNER map_user;
GRANT ALL PRIVILEGES ON DATABASE map_db TO map_user;

# Exit psql
\q
```

### 3. Update Environment Variables

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=postgresql://map_user:map_password@localhost:5432/map_db
```

## Initialize Database Tables

After setting up PostgreSQL, initialize the database schema:

```bash
cd backend

# Option 1: Using Python directly
uv run python -c "from database.session import init_db; init_db()"

# Option 2: Using Alembic (recommended for production)
uv run alembic upgrade head
```

## Verify Connection

Test the database connection:

```bash
cd backend
uv run python -c "from database.session import engine; engine.connect(); print('Database connection successful!')"
```

## Troubleshooting

### Connection Refused
- Ensure PostgreSQL is running: `pg_isready` or `docker ps`
- Check if PostgreSQL is listening on port 5432: `lsof -i :5432`

### Authentication Failed
- Verify username and password in `.env` file
- Check PostgreSQL user exists: `psql -U postgres -c "\du"`
- Reset password: `ALTER USER map_user WITH PASSWORD 'map_password';`

### Database Does Not Exist
- Create it: `CREATE DATABASE map_db;`
- Grant permissions: `GRANT ALL PRIVILEGES ON DATABASE map_db TO map_user;`

## Using Docker Compose

The `docker-compose.yml` file includes PostgreSQL configuration:

```bash
# Start PostgreSQL
docker-compose up -d postgres

# View logs
docker-compose logs postgres

# Stop PostgreSQL
docker-compose stop postgres

# Remove PostgreSQL (WARNING: deletes data)
docker-compose down -v postgres
```

## Environment Variables

The application reads database configuration from environment variables:

- `DATABASE_URL` - Full PostgreSQL connection string
  - Format: `postgresql://user:password@host:port/database`
  - Default: `postgresql://map_user:map_password@localhost:5432/map_db`

You can also set individual components:
- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5432)
- `DB_USER` - Database user (default: map_user)
- `DB_PASSWORD` - Database password (default: map_password)
- `DB_NAME` - Database name (default: map_db)

