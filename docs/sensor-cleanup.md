# Sensor Cleanup

The integration keeps the Home Assistant entity registry in sync with the data
the router actually exposes. A dedicated **entity cleanup subsystem** runs in
two situations:

1. **On every integration reload** — the cleanup pass runs once, immediately
   after the first `fetch_all_data()`. This makes the integration "self-heal"
   the moment you restart Home Assistant or reload the config entry.
2. **Every 30 minutes** in the background — a periodic timer registered with
   `entry.async_on_unload` re-runs the same cleanup so the entity registry
   tracks the router's current state without requiring a reload. The timer is
   cancelled automatically when the config entry unloads.

The cleanup pass is **generic**. It walks a list of `EntityCleanupRule`
objects stored on the hub. Each rule is just a pair of predicates:

| Predicate | Purpose |
| --- | --- |
| `matches(entry)` | Returns `True` for registry entries this rule cares about. |
| `should_keep(entry)` | Returns `True` if the entry is still valid; `False` marks it for removal. |

When a rule matches an entry and `should_keep` returns `False`, the entry is
removed from the Home Assistant entity registry with `entity_registry.async_remove`.
A debug log line records the reason so the behaviour is auditable from
`home-assistant.log`:

```
Removing orphaned sensor sensor.cellular_sim_2_data_limit (cellular traffic limit disabled)
```

## Built-in Rules

The integration ships with one rule today, registered automatically when
cellular data is refreshed:

| Rule | What it cleans up | Source data |
| --- | --- | --- |
| `cellular traffic limit disabled` | The `data_limit` and `days_until_reset` sensors for any SIM slot whose `enable` flag (returned in the `limit` block) is `false`. | `traffic_sim_data`, populated by the `modem/get_traffic_config` call. |

When the router's data is unavailable (e.g. the call failed or returned an
empty response), the cellular rule **keeps** any existing limit sensors — the
rule is intentionally conservative and only acts when the router's current
state is known.

## Adding a New Rule

Future rules can be added in two steps:

1. **Register the rule** on the hub from the place that knows the relevant
   state (e.g. inside the per-feature fetch method, alongside the
   `_refresh_cellular_limit_cleanup_rule` call). The rule's `should_keep`
   closure should capture the relevant state in a local variable so it stays
   in sync with the latest refresh.
2. **Trigger a refresh** of the rule on every data refresh that could change
   its answer, then call `await self._async_cleanup_orphaned_sensor_entities()`.

The periodic 30-minute timer takes care of the case where state changes
between fetches (e.g. a device disappears from the router's client list).

## Adding Sensors Dynamically

The cleanup subsystem is paired with a **dispatcher event**
(`event_cellular_traffic_config_updated`) that fires every time the
`modem/get_traffic_config` call refreshes the per-SIM data. The sensor
platform listens for this event and re-evaluates which entities should
exist; if a SIM's `enable` flag has just been switched on, the
`data_limit` and `days_until_reset` sensors for that SIM are created and
added to Home Assistant on the next coordinator refresh (no reload
required).

The same event also drives the cleanup pass — anything that should no
longer exist is removed, and anything new is added, in a single
round-trip.

## Manual Cleanup

There is no separate user-facing "clean up" action — the periodic timer
and the reload-time pass cover both the immediate and the deferred cases.
If you want to force a fresh cleanup right now, just reload the
integration from **Settings → Devices & Services → GL.iNet Router →
⋯ → Reload**.
