# Developer Reference

This document serves as a guide for anyone looking to contribute to, modify, or extend the `ha-glinet` integration. 

## Codebase Structure

The integration is cleanly separated into two distinct layers:
1. **The API Layer (`api/`)**: A standalone, framework-agnostic asynchronous HTTP client built using `aiohttp` for communicating with the GL.iNet JSON-RPC (`/rpc`) interface.
2. **The Integration Layer (`entities/`, `hub.py`, `services.py`)**: The Home Assistant-specific implementation that translates router data into sensors, trackers, and switches.

## The API Layer (`custom_components/ha_glinet/api/`)

The API client is highly modular.

### Modules (`api/modules/`)
Instead of a single monolithic client class, the API is broken down into specific feature modules (e.g., `wifi.py`, `modem.py`, `vpn.py`). Each module extends `BaseModule` and implements the RPC methods relevant to its domain. 

When adding a new router endpoint (e.g., parental controls), you should:
1. Create a new module file in `api/modules/`.
2. Inherit from `BaseModule` and implement your API calls.
3. Attach the module to the main `GLinetApiClient` class in `api/client.py` via a `@property` so it can be accessed like `client.parental.get_status()`.

### Models (`api/models.py`)
All complex data returned from the router should be parsed into strongly-typed `dataclass` models rather than raw dictionaries. This ensures type safety and autocompletion downstream in Home Assistant. 

## The Integration Layer

### The Hub (`hub.py`)
The `GLinetHub` is the heart of the integration. It inherits from `DataUpdateCoordinator` and manages:
- **Session state:** Handing token expiration and renewal.
- **Polling Loop:** Executing API requests sequentially every scan interval (default 30s) to prevent overwhelming the router's lighttpd server.
- **Caching:** Storing the latest fetched values from the API models so Home Assistant entities can read them instantly without making network calls.

### Entities (`entities/`)
Entities are split by Home Assistant domain (e.g., `sensor.py`, `switch.py`, `button.py`). 
Entities should **never** make direct network calls in their `_async_update_data` properties. Instead, they should return properties directly from the cached `GLinetHub` state. Network calls are strictly reserved for state-mutating actions (e.g., toggling a switch or pressing a button).

## Development Guidelines

### Adding a New Sensor
To add a new sensor for an existing API endpoint:
1. **Models:** Update `api/models.py` if the new field isn't captured in the dataclass.
2. **Hub:** Ensure `hub.py` fetches and exposes the data you need.
3. **Entities:** Add your sensor to `entities/sensor.py` by inheriting from `GLinetCoordinatorEntity`.
4. **Tests:** Update your mock tests to ensure the new sensor state works correctly.

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
