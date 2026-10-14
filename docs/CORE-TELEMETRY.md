# Optional Core Telemetry

The stock package remains unchanged. With a local checkout, add these packages
to enable additional status fields and supply/exhaust fan countdowns:

```yaml
packages:
  core_status: !include packages/core_telemetry.yml
  fan_timers: !include packages/fan_timers.yml
```

Both extend the CAN bus identified by the `comfoair_canbus_id` substitution,
defaulting to `comfoair_canbus`. Override it for an existing custom bus ID.
They append PDO requests and use existing polling delays. Duplicate request
IDs are removed while preserving order, including PDO 16 already in the base.

| Field | PDO | Type |
| --- | --- | --- |
| Complete device state | 16 | UINT8 |
| Filter-changing status | 18 | UINT8 |
| Manual-mode status | 56 | UINT8 |
| Supply/exhaust mode settings | 70, 71 | UINT8 |
| Supply/exhaust change timers | 86, 87 | UINT32 |
| RF pairing status | 176 | UINT8 |
| Display temperature/airflow units | 208, 224 | UINT8 |
| Frost-protection unbalance, raw | 228 | UINT8 |
| Bypass override status | 338 | UINT32 |
| Supply/exhaust override status | 342, 343 | UINT32 |

These diagnostic entities contain no control actions or state-synchronization
automations. Full device state complements the existing away flag rather than
replacing it. Fan mode representations are kept distinct: PDOs 54/55 use 255
for balanced, 70/71 use 0, and 342/343 use 0 with 2 for the corresponding override.

Unrecognized enum values remain numeric text instead of being falsely assigned
to a known mode. PDO 228 remains raw/unscaled because its exact meaning/unit is
uncertain. Display-unit fields do not automatically change measurement labels
or scale other sensors.

Timers are formatted from exact UINT32 values before numeric publication;
`0xffffffff` means `n/a`. The internal numeric timer can lose precision at large
values and is not used to determine that sentinel.

RF pairing or other states not exercised on the test hardware need separate
validation. Reading a field is not authorization to start pairing, change
filters, or activate a fan-mode override.
