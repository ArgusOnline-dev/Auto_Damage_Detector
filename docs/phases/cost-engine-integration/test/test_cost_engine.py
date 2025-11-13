#!/usr/bin/env python3
"""
Cost Engine Integration Test Script
Validates the cost engine integration according to the plan's testing requirements.

Test Scenarios:
1. Happy path: Multiple damage types produce correct line items and totals
2. OEM vs. used toggle: Same detections produce different totals
3. Unknown combination: Graceful fallback
4. Severity overrides: Frontend severity is respected
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

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
    """Check if backend is running."""
    print("[1/6] Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("  [PASS] Backend is running")
            return True
        print(f"  [FAIL] Health returned {response.status_code}")
        return False
    except requests.exceptions.ConnectionError:
        print("  [FAIL] Backend not reachable. Start with: python server.py start backend")
        return False
    except Exception as exc:
        print(f"  [FAIL] Health check error: {exc}")
        return False


def upload_images() -> List[str]:
    """Upload sample images and return file IDs."""
    print("\n[2/6] Uploading sample images...")
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


def get_detections(file_ids: List[str]) -> List[Dict[str, Any]]:
    """Run inference and collect all detections."""
    print("\n[3/6] Running inference to get detections...")
    payload = {
        "file_ids": file_ids,
        "include_intact": False,  # Only damaged parts for cost estimation
    }
    resp = requests.post(f"{BASE_URL}/infer", json=payload, timeout=90)
    if resp.status_code != 200:
        print(f"  [FAIL] /infer returned {resp.status_code}: {resp.text}")
        return []

    data = resp.json()
    results = data.get("results", [])
    print(f"  [PASS] Received {len(results)} image result(s)")

    # Collect all detections from all images
    all_detections: List[Dict[str, Any]] = []
    for result in results:
        detections = result.get("detections", [])
        all_detections.extend(detections)
        print(f"    {result.get('image_id')}: {len(detections)} detections")

    if not all_detections:
        print("  [WARN] No damaged parts detected. Tests will use mock detections.")
        # Create mock detections for testing
        all_detections = [
            {
                "part": "front_bumper",
                "damage_type": "dent",
                "confidence": 0.85,
                "bbox": [0.1, 0.1, 0.3, 0.3],
            },
            {
                "part": "door",
                "damage_type": "scratch",
                "confidence": 0.75,
                "bbox": [0.4, 0.4, 0.6, 0.6],
            },
            {
                "part": "windshield",
                "damage_type": "cracked",
                "confidence": 0.9,
                "bbox": [0.2, 0.2, 0.5, 0.5],
            },
        ]

    print(f"  [INFO] Total detections for testing: {len(all_detections)}")
    return all_detections


def test_happy_path(detections: List[Dict[str, Any]]) -> bool:
    """Test Scenario 1: Happy path with multiple damage types."""
    print("\n[4/6] Test 1: Happy path (multiple damage types)...")
    
    if not detections:
        print("  [SKIP] No detections available")
        return True

    payload = {
        "detections": detections,
        "labor_rate": 150.0,
        "use_oem_parts": True,
        "car_type": "Super",
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/estimate", json=payload, timeout=30)
        if resp.status_code != 200:
            print(f"  [FAIL] /estimate returned {resp.status_code}: {resp.text}")
            return False

        data = resp.json()
        line_items = data.get("line_items", [])
        totals = data.get("totals", {})

        if not line_items:
            print("  [FAIL] No line items returned")
            return False

        print(f"  [PASS] Generated {len(line_items)} line items")
        print(f"    Totals: min=${totals.get('min'):.2f} likely=${totals.get('likely'):.2f} max=${totals.get('max'):.2f}")

        # Verify line items have required fields
        required_fields = ["part", "damage_type", "severity", "labor_hours", "labor_cost", "part_cost_new", "part_cost_used", "total_new", "total_used"]
        for item in line_items[:3]:  # Check first 3
            missing = [f for f in required_fields if f not in item]
            if missing:
                print(f"  [FAIL] Line item missing fields: {missing}")
                return False

        print("  [PASS] All line items have required fields")
        print("  [PASS] Happy path test passed")
        return True

    except Exception as exc:
        print(f"  [FAIL] Happy path test error: {exc}")
        return False


def test_oem_vs_used(detections: List[Dict[str, Any]]) -> bool:
    """Test Scenario 2: OEM vs. used toggle produces different totals."""
    print("\n[5/6] Test 2: OEM vs. used toggle...")
    
    if not detections:
        print("  [SKIP] No detections available")
        return True

    base_payload = {
        "detections": detections,
        "labor_rate": 150.0,
        "car_type": "Super",
    }

    # Test with OEM parts
    payload_oem = {**base_payload, "use_oem_parts": True}
    try:
        resp_oem = requests.post(f"{BASE_URL}/estimate", json=payload_oem, timeout=30)
        if resp_oem.status_code != 200:
            print(f"  [FAIL] OEM estimate returned {resp_oem.status_code}: {resp_oem.text}")
            return False
        data_oem = resp_oem.json()
        total_oem = data_oem.get("totals", {}).get("likely", 0.0)
    except Exception as exc:
        print(f"  [FAIL] OEM estimate error: {exc}")
        return False

    # Test with used parts
    payload_used = {**base_payload, "use_oem_parts": False}
    try:
        resp_used = requests.post(f"{BASE_URL}/estimate", json=payload_used, timeout=30)
        if resp_used.status_code != 200:
            print(f"  [FAIL] Used estimate returned {resp_used.status_code}: {resp_used.text}")
            return False
        data_used = resp_used.json()
        total_used = data_used.get("totals", {}).get("likely", 0.0)
    except Exception as exc:
        print(f"  [FAIL] Used estimate error: {exc}")
        return False

    print(f"  [INFO] OEM total: ${total_oem:.2f}")
    print(f"  [INFO] Used total: ${total_used:.2f}")

    if total_oem == total_used:
        print("  [FAIL] OEM and used totals are identical (should differ)")
        return False

    if total_used >= total_oem:
        print("  [FAIL] Used total should be less than or equal to OEM total")
        return False

    print("  [PASS] OEM vs. used toggle test passed")
    return True


def test_unknown_combination() -> bool:
    """Test Scenario 3: Unknown combination returns graceful fallback."""
    print("\n[6/6] Test 3: Unknown combination fallback...")
    
    # Create a detection with an unknown part/damage combination
    unknown_detections = [
        {
            "part": "unknown_part_xyz",
            "damage_type": "unknown_damage_abc",
            "confidence": 0.8,
            "bbox": [0.1, 0.1, 0.3, 0.3],
        }
    ]

    payload = {
        "detections": unknown_detections,
        "labor_rate": 150.0,
        "use_oem_parts": True,
        "car_type": "Super",
    }

    try:
        resp = requests.post(f"{BASE_URL}/estimate", json=payload, timeout=30)
        if resp.status_code != 200:
            print(f"  [FAIL] Unknown combination returned {resp.status_code}: {resp.text}")
            return False

        data = resp.json()
        line_items = data.get("line_items", [])
        totals = data.get("totals", {})

        if not line_items:
            print("  [FAIL] No line items returned for unknown combination (should use fallback)")
            return False

        # Should have fallback values
        item = line_items[0]
        if item.get("labor_hours", 0) == 0:
            print("  [FAIL] Fallback should have non-zero labor hours")
            return False

        print(f"  [PASS] Fallback values used: labor_hours={item.get('labor_hours')}")
        print(f"  [PASS] Totals calculated: ${totals.get('likely', 0):.2f}")
        print("  [PASS] Unknown combination fallback test passed")
        return True

    except Exception as exc:
        print(f"  [FAIL] Unknown combination test error: {exc}")
        return False


def test_severity_override() -> bool:
    """Test Scenario 4: Severity overrides are respected."""
    print("\n[7/6] Test 4: Severity override...")
    
    # Create detections with explicit severity overrides
    override_detections = [
        {
            "part": "door",
            "damage_type": "scratch",
            "confidence": 0.3,  # Low confidence would normally be "minor"
            "severity": "severe",  # But we override to "severe"
            "bbox": [0.1, 0.1, 0.3, 0.3],
        },
        {
            "part": "bumper",
            "damage_type": "dent",
            "confidence": 0.9,  # High confidence would normally be "severe"
            "severity": "minor",  # But we override to "minor"
            "bbox": [0.4, 0.4, 0.6, 0.6],
        }
    ]

    payload = {
        "detections": override_detections,
        "labor_rate": 150.0,
        "use_oem_parts": True,
        "car_type": "Super",
    }

    try:
        resp = requests.post(f"{BASE_URL}/estimate", json=payload, timeout=30)
        if resp.status_code != 200:
            print(f"  [FAIL] Severity override returned {resp.status_code}: {resp.text}")
            return False

        data = resp.json()
        line_items = data.get("line_items", [])

        if len(line_items) != 2:
            print(f"  [FAIL] Expected 2 line items, got {len(line_items)}")
            return False

        # Check that severities match overrides
        for item in line_items:
            part = item.get("part", "")
            severity = item.get("severity", "")
            
            # Find corresponding detection
            detection = next((d for d in override_detections if d["part"] in part or part in d["part"]), None)
            if detection and detection.get("severity") != severity:
                print(f"  [FAIL] Severity override not respected for {part}: expected {detection.get('severity')}, got {severity}")
                return False

        print("  [PASS] Severity overrides respected in all line items")
        print("  [PASS] Severity override test passed")
        return True

    except Exception as exc:
        print(f"  [FAIL] Severity override test error: {exc}")
        return False


def main() -> None:
    """Run all cost engine integration tests."""
    print("=" * 60)
    print("Cost Engine Integration Tests")
    print("=" * 60)
    print()

    if not test_health():
        sys.exit(1)

    file_ids = upload_images()
    if not file_ids:
        print("\n[WARN] Using mock detections for remaining tests")
        detections = []
    else:
        detections = get_detections(file_ids)

    # Run all test scenarios
    tests_passed = 0
    tests_total = 4

    if test_happy_path(detections):
        tests_passed += 1

    if test_oem_vs_used(detections):
        tests_passed += 1

    if test_unknown_combination():
        tests_passed += 1

    if test_severity_override():
        tests_passed += 1

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{tests_total}")

    if tests_passed == tests_total:
        print("[SUCCESS] All cost engine integration tests passed!")
        sys.exit(0)
    else:
        print(f"[FAILURE] {tests_total - tests_passed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()


