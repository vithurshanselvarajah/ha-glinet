<!--
Thanks for contributing to ha-glinet-router! 🚀

Please make sure your PR targets the `development` branch.
PRs opened against `main` are auto-flagged and will not be merged
(except for release PRs — see `.github/PULL_REQUEST_TEMPLATE/release.md`).

A more specific template may suit your change better:
  - feature  →  .github/PULL_REQUEST_TEMPLATE/feature.md
  - bugfix   →  .github/PULL_REQUEST_TEMPLATE/bugfix.md
  - docs     →  .github/PULL_REQUEST_TEMPLATE/docs.md
  - release  →  .github/PULL_REQUEST_TEMPLATE/release.md  (maintainers only)
-->

## What does this PR do?

<!-- One or two sentence summary of the change. -->

## Related issues

<!-- Link the issues this PR closes or addresses, e.g. "Fixes #123". -->

- Fixes #
- Refs #

## Type of change

<!-- Put an `x` in the box(es) that apply. -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation only
- [ ] Refactor / internal change
- [ ] Release (maintainers only — `development` → `main`)

## How has it been tested?

<!-- Describe how you verified your change. For bug fixes, include steps
     to reproduce both before and after. For new features, include the
     manual checks you ran in Home Assistant. -->

- [ ] `pytest -q` passes locally
- [ ] `ruff check custom_components tests` passes
- [ ] `ruff format --check custom_components tests` passes
- [ ] Manual test in Home Assistant (HA version: ____, router model: ____, firmware: ____)

## Checklist

- [ ] My code follows the project's style (see `CONTRIBUTING.md` and `docs/developer-reference.md`)
- [ ] I have added or updated tests for my change
- [ ] I have added or updated documentation under `docs/` (if user-facing)
- [ ] I have **not** put `release:` in any commit message
- [ ] I have **not** changed the version in `manifest.json` or `pyproject.toml` (unless this is a release PR)
- [ ] My PR targets `development` (**not** `main`)
- [ ] I am opening this PR from a fork (or I am a maintainer)
- [ ] I have read `CONTRIBUTING.md`

## Screenshots / logs

<!-- If applicable, add screenshots or log output to help explain your change. -->
