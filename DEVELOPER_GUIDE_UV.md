# Developer Guide - Using UV with PhotoGen App v3

## Why UV?

UV is a fast Python package installer and resolver, written in Rust. It's designed to be a drop-in replacement for pip with significant performance improvements:

- **10-100x faster** than pip for dependency resolution
- **Better caching** - reuses downloads across projects
- **Improved dependency resolution** - handles conflicts better
- **Modern tooling** - built for Python 3.8+ with modern standards

## Quick Start for Developers

### Option 1: UV Quick Install (Recommended)
```bash
# Clone the repository
git clone https://github.com/hooh777/photogen_app_v3.git
cd photogen_app_v3

# Run the UV quick installer
install-uv-quick.bat
```

### Option 2: Full Developer Install
```bash
# For comprehensive setup with dev tools
install-dev-uv.bat
```

### Option 3: Manual UV Setup
```bash
# Install UV if not already installed
pip install uv

# Create virtual environment
uv venv venv

# Activate environment (Windows)
call venv\Scripts\activate.bat

# Install PhotoGen with GPU support
uv pip install -e ".[gpu]"

# Or CPU-only version
uv pip install -e "."

# Or everything including dev tools
uv pip install -e ".[all]"
```

## Using pyproject.toml

PhotoGen App v3 now includes a `pyproject.toml` file that defines dependency groups:

- **Base dependencies**: API services, web UI (CPU-only)
- **GPU extras**: `[gpu]` - PyTorch, CUDA, local model processing
- **Dev extras**: `[dev]` - Testing, linting, formatting tools
- **All extras**: `[all]` - Everything combined

### Installation Examples

```bash
# CPU-only installation (APIs only)
uv pip install -e "."

# GPU support (local + API processing)  
uv pip install -e ".[gpu]"

# Development tools
uv pip install -e ".[dev]"

# Everything (GPU + dev tools)
uv pip install -e ".[all]"
```

## Daily Development Workflow

### Package Management
```bash
# Install a new package
uv pip install package-name

# Install package with extras
uv pip install "package-name[extra]"

# Install from Git
uv pip install git+https://github.com/user/repo.git

# List installed packages  
uv pip list

# Show package info
uv pip show package-name

# Export requirements
uv pip freeze > requirements.txt

# Sync with requirements file
uv pip sync requirements.txt
```

### Development Tools (if installed with [dev])
```bash
# Format code with Black
black .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy core/

# Run tests
pytest

# Run tests with coverage
pytest --cov=core

# Setup pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

### Virtual Environment Management
```bash
# Create new environment with specific Python version
uv venv venv --python 3.11

# Create with system packages
uv venv venv --system-site-packages

# Remove environment
rmdir /s venv  # Windows

# List UV cache
uv cache dir

# Clean UV cache
uv cache clean
```

## Performance Comparison

Typical installation times for PhotoGen dependencies:

| Tool | CPU Install | GPU Install | Full Dev Install |
|------|-------------|-------------|------------------|
| pip  | 3-5 min     | 8-12 min    | 10-15 min        |
| UV   | 30-60 sec   | 2-3 min     | 3-4 min          |

## Troubleshooting

### UV Not Found
```bash
# Install UV via pip
pip install uv

# Or via conda
conda install -c conda-forge uv

# Or download directly from GitHub releases
# https://github.com/astral-sh/uv/releases
```

### Dependency Conflicts
```bash
# UV has better dependency resolution than pip
# If you encounter conflicts, try:
uv pip install --resolution=lowest-direct

# Or force reinstall
uv pip install --force-reinstall package-name
```

### Slow Network Issues
```bash
# Use different index
uv pip install --index-url https://pypi.python.org/simple/

# Or add extra index
uv pip install --extra-index-url https://download.pytorch.org/whl/cu121
```

### Cache Issues
```bash
# Clear UV cache
uv cache clean

# Check cache location
uv cache dir

# Install without cache
uv pip install --no-cache package-name
```

## Advanced Configuration

### pyproject.toml Customization

You can modify `pyproject.toml` to customize dependencies:

```toml
[project.optional-dependencies]
# Add your custom dependency group
custom = [
    "your-package>=1.0.0",
    "another-package>=2.0.0",
]

# Then install with:
# uv pip install -e ".[custom]"
```

### UV Configuration File

Create `uv.toml` in project root for UV-specific settings:

```toml
[tool.uv]
index-url = "https://pypi.org/simple"
extra-index-url = ["https://download.pytorch.org/whl/cu121"]
no-cache = false
```

## Integration with IDEs

### VS Code
- Install Python extension
- Set interpreter to `venv\Scripts\python.exe`
- UV dependencies are automatically detected

### PyCharm
- Configure interpreter: Settings > Python Interpreter
- Point to `venv\Scripts\python.exe`
- Enable "Inherit global site-packages" if using system packages

## Best Practices

1. **Always use virtual environments** - UV makes this fast
2. **Pin critical dependencies** - Use exact versions for production
3. **Use dependency groups** - Separate dev, testing, and production deps
4. **Regular updates** - `uv pip install --upgrade package-name`
5. **Cache management** - Periodically clean cache with `uv cache clean`

## Migration from pip

If you have an existing pip-based setup:

```bash
# Export existing requirements
pip freeze > requirements-old.txt

# Create new UV environment
uv venv venv-new
call venv-new\Scripts\activate.bat

# Install from old requirements
uv pip install -r requirements-old.txt

# Or migrate to pyproject.toml-based setup
uv pip install -e ".[gpu]"  # or appropriate extras
```

## Getting Help

- UV Documentation: https://docs.astral.sh/uv/
- UV GitHub: https://github.com/astral-sh/uv
- PhotoGen Issues: https://github.com/hooh777/photogen_app_v3/issues

For PhotoGen-specific UV issues, please create an issue with:
- Your UV version: `uv --version`
- Your Python version: `python --version`
- The command that failed
- Full error output
