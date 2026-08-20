# Contributing

Thank you for helping improve Vector PDF Suite.

## Development workflow

1. Fork the repository and create a focused branch.
2. Run `install.cmd` on Windows or follow the manual setup in the README.
3. Keep changes small, documented and covered by tests when applicable.
4. Run the complete validation suite before opening a pull request:

```bash
PYTHONPATH=backend pytest backend/tests -q
pnpm build
```

## Commit messages

Use Conventional Commits where practical:

- `feat:` new functionality
- `fix:` bug fixes
- `docs:` documentation changes
- `refactor:` internal improvements
- `test:` test additions or corrections
- `chore:` maintenance and tooling

## Pull requests

Describe the problem, the chosen solution and how the change was tested. Include screenshots for visible interface changes. Do not commit generated binaries, dependency folders, caches or personal documents.
