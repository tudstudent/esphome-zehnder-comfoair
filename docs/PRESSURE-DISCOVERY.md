# Pressure Discovery: Unidentified PDOs 305 and 306

These channels are experimental and are NOT confirmed pressure measurements.
They are not added to the aiocomfoconnect-derived type inventory or stock package.

The owner reports two Sensirion differential-pressure sensors and confirms the
internal sensor network, including pressure sensors, uses I2C. The inspected
older pressure PCB is marked `SDP511-500Pa`. Its identity must not automatically
be attributed to every unit or hardware revision; KD's exact installed marking
and the pressure-tap locations still need confirmation. SDP8xx on newer units is
an owner hypothesis. Analog SDP816 is excluded by the confirmed I2C interface.
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

### Identified Older Sensor: SDP511-500Pa

Sensirion's SDP600 Series datasheet explicitly covers SDP6xx/5xx. It identifies
SDP511 as an I2C tube-connected, low-cost mass-flow-temperature-compensated
differential-pressure sensor. Its calibrated range is 0 to +500 Pa. The datasheet
notes that SDP5xx can also report negative differential pressure, but its accuracy
in that range is unspecified.

Section 2 gives the standard SDP5xx scale factor as 60 counts/Pa (with a note that
other configurations can differ). Section 5.1 specifies signed two's-complement
output. The standard sensor-level conversion is therefore `DP = signed_raw / 60`.
Section 5.3 explains that the output is still differential pressure, but its
temperature compensation is adapted for mass-flow measurement. It is not simply
an absolute-pressure sensor or a direct airflow reading.

https://sensirion.com/media/documents/63859DD0/6166CF0E/Sensirion_Differential_Pressure_Datasheet_SDP600Series.pdf

Sensirion's January 2026 discontinuation notice lists SDP511 and states that
**SDP611-500Pa is its drop-in replacement**. The SDP800 family is mechanically
equivalent but has a **different I2C command set**; it is not a command-compatible
drop-in replacement. Internal firmware/board changes must be distinguished from
the separate question of whether Zehnder retains the same CAN PDO representation.

https://sensirion.com/media/documents/414C6E44/698330CD/Sensirion_Differential_Pressure_SDP5xx_PTN260201_EOL.pdf

### Possible Newer Digital Sensors

Verified against Sensirion documentation on 2026-10-14; the installed pressure
sensor model in KD is still unconfirmed. These findings describe the chips, not
the Zehnder CAN representation.

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
type, merely because of these sensor datasheets or the older PCB marking. The unit can convert, clamp,
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
