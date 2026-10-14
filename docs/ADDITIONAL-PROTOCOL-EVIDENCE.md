# Additional GitHub Protocol Evidence

Research on 2026-10-14 targets ComfoAir Q/CAN/ComfoConnect implementations, not
older ComfoAir RS232 or E-series Modbus mappings. Other projects' names do not
automatically become verified local mappings. Raw external material and device
captures remain outside Git; only provenance and sanitized observations are here.

## Sources

- `klein0r/node-comfoairq`, revision
  `79e9efab31dd527f8ecbf55dc94994c116d7c5fa`, `lib/const.js`:
  https://github.com/klein0r/node-comfoairq/blob/79e9efab31dd527f8ecbf55dc94994c116d7c5fa/lib/const.js
- App-traffic findings, commit `11817935ec964b011ef2b123715a7910b78a93ab`:
  https://github.com/klein0r/node-comfoairq/commit/11817935ec964b011ef2b123715a7910b78a93ab
- App-status-page labels, commit `eeffac64a81bcc126113680dfcc81757cab3628c`:
  https://github.com/klein0r/node-comfoairq/commit/eeffac64a81bcc126113680dfcc81757cab3628c
- `klein0r/ioBroker.comfoairq` consumes that library and repeats some labels;
  it is not independent corroboration of them.
- `herrJones/node-comfoairq` supplies older labels, including PDO 219, but leaves
  several of the newer names blank.
- Original CAN reverse-engineering discussion, including unit numbers and
  address/fragment/sequence fields:
  https://github.com/marco-hoyer/zcan/issues/1#issuecomment-451735530

The newer commits report decoding app traffic, but the underlying captures were
not independently inspected in this research. Some names are explicitly guesses
from page order on a unit without the relevant accessories.

## Unknown-ID Findings

| PDO | External interpretation | Local evidence / confidence |
| --- | --- | --- |
| 337 | Active fan schedule entries, UINT32 bitmask | Manual bits 1 and 5 corroborated by a bounded KD test; other bits remain source-declared, not locally exercised |
| 219 | Avoided cooling current target | Older and newer library label; KD returns two bytes `00 00`; zero does not establish meaning or scale |
| 384 | Temperature after postheater | External author explicitly assigned from app page order without accessory installed; KD returns `70 FE`, consistent with absent-device -40 C default, not proof of position |
| 400 | Temperature before postheater | Same limitation as 384; KD also returns `70 FE` |
| 386, 401, 402 | Still unnamed in examined library | KD returns one-byte zero values; no new meaning is claimed |
| 33, 37, 53, 321, 325, 341 | Still unnamed in examined library | Targeted reads validate widths/availability only; meanings remain unresolved |

### PDO 337 Validation

The external bitmask model is `1 << schedule_entry_type`. A bounded Low manual
override on KD produced:

- Auto baseline: `00 00 00 00` (0).
- Manual Low override: `02 00 00 00` (bit 1).
- Existing Auto-restoration action briefly enters permanent manual mode:
  `20 00 00 00` (bit 5), then `00 00 00 00`.
- Auto/Medium/Normal was restored and confirmed. No other units were accessed.

This supports the active-entry interpretation and the two manual bits. The
external source labels bit 6 as Boost and bit 11 as Away; neither was deliberately
activated for this validation. Do not confuse a schedule-entry bitmask with a
single operating-mode enum or numeric preset.

### Other Targeted KD Reads

All 13 reads were bounded requests through the existing known-PDO debug action,
with no setting writes. Values: 33=0, 37=0, 53=255, 219=0, 321=1, 325=1, 337=0,
341=0, 384=`70 FE`, 386=0, 400=`70 FE`, 401=0, 402=0. There were no decode errors.
These observations are not validation of all possible states or label hypotheses.

## Pressure Without A Menu

The pinned RMI documentation identifies unit `0x23` as `PRESSURESENSOR`, with
two subunits, and documents `0x01` as a read-only Get-property command:
`01 Unit SubUnit 10 Property`. It does not list pressure-property IDs or units.

https://github.com/michaelarnauts/aiocomfoconnect/blob/8fe395b3f8657e25ef8c5a6ccea5aab06808a514/docs/PROTOCOL-RMI.md

A restricted pressure-unit reader is now implemented separately and exercised
on KD; see `PRESSURE-PROPERTY-READS.md`. It uses only GET, enforces the owning node
and pressure unit/subunits, bounds the property list/rate, validates response
addressing/fragmentation, and exposes no generic factory/configuration commands.
CAN command bits 12/13 remain unclear in the original discussion; response framing
was checked with live success/error replies rather than treating silence as proof
that a property is absent. The bounded property 1-16 experiment found only two
one-byte values and explicit Unknown-property replies, not a pressure scale.

No examined implementation provided an independently verified Pa scale for
PDO 305/306. There is useful new channel association evidence in the existing KD
captures, documented in `PRESSURE-DISCOVERY.md`, but no calibrated Pa mapping yet.
