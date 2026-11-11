# expressir-python

Python runtime for [Expressir](https://github.com/lutaml/expressir):
EXPRESS schema parse, remark attach, format, check, and the
ISO 10303-21 population — through the [expressir-rs](https://github.com/lutaml/expressir-rs)
C ABI, the same engine the ruby, rust, wasm, and TypeScript runtimes use.

```python
import expressir

wire = expressir.parse_schema("SCHEMA demo; ENTITY e; a : STRING; END_ENTITY; END_SCHEMA;")
attached = expressir.attach_remarks(wire, source)
print(expressir.format(attached))

inventory = expressir.parse_population("ISO-10303-21; ...;")
verdict = expressir.validate_population(["E"], population_source)
```

## Development

```sh
git clone --recurse-submodules https://github.com/lutaml/expressir-python
cd expressir-python
(cd expressir-rs && cargo build --release)
EXPRESSIR_CDYLIB=$PWD/expressir-rs/target/release/libexpressir_rs.dylib \
  python3 -m pip install -e . pytest && python3 -m pytest tests -q
```

## Architecture

One core (`expressir-rs`), many tiers: rust (this ABI's home), C
(`expr_*` family), wasm (`expressir-ts`), ruby (`expressir`), and
python (here). Every tier exposes the same six operations over the
model-hash wire JSON. See [expressir.org](https://expressir.org).
