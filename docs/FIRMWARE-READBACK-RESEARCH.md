# Zehnder Firmware Readback Research

This is offline protocol research, not a tested firmware dumper. No Zehnder
firmware-update, bootloader, reset, erase, or flash-read commands have been sent
to KD. ESPHome OTA authorization is not authorization to modify the Zehnder.

## Transport and Evidence

The owner correctly identifies ComfoConnect LAN C as a ComfoNet/CAN-connected
gateway that can facilitate ventilation-unit firmware updates. It exposes a
LAN protocol, forwarding node operations onto CAN. OptionBox is another CAN
node; its existence alone does not prove it initiates firmware updates.

Pinned source: aiocomfoconnect
`8fe395b3f8657e25ef8c5a6ccea5aab06808a514`:

- Protocol: https://github.com/michaelarnauts/aiocomfoconnect/blob/8fe395b3f8657e25ef8c5a6ccea5aab06808a514/docs/PROTOCOL.md
- Message definitions: https://github.com/michaelarnauts/aiocomfoconnect/blob/8fe395b3f8657e25ef8c5a6ccea5aab06808a514/protobuf/zehnder.proto
- Gateway client: https://github.com/michaelarnauts/aiocomfoconnect/blob/8fe395b3f8657e25ef8c5a6ccea5aab06808a514/aiocomfoconnect/bridge.py

The definitions contain a real readback family, separate from programming:

| Operation | Fields / purpose | Research status |
| --- | --- | --- |
| CnFupReadRegisterRequest/Confirm (70/71) | Node, register ID, optional index; returns a register value | Defined, not exercised |
| CnFupReadRequest (78) | Node and optional memory block, default block 0 | Defined, not exercised |
| CnFupReadConfirm (79) | Chunks up to 256 bytes, ending with `last=true` | Supports block streaming at protocol level; runtime permission/layout unknown |
| CnFupProgramBeginRequest (72) | Begins programming a selected block | DESTRUCTIVE: source explicitly says it erases flash |
| CnFupProgramRequest/End (74/76) | Write and finalize memory data | Must not be used for readback research |
| CnFupResetRequest (80) | Reset the selected node | Can disrupt operation; not authorized by ordinary telemetry access |

Operation numbers are LAN gateway message types, NOT raw CAN command bytes.
Do not transmit them directly as CAN payloads. The protobuf comments identify
the read operation as a wrapper around `CN_fupReadBegin`, `CN_fupReadData`,
`CN_fupClearToSend`, and `CN_fupReadEnd`.

`UpgradeRequest` is a separate gateway-upgrade mechanism: it uploads consecutive
binary chunks and reboots the gateway. It must not be confused with ventilation
node readback or firmware-version retrieval.

The high-level Python client has message mappings for FUP but no demonstrated
ready-to-use firmware-dump workflow. Other examined repositories mostly repeat
these definitions/message mappings; they do not establish successful Q600 dumps.

## What Remains Unknown

- Whether KD permits memory reads while in normal mode or requires update mode.
- Memory block identities, readable size, configuration versus application data,
  firmware/bootloader boundaries, and read protection.
- The exact direct-CAN FUP exchange, pacing, acknowledgment/error handling, and
  how to finish/abort a read safely without reset or programming.
- Whether a read temporarily affects ventilation or CAN communication.
- Authentication/session restrictions when using a physical LAN C.

The protocol notes describe firmware traffic using 11-bit IDs or `0x1F800000`,
different from ordinary PDO/RMI traffic. They also state a bus rate that differs
from KD's verified 50 kbit/s setup. Do not change bitrate or frame behavior based
on generic documentation alone.

The upstream maintainer explicitly declined live upgrade reverse engineering
because of the risk of breaking the ventilation unit:
https://github.com/michaelarnauts/aiocomfoconnect/issues/54#issuecomment-2965330382

## Safer Investigation Order

1. Obtain an official update image for offline analysis if available; an update
   file may be wrapped/signed/encrypted and need not equal a complete flash dump.
2. Inspect app/update tooling and existing captures to identify the read protocol
   and memory/register layout without contacting bootloader services.
3. Read the normal software-version/model properties using ordinary documented
   getters; distinguish Zehnder firmware from ESPHome and gateway versions.
4. Only after safe read-mode prerequisites and recovery are known, propose a
   narrowly scoped, separately authorized readback experiment. No programming,
   factory mode, reset, or guessed initialization commands.

A retrieved firmware image could reveal PDO registration tables, sensor-unit
properties, type declarations, pressure scaling, and enum meanings. That is a
useful research goal, not a guarantee that an image is currently readable.

## Owner Constraint: Readback Without Erasing

The owner requests reverse engineering and extraction without erasing. Treat that
as a hard requirement, not a reason to try the programming path as initialization.
The only candidate operations are verified FUP register/block reads and their
documented read-flow acknowledgments. No ProgramBegin, Program, ProgramEnd,
reset, factory-mode commands, readout-protection changes, or guessed mode switches.

"All blocks" must mean every block shown to be readable by a verified map, not
blind probing of all 256 possible block IDs. Protected or inaccessible regions
must be reported as such; never attempt unlocking, which can trigger mass erase
on some microcontrollers. A read can still pause operation even if it does not
erase, so normal-mode behavior and recovery remain prerequisites for live tests.

The GitHub search found FUP message definitions and wrapper dispatch tables, but
not a demonstrated direct-CAN Q600 reader or a verified register/block map. No
readback request has been sent. The concrete offline next step is inspecting the
ComfoControl app/service updater to recover those details; an exported Android APK
or updater package would help even when no firmware image is available.

Once the protocol is verified, any dumper must enforce a read-only operation
whitelist, bounded block sizes/timeouts and transfer rates, correct chunk ordering
and final markers, private output files, and per-block SHA-256 checks. Repeat
reads where safe to check consistency. Do not describe a partial image as a full
flash backup or assume it includes bootloader/configuration memory.

## Spare PCB / STM32F103 Hardware Route

The owner reports an older PCB with an STM32F103 and is willing to consider a
non-erasing chip-reader/JTAG approach. The full part marking and board identity
(main controller versus accessory) are still needed; no hardware probe was made.

For this MCU family, SWD/JTAG is a more appropriate starting point than treating
the device like a removable SPI EEPROM. An ST-Link can identify a properly wired
target and, if readout protection permits, read its internal flash. The exact
suffix determines capacity/page layout; do not assume a fixed size or blindly
read the entire address space.

Proposed capability check on an explicitly identified, disconnected spare PCB:

1. Confirm full MCU marking, PCB role, debug pads, ground, and interface voltage.
   Isolate it from mains, the working ventilation unit, and connected actuators.
2. Use read-only tool operations to identify the device and protection status.
   Do not run auto-programming, erase, unlock, or read-unprotect operations.
3. If readable, extract only the documented main-flash range and save privately.
   Repeat the read and compare SHA-256. Capture device/layout metadata separately.
4. If protection blocks reading, stop. Removing STM32 readout protection can mass
   erase flash, contrary to the owner's hard constraint. Do not attempt bypasses.

Halting/resetting a spare processor may be needed for debug attachment and is not
the same as erasing, but it must not be applied to the working unit or an
unidentified connected board. A debug-readable firmware image may include the
vendor bootloader/application within main flash; external EEPROM, protected
regions, and configuration elsewhere require separate identification.

Whether CAN-mediated readback can access an image that is debug-protected is a
separate unknown. Interface capability is not evidence that a particular board
is readable. The owner need not purchase a LAN C to pursue the hardware route.

## Existing Hardware: ChipWhisperer-Husky

The owner has a ChipWhisperer-Husky and will not buy an ST-Link. Use that existing
hardware rather than adding a purchase requirement. Official Husky documentation
explicitly lists JTAG/SWD through OpenOCD and a built-in STM32 UART interface:

https://chipwhisperer.readthedocs.io/en/latest/Capture/ChipWhisperer-Husky.html
https://chipwhisperer.readthedocs.io/en/latest/debugging.html
https://chipwhisperer.readthedocs.io/en/latest/Capture/20-pin-connector.html

Preferred route: Husky's MPSSE/SWD mode through OpenOCD, using the documented
USERIO/debug connector and correct STM32F1 target definition. The vendor warns
that MPSSE has not been tested on every target, so support is not a guarantee of
readability. On Windows, disconnect the Python process before OpenOCD claims
the Husky USB device. Do not enable MPSSE, power rails, clocks, or target signals
until wiring/board identity and voltage have been confirmed.

Alternative genuine transport: the STM32 factory UART bootloader, if the exact
part supports it and BOOT/reset/UART pins are accessible on the isolated spare.
ChipWhisperer's `programmer_stm32fserial.py` implements `cmdReadMemory` (0x11)
and bounded `readMemory` transfers. This requires boot-mode attachment, not
writing firmware. Readout protection can still prevent extraction.

https://github.com/newaetech/chipwhisperer/blob/develop/software/chipwhisperer/hardware/naeusb/programmer_stm32fserial.py
https://github.com/newaetech/chipwhisperer/blob/develop/docs/source/debugging.rst

Do NOT use `program`, `autoProgram`, `writeMemory`, erase/protect/unprotect, GDB
`load`, or tutorial commands such as `flash write_image erase`. The examined
programmer's `program()` retries a write failure by calling erase; an
`erase=False` option on a programming wrapper is not a safe readback guarantee.
Use a separately reviewed read-only sequence with no automatic programming paths.

No voltage/clock glitching, fault injection, or protection bypass is part of this
plan. Do not connect the glitch/crowbar output. No target wiring or Husky control
commands have been performed. Exact MCU marking, PCB role, and debug-pad photos
remain the prerequisites for a concrete read-only setup.
