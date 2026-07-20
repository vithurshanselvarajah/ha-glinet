# Developer Reference

This document serves as a guide for anyone looking to contribute to, modify, or extend the `glinet-router` integration. 

## Codebase Structure

The integration is cleanly separated into two distinct layers:
1. **The API Layer (`api/`)**: A standalone, framework-agnostic asynchronous HTTP client built using `aiohttp` for communicating with the GL.iNet JSON-RPC (`/rpc`) interface.
2. **The Integration Layer (`entities/`, `hub.py`, `services.py`)**: The Home Assistant-specific implementation that translates router data into sensors, trackers, and switches.

## The API Layer (`custom_components/glinet_router/api/`)

The API client is highly modular.

### Modules (`api/modules/`)
Instead of a single monolithic client class, the API is broken down into specific feature modules. Each module extends `BaseModule` and implements the RPC methods relevant to its domain. Current modules include: `system`, `wifi`, `clients`, `modem`, `mcu`, `wg_client`, `wg_server`, `ovpn_client`, `ovpn_server`, `tailscale`, `repeater`, `fan`, `firewall`, `led`, `macclone`, `diag`, `adguard`, `parental_control`, and `black_white_list`.

When adding a new router endpoint, you should:
1. Create a new module file in `api/modules/`.
2. Inherit from `BaseModule` and implement your API calls.
3. Attach the module to the main `GLinetApiClient` class in `api/client.py` as an instance attribute so it can be accessed like `client.my_feature.get_status()`.

### Models
The integration uses two layers of data models:
- **`api/models.py`**: Strongly-typed `dataclass` models for raw API response fields. These are returned directly from API module calls.
- **`models.py`** (integration layer): Higher-level dataclasses used by the hub and entities, e.g., `ClientDeviceInfo`, `RepeaterStatus`, `WireGuardClient`, `ParentalGroup`. These aggregate, transform, or combine data from one or more API responses.

## The Integration Layer

### The Hub (`hub.py`)
The `GLinetHub` is the heart of the integration. It inherits from `DataUpdateCoordinator` and manages:
- **Session state:** Handing token expiration and renewal.
- **Polling Loop:** Executing API requests sequentially every scan interval (user-configurable, default 30s) to prevent overwhelming the router's lighttpd server.
- **Caching:** Storing the latest fetched values from the API models so Home Assistant entities can read them instantly without making network calls.

> For more details on the Hub's functions and data fetching logic, see the [Runtime State & Poller Reference](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub).

### Diagnostics (`diagnostics.py`)
The integration implements the Home Assistant `diagnostics` platform. This allows users to download a sanitized JSON snapshot of the router's state for debugging. 
When adding new data points to the hub, ensure they are also captured in `async_get_config_entry_diagnostics` and properly redacted if they contain PII (SSIDs, MACs, IPs, etc.).

### Entities (`entities/`)
Entities are split by Home Assistant domain (e.g., `sensor.py`, `switch.py`, `button.py`). 
All entities inherit from `CoordinatorEntity[GLinetHub]`. Entities should **never** make direct network calls in their property methods. Instead, they should return values directly from the cached `GLinetHub` state. Network calls (like toggling a switch) must be performed via the hub's methods.

## Development Guidelines

### Adding a New Sensor
To add a new sensor for an existing API endpoint:
1. **API Models:** Update `api/models.py` if the new field isn't captured in the raw API dataclass.
2. **Hub Models:** Update `models.py` if the new field needs a higher-level model or transformation.
3. **Hub:** Update `hub.py` to fetch, store, and expose the new data point.
4. **Entities:** Add your sensor to `entities/sensor.py`.
5. **Diagnostics:** Update `diagnostics.py` to include the new data point in the export.
6. **Tests:** Update your mock tests in `tests/` to ensure the new sensor state works correctly.

### Tooling
The project relies on standard Python development tools:
- **Testing:** `pytest` and `pytest-asyncio`. Tests mock all network interactions to ensure the API and hub function correctly without a live router.
- **Linting:** We strictly enforce linting and formatting via `ruff`. 

Run the following commands before submitting any pull requests:
```powershell
python -m pytest -q
python -m ruff check custom_components tests --fix
python -m ruff format custom_components tests
```

### Dependencies
Do not add massive third-party library dependencies unless absolutely necessary. Home Assistant integrations should remain lightweight. The core integration relies only on `aiohttp` (which is native to HA).

## Branching & PRs

The repository uses a two-branch model: `main` is the release branch
and `development` is the integration branch. **All day-to-day pull
requests target `development`.** Releases are cut as a `development`
→ `main` PR by the maintainer(s).

A bot ([`pr-target-check.yml`](../.github/workflows/pr-target-check.yml))
comments and applies the `wrong-target` label to any PR opened
against `main` that is not a `development` → `main` release. Outside
contributors fork the repository and submit from a fork — no one
outside the maintainer team has direct write access.

`main` is protected by a ruleset (1 approval, code-owner review,
CI must pass). `development` has no ruleset on purpose: maintainers
can push directly there, and Dependabot and bot updates don't need
to fight branch protection. See
[`.github/BRANCH_PROTECTION.md`](../.github/BRANCH_PROTECTION.md)
for the full ruleset and rationale.

> **Solo-maintainer note:** the `main` ruleset leaves the
> *"Require approval of the most recent reviewable push"* rule
> **off** so the only maintainer can self-merge release PRs.
> Re-enable it when a second maintainer is added.

For the full contribution flow, see
[`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Related Pages

- [Architecture](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/architecture) — How the integration is structured and interacts with Home Assistant.
- [Runtime State & Poller (Hub)](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub) — Details on the `GLinetHub` and `DataUpdateCoordinator`.
- [Router API Notes](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/router-api) — Endpoints, authentication, and module inventory.
- [Modem API Coverage](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/modem-api) — Details on the optional cellular modem API.
- [CI and Release Workflows](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/ci-release) — How automated testing and releases work.
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — Full contributor guide.
