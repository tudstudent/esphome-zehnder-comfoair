# Optional Accessory Telemetry

Accessory packages are not included in the base configuration. They read PDOs
only; they do not enable accessories, change settings, or control valves/heaters.

## ComfoFond / Ground Heat Exchanger

```yaml
packages:
  comfofond: !include packages/comfofond_telemetry.yml
```

The package extends `comfoair_canbus_id` (default `comfoair_canbus`).

| Reading | PDO | Declared type |
| --- | --- | --- |
| Present | 419 | BOOL |
| Outdoor temperature | 416 | INT16, tenths of a degree C |
| Ground temperature | 417 | INT16, tenths of a degree C |
| State percentage | 418 | UINT8 |

The request order reads presence before the measurements. Unknown or false
presence makes all three measurements unavailable (NaN), including device-supplied
default temperatures. A false presence update immediately invalidates previous
measurements so they cannot remain as stale apparently-valid readings.

No software presence is guessed from temperature values. Malformed presence
frames do not replace the last valid state. Real temperatures/valve operation
require validation on a unit with the accessory installed; absence behavior can
be checked without activating anything.

### KD Absence Validation

On 2026-10-14, KD reported presence `00` (false), outdoor default `70 FE`
(signed -400, or -40 C), ground default `64 00` (100, or 10 C), and state `00`.
All three numeric entities remained NaN rather than exposing these defaults as
real readings. No decoding errors were observed, and Auto/Medium/Normal remained
unchanged. This validates absence handling, not actual accessory operation.

## ComfoCool

There is no verified presence PDO in this mapping. Do not infer installed
hardware from an Off/zero value. The package defaults to disabled: it makes no
ComfoCool read requests and ignores its frames until explicitly configured.

```yaml
substitutions:
  comfocool_installed: "true" # Set only after confirming the actual accessory.
packages:
  comfocool: !include packages/comfocool_telemetry.yml
```

Use the literal strings `"true"` or `"false"` for this substitution. PDOs:
85 (UINT32 next-change timer), 784 (UINT8 Off/On), 785 (BOOL reported compressor
state), 802 (INT16 condenser temperature in tenths of a degree C). There are no
cooling/control commands. Unknown enum values retain numeric text.

The timer is formatted before float publication. Synthetic host fixtures cover
enabled decoding, wrong widths, and invalid BOOL values; disabled and enabled
firmware configurations are included in the build matrix. Actual compressor,
temperature, and timer behavior cannot be hardware-validated on KD without the
accessory. Default sensor values remain unknown, not fabricated absence readings.
