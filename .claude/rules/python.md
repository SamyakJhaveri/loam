---
paths:
  - "**/*.py"
---

# Python Rules

> Auto-loaded when working on `*.py` files.

## Interpreter

- Always `python3`, never bare `python`
- Venv: `source env_parbench/bin/activate` (but note: venv was created on Linux, may be broken on Mac)
- Install: `python3 -m pip install <pkg>` inside activated venv

## Testing

```bash
python3 -m pytest c_augmentation/test_transforms.py -v
```

## Style

- Use `ruff` for linting if available
- Follow existing code conventions in the file being edited
- Harness CLI: global flags (`-v`, `--json`) MUST come BEFORE the subcommand
