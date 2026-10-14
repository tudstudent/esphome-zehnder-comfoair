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
