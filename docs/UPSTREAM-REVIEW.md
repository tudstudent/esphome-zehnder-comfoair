# Upstream Issues and Pull Requests

Reviewed on 2026-10-14 against upstream `d123d47` (release 2026.10.1).
All seven open issues and the two pre-existing open PRs were reviewed, including
comments and PR diffs. Closed issue/PR titles were inventoried; relevant merged
fixes were checked against the current code. This is not a claim of reproducing
each reporter's installation or reviewing every historical dependency-bump diff.

## Open Issues

| Issue | Relevant Evidence | Result / Our Scope |
| --- | --- | --- |
| [#33 Analog inputs](https://github.com/yoziru/esphome-zehnder-comfoair/issues/33) | OptionBox with two wired CO2 inputs; voltage-to-ppm is sensor-specific; owner offered potentiometer testing. | Our separate [PR #108](https://github.com/yoziru/esphome-zehnder-comfoair/pull/108) adds four voltage readings. Does not close CO2 calibration; nonzero physical testing is still needed. |
| [#45 Fault entity](https://github.com/yoziru/esphome-zehnder-comfoair/issues/45) | Maintainer reports no documented fault PDO. | Not solved. Passive unknown diagnostics can aid observation but no field is labelled as a fault and no fault is deliberately induced. |
| [#46 ControlS conflict](https://github.com/yoziru/esphome-zehnder-comfoair/issues/46) | Wired controller may overwrite commands; reporter has not supplied confirming traffic/disconnection results. | Not solved. Local node is configurable; do not auto-detect nodes or assert an ID collision. KD testing does not reproduce ControlS coexistence. |
| [#53 Away feedback](https://github.com/yoziru/esphome-zehnder-comfoair/issues/53) | Reported logs show feedback triggering Auto cancellation and later Away commands. | Current upstream already contains #96 feedback guards and #98 timer cancellation. Our tests retain these; do not claim a new fix for the entire report. PDO 337 raw bitmask observations are useful corroboration, not proof of all bits. |
| [#59 Restart changes](https://github.com/yoziru/esphome-zehnder-comfoair/issues/59) | Reporter also reproduced without climate; `update_interval: never` helped the profile text sensor. | Current main already uses passive profile updates and startup/feedback guards (#96). Host tests cover climate/no-climate and saved-preference restarts. Our strict decoder rejects malformed feedback; it is not a replacement for those existing guards. |
| [#69 No readings/display error](https://github.com/yoziru/esphome-zehnder-comfoair/issues/69) | No wiring/traffic evidence from reporter; maintainer requests CAN logs. | Not solved. Bounded capture helps distinguish traffic from decoding failures; it cannot fix wiring, termination, or identify a display fault. |
| [#95 OTA encryption](https://github.com/yoziru/esphome-zehnder-comfoair/issues/95) | Encrypted uploader refuses old firmware; install a password-based 2026.9+ intermediate image first. | Separate migration decision, not bundled with telemetry. KD OTA already negotiated encryption. No automatic plaintext fallback or compatibility branch is added. |

## Pre-Existing Open PRs

- [#63 Preheater](https://github.com/yoziru/esphome-zehnder-comfoair/pull/63)
  supplies PDOs 144/145/146, overlapping our optional preheater package. Maintainer
  asks for a rebase onto the shared request-list layout. Keep our package in the
  fork; do not submit a duplicate upstream PR. A fan-plus-preheater sum does not
  measure electronics, bypass motor, or display power. Do not call it verified
  total device power; account for the proposed existing-entity rename explicitly.
- [#68 Waveshare board](https://github.com/yoziru/esphome-zehnder-comfoair/pull/68)
  adds an isolated CAN board, current Device Builder layout, and board-specific
  publishing manifests because AtomS3 and Waveshare share the ESP32-S3 family.
  Author reports the requested cleanup complete. No new PDO mapping is present.
  Do not duplicate board support or access that hardware. Recheck package/CI
  merge conflicts if it lands while our branches are under review.

## Already in Main

- #83 fixes dump-log lifetime; #84 removes a duplicate PDO request; #85 cleans
  command addressing. Our base is already newer than these changes.
- #96 guards startup/fan feedback; #97 adds host/sanitizer framing tests; #98
  cancels temporary overrides on returning to Auto. These are not our new fixes.
- #99 handles unsigned little-endian assembly; #100 preserves UINT32 timers;
  #101 fixes fragment iterators. Strict PDO typing extends these without losing
  exact timer/bitset behavior or bringing back a length/signedness fallback.
- #102-105 already supply optional modulated speed, airflow constraints, filter
  lifetime, and profile modes. Preserve their APIs/tests; do not re-submit them.
- Closed #55 requested preheater power (overlaps #63); historical board/build/
  installer reports are not new protocol evidence. Existing serial-350 reports
  do not authorize adding UART detection to this direct-CAN Q integration.

## Our Submissions

- [#107 Strict types](https://github.com/yoziru/esphome-zehnder-comfoair/pull/107):
  focused decoder/reference block, ready for review; documents the intentional
  three-argument handler API change. Full fork CI passes at `06ad8e1`.
- [#108 Analog inputs](https://github.com/yoziru/esphome-zehnder-comfoair/pull/108):
  independent voltage-only package, ready for review; full fork CI passes at
  `477adc7`, with physical nonzero calibration explicitly unverified.
- Fork integration PR #3 is validation only, not an upstream mega-PR or an
  authorization to merge. Further blocks retain separate scopes/dependencies.

Raw reporter logs, private KD captures, credentials, and endpoints are not copied
into this document. Firmware/Husky research remains parked separately in
`FIRMWARE-READBACK-RESEARCH.md`; no Zehnder firmware/bootloader operations were sent.
