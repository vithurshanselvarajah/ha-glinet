# Automation Templates

Ready-made Home Assistant automation templates for the GL.iNet integration. These are formatted for the Home Assistant UI automation editor.

## How to Use

1. Open the automation template you want below.
2. Copy the full YAML content.
3. In Home Assistant, go to **Settings → Automations & Scenes → + Create Automation → Create new automation**.
4. Open the automation menu (**⋮**) in the top-right and select **Edit in YAML**.
5. Paste the copied YAML, replacing any existing content.
6. Save.

> [!NOTE]
> All template source files are also available in the [`ha-automations/`](../ha-automations/) directory.

---

## Available Templates

| Template | Description |
|----------|-------------|
| [SMS Notification](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/automation-sms-notification) | Forward incoming SMS from your router to Home Assistant persistent notifications. |

## Related Pages

- [Services & Actions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/services) — How to use Home Assistant services with this integration.
- [Triggers](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/triggers) — Building automations that react to GL.iNet router state.
- [Conditions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/conditions) — Using Home Assistant's built-in conditions on integration entities.
