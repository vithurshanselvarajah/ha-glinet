---
name: Bug Fix
about: Fix a bug in the integration
---

<!--
  Bug fix PRs target `development`, not `main`.
-->

## Bug description

<!-- What went wrong, and what was the expected behaviour? -->

## Reproduction steps

<!-- Minimal, deterministic steps to reproduce the bug. -->
1.
2.
3.

## Environment

- Home Assistant version:
- Integration version (from `custom_components/glinet_router/manifest.json`):
- Router model:
- Router firmware version:
- Relevant config (config flow options, custom modules enabled, etc.):

## Root cause

<!-- Optional but very helpful: a short explanation of what was wrong
     and why your change fixes it. -->

## Fix description

<!-- What did you change, and why? -->

## Regression risk

<!-- What could this break? What did you check to be confident it doesn't? -->

## Checklist

- [ ] `pytest -q` passes locally (including a new regression test)
- [ ] `ruff check custom_components tests` passes
- [ ] `ruff format --check custom_components tests` passes
- [ ] Diagnostics export updated (if applicable)
- [ ] Docs updated (if user-visible behaviour changed)
