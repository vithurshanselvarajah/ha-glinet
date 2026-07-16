---
name: New Feature
about: Add a new user-facing feature to the integration
---

<!--
  Feature PRs target `development`, not `main`.
  Maintainers: for a `development` → `main` release, use release.md instead.
-->

## Feature summary

<!-- One paragraph: what is this and why is it useful? -->

## Affected components

<!-- List the files / modules / entities you changed. -->
- `custom_components/glinet_router/api/modules/...`
- `custom_components/glinet_router/entities/...`
- `custom_components/glinet_router/hub.py`
- `docs/...`

## Router / firmware support

<!-- What routers and firmware versions have you tested this on?
     If a particular feature is unavailable on a model, note that here. -->

| Router model | Firmware | Supported | Notes |
| ------------ | -------- | --------- | ----- |
|              |          |           |       |

## Manual test plan

<!-- Step-by-step manual verification. -->
1.
2.
3.

## Documentation

- [ ] New or updated page under `docs/`
- [ ] Linked from `docs/Home.md` and `README.md` feature matrix (if user-facing)
- [ ] Added entry to the changelog / release notes draft (if appropriate)

## Checklist

- [ ] `pytest -q` passes locally
- [ ] `ruff check custom_components tests` passes
- [ ] `ruff format --check custom_components tests` passes
- [ ] Tests added for the new behaviour
- [ ] Diagnostics export updated (if a new data point is exposed)
- [ ] No new runtime dependencies, or rationale provided in the PR description
