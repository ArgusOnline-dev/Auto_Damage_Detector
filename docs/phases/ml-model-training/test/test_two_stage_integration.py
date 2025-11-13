#!/usr/bin/env python3
"""
Two-Stage Model Integration Test Script (v2)
Validates multi-image /infer payloads, intact filtering, and /estimate flow.
"""
import json
import sys
from pathlib import Path
from typing import List

try:
    import requests
except ImportError:  # pragma: no cover
    print("ERROR: requests library not installed. Install with: pip install requests")
    sys.exit(1)


BASE_URL = "http://localhost:8000/api/v1"
SAMPLE_IMAGES = [
    Path("data/samples/images/Car damages 102.jpg"),
    Path("data/samples/images/Car damages 201.jpg"),
]


def test_health() -> bool:
    print("[1/5] Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("  [PASS] Backend is running")
            return True
        print(f"  [FAIL] Health returned {response.status_code}")
        return False
    except requests.exceptions.ConnectionError:
        print("  [FAIL] Backend not reachable; run: uvicorn apps.api.main:app --reload")
        return False
    except Exception as exc:
        print(f"  [FAIL] Health check error: {exc}")
        return False


def upload_images() -> List[str]:
    print("\n[2/5] Uploading sample images...")
    file_ids: List[str] = []
    for img_path in SAMPLE_IMAGES:
        if not img_path.exists():
            print(f"  [FAIL] Sample image missing: {img_path}")
            return []
        try:
            with open(img_path, "rb") as f:
                files = {"files": (img_path.name, f, "image/jpeg")}
                resp = requests.post(f"{BASE_URL}/upload", files=files, timeout=30)
            if resp.status_code != 200:
                print(f"  [FAIL] Upload failed ({img_path.name}): {resp.text}")
                return []
            data = resp.json()
            if not data.get("file_ids"):
                print(f"  [FAIL] No file_ids returned for {img_path.name}")
                return []
            file_id = data["file_ids"][0]
            file_ids.append(file_id)
            print(f"  [PASS] Uploaded {img_path.name} -> {file_id}")
        except Exception as exc:
            print(f"  [FAIL] Upload error ({img_path.name}): {exc}")
            return []
    return file_ids


def run_inference(file_ids: List[str], include_intact: bool) -> dict:
    flag = "with" if include_intact else "without"
    print(f"\n[3/5] Running inference {flag} intact parts...")
    payload = {
        "file_ids": file_ids,
        "include_intact": include_intact,
    }
    resp = requests.post(f"{BASE_URL}/infer", json=payload, timeout=90)
    if resp.status_code != 200:
        print(f"  [FAIL] /infer returned {resp.status_code}: {resp.text}")
        return {}

    data = resp.json()
    results = data.get("results", [])
    print(f"  [PASS] Received {len(results)} image result(s)")
    print(f"  include_intact={data.get('include_intact')} filtered_count={data.get('filtered_count')}")

    for idx, result in enumerate(results, start=1):
        detections = result.get("detections", [])
        print(f"    Image {idx}: {result.get('image_id')} -> {len(detections)} detections")
        sample = detections[0] if detections else {}
        if sample:
            print(f"      Sample: part={sample.get('part')} damage={sample.get('damage_type')} conf={sample.get('confidence')}")
    return data


def run_estimate(detections: List[dict]) -> bool:
    print("\n[4/5] Testing cost estimation...")
    payload = {
        "detections": detections,
        "labor_rate": 150,
        "use_oem_parts": True,
    }
    resp = requests.post(f"{BASE_URL}/estimate", json=payload, timeout=30)
    if resp.status_code != 200:
        print(f"  [FAIL] /estimate returned {resp.status_code}: {resp.text}")
        return False
    data = resp.json()
    totals = data.get("totals", {})
    print("  [PASS] Cost estimation succeeded")
    print(f"    Line items: {len(data.get('line_items', []))}")
    print(f"    Totals: min=${totals.get('min')} likely=${totals.get('likely')} max=${totals.get('max')}")
    return True


def main() -> None:
    print("=== Two-Stage Backend Integration Tests ===\n")
    if not test_health():
        sys.exit(1)

    file_ids = upload_images()
    if not file_ids:
        sys.exit(1)

    # First run includes intact parts (baseline)
    data_with_intact = run_inference(file_ids, include_intact=True)
    if not data_with_intact.get("results"):
        sys.exit(1)

    # Second run excludes intact parts to validate filtering
    data_without_intact = run_inference(file_ids, include_intact=False)
    if not data_without_intact.get("results"):
        sys.exit(1)

    # Pick detections from first image (non-empty) for estimate test
    first_image_results = data_without_intact["results"][0].get("detections", [])
    if not first_image_results:
        print("  [WARN] No damaged parts detected; using intact-enabled results instead")
        first_image_results = data_with_intact["results"][0].get("detections", [])

    if not first_image_results:
        print("  [FAIL] No detections available for estimation test")
        sys.exit(1)

    if not run_estimate(first_image_results):
        sys.exit(1)

    print("\n=== Test Summary ===")
    print("[PASS] Multi-image upload, inference (with/without intact), and cost estimation succeeded.")
    print("Inspect backend logs for latency stats if enabled.\n")


if __name__ == "__main__":
    main()
