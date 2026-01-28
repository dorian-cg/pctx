# Project Context (PCTX)
Project context information for AI agents.

## Build Project
Follow these instructions to build the project:

### 1. Prerequisites
- Python 3.13

### 2. Ensure `pipx` is installed globally
```bash
python -m pip install --user pipx
```

### 3.Create virtual environment
```bash
python -m venv venv
```

### 4. Activate virtual environment
Mac & Linux
```bash
source venv/bin/activate
```
Windows
```ps1
venv\Scripts\Activate.ps1
```

### 5. Install dependencies
```bash
python -m pip install -e .
```

### 6. Run for development
```bash
python -m pctx
```

### 7. Build & install CLI
```bash
python -m pipx install . --force
```

### 8. Run CLI
```bash
pctx
```