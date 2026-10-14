"""Audit every reference entry against the actual package handlers."""

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def inventory():
    mapping = json.loads((ROOT / "components/zehnder_comfoair_q/pdo_mapping.json").read_text(encoding="utf-8"))
    handlers = {}
    for package in sorted((ROOT / "packages").glob("*.yml")):
        text = package.read_text(encoding="utf-8")
        if "on_frame:" not in text:
            continue
        ids = {int(pdo) for pdo in re.findall(r"comfoair_on_frame_case\(\s*(\d+)", text)}
        ids |= {int(pdo) for pdo in re.findall(r"case\s+(\d+)\s*:", text)}
        ids |= {int(pdo) for pdo in re.findall(r"# PDO (\d+)", text)}
        for pdo in ids:
            handlers.setdefault(pdo, []).append(package.name)
    rows = []
    for entry in mapping["pdos"]:
        pdo = entry["id"]
        packages = handlers.get(pdo, [])
        status = "mapped" if packages else "untyped" if entry["type"] is None else "documented-only"
        rows.append({"id": pdo, "type": entry["type"], "registry": entry["registry_type"] is not None,
                     "status": status, "packages": packages, "description": entry["description"]})
    return rows, handlers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Require every registry entry to have a handler")
    parser.add_argument("--json", action="store_true", help="Emit the complete classification, not just totals")
    args = parser.parse_args()
    rows, handlers = inventory()
    missing = [row["id"] for row in rows if row["registry"] and row["status"] != "mapped"]
    known = {row["id"] for row in rows}
    summary = {"documented_ids": len(rows), "registry_ids": sum(row["registry"] for row in rows),
               "mapped_registry_ids": sum(row["registry"] and row["status"] == "mapped" for row in rows),
               "missing_registry_ids": missing,
               "documented_only_ids": [row["id"] for row in rows if row["status"] == "documented-only"],
               "untyped_ids": [row["id"] for row in rows if row["status"] == "untyped"],
               "experimental_nonreference_ids": sorted(set(handlers) - known)}
    if args.check and missing:
        parser.error(f"Unmapped registry IDs: {missing}")
    print(json.dumps({"summary": summary, "entries": rows} if args.json else summary, indent=2))


if __name__ == "__main__":
    main()
