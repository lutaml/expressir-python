"""The C ABI binding tests: load, version, and the six surfaces.

The cdylib is built by CI from the expressir-rs submodule; locally
point EXPRESSIR_CDYLIB at it. Tests skip with the load error message
when the engine is absent.
"""

import json
import pathlib

import pytest

import expressir
from expressir._ffi import ExpressirError, load

SCHEMA = (
    "SCHEMA demo;\n"
    "ENTITY e;\n"
    "  a : STRING;\n"
    "  (*\"demo.e\" the note *)\n"
    "END_ENTITY;\n"
    "END_SCHEMA;\n"
)
POPULATION = (
    "ISO-10303-21;\nHEADER;\nFILE_NAME('x');\nENDSEC;\n"
    "DATA;\n#1=E('v');\nENDSEC;\nEND-ISO-10303-21;\n"
)


def _cdylib_available() -> bool:
    try:
        load()
        return True
    except ExpressirError:
        return False


pytestmark = pytest.mark.skipif(
    not _cdylib_available(),
    reason="libexpressir_rs not built (cargo build --release in expressir-rs; EXPRESSIR_CDYLIB)",
)


def test_engine_version_is_reported():
    assert expressir.engine_version()


def test_parse_schema_returns_the_model_wire():
    wire = expressir.parse_schema(SCHEMA)
    schema = wire["schemas"][0]
    assert schema["id"] == "demo"
    assert schema["entities"][0]["id"] == "e"


def test_attach_format_round_trip():
    wire = expressir.parse_schema(SCHEMA)
    attached = expressir.attach_remarks(wire, SCHEMA)
    text = expressir.format(attached)
    assert "SCHEMA demo;" in text
    stripped = expressir.format(attached, no_remarks=True)
    assert "END_ENTITY;" in stripped


def test_check_returns_a_findings_array():
    wire = expressir.parse_schema(SCHEMA)
    findings = expressir.check(wire)
    assert isinstance(findings, list)


def test_parse_population_inventory():
    inventory = expressir.parse_population(POPULATION)
    keywords = {record["keyword"] for record in inventory["records"]}
    assert keywords == {"E"}


def test_validate_population_verdict():
    verdict = expressir.validate_population(["E"], POPULATION)
    assert verdict["valid"] is True
    bad = expressir.validate_population(["NotE"], POPULATION)
    assert bad["valid"] is False


def test_parse_failure_raises_with_the_last_error():
    with pytest.raises(ExpressirError):
        expressir.parse_schema("not express at all")
