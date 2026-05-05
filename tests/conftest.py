from __future__ import annotations

import asyncio
import inspect
import sys
import types
from datetime import UTC, datetime
from typing import Any


def pytest_configure() -> None:
    aiohttp = sys.modules.get("aiohttp") or types.ModuleType("aiohttp")
    if not hasattr(aiohttp, "ClientError"):
        aiohttp.ClientError = OSError
    if not hasattr(aiohttp, "ClientResponse"):
        aiohttp.ClientResponse = object
    if not hasattr(aiohttp, "ClientSession"):
        aiohttp.ClientSession = object
    sys.modules.setdefault("aiohttp", aiohttp)

    passlib = sys.modules.get("passlib") or types.ModuleType("passlib")
    passlib_hash = types.ModuleType("passlib.hash")

    class _CryptStub:
        @classmethod
        def using(cls, **_: Any) -> type[_CryptStub]:
            return cls

        @staticmethod
        def hash(password: str) -> str:
            return f"crypt:{password}"

    passlib_hash.md5_crypt = _CryptStub
    passlib_hash.sha256_crypt = _CryptStub
    passlib_hash.sha512_crypt = _CryptStub
    passlib.hash = passlib_hash
    sys.modules.setdefault("passlib", passlib)
    sys.modules.setdefault("passlib.hash", passlib_hash)

    try:
        __import__("homeassistant")
    except ModuleNotFoundError:
        homeassistant = types.ModuleType("homeassistant")
        components = types.ModuleType("homeassistant.components")
        device_tracker = types.ModuleType("homeassistant.components.device_tracker")
        device_tracker.CONF_CONSIDER_HOME = "consider_home"
        device_tracker.DEFAULT_CONSIDER_HOME = types.SimpleNamespace(total_seconds=lambda: 180)
        device_tracker.DOMAIN = "device_tracker"

        const = types.ModuleType("homeassistant.const")
        const.CONF_HOST = "host"
        const.CONF_MAC = "mac"
        const.CONF_MODEL = "model"
        const.CONF_PASSWORD = "password"
        const.CONF_USERNAME = "username"

        exceptions = types.ModuleType("homeassistant.exceptions")
        exceptions.ConfigEntryAuthFailed = type("ConfigEntryAuthFailed", (Exception,), {})
        exceptions.ConfigEntryNotReady = type("ConfigEntryNotReady", (Exception,), {})

        helpers = types.ModuleType("homeassistant.helpers")
        entity_registry = types.ModuleType("homeassistant.helpers.entity_registry")
        entity_registry.async_get = lambda hass: None
        entity_registry.async_entries_for_config_entry = lambda registry, entry_id: []

        aiohttp_client = types.ModuleType("homeassistant.helpers.aiohttp_client")
        aiohttp_client.async_get_clientsession = lambda hass: None

        device_registry = types.ModuleType("homeassistant.helpers.device_registry")
        device_registry.CONNECTION_NETWORK_MAC = "mac"
        device_registry.format_mac = lambda mac: str(mac).lower()
        device_registry.async_get = lambda hass: types.SimpleNamespace(
            async_get_device=lambda connections: None
        )

        dispatcher = types.ModuleType("homeassistant.helpers.dispatcher")
        dispatcher.async_dispatcher_connect = lambda *args, **kwargs: lambda: None
        dispatcher.async_dispatcher_send = lambda *args, **kwargs: None

        entity = types.ModuleType("homeassistant.helpers.entity")
        entity.DeviceInfo = dict

        event = types.ModuleType("homeassistant.helpers.event")
        event.async_track_time_interval = lambda *args, **kwargs: None

        util = types.ModuleType("homeassistant.util")
        dt = types.ModuleType("homeassistant.util.dt")
        dt.utcnow = lambda: datetime.now(UTC).replace(tzinfo=None)
        components.device_tracker = device_tracker
        helpers.entity_registry = entity_registry
        helpers.aiohttp_client = aiohttp_client
        helpers.device_registry = device_registry
        helpers.dispatcher = dispatcher
        helpers.entity = entity
        helpers.event = event
        util.dt = dt
        homeassistant.components = components
        homeassistant.const = const
        homeassistant.exceptions = exceptions
        homeassistant.helpers = helpers
        homeassistant.util = util
        sys.modules.setdefault("homeassistant", homeassistant)
        sys.modules.setdefault("homeassistant.components", components)
        sys.modules.setdefault("homeassistant.components.device_tracker", device_tracker)
        sys.modules.setdefault("homeassistant.const", const)
        sys.modules.setdefault("homeassistant.exceptions", exceptions)
        sys.modules.setdefault("homeassistant.helpers", helpers)
        sys.modules.setdefault("homeassistant.helpers.entity_registry", entity_registry)
        sys.modules.setdefault("homeassistant.helpers.aiohttp_client", aiohttp_client)
        sys.modules.setdefault("homeassistant.helpers.device_registry", device_registry)
        sys.modules.setdefault("homeassistant.helpers.dispatcher", dispatcher)
        sys.modules.setdefault("homeassistant.helpers.entity", entity)
        sys.modules.setdefault("homeassistant.helpers.event", event)
        sys.modules.setdefault("homeassistant.util", util)
        sys.modules.setdefault("homeassistant.util.dt", dt)


def pytest_pyfunc_call(pyfuncitem: Any) -> bool:
    testfunction = pyfuncitem.obj
    if not inspect.iscoroutinefunction(testfunction):
        return False

    kwargs = {
        name: pyfuncitem.funcargs[name]
        for name in pyfuncitem._fixtureinfo.argnames
    }
    asyncio.run(testfunction(**kwargs))
    return True
