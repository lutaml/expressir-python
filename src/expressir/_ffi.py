"""ctypes binding for the expressir C ABI (libexpressir cdylib).

The C surface is expressir-rs's `expr_*` family (expressir#620): JSON
in, JSON out, NULL on failure with `expr_last_error()` holding the
message, and `expr_string_free` releasing every returned string.
Nothing here interprets wires — that is `expressir.api`'s job.
"""

from __future__ import annotations

import ctypes
import os
from pathlib import Path

_LIB_NAMES = (
    "libexpressir_rs.dylib",
    "libexpressir_rs.so",
    "expressir_rs.dll",  # cargo emits no lib prefix on windows
    "libexpressir_rs.dll",
)


class ExpressirError(RuntimeError):
    """The engine reported a hard error (loading, ABI, NULL input)."""


class ParseFailed(ExpressirError):
    """The engine refused the input; `str()` carries the last error."""


def _candidate_paths() -> list[str]:
    candidates: list[str] = []
    env = os.environ.get("EXPRESSIR_CDYLIB")
    if env:
        candidates.append(env)
    packaged = Path(__file__).resolve().parent / "lib"
    for name in _LIB_NAMES:
        candidates.append(str(packaged / name))
    for name in _LIB_NAMES:
        candidates.append(name)  # system loader search
    return candidates


_lib: ctypes.CDLL | None = None
_version: str | None = None


def load() -> ctypes.CDLL:
    """dlopen the cdylib once and bind the entry points."""
    global _lib, _version
    if _lib is not None:
        return _lib

    errors: list[str] = []
    lib: ctypes.CDLL | None = None
    for candidate in _candidate_paths():
        try:
            lib = ctypes.CDLL(candidate)
            break
        except OSError as error:
            errors.append(f"{candidate}: {error}")
    if lib is None:
        raise ExpressirError(
            "libexpressir_rs not found (build it with `cargo build --release` "
            "in expressir-rs and point EXPRESSIR_CDYLIB at the dylib, or "
            "install a wheel that vendors it). Tried:\n  " + "\n  ".join(errors)
        )

    c_char_p = ctypes.c_char_p
    c_void_p = ctypes.c_void_p

    lib.expr_version.argtypes = []
    lib.expr_version.restype = c_char_p
    lib.expr_last_error.argtypes = []
    lib.expr_last_error.restype = c_char_p
    lib.expr_string_free.argtypes = [c_void_p]
    lib.expr_string_free.restype = None

    for name, arity in (
        ("expr_parse_schema", 1),
        ("expr_attach_remarks", 3),
        ("expr_format", 2),
        ("expr_check", 2),
        ("expr_parse_population", 1),
        ("expr_validate_population", 2),
    ):
        fn = getattr(lib, name)
        fn.argtypes = [c_char_p] * arity
        fn.restype = c_void_p

    _lib = lib
    _version = _borrow(lib.expr_version())
    return lib


def _borrow(ptr: int | None) -> str:
    """Copy a returned C string the engine still owns.

    `expr_version` points into static memory and `expr_last_error`
    into a thread-local slot — freeing those is undefined behavior.
    """
    if not ptr:
        return ""
    return ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")


def _take(ptr: int | None) -> str:
    """Copy a returned C string and release it (the expr_* results)."""
    if not ptr:
        raise ExpressirError(_last_error() or "NULL with no error message")
    try:
        return _borrow(ptr)
    finally:
        load().expr_string_free(ptr)


def _last_error() -> str:
    return _borrow(load().expr_last_error())


def call(fn, *args: str | None) -> str:
    """Run one expr_* function; NULL means failure."""
    encoded = [a.encode("utf-8") if isinstance(a, str) else a for a in args]
    ptr = fn(*encoded)
    if not ptr:
        raise ParseFailed(_last_error() or f"{fn.__name__ if hasattr(fn, '__name__') else 'expr_*'} returned NULL")
    return _take(ptr)


def engine_version() -> str:
    load()
    return _version or ""
