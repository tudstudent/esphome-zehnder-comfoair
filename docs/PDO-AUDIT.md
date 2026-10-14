# Initial PDO Mapping Audit

Static comparison on 2026-10-14. No device API connection or firmware upload was
performed for this audit. This is a baseline inventory, not a complete code
review or a claim that every current handler is hardware-verified.

## Revisions and Coverage

- Local upstream: `d123d47cfcf0b57e79b059266bf4be951156bfae` (2026.10.1).
- aiocomfoconnect: `8fe395b3f8657e25ef8c5a6ccea5aab06808a514`.
- Base handlers in `packages/canbus.yml`: 43 distinct PDO IDs.
- Optional handlers: 226 (`modulated_fan_speed.yml`), 230 (`airflow_constraints.yml`).
- Combined: 45 distinct IDs; 41 of 86 Python registry entries remain unmapped.
- Protocol documentation: 158 IDs, of which 113 lack handlers here.

These counts include partially interpreted IDs: PDO 16 provides an away flag,
not a full device-state entity. Unknown and accessory-specific entries should
not automatically become enabled entities.

## Existing Features to Preserve

- The 1/2/4-byte decoder assembles bytes using explicit `uint32_t` arithmetic
  and sign-extends supported multi-byte signed values.
- Timers 81/82 use a dedicated UINT32 helper; their formatted text handles
  `0xffffffff` as no change without relying on float-state equality.
- Away uses state 7; operating-mode labels include boost, away, and auto.
- Normal/Cool/Warm profile decoding is already present.
- PDO 230 uses a lossless `uint64_t` bitset decoder with the validity bit,
  grouped constraints, CO2 zones, and unknown-bit reporting.
- ESPHome native CAN, optional telemetry, and host regression tests already exist.

## Gaps and Verification Targets

1. Types are mostly selected by handler flags and inferred frame length rather
   than one authoritative PDO definition. The generic decoder accepts any
   1/2/4-byte frame; it does not validate each PDO's expected width. Single-byte
   values are always unsigned, and generic signed 8-byte values are unsupported.
   The dedicated PDO 230 bitset path already handles eight bytes correctly.
2. PDO 212 is inconsistent upstream: protocol docs say UINT8, Python definitions
   say INT16. Confirm actual direct-CAN payloads before deciding the mapping.
3. PDO 213/216 scaling is inconsistent upstream: protocol examples imply /100,
   while Python treats raw values as watts. This project's /1000 to kW agrees
   with Python's units, but the physical scaling remains a verification target.
4. Request validation caps IDs at 1023; documented entries extend through 1304.
   The base CAN receive mask also excludes high-ID patterns. Direct-CAN addressing
   and filtering need verification before high-ID support can be claimed.
5. PDO 119/120 comments in `packages/sensors.yml` are reversed. Actual dispatch
   correctly sends 119 to exhaust and 120 to supply; do not swap working handlers.
6. Fan level 0 is represented by an OFF fan entity despite meaning away. Review
   presentation and compatibility without breaking read-only feedback guards.

## Missing Python Registry Entries

All 41 IDs, grouped for implementation planning:

| Group | PDO IDs |
| --- | --- |
| Filter status, manual and fan modes | 18, 56, 70, 71 |
| Change timers | 85, 86, 87 |
| Preheater energy/power | 144, 145, 146 |
| Pairing and display units | 176, 208, 224 |
| Frost unbalance and overrides/modes | 228, 338, 342, 343 |
| Analog inputs | 369, 370, 371, 372 |
| ComfoFond | 416, 417, 418, 419 |
| ComfoCool | 784, 785, 802 |
| Unknown/uncertain registry fields | 33, 37, 53, 219, 321, 325, 337, 341, 384, 386, 400, 401, 402 |

The remaining documentation-only entries also need explicit classification,
not blind exposure. Pressure readings are not identified by this inventory;
their availability, type, scale, and meaning remain research tasks.

## KD Baseline Caveat

KD's saved YAML declares this repository but has no revision pin and contains
custom inline automations. It advertises ESPHome 2025.8.4. Current upstream fixes
cannot be assumed present in that image, and installing this checkout requires
separate explicit permission. Keep secrets/endpoints outside published evidence.
