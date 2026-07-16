# SMS Notification

Forward incoming SMS messages from your GL.iNet router to Home Assistant as persistent notifications.

**Source:** [`SMS-Notification.yaml`](../ha-automations/SMS-Notification.yaml)

---

## What It Does

1. Polls for SMS every 30 seconds using a time pattern trigger.
2. Calls `glinet_router.get_sms` to fetch all messages from the router.
3. Filters to **incoming** messages only.
4. For each message, creates a persistent notification showing the sender's phone number and message text.
5. Removes the processed message from the router via `glinet_router.remove_sms`.

---

## How to Install

1. Copy the YAML below.
2. In Home Assistant, go to **Settings → Automations & Scenes → + Create Automation → Create new automation**.
3. Open the automation menu (**⋮**) in the top-right and select **Edit in YAML**.
4. Paste the copied YAML, replacing any existing content.
5. Save.

---

## YAML

```yaml
alias: test
description: ""
triggers:
  - seconds: "30"
    trigger: time_pattern
conditions: []
actions:
  - response_variable: sms_data
    action: glinet_router.get_sms
  - repeat:
      for_each: >-
        {{ sms_data.messages | selectattr('direction', 'eq', 'incoming') | list
        }}
      sequence:
        - data:
            title: 📱 {{ repeat.item.phone_number }}
            message: "{{ repeat.item.text }}"
            data:
              notification_id: sms_{{ repeat.item.id }}
          action: notify.persistent_notification
        - data:
            scope: 10
            message_id: "{{ repeat.item.id }}"
          action: glinet_router.remove_sms
          enabled: true
mode: single
```

## Related Pages

- [Automation Templates](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/automations) — Index of available automation templates.
- [SMS](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/sms) — SMS feature reference.
