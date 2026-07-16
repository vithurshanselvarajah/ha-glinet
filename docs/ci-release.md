# CI and Release Workflows (`.github/workflows/`)

The repository has two GitHub Actions workflows.

## CI

`.github/workflows/ci.yml` runs on pull requests and as a reusable workflow call.

It performs:

- JSON validation for `manifest.json` and `hacs.json`.
- Python compilation for `custom_components` and `tests`.
- Pytest.
- Ruff linting.
- Version consistency check between `custom_components/glinet_router/manifest.json` and `pyproject.toml`.

## Release

`.github/workflows/release.yml` runs only on `main` and publishes releases when a stable release is requested.

Release triggers:

- Stable release: push to `main` with `release:` anywhere in the head commit message.
- Manual run: trigger workflow dispatch on `main`.

The workflow reads the version from `custom_components/glinet_router/manifest.json`.

Stable releases create:

```text
v<manifest-version>
```

The release job runs CI first, builds a HACS-friendly zip containing `custom_components/glinet_router`, asks GitHub Models to generate release notes via `actions/ai-inference`, then publishes a GitHub release. If GitHub Models is not available, the workflow falls back to commit-based release notes.

## Related Pages

- [Developer Reference](developer-reference.md) — Contributing, tooling, and project structure.
