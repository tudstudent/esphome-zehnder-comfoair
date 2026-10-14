# Reviewable Change Sets

The owner approved starting fork pushes/upstream submissions on 2026-10-14.
The development branches are stacked so one combined firmware can validate them. Each
functional commit can be reviewed separately; split/rebase onto the chosen
upstream base before opening PRs rather than opening a cumulative mega-PR.
The owner confirms this workflow: build on our integrated work during development,
then provide a separate PR for each main block so reviewers can choose their own
acceptance order and integration approach. Keep necessary dependencies explicit.

| Change set | Branch | Functional commit | Dependency/scope |
| --- | --- | --- | --- |
| PDO inventory and typed decoders | `feat/pdo-type-mapping` | `e8fa12b` | Pinned data, generated table, converters, exact widths; no new entity defaults |
| Read-only diagnostics | `feat/read-only-diagnostics` | `88c3189` | Command guard and bounded capture; can be adapted independently |
| Core status and timers | `feat/core-pdo-telemetry` | `b105d65` | Requires typed decoding; opt-in status fields, two timers, unique requests |
| Preheater energy/power | `feat/preheater-telemetry` | `80f6294` | Requires typed decoding; independent optional package |
| Analog inputs | `feat/analog-input-telemetry` | `e9728bd` | Requires typed decoding; independent optional package |
| Unidentified pressure candidates | `experiment/unidentified-pressure-pdos` | `42e2e88` | Experimental raw data only; no Pa/side claims |
| Strict-type cleanup | `refactor/strict-pdo-types` | `b484dd3` | Required cleanup: one type per PDO, three-argument handlers, explicit raw representation; no compatibility paths |
| ComfoFond telemetry | `feat/comfofond-telemetry` | `d2173af` | Independent optional package, strict types, presence-gated availability; absence validated on KD |
| ComfoCool telemetry | `feat/comfocool-telemetry` | `f6bda14` | Explicit installation declaration, enabled/disabled host variants; no cooling controls |
| Passive unidentified entries | `feat/unidentified-pdo-diagnostics` | `2226bcd` | Thirteen unscaled integer-text fields; no startup reads or physical labels |
| Pressure GET experiment | `experiment/pressure-property-reads` | `173c371`, `636e51a` | Fixed GET/unit/subunits, bounded replies; KD results documented without scale |
| High-PDO addressing | `fix/extended-pdo-addressing` | `0529d22`, `736f499` | Eleven PDO bits, namespace filtering, KD 1304 reception; no new startup reads |

## Submitted Independent Blocks

| Block | Branch / Commit | Upstream | Passing Fork CI |
| --- | --- | --- | --- |
| Strict PDO types | `pr/strict-pdo-types` / `06ad8e1` | [#107](https://github.com/yoziru/esphome-zehnder-comfoair/pull/107), ready | [38605529783](https://github.com/tudstudent/esphome-zehnder-comfoair/actions/runs/38605529783) |
| Analog voltage inputs | `pr/analog-inputs` / `477adc7` | [#108](https://github.com/yoziru/esphome-zehnder-comfoair/pull/108), ready | [38606668903](https://github.com/tudstudent/esphome-zehnder-comfoair/actions/runs/38606668903) |

Both start directly from upstream main, not the full stack. The analog block
validates UINT8/one-byte payloads explicitly and therefore does not require #107.
Fork PRs #1/#2 are test mirrors; #3 exercises `integration/kd-development` only.
No PR is merged automatically. Further upstream submissions stay independent.
Preheater already overlaps upstream PR #63, so do not submit a competing copy.

Do not submit the earlier type-mapping branch as-is: it contained compatibility
paths that the strict cleanup removes. Fold the final strict implementation into
the type-mapping PR and distribute its mechanical consumer updates across their
respective PRs. Compatibility behavior is not an optional feature to retain.

The development test harness also includes earlier diagnostic helpers, so a
standalone PR may need small test-context adjustments when rebased. Production
package dependencies should not be confused with the current branch ancestry.
Planning notes are in a separate documentation commit (`929f99d`).
The diagnostic capture parser has a small follow-up fix (`81cd411`) to reject
malformed hexadecimal suffixes; include it with the diagnostic change set.

## Validation Boundaries

- All 26 Python inventory, capture, request/schema, and optional-package tests
  pass locally, as do generated-table and pinned upstream-reference checks.
- The production standalone C++ decoders compile/run with MSVC on Windows.
- KD-specific ESP32-C3/ESP-IDF/DM9051 builds, encrypted API reconnection, OTA,
  read-only suppression, optional core readings, and bounded fan changes have
  been exercised on the authorized Q600.
- The latest implementation is built/uploaded and checked on KD: 109 entities,
  target 23.3 C, valid no-change timers, raw candidate readings, Auto/Medium/Normal,
  and no decoding errors. PDO 212 accepts only its declared two-byte INT16 type.
- The combined normal-control image exposes 109 API entities. Preheater and
  analog fields returned device-supplied zeros; active/nonzero inputs have not
  been stimulated. PDO 212 returned a two-byte 233 sample matching 23.3 C.
- Full Linux generated ESPHome host startup/feedback, saved-preference restart,
  ASan/UBSan, iterator-bounds, dashboard, and firmware-build tests pass in fork CI
  for the two isolated submissions and integration through `2226bcd`:
  [38610547246](https://github.com/tudstudent/esphome-zehnder-comfoair/actions/runs/38610547246).
  Latest pressure/addressing changes are under a separate expanded run. Linux
  results are CI results, not local Windows execution.
- KD normal image is privately archived with SHA-256; the temporary pressure API
  action is removed and verified absent after encrypted OTA. Auto/Medium/Normal,
  all 109 entities, and accessory missing-state gates remain intact. A 90-second
  observation is bounded testing, not a long-term uptime/soak guarantee.
- All RF/factory/seasonal modes, active preheating, counter wraps/resets, accessory
  installations, other units, and calibrated pressure meaning are not all
  hardware-validated. Claims must remain limited to recorded observations.

## Remaining Separate Work

- Installed ComfoCool/ComfoFond operation remains untested; software gates and
  absence handling are implemented. Do not fabricate accessory presence.
- Coverage/classification is complete for the pinned inventory; physical meaning
  remains unknown for passive diagnostics and many documented-only IDs.
- High-ID framing is implemented/tested and PDO 1304 observed; availability of
  other high IDs is not established.
- Resolve reference scaling/width disagreements with direct evidence.
- Establish pressure units, signedness, and physical port/side assignment before
  offering calibrated pressure entities.
