# Experimental Pressure GET Reader

This opt-in debug facility sends only the documented RMI GET operation `01` to
fixed unit `23` (PRESSURESENSOR), subunit 1 or 2, actual-value flag `10`.
An explicitly selected property must be 1-16. The documentation identifies the
unit but not individual property meanings; responses remain raw research data.

It cannot send SET, factory, firmware/FUP, erase, reset, or arbitrary node/unit
commands. It remains available under the CAN read-only guard. Only one read may
be pending, with a 2.5-second timeout; normal user control cancels a pending read
and takes priority so sequence wrap cannot confuse control acknowledgments.

Responses must match an extended non-RTR RMI reply from the known Q node 1 to
the configured local node, with the expected sequence. Request echoes, firmware
frames, other nodes/recipients/sequences are ignored. Fragment ordering and error
consistency are checked; responses are bounded to 256 bytes. No type, scale,
pressure unit, or sensor meaning is inferred from a returned byte count.

Expose the fixed helper in a private debug configuration:

```yaml
api:
  custom_services: true
  actions:
    - action: read_pressure_property_debug
      variables:
        subunit: int
        property: int
      then:
        - lambda: |-
            if (!id(comfoair)->request_pressure_property(subunit, property))
              ESP_LOGW("pressure_rmi", "Read rejected (busy or out of scope)");
```

After identity verification, request an explicit small property list:

```sh
python -m scripts.capture_pressure_properties --config /private/device.yaml \
  --device AUTHORIZED_HOST --expected-name EXACT_DEVICE_NAME \
  --property 3 --output /private/pressure-get.json
```

The tool does no discovery, controls, reset, or firmware operations. It preserves
error/timeout responses and writes private raw bytes, not guessed Pa readings.
A timeout does not prove a property is absent. Do not expand the scope into a
generic command scanner. Remove the debug API action when research is complete.

## KD Results

The fixed GET path was exercised on KD on 2026-10-14, with no setting writes:
subunits 1 and 2 each return `01` for properties 1 and 2. Properties 3-16 each
return the protocol's explicit error flag with payload `0E` (Unknown property).
All 32 selected reads completed with matching replies, not timeouts.

This validates the scoped transport, response addressing/sequence, and error
handling. It does not identify the meaning of the two one-byte values or prove
that dynamic pressure/scaling is available through these property IDs. No
undocumented command IDs, mode switches, firmware operations, or factory commands
were attempted. Further investigation must not simply enlarge a blind scan.
