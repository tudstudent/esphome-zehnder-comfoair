"""Capture a single identity-checked ESPHome endpoint without ventilation commands."""

import argparse
import asyncio
import dataclasses
import json
from pathlib import Path
import re
import time

import yaml
from aioesphomeapi import APIClient, LogLevel

FRAME = re.compile(r"Node:\s*(\d+), PDO:\s*(\d+), rtr:\s*([01]), length:\s*(\d+), content:\s*([0-9a-fA-F.]+|n/a)")
ANSI = re.compile(r"\x1b\[[0-9;]*m")
MAX_FRAMES = 20000


def parse_frame(text):
    match = FRAME.search(ANSI.sub("", text))
    if match is None:
        return None
    node, pdo, rtr, length = map(int, match.groups()[:4])
    if length > 8:
        return None
    try:
        payload = b"" if rtr else bytes.fromhex(match[5].replace(".", ""))
    except ValueError:
        return None
    if not rtr and len(payload) != length:
        return None
    return {"node": node, "pdo": pdo, "rtr": bool(rtr), "length": length,
            "hex": payload.hex(), "unsigned": int.from_bytes(payload, "little") if payload else None}


def credentials(path):
    class Loader(yaml.SafeLoader):
        pass

    secrets = None

    def secret(loader, node):
        nonlocal secrets
        if secrets is None:
            secrets = yaml.safe_load((path.parent / "secrets.yaml").read_text(encoding="utf-8-sig"))
        return secrets[loader.construct_scalar(node)]

    Loader.add_constructor("!secret", secret)
    Loader.add_multi_constructor("!", lambda loader, tag, node: loader.construct_scalar(node)
                                 if isinstance(node, yaml.ScalarNode) else None)
    try:
        config = yaml.load(path.read_text(encoding="utf-8-sig"), Loader=Loader)
    except yaml.YAMLError:
        # YAML exception snippets can otherwise reveal an inline credential.
        raise ValueError("Unable to parse API configuration") from None
    api = config.get("api") or {}
    return (api.get("encryption") or {}).get("key"), api.get("password")


async def capture(args):
    key, password = credentials(args.config)
    client = APIClient(args.device, 6053, password=password, noise_psk=key,
                       expected_name=args.expected_name, client_info="PDO read-only capture", provide_time=False)
    frames, states = [], {}
    dropped = 0
    start = time.monotonic()

    def log(message):
        nonlocal dropped
        text = message.message
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="replace")
        frame = parse_frame(text)
        if frame is None:
            return
        if args.pdo and frame["pdo"] not in args.pdo:
            return
        if len(frames) >= MAX_FRAMES:
            dropped += 1
            return
        frames.append({"elapsed": round(time.monotonic() - start, 3), **frame})

    try:
        await asyncio.wait_for(client.connect(login=True), 20)
        info = await client.device_info()
        if info.name != args.expected_name:
            raise RuntimeError("Device identity mismatch; capture aborted")
        entities, _ = await client.list_entities_services()
        labels = {entity.key: entity.object_id or entity.name for entity in entities}
        client.subscribe_states(lambda state: states.update({labels.get(state.key, str(state.key)): dataclasses.asdict(state)}))
        client.subscribe_logs(log, log_level=LogLevel.LOG_LEVEL_DEBUG, dump_config=False)
        await asyncio.sleep(args.seconds)
        result = {"firmware": info.esphome_version, "entity_count": len(entities),
                  "frames": frames, "dropped_frames": dropped, "states": states}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
        print(f"Captured {len(frames)} frames and {len(states)} states from the verified endpoint; no ventilation commands sent")
        print(f"Observed PDO IDs: {sorted({frame['pdo'] for frame in frames})}")
    finally:
        await client.disconnect()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path, help="Local YAML containing API credentials")
    parser.add_argument("--device", required=True, help="Explicit single hostname/IP; no discovery or scanning")
    parser.add_argument("--expected-name", required=True, help="Require an exact device name match")
    parser.add_argument("--seconds", type=int, default=30)
    parser.add_argument("--pdo", type=int, action="append", help="Optional PDO filter; repeat as needed")
    parser.add_argument("--output", required=True, type=Path, help="Private capture path; do not commit raw captures")
    args = parser.parse_args()
    if not 1 <= args.seconds <= 300:
        parser.error("Capture duration must be between 1 and 300 seconds")
    if args.output.exists():
        parser.error("Output already exists; choose a new capture path")
    asyncio.run(capture(args))


if __name__ == "__main__":
    main()
