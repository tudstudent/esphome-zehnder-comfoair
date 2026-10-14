# PDO Type Mapping

`components/zehnder_comfoair_q/pdo_mapping.json` records every documented PDO
at a pinned aiocomfoconnect revision, the Python sensor registry's type/unit/
conversion where present, and any reviewed type alternatives. This inventory
does not enable new sensors, change CAN addressing, or poll unknown accessories.

`scripts/generate_pdo_map.py` generates `pdo_types.h` from that data. The runtime
table deliberately contains only IDs and accepted types; labels, units, and
scaling remain in existing YAML entities until a separately reviewed migration.
`pdo_decode.h` handles BOOL, UINT8/16/32, and INT8/16/64 in little-endian form.
All integer and bitset decoding stays in integer form until sensor publication.

The existing four-argument `comfoair_on_frame_case` macro remains source
compatible. Known PDO IDs now use the type table instead of the legacy unsigned
flag and reject incorrect payload lengths without publishing a replacement
state. Custom unregistered PDOs still use the legacy length/flag decoder. New
handlers can call `publish_pdo_state(entity, bytes, pdo_id)` directly.

The legacy `publish_state(entity, bytes, unsigned)` API remains available for
custom code without a PDO ID; it cannot enforce a known PDO's exact width.

## Unresolved Reference Disagreements

- PDO 212 explicitly accepts UINT8 or INT16, because documentation and Python
  disagree. It rejects other widths. Both forms remain raw tenths of a degree.
  A targeted Q600 KD read on 2026-10-14 returned `E9 00` (two bytes, 233), matching
  its displayed 23.3 C value. This confirms the two-byte width on that unit, not
  every hardware variant or the signedness of a positive-only sample.
- PDO 213/216 keep their existing raw-watts interpretation and YAML conversion
  to kW. Documentation examples implying /100 are recorded, not silently applied.
- PDO 69 has no documented type and no registry definition. No type is invented.
- Undocumented PDOs, including pressure-discovery candidates, are not assigned
  meanings or types by this reference import.

## Precision and Coverage

ESPHome numeric states are floats. UINT32/INT64 values may lose precision when
published as numeric sensors; exact text/bitset processing must use integer
values before publication. The duration formatter and PDO 230 constraint path
already follow this rule. A type table entry is not a claim of a reachable CAN
handler: high-ID addressing/filtering and unexposed telemetry are separate work.

## Updating the Reference

```sh
python scripts/sync_pdo_reference.py --check
python scripts/generate_pdo_map.py --check
```

Updating deliberately requires a full upstream commit SHA. The importer reads
documentation and parses the Python AST; it never executes fetched Python code.
Review changes and direct-CAN evidence before accepting a new reference:

```sh
python scripts/sync_pdo_reference.py --revision FULL_COMMIT_SHA
python scripts/generate_pdo_map.py
python -m unittest discover -s tests -p 'test_pdo_mapping.py'
python tests/test_pdo_decode.py
```
