# 📦 PyPI Release Guide

This guide outlines the process for updating the version and publishing **Agent-Harness** (`agentharnessengine`) to PyPI.

## Prerequisites

1.  **PyPI Account**: Ensure you have an account on [PyPI](https://pypi.org/).
2.  **API Token**: Generate an API token in your PyPI account settings for secure authentication.
3.  **Tools**: Install `build` and `twine`:
    ```bash
    pip install build twine
    ```

## Step-by-Step Release Process

### 1. Update Version Numbers
Update the version string to `v1.1.0` (or the next version) in the following files:
- `pyproject.toml`: `version = "1.1.0"`
- `src/governance/__init__.py`: `__version__ = "1.1.0"`

### 2. Clean Previous Builds
Delete the `dist/` and `build/` directories if they exist:
```powershell
Remove-Item -Recurse -Force dist, build
```

### 3. Build the Distribution
Run the build command from the repository root:
```powershell
python -m build
```
This will create `.tar.gz` and `.whl` files in the `dist/` directory.

### 4. Upload to PyPI
Use `twine` to upload the package:
```powershell
python -m twine upload dist/*
```
When prompted:
- **Username**: `__token__`
- **Password**: Your PyPI API token (including the `pypi-` prefix).

### 5. Verify the Release
Check the project page on PyPI: [https://pypi.org/project/agentharnessengine/](https://pypi.org/project/agentharnessengine/)

---
> [!IMPORTANT]
> Always run tests (`pytest`) before building a release to ensure no regressions are introduced.
