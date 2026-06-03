#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["google-genai", "pillow", "pyyaml"]
# ///
"""Track B render engine (glue only): registry -> prompt -> refs -> Gemini -> PNG."""

import argparse
import io
import os
import sys
from pathlib import Path

import yaml
from PIL import Image

MODEL = "gemini-3-pro-image"
MAX_REFS = 6  # gemini-3-pro-image accepts at most 6 reference images.
LABEL_STRATEGIES = {"track-a", "vector-overlay", "label-light", "label-free"}

PREAMBLE = (
    "Japanese shin-hanga woodblock print: atmospheric and luminous, built from many layered "
    "transparent color impressions; a single "
    "harmonious tonal key per image; soft graded skies (bokashi) suggesting dawn, dusk, or mist; "
    "fine hand-carved directional linework; calm, centered, contemplative composition beside "
    "gently moving water; matte, slightly grainy printed texture on fine paper; fresh, bright, "
    "inviting color; clear luminous daylight; soft even tonal transitions with a gentle contrast "
    "range. Wide 16:9 landscape banner. Use clean blank paper margins with no seal, stamp, "
    "signature, date column, lettering, or ruled border anywhere, and let the composition "
    "communicate pictorially. Subject:"
)

LABEL_GUIDANCE = {
    "label-free": (
        "Label treatment: wide plain cream paper margins, the lower-right margin stays plain cream "
        "paper texture, pictorial plant forms carry the meaning."
    ),
    "label-light": (
        "Label treatment: one small decorative title of at most two short words may sit in the margin."
    ),
    "vector-overlay": (
        "Label treatment: leave calm open bands and clear destination areas for deterministic vector labels added later."
    ),
    "track-a": (
        "Label treatment: keep the hero image pictorial; exact labels belong in the separate Track A figure."
    ),
}


def write_qa_manifest(out_path, concept, full_prompt, attached, missing, size, render_status):
    manifest_path = out_path.with_suffix(".qa.yaml")
    manifest = {
        "concept": {
            "id": concept.get("id"),
            "slug": concept.get("slug"),
            "name": concept.get("name"),
            "viewer_should_understand": concept.get("viewer_should_understand"),
            "must_show": concept.get("must_show", []),
            "label_strategy": concept.get("label_strategy"),
        },
        "render": {
            "model": MODEL,
            "size": size,
            "output": str(out_path),
            "status": render_status,
            "prompt": full_prompt,
            "refs_attached": [str(p) for p in attached],
            "refs_missing": missing,
        },
        "qa": {
            "status": "needs_review",
            "keep": None,
            "rubric": [
                "concept clarity",
                "required visual evidence",
                "taste and coherence",
                "bright inviting palette",
                "label strategy",
            ],
            "notes": "",
        },
    }
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    print(f"manifest: {manifest_path}")


def validate_concept_contract(concept, slug):
    errors = []
    if not str(concept.get("viewer_should_understand", "")).strip():
        errors.append("missing non-empty viewer_should_understand")
    must_show = concept.get("must_show")
    if not isinstance(must_show, list) or not any(str(item).strip() for item in must_show):
        errors.append("must_show must be a non-empty list")
    label_strategy = concept.get("label_strategy")
    if label_strategy not in LABEL_STRATEGIES:
        allowed = ", ".join(sorted(LABEL_STRATEGIES))
        errors.append(f"label_strategy must be one of: {allowed}")
    if errors:
        sys.exit(f"ERROR: concept '{slug}' has an invalid quality-gate contract: " + "; ".join(errors))


def main() -> int:
    ap = argparse.ArgumentParser(description="Render a Track B Yoshida hero image for a concept.")
    ap.add_argument("--concept", required=True, help="concept slug (matches `slug:` in registry)")
    ap.add_argument("--candidates", type=int, default=1, help="number of image variations")
    ap.add_argument("--registry", default="docs/diagrams/concepts.yaml")
    ap.add_argument("--refs", default="yoshida_hiroshi/", help="directory holding reference images")
    ap.add_argument("--out", default="docs/diagrams/", help="output directory for PNGs")
    ap.add_argument("--size", default="4K", choices=["2K", "4K"], help="requested image size")
    args = ap.parse_args()

    # 1. Load registry.
    reg_path = Path(args.registry)
    if not reg_path.is_file():
        sys.exit(f"ERROR: registry not found: {reg_path}")
    concepts = yaml.safe_load(reg_path.read_text())

    # 2. Find concept.
    concept = next((c for c in concepts if c.get("slug") == args.concept), None)
    if concept is None:
        sys.exit(f"ERROR: concept slug '{args.concept}' not found in {reg_path}")

    # 3. Stub guard.
    if "track_b" not in concept or "palette" not in concept:
        sys.exit(f"ERROR: concept '{args.concept}' is a stub, not yet authored (no track_b/palette).")

    validate_concept_contract(concept, args.concept)

    cid = concept["id"]
    listed_refs = concept["track_b"].get("refs", [])

    # 4. Ref-cap hard-fail (BEFORE any no-key check or network call).
    if len(listed_refs) > MAX_REFS:
        sys.exit(
            f"ERROR: concept '{args.concept}' lists {len(listed_refs)} reference images; "
            f"model {MODEL} accepts at most {MAX_REFS}. Will not silently truncate."
        )

    # 5. Resolve refs; warn (not fail) on missing files.
    refs_dir = Path(args.refs)
    attached, missing = [], []
    for name in listed_refs:
        p = refs_dir / name
        if p.is_file():
            attached.append(p)
        else:
            missing.append(name)
            print(f"WARNING: reference image missing, skipping: {p}", file=sys.stderr)

    # 6. Assemble prompt.
    label_guidance = LABEL_GUIDANCE[concept["label_strategy"]]
    full_prompt = (
        PREAMBLE
        + " "
        + concept["track_b"]["prompt"]
        + " Palette: "
        + concept["palette"]
        + ". "
        + label_guidance
    )

    # 7. Reproducibility log.
    out_dir = Path(args.out)
    out_paths = [out_dir / f"loam-hero-{cid:02d}-{args.concept}-c{i}.png" for i in range(1, args.candidates + 1)]
    print(f"concept: id={cid} slug={args.concept}")
    print(f"model: {MODEL}  size: {args.size}  candidates: {args.candidates}")
    print(f"full_prompt: {full_prompt}")
    print(f"refs attached ({len(attached)}): {[str(p) for p in attached]}")
    print(f"refs missing ({len(missing)}): {missing}")
    print(f"outputs: {[str(p) for p in out_paths]}")

    # 8. No-key SKIP branch (non-fatal) — after all arg/registry validation.
    if not os.environ.get("GEMINI_API_KEY"):
        print("SKIP: GEMINI_API_KEY not set — no render performed (scaffold intact).")
        return 0

    # 9. API call — shape verified against installed google-genai SDK (image_config, not response_format).
    from google import genai
    from google.genai.types import GenerateContentConfig, ImageConfig

    ref_images = [Image.open(p) for p in attached]
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    config = GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=ImageConfig(aspect_ratio="16:9", image_size=args.size),
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    for out_path in out_paths:
        resp = client.models.generate_content(
            model=MODEL,
            contents=[full_prompt, *ref_images],
            config=config,
        )
        saved = False
        for part in resp.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                Image.open(io.BytesIO(part.inline_data.data)).save(out_path)
                print(f"saved: {out_path}")
                write_qa_manifest(out_path, concept, full_prompt, attached, missing, args.size, "saved")
                saved = True
                break
        if not saved:
            print(f"WARNING: no image data returned for {out_path}", file=sys.stderr)
            write_qa_manifest(out_path, concept, full_prompt, attached, missing, args.size, "no_image_data")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
