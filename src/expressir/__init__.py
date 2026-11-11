"""expressir — Python runtime for the EXPRESS/Part-21 core.

Drives the expressir-rs engine through its C ABI: schema parse,
remark attach, format, check, and the ISO 10303-21 population — the
same engine the ruby, rust, wasm, and TypeScript runtimes use.
"""

from ._ffi import ExpressirError, ParseFailed, engine_version, load
from .api import (
    attach_remarks,
    check,
    format,
    parse_population,
    parse_schema,
    validate_population,
)

try:
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version("expressir")
except PackageNotFoundError:  # running from a source checkout
    __version__ = "0.0.0.dev0"

__all__ = [
    "ExpressirError",
    "ParseFailed",
    "attach_remarks",
    "check",
    "engine_version",
    "format",
    "load",
    "parse_population",
    "parse_schema",
    "validate_population",
    "__version__",
]
