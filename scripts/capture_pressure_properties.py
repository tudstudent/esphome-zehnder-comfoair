"""Collect explicitly selected pressure GET results from one verified endpoint."""

import argparse
import asyncio
import json
from pathlib import Path
import re

from aioesphomeapi import APIClient, LogLevel

from scripts.capture_pdos import ANSI, credentials

RESULT = re.compile(r"subunit:\s*(\d+), property:\s*(\d+), error:\s*([01]), length:\s*(\d+), data:\s*(.*)$")


def parse_result(message):
    match = RESULT.search(ANSI.sub("", message))
    if match is None:
        return None
    subunit, prop, error, length = map(int, match.groups()[:4])
    content = match[5].split(" (", 1)[0].strip()
    try:
        payload = bytes.fromhex(content.replace(".", ""))
    except ValueError:
        return None
    if len(payload) != length or length > 256:
        return None
    return {"subunit": subunit, "property": prop, "error": bool(error), "hex": payload.hex(), "length": length}


async def capture(args):
    key, password = credentials(args.config)
    client = APIClient(args.device, 6053, password=password, noise_psk=key,
                       expected_name=args.expected_name, client_info="Pressure GET-only research", provide_time=False)
    results = []
    pending = None
    event = asyncio.Event()
    received = None

    def log(message):
        nonlocal received
        text = message.message
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="replace")
        result = parse_result(text)
        if result and pending == (result["subunit"], result["property"]):
            received = result
            event.set()

    try:
        await asyncio.wait_for(client.connect(login=True), 20)
        info = await client.device_info()
        if info.name != args.expected_name:
            raise RuntimeError("Device identity mismatch")
        _, services = await client.list_entities_services()
        service = next((item for item in services if item.name == args.action), None)
        if service is None:
            raise RuntimeError("The fixed pressure-read action is not exposed by this firmware")
        client.subscribe_logs(log, log_level=LogLevel.LOG_LEVEL_DEBUG, dump_config=False)
        await asyncio.sleep(0.5)
        for subunit in args.subunit:
            for prop in args.property:
                pending = (subunit, prop)
                received = None
                event.clear()
                await client.execute_service(service, {"subunit": subunit, "property": prop})
                try:
                    await asyncio.wait_for(event.wait(), 3.5)
                    results.append(received)
                except asyncio.TimeoutError:
                    results.append({"subunit": subunit, "property": prop, "timeout": True})
                await asyncio.sleep(0.5)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({"firmware": info.esphome_version, "results": results}, indent=2) + "\n",
                               encoding="utf-8", newline="\n")
        print(json.dumps(results, indent=2))
    finally:
        await client.disconnect()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--device", required=True)
    parser.add_argument("--expected-name", required=True)
    parser.add_argument("--action", default="read_pressure_property_debug")
    parser.add_argument("--subunit", type=int, choices=(1, 2), action="append")
    parser.add_argument("--property", type=int, action="append", required=True, help="Explicit property IDs, 1-16")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.subunit = list(dict.fromkeys(args.subunit or [1, 2]))
    args.property = list(dict.fromkeys(args.property))
    if any(prop < 1 or prop > 16 for prop in args.property) or len(args.subunit) * len(args.property) > 32:
        parser.error("Only pressure subunits 1/2 and property IDs 1-16 are permitted")
    if args.output.exists():
        parser.error("Output exists; choose a new private capture path")
    asyncio.run(capture(args))


if __name__ == "__main__":
    main()
