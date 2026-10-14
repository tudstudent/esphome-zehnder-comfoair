# Pressure Discovery: Unidentified PDOs 305 and 306

These channels are experimental and are NOT confirmed pressure measurements.
They are not added to the aiocomfoconnect-derived type inventory or stock package.

The owner reports two likely Sensirion differential-pressure sensors on a Q600
and confirms the internal sensor network, including these sensors, uses I2C.
The exact digital sensor models/ranges and differential port locations remain
unknown. SDP810 remains a candidate; SDP816 is excluded because it is analog.
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

## Manufacturer Datasheet Findings

Verified against Sensirion documentation on 2026-10-14; the installed pressure
sensor model is still unconfirmed. These findings describe the chips, not the
Zehnder CAN representation.

- SDP810 is in the digital SDP8xx family: I2C, differential pressure of air or
  non-aggressive gas, with bidirectional 500 Pa or 125 Pa variants. It measures
  the difference between its two pressure ports, not absolute/barometric pressure.
  The pressure signal is a signed two's-complement integer. Section 6.5 specifies
  division by 60 for the 500 Pa variant or 240 for the 125 Pa variant to obtain Pa.
  It also reports sensor temperature; the datasheet cautions that this is bulk
  silicon temperature, not necessarily the measured air temperature.
  https://sensirion.com/media/documents/90500156/6167E43B/Sensirion_Differential_Pressure_Datasheet_SDP8xx_Digital.pdf
- SDP816 is excluded by the owner's confirmed I2C interface. It is an analog
  SDP8xx sensor, NOT an I2C equivalent of SDP810. Its
  ratiometric voltage represents differential pressure. The OCS pin selects
  linear or square-root output; section 3.1 gives the corresponding conversions
  and ranges. The 500 Pa linear configuration covers -50 to +500 Pa, while the
  square-root configuration is fully bidirectional, -500 to +500 Pa.
  https://sensirion.com/media/documents/68DF0025/6667FEEF/DP_DS_SDP8xx_analog.pdf

Differential pressure can be used to derive airflow with system-specific
calibration. Each installed sensor has its own pair of pressure taps; two sensors
do not establish which taps are on the supply/extract side or whether either
signal represents static duct, fan, or flow-restriction pressure.

Do not divide CAN PDOs 305/306 by 60 or 240, or change them to a signed pressure
type, merely because of these sensor datasheets. The unit can convert, clamp,
temperature-compensate, or re-encode the readings before CAN transmission. The
exact model, port plumbing, CAN units, and signal identity still need evidence.
The confirmed internal I2C interface must not be confused with this ESP32
bridge's external CAN interface: firmware-generated PDOs need not preserve
the sensor's raw I2C words, signedness, or scale factor.

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
