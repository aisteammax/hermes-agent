"""Contract: the ``tool_call`` schema advertises exactly the batches the dispatcher accepts.

Regression guard for the wasted-round-trip class behind upstream #119891: ``calls`` was
described as an unconstrained array, so a two-local-tool batch looked legal, was rejected
wholesale by ``resolve_underlying_call``, and cost a full API round trip every time (10
occurrences in 4 days on one host, all of them two independent read-only lookups).

Red on base: upstream advertises two local entries as valid while the dispatcher rejects
them. When upstream accepts ordered local batches, this test fails again — that is the
signal to drop the fork patch.
"""

from __future__ import annotations

import pytest

_LOCAL = {"name": "web_search_plus", "arguments": {"query": "alpha"}}
_LOCAL_2 = {"name": "web_search_plus", "arguments": {"query": "beta"}}
_CONNECTOR = {"name": "connectors__gmail__SEND_EMAIL", "arguments": {}}
_CONNECTOR_2 = {"name": "connectors__linear__CREATE_ISSUE", "arguments": {}}

_CASES = [
    ("one local", [_LOCAL], True),
    ("one connector", [_CONNECTOR], True),
    ("two connectors", [_CONNECTOR, _CONNECTOR_2], True),
    ("two local", [_LOCAL, _LOCAL_2], False),
    ("mixed local + connector", [_LOCAL, _CONNECTOR], False),
]


def _schema_accepts(calls: list) -> bool:
    """Does the schema the model is shown accept this ``calls`` array?"""
    from jsonschema.validators import validator_for

    from tools.tool_search import bridge_tool_schemas

    schemas = {s["function"]["name"]: s["function"] for s in bridge_tool_schemas(3)}
    schema = {
        "type": "object",
        "properties": {"calls": schemas["tool_call"]["parameters"]["properties"]["calls"]},
        "required": ["calls"],
    }
    validator_cls = validator_for(schema)
    validator_cls.check_schema(schema)
    return validator_cls(schema).is_valid({"calls": calls})


def _dispatcher_rejects_batch(calls: list, monkeypatch) -> bool:
    """Does ``resolve_underlying_call`` reject this array as an unsupported batch?"""
    from tools.connectors.gateway import bridge, config
    from tools.registry import invalidate_check_fn_cache
    from tools.tool_search import resolve_underlying_call

    monkeypatch.setattr(config, "connectors_available", lambda: True)
    monkeypatch.setattr(bridge, "connectors_available", lambda: True)
    invalidate_check_fn_cache()
    _name, _args, error = resolve_underlying_call({"calls": calls})
    return bool(error) and "exactly one entry" in error


@pytest.mark.parametrize("label,calls,supported", _CASES, ids=[c[0] for c in _CASES])
def test_advertised_shape_matches_dispatcher(label, calls, supported, monkeypatch):
    assert _schema_accepts(calls) is supported, f"schema and dispatcher disagree on {label!r}"
    assert _dispatcher_rejects_batch(calls, monkeypatch) is (not supported), (
        f"dispatch behaviour changed for {label!r} — revisit the schema"
    )
