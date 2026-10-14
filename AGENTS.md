# Engineering Rules

- Write clean, maintainable code against current supported ESPHome APIs and
  standard platform components. Upgrade dependencies deliberately; do not wrap
  obsolete interfaces or downgrade packages to preserve old behavior.
- Do not add shims, legacy fallbacks, compatibility branches, deprecated aliases,
  or automatic protocol-type detection. Update call sites and documentation.
- Each known PDO has exactly one declared runtime type and one required width.
  Reject unknown types and malformed frames; never infer a type from length.
- Record evidence accurately: payload width does not prove signedness. If evidence
  changes a type, correct the mapping and documentation rather than accepting both.
- Experimental raw diagnostics use an explicit representation and no unverified
  physical units, scaling, or side assignment.
- Keep work in small reviewable commits/PRs with tests and validation limits.
- Only the owner-confirmed KD ESP32 may be accessed. KD development uploads and
  bounded fan-speed tests are authorized; other devices and unrelated setting
  changes are not. Preserve networking/credentials and restore test settings.
- ESP32 upload permission does not authorize Zehnder firmware/bootloader actions.
  Do not send Zehnder flash, erase, factory-mode, reset, or unverified firmware-read
  operations without separate explicit approval and an established recovery plan.
- Keep secrets, private endpoints, and raw captures out of Git. Do not push or
  open upstream PRs without the owner's approval.
