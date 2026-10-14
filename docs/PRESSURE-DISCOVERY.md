# Pressure Discovery: Unidentified PDOs 305 and 306

These channels are experimental and are NOT confirmed pressure measurements.
They are not added to the aiocomfoconnect-derived type inventory or stock package.

The owner reports two likely Sensirion differential-pressure sensors on a Q600,
possibly SDP810/SDP816; exact models and differential port locations are unknown.
Only the authorized Q600 was accessed. No ducts were blocked, fan balance changed,
or safety mechanisms disabled.

## Observations (2026-10-14)

Both channels appear as spontaneous 2-byte little-endian CAN PDOs. A bounded
Low/Medium/High test used 30 seconds per level, excluding the first 10 seconds
from the summaries below. The final 20-second windows are not guaranteed to have
reached equilibrium; airflow/RPM and raw channels still fluctuate.

| Fan level | Exhaust flow, m3/h | Supply flow, m3/h | PDO 305 raw mean | PDO 306 raw mean |
| --- | ---: | ---: | ---: | ---: |
| Low | 159.87 | 168.38 | 30.00 | 32.80 |
| Medium | 294.85 | 293.93 | 101.50 | 98.86 |
| High | 522.28 | 504.16 | 307.75 | 282.36 |

The channels rise approximately with squared airflow, consistent with a
differential-pressure signal used for airflow measurement/control. This is
supporting evidence, not independent calibration: either value might instead
be a calculated proxy, and balanced fan operation cannot prove side assignment.

The test restored Auto/Medium/Normal. Raw captures contain private API details
and stay outside Git; this table contains only sanitized aggregate observations.

The existing upstream discussion does not establish IDs or a scale:
https://github.com/michaelarnauts/aiocomfoconnect/issues/51

## Optional Raw Package

```yaml
packages:
  raw_candidates: !include packages/unidentified_pressure_candidates.yml
```

The package extends `comfoair_canbus_id` (default `comfoair_canbus`), requests
only the two observed IDs, and exposes the two-byte bit patterns as unsigned
numbers. It assigns no unit, scale, physical side, or device class. The unsigned
presentation is NOT proof that the underlying physical quantity is unsigned;
negative signed values would appear as their corresponding raw bit patterns.
Incorrect frame widths are ignored. There are no control automations.

## Required Before Publishing Pressure Sensors

- Confirm measured pressure versus calculated proxy using an independent reading
  or trustworthy manufacturer/protocol evidence.
- Confirm signedness and scale; positive samples cannot distinguish INT16 from
  UINT16. Do not assume one raw count equals one Pascal.
- Identify each channel's physical differential port/reference arrangement and
  distinguish supply/extract/fan measurements from static duct pressure.
- Confirm behavior at another condition without obstructing ducts or deliberately
  creating an unsafe imbalance; keep tests bounded and restore prior settings.
- Validate applicable unit/firmware variants and record limitations.

Until then these remain diagnostic raw channels, not calibrated Pa sensors.
