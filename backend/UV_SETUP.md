# Using uv Package Manager

This project uses `uv` - a fast Python package manager written in Rust.

## Why uv?

- **Fast**: 10-100x faster than pip
- **Reliable**: Better dependency resolution
- **Modern**: Built for Python 3.10+
- **Simple**: Single tool for package management

## Installation

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Using pip
```bash
pip install uv
```

## Usage

### Install Dependencies

```bash
# Install all dependencies (creates .venv automatically)
uv sync
```

This will:
- Create a virtual environment in `.venv/`
- Install all dependencies from `pyproject.toml`
- Generate `uv.lock` for reproducible builds

### Run Commands

```bash
# Run without activating venv
uv run uvicorn api.main:app --reload
uv run alembic upgrade head
uv run pytest

# Or activate venv first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uvicorn api.main:app --reload
```

### Add Dependencies

```bash
# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Add with version
uv add "package-name==1.2.3"
```

### Update Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add --upgrade package-name
```

### Remove Dependencies

```bash
uv remove package-name
```

## Project Structure

- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Locked dependency versions (auto-generated)
- `.venv/` - Virtual environment (auto-created, git-ignored)

## Migration from pip

If you were using `requirements.txt`:

1. Dependencies are now in `pyproject.toml`
2. Run `uv sync` instead of `pip install -r requirements.txt`
3. Use `uv run` or activate `.venv` instead of `venv`

## Benefits

1. **Faster installs**: uv is much faster than pip
2. **Better resolution**: Handles complex dependency graphs
3. **Lock file**: `uv.lock` ensures reproducible builds
4. **Single tool**: No need for pip, venv, setuptools separately

## Troubleshooting

### Clear cache
```bash
uv cache clean
```

### Reinstall everything
```bash
rm -rf .venv uv.lock
uv sync
```

### Check installed packages
```bash
uv pip list
```

