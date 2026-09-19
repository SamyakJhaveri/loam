"""Validate the planning packet, not the proposed factory runtime."""

import argparse
import hashlib
import json
import re
from pathlib import Path


def main():
    arc = Path(__file__).resolve().parents[1]
    root = arc.parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, help="Verify approved source manifests against a preserved repository-root snapshot")
    args = parser.parse_args()
    source_root = args.source_root.resolve() if args.source_root else root
    packet = json.loads((arc / "ticket-backlog.json").read_text())
    tickets = packet["tickets"]
    errors = []
    ids = {t["id"] for t in tickets}
    if len(ids) != len(tickets) or not tickets:
        errors.append("empty population or duplicate ticket IDs")
    if packet["runtime_authorized"] is not False:
        errors.append("runtime deferral missing")
    seen = set()
    for ticket in tickets:
        identity = ticket["id"]
        if not set(ticket["depends"]).issubset(seen):
            errors.append(f"{identity}: unresolved or non-topological dependency")
        seen.add(identity)
        path = arc / "tickets" / ticket["file"]
        if not path.is_file():
            errors.append(f"{identity}: missing body")
            continue
        body = path.read_text()
        if hashlib.sha256(path.read_bytes()).hexdigest() != ticket["sha256"]:
            errors.append(f"{identity}: body digest differs from backlog")
        if ticket["body"] not in body:
            errors.append(f"{identity}: JSON/body content differs")
        for requirement in ["acceptance", "canonical", "Campaign requirements"]:
            if requirement.lower() not in body.lower():
                errors.append(f"{identity}: missing {requirement}")
        if "node --test" not in body or "unimplemented" not in body:
            errors.append(f"{identity}: missing explicitly proposed check")
        if not ticket["source_paths"]:
            errors.append(f"{identity}: missing source packet")
        groups = ticket.get("verification_groups", [])
        allowed = {"installation", "store", "execution", "complete-slice", "release-only", "post-installation"}
        if not groups or not set(groups).issubset(allowed):
            errors.append(f"{identity}: missing or unknown verification group assignment")
        if any(group not in body for group in groups):
            errors.append(f"{identity}: verification group absent from body")
        for source in ticket["source_paths"]:
            if not (source_root / source).is_file():
                errors.append(f"{identity}: source missing: {source}")
        if [x["file"] for x in ticket["source_manifest"]] != ticket["source_paths"]:
            errors.append(f"{identity}: source manifest population differs")
        for record in ticket["source_manifest"]:
            source_path = source_root / record["file"]
            if source_path.is_file() and hashlib.sha256(source_path.read_bytes()).hexdigest() != record["sha256"]:
                errors.append(f"{identity}: source packet changed: {record['file']}")
        digest = hashlib.sha256(json.dumps(ticket["source_manifest"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if digest != ticket["source_packet_sha256"] or digest not in body:
            errors.append(f"{identity}: source packet digest differs")
        for relative in re.findall(r"\]\(([^)]+)\)", body):
            if "://" not in relative and not (path.parent / relative.split("#")[0]).exists():
                errors.append(f"{identity}: broken link: {relative}")
    inventory = (arc / "source-inventory.md").read_text()
    source_index = (root / "docs/research/INDEX.md").read_text()
    urls = set(re.findall(r"https?://[^\s<>`|)]+", source_index))
    for url in urls:
        url = url.rstrip(".,;")
        if url not in inventory:
            errors.append(f"INDEX URL not accounted for: {url}")
    for target in re.findall(r"\]\(([^)]+)\)", inventory):
        if "://" in target:
            continue
        path = Path(target.split("#")[0])
        if not path.is_absolute():
            path = arc / path
        if not path.exists():
            errors.append(f"inventory link missing: {target}")
    prior = json.loads((arc / "delivery-checkpoint.json").read_text())
    preserved = [x for x in prior["files"] if x["file"].startswith("prior-design/")]
    for record in preserved:
        if hashlib.sha256((arc / record["file"]).read_bytes()).hexdigest() != record["sha256"]:
            errors.append(f"historical snapshot changed: {record['file']}")
    bundle = arc / "tooling/mattpocock-skills"
    provenance = json.loads((bundle / "provenance.json").read_text())
    for record in provenance["files"]:
        path = bundle / record["file"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            errors.append(f"staged upstream source changed: {record['file']}")
    if errors:
        print("Ticket packet: FAILED")
        print("\n".join(errors))
        raise SystemExit(1)
    stages = {stage: sum(t["stage"] == stage for t in tickets) for stage in sorted({t["stage"] for t in tickets})}
    print(f"Ticket packet: PASSED; {len(tickets)} tickets; dependency DAG valid; source paths and body hashes match")
    print(f"INDEX URL coverage: {len(urls)} checked; historical snapshots: {len(preserved)} unchanged; upstream source files: {len(provenance['files'])} unchanged")
    print(f"Stages: {stages}")


if __name__ == "__main__":
    main()
