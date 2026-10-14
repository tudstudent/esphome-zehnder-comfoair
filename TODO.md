# Zehnder ComfoAir Q Roadmap

## Goal and Scope

Improve `yoziru/esphome-zehnder-comfoair` to match current aiocomfoconnect PDO
definitions, correct incomplete or incorrect types/conversions, validate on the
Zehnder Q600 KD, investigate pressure telemetry, and prefer standard ESPHome
building blocks. Deliver small PRs the upstream maintainer can accept separately.

The earlier `../comfoair-esp32` fork is reference material only. Reuse useful
ideas or code with appropriate licensing/attribution, but do not import its
findings as confirmed bugs in this project. KD's saved configuration already
declares this project's `zehnder_comfoair_q` component, ESP-IDF, and native CAN.

## Access and Change Rules

- Only the owner-confirmed KD ESP32 may be accessed. ESPHome mDNS discovery is
  allowed; no port scans, API connections, tests, or recovery on other devices.
- The owner authorized KD firmware uploads for development/debugging on
  2026-10-14. This applies only to the confirmed KD ESP32, not other devices.
  Preserve networking/access credentials and validate builds before uploading.
- KD access is read-only until separately authorized: no ventilation commands,
  configuration writes or unrelated setting changes. The owner approved fan-speed
  variation for pressure investigation on 2026-10-14; use bounded tests, record
  the original state, and restore the original fan/operating mode afterwards.
- Preserve known-good configuration/firmware and a recovery path before any
  authorized firmware replacement. Preserve normal ventilation during tests.
- Keep secrets, private endpoints, and identifiable captures out of commits.
- No shims, legacy fallbacks, compatibility branches, deprecated aliases, or
  automatic type detection. Use current ESPHome interfaces and standard packages;
  update call sites/documentation instead of preserving obsolete behavior.
  Correct verified type errors directly. Width alone does not prove signedness.
- Make uncertain mappings and accessory diagnostics opt-in. Do not enable an
  unbounded scan or request every unknown PDO on boot.
- Include regression tests, documentation, and validation evidence in each PR.
  Do not claim hardware validation for absent accessories or untested features.
- Obtain the owner's approval before pushing work branches or opening PRs.

## Development Progress

Local PR-sized branches/commits are listed in `docs/PR-PLAN.md`; nothing is pushed
or submitted upstream yet. The pinned inventory covers 158 documented IDs and
all 86 Python registry definitions. Base plus implemented known optional handlers
now cover 65 registry IDs. The other 21 are 8 accessory entries and 13 uncertain
entries requiring separate work. Experimental PDOs 305/306 are outside that
inventory and deliberately retain unscaled, unitless raw labels.

KD builds and OTA/API checks pass on ESPHome 2026.9.1 / ESP-IDF 5.5.5. The core
status/timer package returns plausible normal states without payload errors.
The owner-approved fan experiment restored Auto/Medium/Normal. Normal command
availability is restored; read-only mode is an opt-in development guard.
Original YAML/credentials remain unchanged; a separate development YAML, validated
OTA image, and checksum manifest are preserved locally outside Git. KD exposes
88 API entities, including the unitless raw candidates. Serial recovery and an
original 2025 firmware binary are not confirmed. Preheater/analog channels were
read as zero in the current condition; active/nonzero behavior remains untested.

A targeted PDO 212 read returned two bytes `E9 00` (233, or 23.3 C) on KD. The
decoder accepts only the declared two-byte INT16 type; no one-byte variant has
been demonstrated. Positive readings alone do not establish signedness
independently of the reference. SHT20/SHT30 I2C formats are documented separately
and do not establish the downstream PDO encoding.

Pressure evidence and remaining uncertainty are in `docs/PRESSURE-DISCOVERY.md`.
No calibrated Pa values or physical side assignments are asserted.

## Initial Baseline

Initial checkout: `d123d47cfcf0b57e79b059266bf4be951156bfae`, project release
2026.10.1. Reference aiocomfoconnect revision:
`8fe395b3f8657e25ef8c5a6ccea5aab06808a514` (2026-10-10).

- PDO documentation: https://github.com/michaelarnauts/aiocomfoconnect/blob/8fe395b3f8657e25ef8c5a6ccea5aab06808a514/docs/PROTOCOL-PDO.md
- Sensor registry: https://github.com/michaelarnauts/aiocomfoconnect/blob/8fe395b3f8657e25ef8c5a6ccea5aab06808a514/aiocomfoconnect/sensors.py
- Constraint definitions: https://github.com/michaelarnauts/aiocomfoconnect/blob/8fe395b3f8657e25ef8c5a6ccea5aab06808a514/aiocomfoconnect/util.py

The stock base package dispatches 43 PDO IDs; optional packages add 226 and 230,
giving 45 IDs versus 86 registry entries and 158 documented IDs. Coverage counts
describe handlers, not complete interpretation of every state (PDO 16 currently
feeds an away indicator). Many documented IDs are unknown or hardware-specific.
See `docs/PDO-AUDIT.md` for the initial static comparison.

Already implemented upstream, not new work to duplicate:

- Explicit unsigned assembly and no-change formatting for timers 81/82.
- PDO 16 away value 7; PDO 49 boost/away/auto labels; normal profile value 0.
- Optional lossless 64-bit PDO 230 constraint decoding, including validity,
  grouped reasons, high CO2 bits, and unknown bits.
- Optional modulated fan speed, PDO 226.
- Standard ESPHome CAN and ESP-IDF; host regression tests for decoding,
  framing, scheduling, startup, feedback, and explicit controls.

These observations concern the current checkout, not necessarily KD's older
running image. aiocomfoconnect uses a ComfoConnect bridge; this project uses
direct CAN. Verify ambiguous payload representation on the actual CAN bus.

## Block 0 - KD Test Access and Recovery

- [x] Discover the KD advertisement and have the owner confirm its identity.
- [x] Locate the saved KD YAML and identify this project's source declaration.
- [x] Update PC tooling: ESPHome 2026.9.1 and aioesphomeapi 46.3.0 on Python 3.13;
  verify versions, API/discovery imports, and dependency consistency.
- [x] Verify authenticated KD-only API/log access using locally held credentials.
- [x] Capture device version, baseline readings, and CAN/log behavior; retain
  private captures locally. Long-term stability/uptime observation remains pending.
- [x] Establish the current development image's source revision and retain a
  checksum manifest. The original 2025 image's exact component revision is unknown.
- [x] Preserve a tested development configuration/OTA image; authenticated OTA
  recovery has been exercised. Original-image and serial recovery remain pending.
- [x] Review the saved KD YAML's custom startup/feedback automations and apply
  the upstream safety guards in a separate private development configuration.

## Block 1 / PR 1 - Existing Types, States, and Safety

- [ ] Review each current handler's type, signedness, length, endian conversion,
  scaling, enum meaning, and unit; add type-specific width checks rather than
  accepting any supported length regardless of the PDO definition.
- [x] Verify PDO 212's width on KD: two bytes, matching the Python registry width.
  Reject truncated one-byte payloads; document the erroneous UINT8 declaration.
- [ ] Resolve PDO 213/216 power scaling: documentation examples imply /100,
  whereas aiocomfoconnect treats raw values as watts and this project's YAML
  converts raw values to kW with /1000. Use evidence before changing scaling.
- [ ] Review PDO 65 away versus fan OFF presentation without breaking feedback
  guards or introducing outbound commands during state synchronization.
- [x] Fix reversed PDO 119/120 comments in `packages/sensors.yml`; the CAN
  dispatch currently routes exhaust 119 and supply 120 correctly.
- [ ] Review temperature-location names and unknown enum handling; do not assert
  meanings that the reference itself marks uncertain.
- [ ] Test unsigned/signed boundaries, negative temperatures, sentinels, malformed
  frames, startup, and feedback-only operation using the existing host suite.
- [x] Document numeric float precision and keep no-change formatting/bitsets
  outside lossy numeric-state interpretation where needed.

Acceptance: focused confirmed fixes with regression tests, updated YAML call
sites, and documented API changes; hardware-dependent findings remain pending.

## Block 2 / PR 2 - Canonical Mapping and Converter Coverage

- [ ] Create one authoritative local mapping with PDO ID, reference type,
  conversion, scale, unit, enums, certainty, and upstream revision.
- [x] Add a reproducible comparison against pinned aiocomfoconnect definitions;
  record documentation/implementation disagreements instead of copying blindly.
- [ ] Keep request lists, CAN dispatch, and entity metadata consistent; reduce
  duplicated hand-maintained mappings and update user YAML to current interfaces.
- [x] Add reusable BOOL, UINT8/16/32, and INT8/16/64 decoders with exact widths.
  PDO 230 already has a dedicated 8-byte decoder; preserve or reuse it rather
  than replacing its integer bitset with a floating-point sensor value.
- [x] Add boundary/width tests for all implemented integer converters; retain
  existing constraint tests. Full Linux host/sanitizer execution remains pending.
- [ ] Investigate support for documented PDO IDs above 1023: the schema currently
  caps request IDs at 0x3ff and the base receive mask also constrains high bits.
  Validate direct-CAN addressing/filter behavior before expanding either.

Acceptance: reference drift and exclusions are auditable, and typed decoding
does not silently lose information. Keep this separate from added telemetry.

## Block 3 / PR 3 Series - Missing Known Telemetry

- [x] Add complete device state, filter-changing status (18), manual/fan-mode
  alternatives (56, 70, 71), RF pairing (176), and unit settings (208, 224).
- [x] Add timer PDOs 86/87 using the existing unsigned duration helper.
- [ ] Add optional ComfoCool timer PDO 85 with accessory validation.
- [x] Add preheater energy/current power (144/145/146), frost unbalance (228),
  bypass override (338), additional fan-mode representations (342/343), and
  analog inputs (369-372).
- [ ] Add optional ComfoFond (416-419) and ComfoCool (784/785/802) telemetry;
  assess other documented accessory fields individually.
- [ ] Account for every remaining reference entry: implemented, optional raw
  diagnostic, uncertain, unavailable on KD, or deliberately excluded.
- [x] Preserve existing optional PDO 226/230 packages and verify merging behavior;
  do not enable unsupported accessories by default.
- [ ] Choose device/state classes and precision carefully; verify counter resets
  and wraps before choosing energy state classes.
- [x] Add separate examples/branches for core telemetry, preheater, analog inputs,
  and experimental raw candidates. Accessory coverage remains separate/pending.

Acceptance: each subset has tests and explicit availability/validation notes.

## Block 4 / PR 4 - Bounded Read-Only Diagnostics

- [ ] Reuse existing `comfoair_dump` logs and request helpers where sufficient;
  add opt-in/rate-limited capture rather than a second CAN transport.
- [x] Capture PDO IDs, raw bytes, lengths, relative timestamps, and requested versus
  spontaneous observations, including unregistered PDOs.
- [ ] Support targeted bounded read requests; verify read-only RMI mechanisms
  individually before use. No configuration writes or unbounded bus scans.
- [ ] Create sanitized fixtures and a repeatable hardware validation procedure.
- [ ] Monitor bus load, responsiveness, uptime, and normal ventilation; keep
  diagnostics disabled or restricted for routine operation.

May be developed alongside earlier blocks to resolve ambiguous values; remains
a separate PR. No new firmware may be installed without explicit permission.

## Block 5 / PR 5 Series - Pressure Discovery

Owner reports two likely Sensirion differential-pressure sensors (possibly
SDP810/SDP816; exact model unconfirmed), one on the intake side and one on the
house side. Do not assume their differential port/reference arrangement or units.
The initial KD read-only capture observed undocumented PDOs 305/306 as 2-byte
values around 103/105. These are candidates only, not identified pressure signals.

- [ ] Confirm the Q600 KD pressure-sensor arrangement and whether readings are
  exposed through PDO/direct CAN or read-only RMI at all.
- [ ] Research candidates in upstream protocol notes and related implementations;
  do not label unknown IDs as pressure without evidence.
- [x] Correlate candidates with airflow/RPM and owner-approved fan-level changes.
  Never obstruct ducts or disable safety mechanisms to stimulate readings.
- [ ] Establish payload type, units (for example Pa), scale, location,
  differential/reference meaning, range, and update behavior.
- [ ] Separate measured pressure from derived resistance/airflow indicators.
- [ ] Publish verified mappings with fixtures; document inconclusive results.
- [ ] Investigate other useful identifiable telemetry without delaying pressure.

Pressure is the priority after existing mapping faults are resolved. Availability
is not yet confirmed. Keep discovery tools and verified sensor additions separate.

## Block 6 / PR 6 Series - ESPHome Modernization

- [ ] Audit dependencies and API usage against supported ESPHome versions.
  Native CAN and ESP-IDF already exist; do not plan an unnecessary replacement.
- [ ] Use `../esphome-nibe` as a reference for standard abstraction adoption,
  not as a reason to introduce UDP into this CAN bridge.
- [ ] Review scheduling, ownership, receive filtering, API actions, and YAML
  lifecycle/feedback behavior in narrowly scoped modernization PRs.
- [ ] Preserve 50 kbit/s, extended frames, RTR requests, fragmented commands,
  request scheduling, and read-only feedback behavior.
- [ ] Adapt baseline host tests/build tooling for Windows where needed; CI
  already exists, so extend existing coverage rather than duplicating it.
- [ ] Validate the ESP32-C3/Ethernet KD configuration locally and on hardware
  only after the required authorization. Keep pressure work independent.

## PR Submission Gates

- [ ] State scope, dependencies, reference revisions, API changes, and evidence.
- [ ] Run existing/added host tests and representative configuration/build checks.
- [x] Obtain explicit KD upload permission for development/debugging.
- [ ] Record tested versions/models and distinguish host tests from hardware tests.
- [ ] Update documentation/examples and obtain approval before pushing/opening PRs.
