# Read-Only Diagnostics

To observe device-owned states without permitting ventilation commands:

```yaml
zehnder_comfoair_q:
  read_only: true
```

The default is `false`, preserving existing control behavior. When enabled,
`send_command` blocks all setting/timer writes, including those invoked by YAML
automations or startup restoration. PDO requests, CAN reception, API access,
and OTA still work. This is a CAN-command safety guard, not a firewall or an
API permission system. Optimistic control entities may still display requested
states even though their writes are suppressed; actual PDO feedback is the
authoritative device state.

The guard does not authorize OTA: get permission before installing diagnostic
firmware. Preserve the working hardware/network configuration and credentials.

## Capture Existing Logs Without New Firmware

With an explicit authorized endpoint, exact device name, and local API YAML:

```sh
python scripts/capture_pdos.py --config /private/device.yaml \
  --device AUTHORIZED_HOST --expected-name EXACT_DEVICE_NAME \
  --seconds 30 --output /private/capture.json
```

The tool reads the API key/password locally, supports `!secret`, verifies the
connected device name, and subscribes only to entity states and DEBUG logs. It
does not discover devices, call controls, request a reboot, dump configuration,
or upload firmware. Time synchronization responses are disabled.

`--pdo ID` can be repeated to filter the captured frames. Captures are bounded
to 300 seconds and 20,000 frames, and existing output files are not overwritten.
Raw API state captures may contain private identifiers/values: keep them out of
Git. Sanitize individual fixtures separately before publication.

The parser expects the existing `comfoair_dump` log format and ignores malformed
payloads/length mismatches. It cannot see PDO traffic the firmware does not log,
and inferred unsigned raw values are not a verified protocol type or unit.

Pressure research must retain unknown labels until type, scale, physical meaning,
and readout behavior are verified. Correlation with fan speed alone does not
prove a value is pressure or establish a Pascal conversion.
