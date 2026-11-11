"""The expressir core surface, one function per C ABI entry point.

Every tier (rust, C, wasm, python) exposes the same six operations
over the model-hash wire JSON; this module is the python projection.
"""

from __future__ import annotations

import json

from ._ffi import call, engine_version, load


def parse_schema(source: str) -> dict:
    """Parses an EXPRESS schema into the model-hash wire JSON."""
    return json.loads(call(load().expr_parse_schema, source))


def attach_remarks(wire: dict | str, source: str, annotations: bool = False) -> dict:
    """Attaches tagged + untagged remarks to a wire."""
    wire_json = wire if isinstance(wire, str) else json.dumps(wire)
    return json.loads(call(load().expr_attach_remarks, wire_json, source, "1" if annotations else "0"))


def format(wire: dict | str, no_remarks: bool = False) -> str:
    """Formats a wire to EXPRESS text."""
    wire_json = wire if isinstance(wire, str) else json.dumps(wire)
    return call(load().expr_format, wire_json, "1" if no_remarks else "0")


def check(wire: dict | str, dialect: str | None = None) -> list:
    """Runs the checker over a wire; returns the findings array."""
    wire_json = wire if isinstance(wire, str) else json.dumps(wire)
    return json.loads(call(load().expr_check, wire_json, dialect))


def parse_population(source: str) -> dict:
    """Parses an ISO-10303-21 population into its structural inventory."""
    return json.loads(call(load().expr_parse_population, source))


def validate_population(entities: list[str], source: str) -> dict:
    """Validates a population's records against an entity inventory."""
    return json.loads(call(load().expr_validate_population, json.dumps(list(entities)), source))


__all__ = [
    "attach_remarks",
    "check",
    "engine_version",
    "format",
    "parse_population",
    "parse_schema",
    "validate_population",
]
