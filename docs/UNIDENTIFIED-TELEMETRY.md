# Passive Unidentified Telemetry

All unnamed registry fields have declared types, but their physical meanings
are not all established. The optional package exposes decoded integer text for
the 13 reviewed IDs without guessing those meanings:

```yaml
packages:
  unidentified: !include packages/unidentified_telemetry.yml
```

IDs: 33, 37, 53, 219, 321, 325, 337, 341, 384, 386, 400, 401, 402.

- No read requests are added, including at boot. Observe spontaneous frames or
  perform an explicitly bounded targeted read through separate diagnostics.
- Entities are diagnostic and disabled by default in Home Assistant.
- Integers use the one canonical declared type; wrong widths/invalid BOOL values
  cannot replace a valid state. There are no type alternatives or length inference.
- Text preserves all UINT32 bits without converting through an ESPHome float.
- Values remain decoded, unscaled integers. For example, INT16 `70 FE` is `-400`,
  not asserted to be a measured -40 C temperature. No units are assigned.
- Presence, accessory location, or hardware availability is not invented from
  default values. The labels intentionally describe data, not a physical sensor.

The package is generated from the pinned type inventory and an explicit reviewed
ID list. Check it with `python scripts/generate_unidentified_telemetry.py --check`.
Its classification rationale and tentative external labels are documented in
`ADDITIONAL-PROTOCOL-EVIDENCE.md`; PDO 337 manual bits have local evidence, but the
passive package deliberately does not promote all possible bit meanings.
