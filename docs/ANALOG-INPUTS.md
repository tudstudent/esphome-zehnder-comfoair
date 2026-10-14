# Optional Analog Inputs

With a local checkout, enable four known analog-input PDOs:

```yaml
packages:
  analog_inputs: !include packages/analog_inputs.yml
```

The package extends `comfoair_canbus_id` (default `comfoair_canbus`). PDOs 369-372
are exactly one-byte UINT8 values, scaled by 0.1 V according to the pinned
aiocomfoconnect registry. Wrong-width frames retain previous readings; no response
remains unknown, not zero. There are no input-priority or ventilation controls.

Voltage-to-CO2 ppm conversion depends on the connected sensor and is not guessed.
KD returned zeros; that tests transport, not calibrated nonzero OptionBox voltage.
Host tests verify nonzero conversion (75 -> 7.5 V), malformed frames, and no writes.
Known-voltage verification by an OptionBox owner remains needed.

Standalone upstream PR #108 is independent of strict-decoder PR #107: its
one-byte handlers validate width explicitly. The integrated package uses the
canonical type table. Both paths enforce UINT8 only, without compatibility logic.

References:
- https://github.com/michaelarnauts/aiocomfoconnect/blob/8fe395b3f8657e25ef8c5a6ccea5aab06808a514/aiocomfoconnect/sensors.py
- https://github.com/yoziru/esphome-zehnder-comfoair/issues/33
- https://github.com/yoziru/esphome-zehnder-comfoair/pull/108
