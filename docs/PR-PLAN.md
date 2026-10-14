# Reviewable Change Sets

Work is committed locally, not pushed and not submitted upstream. The development
branches are currently stacked so one combined firmware can validate them. Each
functional commit can be reviewed separately; split/rebase onto the chosen
upstream base before opening PRs rather than opening a cumulative mega-PR.

| Change set | Branch | Functional commit | Dependency/scope |
| --- | --- | --- | --- |
| PDO inventory and typed decoders | `feat/pdo-type-mapping` | `e8fa12b` | Pinned data, generated table, converters, exact widths; no new entity defaults |
| Read-only diagnostics | `feat/read-only-diagnostics` | `88c3189` | Command guard and bounded capture; can be adapted independently |
| Core status and timers | `feat/core-pdo-telemetry` | `b105d65` | Requires typed decoding; opt-in status fields, two timers, unique requests |
| Preheater energy/power | `feat/preheater-telemetry` | `80f6294` | Requires typed decoding; independent optional package |
| Analog inputs | `feat/analog-input-telemetry` | `e9728bd` | Requires typed decoding; independent optional package |
| Unidentified pressure candidates | `experiment/unidentified-pressure-pdos` | `42e2e88` | Experimental raw data only; no Pa/side claims |

The development test harness also includes earlier diagnostic helpers, so a
standalone PR may need small test-context adjustments when rebased. Production
package dependencies should not be confused with the current branch ancestry.
Planning notes are in a separate documentation commit (`929f99d`).
The diagnostic capture parser has a small follow-up fix (`81cd411`) to reject
malformed hexadecimal suffixes; include it with the diagnostic change set.

## Validation Boundaries

- All 17 Python inventory, capture, request/schema, and optional-package tests
  pass locally, as do generated-table and pinned upstream-reference checks.
- The production standalone C++ decoders compile/run with MSVC on Windows.
- KD-specific ESP32-C3/ESP-IDF/DM9051 builds, encrypted API reconnection, OTA,
  read-only suppression, optional core readings, and bounded fan changes have
  been exercised on the authorized Q600.
- The combined normal-control image exposes 88 API entities. Preheater and
  analog fields returned device-supplied zeros; active/nonzero inputs have not
  been stimulated. PDO 212 returned a two-byte 233 sample matching 23.3 C.
- The full generated ESPHome host startup/feedback suite and sanitizer jobs are
  extended in CI but have not been run locally: this Windows PC has no usable
  Linux/WSL host environment. Do not describe those as locally passed.
- All RF/factory/seasonal modes, active preheating, counter wraps/resets, accessory
  installations, other units, and calibrated pressure meaning are not all
  hardware-validated. Claims must remain limited to recorded observations.

## Remaining Separate Work

- ComfoFond/ComfoCool accessory packages with availability guards and explicit
  installed-hardware validation; do not fabricate presence or default temperatures.
- Classify the remaining unknown/uncertain Python registry fields and
  documentation-only IDs; retain opt-in raw observation rather than guessed names.
- Verify high-PDO addressing/filtering before expanding the 1023 request limit.
- Resolve reference scaling/width disagreements with direct evidence.
- Establish pressure units, signedness, and physical port/side assignment before
  offering calibrated pressure entities.
