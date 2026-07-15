from __future__ import annotations

from typing import Any

from custom_components.glinet_router.api.client import GLinetApiClient
from custom_components.glinet_router.api.const import FIRMWARE_4_9
from custom_components.glinet_router.api.modules.modem import (
    ModemModule,
    _index_networks_by_bus_slot,
    _target_lookup_key,
)
from tests.test_api_client import FakeSession


def _make_module(responses: list[Any]) -> tuple[ModemModule, FakeSession]:
    session = FakeSession(responses)
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    client._firmware_version = FIRMWARE_4_9
    return client.modem, session


def test_target_lookup_key_coerces_slot_to_string() -> None:
    assert _target_lookup_key({"bus": "0001:01:00.0", "slot": 1}) == (
        "0001:01:00.0",
        "1",
    )
    assert _target_lookup_key({"bus": "0001:01:00.0", "slot": "2"}) == (
        "0001:01:00.0",
        "2",
    )
    assert _target_lookup_key({"bus": "0001:01:00.0"}) == ("0001:01:00.0", "")


def test_index_networks_by_bus_slot_indexes_list_payload() -> None:
    response = {
        "ret": 0,
        "resp": "Success",
        "networks": [
            {
                "network_interface": "modem_0001_s1",
                "bus": "0001:01:00.0",
                "slot": "1",
                "ipv4": {"ip": "10.77.58.41", "gateway": "10.77.58.42"},
            },
            {
                "network_interface": "modem_0001_s2",
                "bus": "0001:01:00.0",
                "slot": "2",
                "ipv4": {"ip": "10.77.58.45"},
            },
        ],
    }

    indexed = _index_networks_by_bus_slot(response)

    assert set(indexed) == {("0001:01:00.0", "1"), ("0001:01:00.0", "2")}
    assert indexed[("0001:01:00.0", "1")]["ipv4"]["ip"] == "10.77.58.41"
    assert indexed[("0001:01:00.0", "2")]["ipv4"]["ip"] == "10.77.58.45"


def test_index_networks_by_bus_slot_handles_bare_dict_payload() -> None:
    indexed = _index_networks_by_bus_slot(
        {
            "bus": "0001:01:00.0",
            "slot": "1",
            "ipv4": {"ip": "10.77.58.41"},
        }
    )

    assert indexed == {
        ("0001:01:00.0", "1"): {"bus": "0001:01:00.0", "slot": "1", "ipv4": {"ip": "10.77.58.41"}}
    }


def test_index_networks_by_bus_slot_skips_records_without_bus_or_slot() -> None:
    indexed = _index_networks_by_bus_slot(
        {
            "networks": [
                {"bus": "0001:01:00.0", "slot": "1"},
                {"slot": "2"},  # missing bus
                {"bus": "0001:01:00.0"},  # missing slot
            ]
        }
    )

    assert indexed == {("0001:01:00.0", "1"): {"bus": "0001:01:00.0", "slot": "1"}}


async def test_get_status_49_uses_bodyless_network_calls() -> None:
    targets_response = {"interfaces": ["modem_0001_s1"]}
    signals_response = {"signals": [{"slot": "1", "strength": 70, "timestamp": 1}]}
    network_status_response = {
        "ret": 0,
        "resp": "Success",
        "networks": [
            {
                "bus": "0001:01:00.0",
                "slot": "1",
                "status": 0,
                "iccid": "12345",
                "protocol": "ipv4",
            }
        ],
    }
    network_info_response = {
        "ret": 0,
        "resp": "Success",
        "networks": [
            {
                "network_interface": "modem_0001_s1",
                "bus": "0001:01:00.0",
                "slot": "1",
                "ipv4": {
                    "ip": "10.77.58.41",
                    "gateway": "10.77.58.42",
                    "netmask": "255.255.255.252",
                },
                "ipv6": {"ip": "2001:db8::42"},
                "cell_info": {"mode": "NR5G-NSA", "band": 78},
            }
        ],
    }

    modem, session = _make_module(
        [
            {"result": targets_response},
            {"result": signals_response},
            {"result": network_status_response},
            {"result": network_info_response},
        ]
    )

    result = await modem.get_status()

    assert len(result["modems"]) == 1
    modem_record = result["modems"][0]
    assert modem_record["bus"] == "0001:01:00.0"
    assert modem_record["slot"] == "1"
    assert modem_record["network"]["ipv4"]["ip"] == "10.77.58.41"
    assert modem_record["network"]["ipv6"]["ip"] == "2001:db8::42"
    assert modem_record["network_interface"] == "modem_0001_s1"

    network_status_call = session.requests[2]
    network_info_call = session.requests[3]
    assert network_status_call["json"]["params"] == [
        "sid-1",
        "call",
        ["modem", "get_network_status", {}],
    ]
    assert network_info_call["json"]["params"] == [
        "sid-1",
        "call",
        ["modem", "get_network_info", {}],
    ]


async def test_get_status_49_picks_correct_entry_per_target() -> None:
    targets_response = {"interfaces": ["modem_0001_s1", "modem_0001_s2"]}
    signals_response = {"signals": []}
    network_status_response = {
        "ret": 0,
        "resp": "Success",
        "networks": [
            {"bus": "0001:01:00.0", "slot": "1", "status": 0, "iccid": "AAA"},
            {"bus": "0001:01:00.0", "slot": "2", "status": 0, "iccid": "BBB"},
        ],
    }
    network_info_response = {
        "ret": 0,
        "resp": "Success",
        "networks": [
            {
                "bus": "0001:01:00.0",
                "slot": "1",
                "network_interface": "modem_0001_s1",
                "ipv4": {"ip": "10.77.58.41"},
            },
            {
                "bus": "0001:01:00.0",
                "slot": "2",
                "network_interface": "modem_0001_s2",
                "ipv4": {"ip": "10.77.58.49"},
            },
        ],
    }

    modem, _ = _make_module(
        [
            {"result": targets_response},
            {"result": signals_response},
            {"result": network_status_response},
            {"result": network_info_response},
        ]
    )

    result = await modem.get_status()
    modems_by_slot = {m["slot"]: m for m in result["modems"]}

    assert modems_by_slot["1"]["network"]["ipv4"]["ip"] == "10.77.58.41"
    assert modems_by_slot["2"]["network"]["ipv4"]["ip"] == "10.77.58.49"
    assert modems_by_slot["1"]["network_interface"] == "modem_0001_s1"
    assert modems_by_slot["2"]["network_interface"] == "modem_0001_s2"


async def test_get_status_49_falls_back_to_per_target_call() -> None:
    targets_response = {"interfaces": ["modem_0001_s1"]}
    signals_response = {"signals": []}
    empty_bodyless = {"ret": 0, "resp": "Success", "networks": []}
    fallback_status = {
        "ret": 0,
        "resp": "Success",
        "networks": [
            {"bus": "0001:01:00.0", "slot": "1", "status": 0, "iccid": "ZZZ"},
        ],
    }
    fallback_info = {
        "ret": 0,
        "resp": "Success",
        "networks": [
            {"bus": "0001:01:00.0", "slot": "1", "ipv4": {"ip": "10.77.58.99"}},
        ],
    }

    modem, session = _make_module(
        [
            {"result": targets_response},
            {"result": signals_response},
            {"result": empty_bodyless},
            {"result": empty_bodyless},
            {"result": fallback_status},
            {"result": fallback_info},
        ]
    )

    result = await modem.get_status()
    assert len(result["modems"]) == 1
    assert result["modems"][0]["network"]["ipv4"]["ip"] == "10.77.58.99"

    per_target_status = session.requests[4]
    assert per_target_status["json"]["params"][2] == [
        "modem",
        "get_network_status",
        {"bus": "0001:01:00.0", "slot": "1"},
    ]


def test_bus_aliases_expand_pci_to_short_form() -> None:
    from custom_components.glinet_router.api.modules.modem import _bus_aliases

    assert _bus_aliases("0001:01:00.0") == ["0001:01:00.0", "0001", "0001:01:00"]
    assert _bus_aliases("0001-0200.0") == ["0001-0200.0", "0001-0200"]
    assert _bus_aliases("0001") == ["0001"]
    assert _bus_aliases("") == [""]


def test_targets_from_interface_handles_short_bus_form() -> None:
    from custom_components.glinet_router.api.modules.modem import _targets_from_interface

    assert _targets_from_interface("modem_0001_s1") == [{"bus": "0001", "slot": 1}]
    assert _targets_from_interface("modem_0001_0200_0_s1") == [{"bus": "0001-0200.0", "slot": 1}]


async def test_get_status_49_resolves_ip_when_bus_uses_short_form() -> None:
    targets_response = {"interfaces": ["modem_0001_s1"]}
    signals_response = {"signals": []}
    network_status_response = {
        "ret": 0,
        "resp": "Success",
        "networks": [
            {
                "traffic_total": "2515490956",
                "protocol": "qcm",
                "slot": "1",
                "iccid": "8944200204977051694F",
                "dial_status": 0,
                "call_reason": "Success",
                "bus": "0001:01:00.0",
                "callcode": 0,
                "status": 0,
                "calltype": 0,
            }
        ],
    }
    network_info_response = {
        "ret": 0,
        "resp": "Success",
        "networks": [
            {
                "network_interface": "modem_0001_s1",
                "bus": "0001:01:00.0",
                "ip_type": 1,
                "slot": "1",
                "cell_info": {
                    "band": 78,
                    "type": "servingcell",
                    "rsrp_level": 4,
                    "sinr": "22",
                    "tx_channel": "",
                    "rsrq_level": 4,
                    "rsrq": "-10",
                    "dl_bandwidth": "100MHz",
                    "mode": "NR5G-NSA",
                    "sinr_level": 4,
                    "rsrp": "-86",
                },
                "network_mode": "AUTO",
                "mtu_sync": 0,
                "ipv4": {
                    "netmask": "255.255.255.252",
                    "gateway": "10.77.58.42",
                    "dns": ["188.31.250.128", "188.31.250.129"],
                    "ip": "10.77.58.41",
                },
            }
        ],
    }

    modem, _ = _make_module(
        [
            {"result": targets_response},
            {"result": signals_response},
            {"result": network_status_response},
            {"result": network_info_response},
        ]
    )

    result = await modem.get_status()
    assert len(result["modems"]) == 1
    modem_record = result["modems"][0]
    assert modem_record["network"]["ipv4"]["ip"] == "10.77.58.41"
    assert modem_record["bus"] == "0001:01:00.0"
    assert modem_record["slot"] == "1"
    assert modem_record["network_interface"] == "modem_0001_s1"


async def test_get_sim_config_calls_endpoint_with_bus() -> None:
    expected = {
        "8944200204977051694F": {
            "manual": True,
            "username": "",
            "pincode": "",
            "ip_type": 1,
            "cid": 1,
            "roaming": False,
            "apn": "mob.asm.net",
            "password": "",
            "auth": "NONE",
        }
    }

    modem, session = _make_module([{"result": expected}])

    result = await modem.get_sim_config("0001:01:00.0")

    assert result == expected
    request = session.requests[0]
    assert request["json"]["params"] == [
        "sid-1",
        "call",
        ["modem", "get_sim_config", {"bus": "0001:01:00.0"}],
    ]


async def test_get_sms_list_49_uses_full_pci_bus() -> None:
    targets_response = {"interfaces": ["modem_0001_s1"]}
    signals_response = {"signals": []}
    network_status_response = {
        "ret": 0,
        "resp": "Success",
        "networks": [
            {
                "bus": "0001:01:00.0",
                "slot": "1",
                "iccid": "8944200204977051694F",
                "status": 0,
            }
        ],
    }
    network_info_response = {
        "ret": 0,
        "resp": "Success",
        "networks": [
            {
                "network_interface": "modem_0001_s1",
                "bus": "0001:01:00.0",
                "slot": "1",
                "ipv4": {"ip": "10.77.58.41"},
            }
        ],
    }
    sms_response = {
        "list": [
            {
                "name": "GMS1.gcKIin",
                "phone_number": "447587541306",
                "body": "Hello",
                "status": 0,
                "date": "26-07-15 13:48:50",
                "bus": "0001:01:00.0",
                "slot": 1,
            }
        ]
    }

    modem, session = _make_module(
        [
            {"result": targets_response},
            {"result": signals_response},
            {"result": network_status_response},
            {"result": network_info_response},
            {"result": sms_response},
        ]
    )

    result = await modem.get_sms_list()

    assert len(result) == 1
    assert result[0]["body"] == "Hello"
    assert result[0]["phone_number"] == "447587541306"

    sms_call = session.requests[4]
    assert sms_call["json"]["params"] == [
        "sid-1",
        "call",
        ["modem", "get_sms_list", {"bus": "0001:01:00.0"}],
    ]


async def test_get_sms_list_49_falls_back_to_short_bus_when_no_network_info() -> None:
    targets_response = {"interfaces": ["modem_0001_s1"]}
    signals_response = {"signals": []}
    empty_bodyless = {"ret": 0, "resp": "Success", "networks": []}
    sms_response = {
        "list": [
            {
                "name": "GMS1.gcKIin",
                "phone_number": "447587541306",
                "body": "Hello",
                "status": 0,
                "date": "26-07-15 13:48:50",
            }
        ]
    }

    modem, _ = _make_module(
        [
            {"result": targets_response},
            {"result": signals_response},
            {"result": empty_bodyless},
            {"result": empty_bodyless},
            {"result": sms_response},
        ]
    )

    result = await modem.get_sms_list()

    assert len(result) == 1
    assert result[0]["body"] == "Hello"


def test_send_sms_coerces_string_slot_to_int() -> None:
    """Firmware 4.9+ only tags the sent message with the SIM when
    ``slot`` is an integer. The bodyless ``get_network_status`` response
    surfaces it as a string, so the integration must coerce it.
    """

    async def run() -> None:
        modem, session = _make_module(
            [
                {"result": {"ret": 0, "resp": "Success"}},
            ]
        )
        await modem.send_sms(
            "0001:01:00.0",
            "+447587541306",
            "Test Message",
            slot="1",
        )

        last_request = session.requests[-1]
        params = last_request["json"]["params"]
        assert params[2] == "send_sms"
        assert params[3]["bus"] == "0001:01:00.0"
        assert params[3]["slot"] == 1
        assert isinstance(params[3]["slot"], int)

    import asyncio

    asyncio.run(run())


def test_send_sms_passes_int_slot_unchanged() -> None:
    async def run() -> None:
        modem, session = _make_module(
            [
                {"result": {"ret": 0, "resp": "Success"}},
            ]
        )
        await modem.send_sms(
            "0001:01:00.0",
            "+447587541306",
            "Test Message",
            slot=1,
        )

        last_request = session.requests[-1]
        params = last_request["json"]["params"]
        assert params[3]["slot"] == 1
        assert isinstance(params[3]["slot"], int)

    import asyncio

    asyncio.run(run())


def test_send_sms_omits_slot_when_none() -> None:
    async def run() -> None:
        modem, session = _make_module(
            [
                {"result": {"ret": 0, "resp": "Success"}},
            ]
        )
        await modem.send_sms(
            "0001:01:00.0",
            "+447587541306",
            "Test Message",
        )

        last_request = session.requests[-1]
        params = last_request["json"]["params"]
        assert "slot" not in params[3]

    import asyncio

    asyncio.run(run())


def test_remove_sms_does_not_send_slot_field() -> None:
    async def run() -> None:
        modem, session = _make_module(
            [
                {"result": {"ret": 0, "resp": "Success"}},
            ]
        )
        await modem.remove_sms(
            "0001:01:00.0",
            scope=10,
            message_id="GMS1.gcKIin",
        )

        last_request = session.requests[-1]
        params = last_request["json"]["params"]
        assert params[2] == "remove_sms"
        assert params[3]["bus"] == "0001:01:00.0"
        assert params[3]["scope"] == 10
        assert params[3]["name"] == "GMS1.gcKIin"
        assert "slot" not in params[3]

    import asyncio

    asyncio.run(run())


def test_remove_sms_omits_name_when_no_message_id() -> None:
    async def run() -> None:
        modem, session = _make_module(
            [
                {"result": {"ret": 0, "resp": "Success"}},
            ]
        )
        await modem.remove_sms(
            "0001:01:00.0",
            scope=0,
        )

        last_request = session.requests[-1]
        params = last_request["json"]["params"]
        assert params[2] == "remove_sms"
        assert params[3] == {"bus": "0001:01:00.0", "scope": 0}

    import asyncio

    asyncio.run(run())
